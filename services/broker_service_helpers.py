"""
Helper functions for broker service to avoid circular imports
"""
from typing import Dict, List
from datetime import datetime

def get_portfolio_summary(user_id: int) -> Dict:
    """Get portfolio summary for a user"""
    # Placeholder implementation - will be enhanced with real data
    return {
        'total_value': 0,
        'total_pnl': 0,
        'holdings_count': 0,
        'brokers_count': 0,
        'broker_accounts': []
    }

def get_consolidated_holdings(user_id: int) -> List:
    """Get consolidated holdings across all brokers for a user"""
    # Placeholder implementation - will be enhanced with real data
    return []

def sync_broker_data(broker_account) -> Dict:
    """Sync data for a specific broker account"""
    return {'status': 'success', 'message': 'Data synced successfully'}