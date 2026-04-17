import time
import logging
from enum import Enum
from typing import Callable, Any, Dict, Optional
from datetime import datetime, timedelta
from functools import wraps
import threading

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: str = "CircuitBreaker"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation for handling LLM API failures
    Prevents cascading failures by failing fast when service is down
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"{self.config.name}: Circuit transitions to HALF_OPEN")
                else:
                    raise CircuitBreakerOpenError(
                        f"{self.config.name}: Circuit is OPEN. Service unavailable."
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info(f"{self.config.name}: Circuit recovered, transitioning to CLOSED")
                self.success_count += 1

    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(
                    f"{self.config.name}: Circuit OPEN after {self.failure_count} failures"
                )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if not self.last_failure_time:
            return True

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.recovery_timeout

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        with self._lock:
            return {
                "name": self.config.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout
            }

    def reset(self):
        """Manually reset circuit breaker"""
        with self._lock:
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.state = CircuitState.CLOSED
            logger.info(f"{self.config.name}: Circuit manually reset")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class LLMCircuitBreakerManager:
    """
    Manages circuit breakers for different LLM providers
    """

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._initialize_breakers()

    def _initialize_breakers(self):
        """Initialize circuit breakers for each LLM provider"""
        providers = ["openrouter", "groq", "nvidia"]

        for provider in providers:
            config = CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=Exception,
                name=f"{provider}_breaker"
            )
            self.circuit_breakers[provider] = CircuitBreaker(config)

    def execute_with_fallback(
        self,
        primary_func: Callable,
        fallback_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute primary function with fallback
        If primary fails (circuit open or exception), try fallback
        """
        primary_result = None
        primary_error = None

        # Try primary function
        try:
            primary_result = primary_func(*args, **kwargs)
            return primary_result
        except CircuitBreakerOpenError as e:
            logger.warning(f"Primary function circuit open: {e}")
            primary_error = e
        except Exception as e:
            logger.error(f"Primary function failed: {e}")
            primary_error = e

        # Try fallback function
        try:
            logger.info("Attempting fallback function")
            fallback_result = fallback_func(*args, **kwargs)
            return fallback_result
        except Exception as e:
            logger.error(f"Fallback function also failed: {e}")
            raise Exception(
                f"Both primary and fallback functions failed. "
                f"Primary error: {primary_error}. Fallback error: {e}"
            )

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get state of all circuit breakers"""
        return {
            name: breaker.get_state()
            for name, breaker in self.circuit_breakers.items()
        }

    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.circuit_breakers.values():
            breaker.reset()
        logger.info("All circuit breakers reset")

    def reset_provider(self, provider: str):
        """Reset circuit breaker for specific provider"""
        if provider in self.circuit_breakers:
            self.circuit_breakers[provider].reset()
            logger.info(f"Circuit breaker reset for {provider}")
        else:
            raise ValueError(f"Unknown provider: {provider}")


# Global circuit breaker manager
_llm_breaker_manager: Optional[LLMCircuitBreakerManager] = None


def get_llm_breaker_manager() -> LLMCircuitBreakerManager:
    """Get or create global circuit breaker manager"""
    global _llm_breaker_manager
    if _llm_breaker_manager is None:
        _llm_breaker_manager = LLMCircuitBreakerManager()
    return _llm_breaker_manager


def llm_circuit_breaker(provider: str):
    """
    Decorator for LLM function calls with circuit breaker protection
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            manager = get_llm_breaker_manager()
            breaker = manager.circuit_breakers.get(provider)

            if not breaker:
                # No circuit breaker for this provider, execute normally
                return func(*args, **kwargs)

            try:
                return breaker.call(func, *args, **kwargs)
            except CircuitBreakerOpenError:
                logger.error(f"Circuit breaker open for {provider}")
                raise

        return wrapper
    return decorator
