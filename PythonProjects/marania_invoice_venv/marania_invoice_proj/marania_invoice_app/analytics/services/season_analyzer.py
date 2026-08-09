"""
Season analyzer for custom season logic and year-over-year comparison.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
import calendar

from marania_invoice_app.analytics.services.models import NormalizedSale, TrendFilters


class SeasonAnalyzer:
    """Analyzer for season-based calculations."""
    
    @staticmethod
    def get_season_dates(year: int, start_month: int, start_day: int, end_month: int, end_day: int) -> Tuple[date, date]:
        """
        Get start and end dates for a season in a given year.
        
        Handles cross-year seasons (e.g., Oct 1 - Feb 28).
        
        Args:
            year: Calendar year
            start_month: Season start month (1-12)
            start_day: Season start day
            end_month: Season end month (1-12)
            end_day: Season end day
            
        Returns:
            Tuple of (start_date, end_date)
        """
        # Determine if season crosses year boundary
        crosses_year = end_month < start_month or (end_month == start_month and end_day < start_day)
        
        if crosses_year:
            # Season spans two years
            # Start date is in the given year
            start_date = date(year, start_month, start_day)
            
            # End date is in the next year
            end_year = year + 1
            # Handle leap year for February
            if end_month == 2 and end_day == 29:
                # If next year is not a leap year, use Feb 28
                if not calendar.isleap(end_year):
                    end_day = 28
            end_date = date(end_year, end_month, end_day)
        else:
            # Season is within the same year
            start_date = date(year, start_month, start_day)
            end_date = date(year, end_month, end_day)
        
        return start_date, end_date
    
    @staticmethod
    def filter_by_season(normalized_sales: List[NormalizedSale], start_month: int, start_day: int, end_month: int, end_day: int) -> List[NormalizedSale]:
        """
        Filter sales records by season across all years.
        
        Args:
            normalized_sales: List of normalized sale records
            start_month: Season start month (1-12)
            start_day: Season start day
            end_month: Season end month (1-12)
            end_day: Season end day
            
        Returns:
            Filtered list of sales within the season
        """
        filtered_sales = []
        
        # Get all years in the data
        years = set(sale.sales_entry_date.year for sale in normalized_sales)
        
        for year in years:
            season_start, season_end = SeasonAnalyzer.get_season_dates(year, start_month, start_day, end_month, end_day)
            
            for sale in normalized_sales:
                if sale.sales_entry_date.year == year:
                    if season_start <= sale.sales_entry_date <= season_end:
                        filtered_sales.append(sale)
        
        return filtered_sales
    
    @staticmethod
    def get_season_comparison(normalized_sales: List[NormalizedSale], start_month: int, start_day: int, end_month: int, end_day: int) -> Dict[int, Dict]:
        """
        Get year-by-year season comparison.
        
        Args:
            normalized_sales: List of normalized sale records
            start_month: Season start month (1-12)
            start_day: Season start day
            end_month: Season end month (1-12)
            end_day: Season end day
            
        Returns:
            Dictionary mapping year to season statistics
        """
        years = set(sale.sales_entry_date.year for sale in normalized_sales)
        season_data = {}
        
        for year in sorted(years):
            season_start, season_end = SeasonAnalyzer.get_season_dates(year, start_month, start_day, end_month, end_day)
            
            # Filter sales for this year's season
            year_season_sales = [
                sale for sale in normalized_sales
                if sale.sales_entry_date.year == year and season_start <= sale.sales_entry_date <= season_end
            ]
            
            if year_season_sales:
                total_sales = sum(s.total_amount for s in year_season_sales)
                total_weight = sum(s.processed_weight for s in year_season_sales)
                total_pieces = sum(s.piece_count or 0 for s in year_season_sales)
                order_count = len(year_season_sales)
                
                season_data[year] = {
                    'start_date': season_start,
                    'end_date': season_end,
                    'sales': total_sales,
                    'weight': total_weight,
                    'pieces': total_pieces,
                    'orders': order_count
                }
        
        return season_data
    
    @staticmethod
    def calculate_yoy_growth(current_value: Decimal, previous_value: Decimal) -> Optional[float]:
        """
        Calculate year-over-year growth percentage.
        
        Args:
            current_value: Current period value
            previous_value: Previous period value
            
        Returns:
            Growth percentage or None if previous value is zero
        """
        if previous_value == 0:
            return None
        
        growth = ((current_value - previous_value) / previous_value) * 100
        return float(growth)
    
    @staticmethod
    def calculate_seasonality_score(season_sales: Decimal, total_annual_sales: Decimal) -> Optional[float]:
        """
        Calculate seasonality score (percentage of annual sales in season).
        
        Args:
            season_sales: Sales during the season
            total_annual_sales: Total annual sales
            
        Returns:
            Seasonality percentage or None if total is zero
        """
        if total_annual_sales == 0:
            return None
        
        seasonality = (season_sales / total_annual_sales) * 100
        return float(seasonality)
    
    @staticmethod
    def get_peak_month(normalized_sales: List[NormalizedSale]) -> Optional[Tuple[int, Decimal]]:
        """
        Find the peak sales month.
        
        Args:
            normalized_sales: List of normalized sale records
            
        Returns:
            Tuple of (month_number, sales_value) or None if no data
        """
        monthly_sales = {}
        
        for sale in normalized_sales:
            month = sale.sales_entry_date.month
            if month not in monthly_sales:
                monthly_sales[month] = Decimal('0')
            monthly_sales[month] += sale.total_amount
        
        if not monthly_sales:
            return None
        
        peak_month = max(monthly_sales.items(), key=lambda x: x[1])
        return peak_month
