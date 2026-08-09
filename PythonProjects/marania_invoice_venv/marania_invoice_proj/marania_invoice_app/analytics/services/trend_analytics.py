"""
Main trend analytics service.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from django.db.models import Sum, Count, Q
from django.db import models

from marania_invoice_app.models import Sales
from marania_invoice_app.analytics.services.product_parser import ProductParser
from marania_invoice_app.analytics.services.specification_parser import SpecificationParser
from marania_invoice_app.analytics.services.models import (
    NormalizedSale,
    TrendFilters,
    TrendThresholds,
    ProductSpecificationTrend
)


class TrendAnalyticsService:
    """Service for trend analytics calculations."""
    
    def __init__(self):
        self.product_parser = ProductParser()
        self.spec_parser = SpecificationParser()
        self.thresholds = TrendThresholds()
    
    def normalize_sales(self, sales_queryset) -> List[NormalizedSale]:
        """
        Convert Sales queryset to normalized sale records.
        
        Args:
            sales_queryset: Django Sales queryset
            
        Returns:
            List of NormalizedSale objects
        """
        normalized_sales = []
        
        for sale in sales_queryset:
            # Parse product code
            product_code = self.product_parser.extract_product_code(sale.twine)
            
            # Parse specification
            mm, md, normalized_spec = self.spec_parser.parse_specification(sale.speification)
            
            # Create normalized sale record
            normalized_sale = NormalizedSale(
                sales_key=sale.sales_key,
                order_no=sale.order_no,
                sales_entry_date=sale.sales_entry_date,
                product_code=product_code,
                mm=mm,
                md=md,
                specification=sale.speification or '',
                normalized_specification=normalized_spec,
                total_amount=sale.total_amount or Decimal('0'),
                processed_weight=sale.processed_weight or Decimal('0'),
                piece_count=sale.piece_count,
                customer=sale.customer or '',
                colour=sale.colour or '',
                status=sale.status,
                raw_specification=sale.speification or ''
            )
            
            normalized_sales.append(normalized_sale)
        
        return normalized_sales
    
    def apply_filters(self, sales_queryset: models.QuerySet, filters: TrendFilters) -> models.QuerySet:
        """
        Apply filters to Sales queryset.
        
        Args:
            sales_queryset: Django Sales queryset
            filters: TrendFilters object
            
        Returns:
            Filtered queryset
        """
        queryset = sales_queryset.all()
        
        # Date range filter
        if filters.start_date:
            queryset = queryset.filter(sales_entry_date__gte=filters.start_date)
        if filters.end_date:
            queryset = queryset.filter(sales_entry_date__lte=filters.end_date)
        
        # Product code filter (need to filter on twine field)
        if filters.product_codes:
            product_q = Q()
            for product in filters.product_codes:
                product_q |= Q(twine__icontains=product)
            queryset = queryset.filter(product_q)
        
        # Customer filter
        if filters.customers:
            queryset = queryset.filter(customer__in=filters.customers)
        
        # Status filter
        if filters.statuses:
            queryset = queryset.filter(status__in=filters.statuses)
        
        return queryset
    
    def get_summary(self, normalized_sales: List[NormalizedSale]) -> Dict:
        """
        Calculate summary statistics.
        
        Args:
            normalized_sales: List of normalized sale records
            
        Returns:
            Dictionary with summary statistics
        """
        if not normalized_sales:
            return {
                'orders': 0,
                'sales': Decimal('0'),
                'weight': Decimal('0'),
                'pieces': 0,
                'products': 0,
                'specifications': 0
            }
        
        total_orders = len(normalized_sales)
        total_sales = sum(s.total_amount for s in normalized_sales)
        total_weight = sum(s.processed_weight for s in normalized_sales)
        total_pieces = sum(s.piece_count or 0 for s in normalized_sales)
        
        unique_products = len(set(s.product_code for s in normalized_sales))
        unique_specs = len(set(s.normalized_specification for s in normalized_sales))
        
        return {
            'orders': total_orders,
            'sales': total_sales,
            'weight': total_weight,
            'pieces': total_pieces,
            'products': unique_products,
            'specifications': unique_specs
        }
    
    def get_monthly_trend(self, normalized_sales: List[NormalizedSale], metric: str = 'sales') -> List[Dict]:
        """
        Calculate monthly trend data.
        
        Args:
            normalized_sales: List of normalized sale records
            metric: Metric to use (sales, weight, pieces, orders)
            
        Returns:
            List of monthly data points
        """
        monthly_data = {}
        
        for sale in normalized_sales:
            year = sale.sales_entry_date.year
            month = sale.sales_entry_date.month
            key = f"{year}-{month:02d}"
            
            if key not in monthly_data:
                monthly_data[key] = {
                    'year': year,
                    'month': month,
                    'sales': Decimal('0'),
                    'weight': Decimal('0'),
                    'pieces': 0,
                    'orders': 0
                }
            
            monthly_data[key]['sales'] += sale.total_amount
            monthly_data[key]['weight'] += sale.processed_weight
            monthly_data[key]['pieces'] += sale.piece_count or 0
            monthly_data[key]['orders'] += 1
        
        # Sort by date
        sorted_data = sorted(monthly_data.values(), key=lambda x: (x['year'], x['month']))
        
        return sorted_data
    
    def get_product_trends(self, normalized_sales: List[NormalizedSale], metric: str = 'sales', top_n: int = 10) -> List[Dict]:
        """
        Calculate product trends.
        
        Args:
            normalized_sales: List of normalized sale records
            metric: Metric to use for sorting
            top_n: Number of top products to return
            
        Returns:
            List of product trend data
        """
        product_data = {}
        
        for sale in normalized_sales:
            product = sale.product_code
            
            if product not in product_data:
                product_data[product] = {
                    'product': product,
                    'sales': Decimal('0'),
                    'weight': Decimal('0'),
                    'pieces': 0,
                    'orders': 0
                }
            
            product_data[product]['sales'] += sale.total_amount
            product_data[product]['weight'] += sale.processed_weight
            product_data[product]['pieces'] += sale.piece_count or 0
            product_data[product]['orders'] += 1
        
        # Sort by selected metric
        sorted_data = sorted(product_data.values(), key=lambda x: x[metric], reverse=True)
        
        return sorted_data[:top_n]
    
    def get_specification_trends(self, normalized_sales: List[NormalizedSale], metric: str = 'sales', top_n: int = 10) -> List[Dict]:
        """
        Calculate specification trends (MM-MD combinations).
        
        Args:
            normalized_sales: List of normalized sale records
            metric: Metric to use for sorting
            top_n: Number of top specifications to return
            
        Returns:
            List of specification trend data
        """
        spec_data = {}
        
        for sale in normalized_sales:
            spec = sale.normalized_specification
            
            if spec not in spec_data:
                spec_data[spec] = {
                    'specification': spec,
                    'mm': sale.mm,
                    'md': sale.md,
                    'sales': Decimal('0'),
                    'weight': Decimal('0'),
                    'pieces': 0,
                    'orders': 0
                }
            
            spec_data[spec]['sales'] += sale.total_amount
            spec_data[spec]['weight'] += sale.processed_weight
            spec_data[spec]['pieces'] += sale.piece_count or 0
            spec_data[spec]['orders'] += 1
        
        # Sort by selected metric
        sorted_data = sorted(spec_data.values(), key=lambda x: x[metric], reverse=True)
        
        return sorted_data[:top_n]
    
    def get_product_specification_matrix(self, normalized_sales: List[NormalizedSale]) -> List[Dict]:
        """
        Calculate product × specification matrix.
        
        Args:
            normalized_sales: List of normalized sale records
            
        Returns:
            List of product-specification combinations
        """
        matrix_data = {}
        
        for sale in normalized_sales:
            key = f"{sale.product_code}|{sale.normalized_specification}"
            
            if key not in matrix_data:
                matrix_data[key] = {
                    'product': sale.product_code,
                    'specification': sale.normalized_specification,
                    'mm': sale.mm,
                    'md': sale.md,
                    'sales': Decimal('0'),
                    'weight': Decimal('0'),
                    'pieces': 0,
                    'orders': 0
                }
            
            matrix_data[key]['sales'] += sale.total_amount
            matrix_data[key]['weight'] += sale.processed_weight
            matrix_data[key]['pieces'] += sale.piece_count or 0
            matrix_data[key]['orders'] += 1
        
        # Sort by sales
        sorted_data = sorted(matrix_data.values(), key=lambda x: x['sales'], reverse=True)
        
        return sorted_data
    
    def get_data_quality(self, normalized_sales: List[NormalizedSale]) -> Dict:
        """
        Calculate data quality metrics.
        
        Args:
            normalized_sales: List of normalized sale records
            
        Returns:
            Dictionary with data quality information
        """
        total_records = len(normalized_sales)
        
        records_with_product = sum(1 for s in normalized_sales if s.product_code != "Unknown")
        records_with_valid_spec = sum(1 for s in normalized_sales if s.normalized_specification != "Unknown")
        records_with_missing_spec = sum(1 for s in normalized_sales if not s.raw_specification)
        records_with_invalid_spec = sum(1 for s in normalized_sales if s.raw_specification and s.normalized_specification == "Unknown")
        
        return {
            'total_records': total_records,
            'records_with_product': records_with_product,
            'records_with_valid_spec': records_with_valid_spec,
            'records_with_missing_spec': records_with_missing_spec,
            'records_with_invalid_spec': records_with_invalid_spec
        }
