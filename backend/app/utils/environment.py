"""
Environment Configuration Validator
Validates all required environment variables on startup
"""

import os
import logging
from typing import List, Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# ============================================================================
# Required Environment Variables by Environment
# ============================================================================

REQUIRED_VARS_COMMON = [
    "DATABASE_URL",
    "ENVIRONMENT",
]

REQUIRED_VARS_PRODUCTION = [
    *REQUIRED_VARS_COMMON,
    "SECRET_KEY",
    "RESEND_API_KEY",
    "RESEND_FROM_EMAIL",
]

REQUIRED_VARS_DEVELOPMENT = [
    *REQUIRED_VARS_COMMON,
]

# ============================================================================
# Validation Functions
# ============================================================================

def validate_database_url(url: str) -> bool:
    """Validate database URL format"""
    if not url:
        return False
    return url.startswith(("postgresql://", "sqlite:///"))


def validate_environment(env: str) -> bool:
    """Validate environment value"""
    valid_envs = ["development", "staging", "production"]
    return env.lower() in valid_envs


def validate_secret_key(key: str) -> bool:
    """Validate secret key (should be at least 32 characters)"""
    return len(key) >= 32


def validate_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email


def check_environment_variables() -> Dict[str, any]:
    """
    Check all required environment variables
    Returns dict with validation results
    """
    
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    # Determine which vars to check
    if environment == "production":
        required_vars = REQUIRED_VARS_PRODUCTION
    else:
        required_vars = REQUIRED_VARS_DEVELOPMENT
    
    results = {
        "valid": True,
        "environment": environment,
        "checks": {},
        "missing": [],
        "invalid": [],
    }
    
    # Check each required variable
    for var_name in required_vars:
        value = os.getenv(var_name)
        
        if value is None:
            results["missing"].append(var_name)
            results["valid"] = False
            results["checks"][var_name] = {"status": "MISSING"}
            continue
        
        # Special validation for certain variables
        is_valid = True
        reason = None
        
        if var_name == "DATABASE_URL":
            is_valid = validate_database_url(value)
            reason = "Invalid database URL format" if not is_valid else None
        
        elif var_name == "ENVIRONMENT":
            is_valid = validate_environment(value)
            reason = f"Invalid environment. Must be one of: development, staging, production" if not is_valid else None
        
        elif var_name == "SECRET_KEY":
            is_valid = validate_secret_key(value)
            reason = "Secret key must be at least 32 characters" if not is_valid else None
        
        elif var_name == "RESEND_FROM_EMAIL":
            is_valid = validate_email(value)
            reason = "Invalid email format" if not is_valid else None
        
        if not is_valid:
            results["invalid"].append(var_name)
            results["valid"] = False
            results["checks"][var_name] = {
                "status": "INVALID",
                "reason": reason
            }
        else:
            results["checks"][var_name] = {"status": "OK"}
    
    return results


def validate_startup() -> bool:
    """
    Validate all environment variables on startup
    Raises exception if validation fails
    """
    
    results = check_environment_variables()
    
    logger.info("=" * 70)
    logger.info("ENVIRONMENT VALIDATION")
    logger.info("=" * 70)
    logger.info(f"Environment: {results['environment'].upper()}")
    
    # Log all checks
    for var_name, check in results["checks"].items():
        status = check["status"]
        icon = "✅" if status == "OK" else "❌"
        logger.info(f"{icon} {var_name}: {status}")
        
        if "reason" in check:
            logger.warning(f"   Reason: {check['reason']}")
    
    # Log missing variables
    if results["missing"]:
        logger.error(f"\n❌ Missing required environment variables:")
        for var in results["missing"]:
            logger.error(f"   - {var}")
    
    # Log invalid variables
    if results["invalid"]:
        logger.error(f"\n❌ Invalid environment variables:")
        for var in results["invalid"]:
            reason = results["checks"][var].get("reason", "Invalid value")
            logger.error(f"   - {var}: {reason}")
    
    logger.info("=" * 70)
    
    # Fail fast if validation failed
    if not results["valid"]:
        raise RuntimeError(
            f"❌ Environment validation failed!\n"
            f"Missing: {results['missing']}\n"
            f"Invalid: {results['invalid']}"
        )
    
    logger.info("✅ Environment validation PASSED")
    return True
