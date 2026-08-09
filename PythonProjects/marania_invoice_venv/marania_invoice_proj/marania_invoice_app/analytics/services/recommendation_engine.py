"""
Recommendation engine for trend analytics.
"""
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from enum import Enum

from marania_invoice_app.analytics.services.models import (
    ProductSpecificationTrend,
    TrendThresholds
)
from marania_invoice_app.analytics.services.season_analyzer import SeasonAnalyzer


class TrendClassification(Enum):
    """Trend classification enum."""
    STRONG_GROWTH = "Strong Growth"
    MODERATE_GROWTH = "Moderate Growth"
    STABLE = "Stable"
    MODERATE_DECLINE = "Moderate Decline"
    STRONG_DECLINE = "Strong Decline"
    INSUFFICIENT_DATA = "Insufficient Data"


class TrendConfidence(Enum):
    """Trend confidence enum."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INSUFFICIENT_DATA = "Insufficient Data"


class RecommendationCategory(Enum):
    """Recommendation category enum."""
    RECOMMENDED = "Recommended"
    EMERGING = "Emerging"
    STABLE = "Stable"
    DECLINING = "Declining"
    SEASONAL = "Seasonal"
    WATCH = "Watch"


class RecommendationEngine:
    """Engine for generating trend recommendations."""
    
    def __init__(self, thresholds: TrendThresholds = None):
        """
        Initialize recommendation engine.
        
        Args:
            thresholds: Trend thresholds for classification
        """
        self.thresholds = thresholds or TrendThresholds()
        self.season_analyzer = SeasonAnalyzer()
    
    def classify_trend(self, yoy_growth: Optional[float]) -> TrendClassification:
        """
        Classify trend based on YoY growth.
        
        Args:
            yoy_growth: Year-over-year growth percentage
            
        Returns:
            TrendClassification enum value
        """
        if yoy_growth is None:
            return TrendClassification.INSUFFICIENT_DATA
        
        if yoy_growth >= self.thresholds.strong_growth:
            return TrendClassification.STRONG_GROWTH
        elif yoy_growth >= self.thresholds.moderate_growth:
            return TrendClassification.MODERATE_GROWTH
        elif yoy_growth >= self.thresholds.moderate_decline:
            return TrendClassification.STABLE
        elif yoy_growth >= self.thresholds.strong_decline:
            return TrendClassification.MODERATE_DECLINE
        else:
            return TrendClassification.STRONG_DECLINE
    
    def calculate_confidence(self, num_seasons: int, order_count: int) -> TrendConfidence:
        """
        Calculate trend confidence based on data availability.
        
        Args:
            num_seasons: Number of comparable seasons
            order_count: Total order count
            
        Returns:
            TrendConfidence enum value
        """
        if num_seasons < 2:
            return TrendConfidence.INSUFFICIENT_DATA
        
        if num_seasons >= 3 and order_count >= 50:
            return TrendConfidence.HIGH
        
        if num_seasons >= 2 and order_count >= 20:
            return TrendConfidence.MEDIUM
        
        return TrendConfidence.LOW
    
    def calculate_multi_year_score(self, season_data: Dict[int, Dict]) -> float:
        """
        Calculate multi-year trend score.
        
        Args:
            season_data: Dictionary of year to season statistics
            
        Returns:
            Multi-year trend score (0-100)
        """
        years = sorted(season_data.keys())
        
        if len(years) < 2:
            return 0.0
        
        # Calculate CAGR (Compound Annual Growth Rate)
        if len(years) >= 2:
            first_year = years[0]
            last_year = years[-1]
            first_sales = season_data[first_year]['sales']
            last_sales = season_data[last_year]['sales']
            
            if first_sales == 0:
                return 0.0
            
            num_years = last_year - first_year
            if num_years == 0:
                return 0.0
            
            # CAGR formula: (End/Start)^(1/n) - 1
            cagr = (float(last_sales / first_sales) ** (1 / num_years)) - 1
            cagr_percentage = cagr * 100
            
            # Normalize to 0-100 score
            # Assume -50% to +50% range maps to 0-100
            score = max(0, min(100, (cagr_percentage + 50) * 1))
            
            return score
        
        return 0.0
    
    def calculate_consistency_score(self, season_data: Dict[int, Dict]) -> float:
        """
        Calculate consistency of growth across seasons.
        
        Args:
            season_data: Dictionary of year to season statistics
            
        Returns:
            Consistency score (0-100)
        """
        years = sorted(season_data.keys())
        
        if len(years) < 3:
            return 50.0  # Neutral score for insufficient data
        
        # Calculate year-over-year changes
        changes = []
        for i in range(1, len(years)):
            prev_year = years[i - 1]
            curr_year = years[i]
            
            prev_sales = season_data[prev_year]['sales']
            curr_sales = season_data[curr_year]['sales']
            
            if prev_sales > 0:
                change = float((curr_sales - prev_sales) / prev_sales)
                changes.append(change)
        
        if not changes:
            return 50.0
        
        # Calculate standard deviation of changes
        import statistics
        if len(changes) > 1:
            std_dev = statistics.stdev(changes)
            # Lower std_dev = more consistent
            # Normalize: assume std_dev of 0.5 is very inconsistent
            consistency = max(0, 100 - (std_dev * 200))
            return consistency
        
        return 50.0
    
    def generate_recommendation(
        self,
        product_spec_trend: ProductSpecificationTrend,
        season_data: Dict[int, Dict]
    ) -> Tuple[RecommendationCategory, str]:
        """
        Generate recommendation for a product/specification combination.
        
        Args:
            product_spec_trend: ProductSpecificationTrend object
            season_data: Dictionary of year to season statistics
            
        Returns:
            Tuple of (RecommendationCategory, reason)
        """
        # Get trend classification
        trend_class = self.classify_trend(product_spec_trend.yoy_growth)
        
        # Get confidence
        num_seasons = len(season_data)
        confidence = self.calculate_confidence(num_seasons, product_spec_trend.order_count)
        
        # Get seasonality
        seasonality = product_spec_trend.seasonality_score or 0
        
        # Get sales volume
        sales = float(product_spec_trend.total_sales)
        
        # Determine recommendation category
        if confidence == TrendConfidence.INSUFFICIENT_DATA:
            return RecommendationCategory.WATCH, "Insufficient historical data for reliable recommendation"
        
        if trend_class in [TrendClassification.STRONG_GROWTH, TrendClassification.MODERATE_GROWTH]:
            if sales >= 100000:  # High volume + growth
                return RecommendationCategory.RECOMMENDED, (
                    f"High sales volume ({sales:,.0f}) with {trend_class.value} trend. "
                    f"Strong candidate for upcoming season."
                )
            else:
                return RecommendationCategory.EMERGING, (
                    f"Strong growth trend ({trend_class.value}) but moderate sales volume. "
                    f"Emerging product to monitor."
                )
        
        if trend_class == TrendClassification.STABLE:
            if seasonality >= 70:
                return RecommendationCategory.SEASONAL, (
                    f"Stable demand with high seasonality ({seasonality:.1f}%). "
                    f"Consistently strong during selected season."
                )
            else:
                return RecommendationCategory.STABLE, (
                    f"Stable demand with consistent sales. "
                    f"Reliable product for inventory planning."
                )
        
        if trend_class in [TrendClassification.MODERATE_DECLINE, TrendClassification.STRONG_DECLINE]:
            if sales >= 50000:  # Meaningful volume but declining
                return RecommendationCategory.DECLINING, (
                    f"Significant sales volume but {trend_class.value} trend. "
                    f"Review inventory levels and customer demand."
                )
            else:
                return RecommendationCategory.WATCH, (
                    f"Declining trend with moderate sales volume. "
                    f"Monitor closely before restocking."
                )
        
        return RecommendationCategory.STABLE, "Stable product with consistent performance"
    
    def rank_recommendations(
        self,
        product_spec_trends: List[ProductSpecificationTrend]
    ) -> List[ProductSpecificationTrend]:
        """
        Rank product/specification combinations by recommendation score.
        
        Args:
            product_spec_trends: List of ProductSpecificationTrend objects
            
        Returns:
            Sorted list by recommendation score
        """
        def calculate_score(trend: ProductSpecificationTrend) -> float:
            """
            Calculate overall recommendation score.
            
            Score components:
            - 40%: Sales volume (normalized)
            - 30%: YoY growth (normalized)
            - 20%: Consistency
            - 10%: Seasonality
            """
            # Normalize sales (log scale to handle wide range)
            sales_score = min(100, (float(trend.total_sales) / 1000000) * 100)
            
            # Normalize growth
            growth = trend.yoy_growth or 0
            growth_score = max(0, min(100, (growth + 50) * 1))
            
            # Confidence score
            confidence_map = {
                TrendConfidence.HIGH: 100,
                TrendConfidence.MEDIUM: 70,
                TrendConfidence.LOW: 40,
                TrendConfidence.INSUFFICIENT_DATA: 10
            }
            confidence_score = confidence_map.get(
                TrendConfidence(trend.trend_confidence), 50
            )
            
            # Seasonality score
            seasonality_score = trend.seasonality_score or 50
            
            # Weighted score
            total_score = (
                0.40 * sales_score +
                0.30 * growth_score +
                0.20 * confidence_score +
                0.10 * seasonality_score
            )
            
            return total_score
        
        # Calculate scores and sort
        scored_trends = [(trend, calculate_score(trend)) for trend in product_spec_trends]
        scored_trends.sort(key=lambda x: x[1], reverse=True)
        
        return [trend for trend, score in scored_trends]
    
    def generate_executive_summary(self, product_spec_trends: List[ProductSpecificationTrend]) -> str:
        """
        Generate executive summary from trend data.
        
        Args:
            product_spec_trends: List of ProductSpecificationTrend objects
            
        Returns:
            Executive summary text
        """
        if not product_spec_trends:
            return "No trend data available for summary generation."
        
        # Get top performers
        ranked_trends = self.rank_recommendations(product_spec_trends)
        
        if not ranked_trends:
            return "No trend data available for summary generation."
        
        top_trend = ranked_trends[0]
        
        # Count by trend classification
        trend_counts = {}
        for trend in product_spec_trends:
            classification = trend.trend_classification
            trend_counts[classification] = trend_counts.get(classification, 0) + 1
        
        # Build summary
        summary_parts = []
        
        # Top product/spec
        summary_parts.append(
            f"{top_trend.product} / {top_trend.specification} is the strongest "
            f"performer by sales volume ({top_trend.total_sales:,.0f})."
        )
        
        # Growth leader
        growth_leaders = [t for t in product_spec_trends if t.yoy_growth and t.yoy_growth > 0]
        if growth_leaders:
            growth_leader = max(growth_leaders, key=lambda x: x.yoy_growth or 0)
            summary_parts.append(
                f"{growth_leader.product} / {growth_leader.specification} "
                f"shows the highest growth ({growth_leader.yoy_growth:+.1f}%)."
            )
        
        # Declining products
        declining = [t for t in product_spec_trends if t.yoy_growth and t.yoy_growth < -10]
        if declining:
            summary_parts.append(
                f"{len(declining)} product/specification combinations show declining trends "
                f"and may require attention."
            )
        
        # Overall trend
        if trend_counts.get("Strong Growth", 0) > trend_counts.get("Strong Decline", 0):
            summary_parts.append("Overall market trend is positive with more products showing growth.")
        elif trend_counts.get("Strong Decline", 0) > trend_counts.get("Strong Growth", 0):
            summary_parts.append("Overall market trend shows declining demand across multiple products.")
        else:
            summary_parts.append("Market trends are mixed with both growth and decline across products.")
        
        return " ".join(summary_parts)
