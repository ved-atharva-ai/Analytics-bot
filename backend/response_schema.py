from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union


class ChartConfig(BaseModel):
    """Configuration for a single chart with data"""
    chart_type: str  # 'bar', 'line', 'pie', 'scatter', 'area'
    data: List[Dict[str, Any]]  # Actual data points
    x_key: str  # Key for x-axis
    y_key: Optional[str] = None  # Key for y-axis (optional for pie charts)
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    colors: Optional[List[str]] = None


class KPICard(BaseModel):
    """Key Performance Indicator card"""
    label: str
    value: Union[str, int, float]
    change: Optional[float] = None  # Percentage change
    trend: Optional[str] = None  # 'up', 'down', 'neutral'
    unit: Optional[str] = None  # '%', '°C', etc.
    description: Optional[str] = None


class DataTable(BaseModel):
    """Data table configuration"""
    columns: List[str]
    rows: List[Dict[str, Any]]
    title: Optional[str] = None


class AnalyticsResponse(BaseModel):
    """Structured response for analytics dashboard"""
    type: str = "analytics_response"
    text: str  # Natural language explanation
    charts: List[ChartConfig] = []
    kpis: List[KPICard] = []
    tables: List[DataTable] = []


class ChatResponseWrapper(BaseModel):
    """Wrapper for chat responses"""
    response_type: str  # 'text' or 'analytics'
    content: Union[str, AnalyticsResponse]
