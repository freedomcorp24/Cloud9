"""Example configuration for marketplace settings"""

# FE Permission Settings
FE_RATING_THRESHOLD = None  # Minimum rating (0-5) required for automatic FE permission
FE_MIN_ORDERS = None  # Minimum completed orders required for FE eligibility
FE_MIN_ACCOUNT_AGE_DAYS = None  # Minimum account age in days for FE eligibility

"""
Required Environment Variables:
FE_RATING_THRESHOLD=<float>  # Rating threshold (0-5)
FE_MIN_ORDERS=<int>  # Minimum order count
FE_MIN_ACCOUNT_AGE_DAYS=<int>  # Minimum account age in days
"""
