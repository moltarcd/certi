# performance/models.py
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class MetricSnapshot:
    """Mapeo directo para cada endpoint o transacción evaluada."""
    name: str
    method: str
    total_requests: int
    success_rate: float
    failure_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p90: float
    p95: float
    p99: float
    throughput: float  # Requests/sec

@dataclass
class PerformanceResult:
    """Contenedor de resultados globales que consume reporter.py."""
    test_type: str  # Load, Stress, Spike, Soak
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    max_concurrent_users: int
    global_total_requests: int
    global_success_rate: float
    global_failure_rate: float
    global_throughput: float
    endpoints_metrics: List[MetricSnapshot] = field(default_factory=list)
    raw_locust_stats: List[Dict[str, Any]] = field(default_factory=list)