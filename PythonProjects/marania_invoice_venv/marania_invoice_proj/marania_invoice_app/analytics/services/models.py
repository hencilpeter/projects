"""
Data models for analytics.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class NormalizedSale:
    """Normalized sale record for analytics."""
    sales_key: int
    order_no: str
    sales_entry_date: date
    product_code: str
    mm: Optional[Decimal]
    md: Optional[Decimal]
    specification: str
    normalized_specification: str
    total_amount: Decimal
    processed_weight: Decimal
    piece_count: Optional[int]
    customer: str
    colour: str
    status: str
    raw_specification: str


@dataclass
class TrendFilters:
    """Filter object for trend analytics queries."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    product_codes: list = None
    mm_values: list = None
    md_values: list = None
    customers: list = None
    statuses: list = None
    season_start_month: Optional[int] = None
    season_start_day: Optional[int] = None
    season_end_month: Optional[int] = None
    season_end_day: Optional[int] = None
    metric: str = 'sales'  # sales, weight, pieces, orders
    
    def __post_init__(self):
        """Initialize default values for lists."""
        if self.product_codes is None:
            self.product_codes = []
        if self.mm_values is None:
            self.mm_values = []
        if self.md_values is None:
            self.md_values = []
        if self.customers is None:
            self.customers = []
        if self.statuses is None:
            self.statuses = []


@dataclass
class TrendThresholds:
    """Thresholds for trend classification."""
    strong_growth: float = 20.0
    moderate_growth: float = 5.0
    moderate_decline: float = -5.0
    strong_decline: float = -20.0


@dataclass
class ProductSpecificationTrend:
    """Trend data for a product + specification combination."""
    product: str
    specification: str
    mm: Optional[Decimal]
    md: Optional[Decimal]
    total_sales: Decimal
    total_weight: Decimal
    total_pieces: int
    order_count: int
    yoy_growth: Optional[float]
    trend_classification: str
    trend_confidence: str
    seasonality_score: Optional[float]
    peak_month: Optional[int]
