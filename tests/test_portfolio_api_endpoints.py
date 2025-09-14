"""
Test Portfolio API endpoints for asset filtering and broker filtering
"""

import pytest
import json
from datetime import date


class TestPortfolioUnifiedAPI:
    """Test /api/portfolio/unified endpoint"""
    
    def test_unified_portfolio_basic_response(self, authenticated_user, sample_equity_portfolio):
        """Test basic unified portfolio response structure"""
        response = authenticated_user.get('/api/portfolio/unified')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_portfolio_value' in data
        assert 'total_invested_value' in data
        assert 'total_pnl' in data
        assert 'total_pnl_percentage' in data
        assert 'holdings_by_asset_type' in data
        assert 'holdings_count' in data
        assert 'timestamp' in data
    
    def test_unified_portfolio_asset_type_filtering(self, authenticated_user, sample_multi_asset_portfolio):
        """Test asset type filtering in unified portfolio"""
        # Test equities filter
        response = authenticated_user.get('/api/portfolio/unified?type=equities')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        # Should only return equity holdings
        for asset_type, holdings in data['holdings_by_asset_type'].items():
            if holdings:  # If there are holdings of this type
                assert asset_type == 'equities'
    
    def test_unified_portfolio_broker_filtering(self, authenticated_user, sample_equity_portfolio, test_broker_account):
        """Test broker filtering in unified portfolio"""
        # Assign broker to holdings
        from models import Portfolio
        from app import db
        
        portfolio = Portfolio.query.first()
        portfolio.broker_id = str(test_broker_account.id)
        db.session.commit()
        
        # Test broker filter
        response = authenticated_user.get(f'/api/portfolio/unified?broker={test_broker_account.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['holdings_count'] > 0
    
    def test_unified_portfolio_empty_result(self, authenticated_user):
        """Test unified portfolio with no holdings"""
        response = authenticated_user.get('/api/portfolio/unified')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_portfolio_value'] == 0
        assert data['holdings_count'] == 0
        assert data['holdings_by_asset_type'] == {}


class TestPortfolioAPI:
    """Test /api/portfolio endpoint"""
    
    def test_portfolio_basic_response(self, authenticated_user, sample_equity_portfolio):
        """Test basic portfolio response"""
        response = authenticated_user.get('/api/portfolio')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'holdings' in data
        assert 'total_value' in data
        assert 'total_invested' in data
        assert 'total_pnl' in data
        assert 'count' in data
    
    def test_portfolio_asset_type_filtering(self, authenticated_user, sample_multi_asset_portfolio):
        """Test asset type filtering in portfolio API"""
        response = authenticated_user.get('/api/portfolio?asset_type=gold')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify all holdings are gold assets
        for holding in data['holdings']:
            assert holding['asset_type'] == 'gold'


class TestPortfolioByBrokerAPI:
    """Test /api/portfolio/by-broker endpoint"""
    
    def test_portfolio_by_broker_response(self, authenticated_user, sample_equity_portfolio, test_broker_account):
        """Test portfolio grouped by broker"""
        # Assign broker to holdings
        from models import Portfolio
        from app import db
        
        portfolio = Portfolio.query.first()
        portfolio.broker_id = str(test_broker_account.id)
        db.session.commit()
        
        response = authenticated_user.get('/api/portfolio/by-broker')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'brokers' in data
        assert 'total_portfolio_value' in data


class TestPortfolioByAssetTypeAPI:
    """Test /api/portfolio/by-asset-type/<asset_type> endpoint"""
    
    def test_portfolio_by_asset_type_equities(self, authenticated_user, sample_equity_portfolio):
        """Test portfolio filtering by equities"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/equities')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'equities'
        assert 'holdings' in data
        
        # Verify all holdings are equity
        for holding in data['holdings']:
            assert holding['asset_type'] == 'equities'
    
    def test_portfolio_by_asset_type_fo(self, authenticated_user, sample_fo_portfolio):
        """Test portfolio filtering by F&O"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/futures_options')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'futures_options'
        
        # Verify F&O specific fields are present
        for holding in data['holdings']:
            assert holding['asset_type'] == 'futures_options'
            assert 'contract_type' in holding
            assert 'expiry_date' in holding
    
    def test_portfolio_by_asset_type_gold(self, authenticated_user, sample_multi_asset_portfolio):
        """Test portfolio filtering by gold"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/gold')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'gold'
        
        # Verify gold specific fields are present
        for holding in data['holdings']:
            assert holding['asset_type'] == 'gold'
            if 'gold_form' in holding:
                assert holding['gold_form'] is not None
    
    def test_portfolio_by_asset_type_real_estate(self, authenticated_user, sample_multi_asset_portfolio):
        """Test portfolio filtering by real estate"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/real_estate')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'real_estate'
        
        # Verify real estate specific fields
        for holding in data['holdings']:
            assert holding['asset_type'] == 'real_estate'
            if 'property_type' in holding:
                assert holding['property_type'] is not None
    
    def test_portfolio_by_asset_type_nps(self, authenticated_user, sample_multi_asset_portfolio):
        """Test portfolio filtering by NPS"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/nps')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'nps'
        
        # Verify NPS specific fields
        for holding in data['holdings']:
            assert holding['asset_type'] == 'nps'
            if 'nps_scheme' in holding:
                assert holding['nps_scheme'] is not None
    
    def test_portfolio_by_asset_type_fixed_income(self, authenticated_user, sample_multi_asset_portfolio):
        """Test portfolio filtering by fixed income"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/fixed_income')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'fixed_income'
        
        # Verify fixed income specific fields
        for holding in data['holdings']:
            assert holding['asset_type'] == 'fixed_income'
            if 'maturity_date' in holding:
                assert holding['maturity_date'] is not None
    
    def test_portfolio_by_asset_type_invalid(self, authenticated_user):
        """Test portfolio filtering by invalid asset type"""
        response = authenticated_user.get('/api/portfolio/by-asset-type/invalid_asset')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['asset_type'] == 'invalid_asset'
        assert len(data['holdings']) == 0  # Should return empty


class TestPortfolioAPIAuthentication:
    """Test Portfolio API authentication requirements"""
    
    def test_unified_portfolio_requires_auth(self, client):
        """Test that unified portfolio requires authentication"""
        response = client.get('/api/portfolio/unified')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_portfolio_api_requires_auth(self, client):
        """Test that portfolio API requires authentication"""
        response = client.get('/api/portfolio')
        assert response.status_code in [302, 401]
    
    def test_portfolio_by_asset_type_requires_auth(self, client):
        """Test that portfolio by asset type requires authentication"""
        response = client.get('/api/portfolio/by-asset-type/equities')
        assert response.status_code in [302, 401]


class TestPortfolioAPIErrorHandling:
    """Test Portfolio API error handling"""
    
    def test_portfolio_api_handles_database_error(self, authenticated_user, monkeypatch):
        """Test graceful handling of database errors"""
        # Mock a database error
        def mock_query_error(*args, **kwargs):
            raise Exception("Database connection error")
        
        from models import Portfolio
        monkeypatch.setattr(Portfolio.query, 'filter_by', mock_query_error)
        
        response = authenticated_user.get('/api/portfolio')
        data = json.loads(response.data)
        
        # Should handle error gracefully
        assert 'error' in data or data['success'] is False


class TestPortfolioResponseStructure:
    """Test Portfolio API response structure consistency"""
    
    def test_unified_portfolio_response_keys(self, authenticated_user, sample_multi_asset_portfolio):
        """Test that unified portfolio response has required keys"""
        response = authenticated_user.get('/api/portfolio/unified')
        data = json.loads(response.data)
        
        required_keys = [
            'success', 'total_portfolio_value', 'total_invested_value',
            'total_pnl', 'total_pnl_percentage', 'holdings_by_asset_type',
            'holdings_count', 'timestamp'
        ]
        
        for key in required_keys:
            assert key in data
    
    def test_holding_structure_in_response(self, authenticated_user, sample_fo_portfolio):
        """Test individual holding structure in responses"""
        response = authenticated_user.get('/api/portfolio')
        data = json.loads(response.data)
        
        if data['holdings']:
            holding = data['holdings'][0]
            
            # Common fields that should be present
            expected_fields = [
                'id', 'ticker_symbol', 'stock_name', 'asset_type',
                'quantity', 'purchase_price', 'current_price',
                'purchased_value', 'current_value', 'pnl_amount',
                'pnl_percentage'
            ]
            
            for field in expected_fields:
                assert field in holding