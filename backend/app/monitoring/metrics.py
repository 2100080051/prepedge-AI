"""
Performance monitoring and metrics collection.
Tracks request latency, cache hit rates, task execution times, etc.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    value: float
    timestamp: datetime
    metric_type: MetricType
    tags: Dict[str, str]


class MetricsCollector:
    """Collects and aggregates application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict = None):
        """Increment a counter metric."""
        key = f"{name}:{self._format_tags(tags)}"
        self.counters[key] = self.counters.get(key, 0) + value
        
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            metric_type=MetricType.COUNTER,
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def set_gauge(self, name: str, value: float, tags: Dict = None):
        """Set a gauge metric."""
        key = f"{name}:{self._format_tags(tags)}"
        self.gauges[key] = value
        
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            metric_type=MetricType.GAUGE,
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def add_histogram(self, name: str, value: float, tags: Dict = None):
        """Add value to histogram."""
        key = f"{name}:{self._format_tags(tags)}"
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def record_timer(self, name: str, duration_ms: float, tags: Dict = None):
        """Record a timer metric."""
        self.add_histogram(name, duration_ms, tags)
        logger.debug(f"Timer {name}: {duration_ms}ms", extra={"duration": duration_ms})
    
    def get_counter(self, name: str, tags: Dict = None) -> float:
        """Get counter value."""
        key = f"{name}:{self._format_tags(tags)}"
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, tags: Dict = None) -> Optional[float]:
        """Get gauge value."""
        key = f"{name}:{self._format_tags(tags)}"
        return self.gauges.get(key)
    
    def get_histogram_stats(self, name: str, tags: Dict = None) -> Dict:
        """Get histogram statistics."""
        key = f"{name}:{self._format_tags(tags)}"
        values = self.histograms.get(key, [])
        
        if not values:
            return {}
        
        sorted_vals = sorted(values)
        n = len(values)
        
        return {
            "count": n,
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "mean": sum(values) / n,
            "median": sorted_vals[n // 2],
            "p95": sorted_vals[int(n * 0.95)],
            "p99": sorted_vals[int(n * 0.99)],
        }
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics."""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "counters": self.counters,
            "gauges": self.gauges,
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in set(k.split(":")[0] for k in self.histograms.keys())
            }
        }
        return summary
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
    
    @staticmethod
    def _format_tags(tags: Dict) -> str:
        """Format tags for key generation."""
        if not tags:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))


# Global metrics instance
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance


# Common metric names
METRIC_NAMES = {
    "requests": {
        "total": "http.requests.total",
        "duration": "http.requests.duration_ms",
        "errors": "http.requests.errors",
    },
    "database": {
        "queries": "db.queries.total",
        "duration": "db.query.duration_ms",
        "connection_pool_size": "db.connection.pool_size",
    },
    "cache": {
        "hits": "cache.hits.total",
        "misses": "cache.misses.total",
        "hit_rate": "cache.hit_rate",
    },
    "tasks": {
        "total": "celery.tasks.total",
        "duration": "celery.task.duration_ms",
        "failures": "celery.tasks.failures",
        "retries": "celery.tasks.retries",
    },
    "api": {
        "searches": "api.searches.total",
        "recommendations": "api.recommendations.total",
    }
}


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, metric_name: str, tags: Dict = None):
        """Initialize timer context."""
        self.metric_name = metric_name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metric."""
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            metrics = get_metrics()
            metrics.record_timer(self.metric_name, duration_ms, self.tags)
