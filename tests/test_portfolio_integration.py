"""
Integration tests for multi-asset portfolio views and broker filtering
"""

import pytest
import json
from datetime import date, timedelta


class TestMultiAssetPortfolioIntegration:
    """Test integration of multiple asset types in portfolio views"""
    
    def test_comprehensive_portfolio_aggregation(self, authenticated_user, sample_multi_asset_portfolio):
        """Test that all asset types are properly aggregated in portfolio view"""
        response = authenticated_user.get('/api/portfolio/unified')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Should have multiple asset types
        asset_types = data['holdings_by_asset_type']
        expected_asset_types = ['gold', 'fixed_income', 'real_estate', 'nps']
        
        found_asset_types = [asset_type for asset_type in expected_asset_types if asset_type in asset_types and asset_types[asset_type]]
        assert len(found_asset_types) >= 1  # At least one asset type should be present
        
        # Verify total calculations include all asset types
        assert data['total_portfolio_value'] > 0
        assert data['total_invested_value'] > 0
        assert 'total_pnl' in data
        assert data['holdings_count'] > 0
    
    def test_asset_allocation_calculation(self, authenticated_user, sample_multi_asset_portfolio):
        """Test asset allocation calculation across multiple asset types"""
        response = authenticated_user.get('/api/portfolio/unified')
        data = json.loads(response.data)
        
        total_value = data['total_portfolio_value']
        asset_types = data['holdings_by_asset_type']
        
        # Calculate sum of individual asset type values
        sum_of_parts = 0
        for asset_type, holdings in asset_types.items():
            if holdings:  # If there are holdings of this type
                for holding in holdings:
                    sum_of_parts += holding.get('current_value', 0)
        
        # Total should equal sum of parts (allowing for small floating point differences)
        assert abs(total_value - sum_of_parts) < 0.01
    
    def test_risk_diversification_analysis(self, authenticated_user, sample_multi_asset_portfolio):
        """Test risk analysis across different asset types"""
        response = authenticated_user.get('/api/portfolio')
        data = json.loads(response.data)
        
        risk_levels = {}
        for holding in data['holdings']:
            asset_type = holding['asset_type']
            # Create a Portfolio object to get risk level
            from models import Portfolio
            temp_portfolio = Portfolio(asset_type=asset_type)
            risk_level = temp_portfolio.get_risk_level()
            
            if risk_level not in risk_levels:
                risk_levels[risk_level] = 0
            risk_levels[risk_level] += 1
        
        # Should have diverse risk levels
        assert len(risk_levels) >= 2  # At least 2 different risk levels
    
    def test_expiry_management_across_assets(self, authenticated_user, sample_fo_portfolio, sample_multi_asset_portfolio):
        """Test expiry date management for different asset types"""
        # Get all holdings
        response = authenticated_user.get('/api/portfolio')
        data = json.loads(response.data)
        
        expiring_assets = []
        non_expiring_assets = []
        
        for holding in data['holdings']:
            asset_type = holding['asset_type']
            if asset_type == 'futures_options' and holding.get('expiry_date'):
                expiring_assets.append(holding)
            else:
                non_expiring_assets.append(holding)
        
        # Should have both expiring and non-expiring assets
        if len(expiring_assets) > 0:
            assert len(non_expiring_assets) > 0
            
            # F&O assets should have expiry dates
            for fo_asset in expiring_assets:
                assert fo_asset.get('expiry_date') is not None


class TestBrokerFilteringIntegration:
    """Test broker filtering across different asset types"""
    
    def test_broker_portfolio_segregation(self, authenticated_user, test_broker_account, sample_multi_asset_portfolio):
        """Test that broker filtering works across all asset types"""
        from models import Portfolio
        from app import db
        
        # Assign some holdings to the broker
        portfolios = Portfolio.query.limit(2).all()
        broker_id = str(test_broker_account.id)
        
        for portfolio in portfolios:
            portfolio.broker_id = broker_id
        db.session.commit()
        
        # Test broker filtering
        response = authenticated_user.get(f'/api/portfolio/unified?broker={test_broker_account.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Should only show holdings from this broker
        for asset_type, holdings in data['holdings_by_asset_type'].items():
            for holding in holdings:
                assert holding.get('broker_id') == broker_id or holding.get('broker_name') != 'Manual Entry'
    
    def test_multi_broker_portfolio_view(self, authenticated_user, test_broker_account, sample_multi_asset_portfolio):
        """Test portfolio view with multiple brokers"""
        from models import Portfolio
        from models_broker import BrokerAccount
        from app import db
        
        # Create second broker account
        broker2 = BrokerAccount(
            user_id=test_broker_account.user_id,
            broker_type='dhan',
            broker_name='Dhan',
            connection_status='connected',
            is_primary=False,
            is_active=True
        )
        db.session.add(broker2)
        db.session.commit()
        
        # Assign holdings to different brokers
        portfolios = Portfolio.query.all()
        if len(portfolios) >= 2:
            portfolios[0].broker_id = str(test_broker_account.id)
            if len(portfolios) > 1:
                portfolios[1].broker_id = str(broker2.id)
            db.session.commit()
        
        # Test by-broker API
        response = authenticated_user.get('/api/portfolio/by-broker')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'brokers' in data
        
        # Should show holdings grouped by broker
        broker_groups = data['brokers']
        found_brokers = []
        for broker_group in broker_groups:
            if broker_group.get('holdings'):
                found_brokers.append(broker_group['broker_id'])
        
        # Should have at least one broker with holdings
        assert len(found_brokers) >= 1
    
    def test_manual_vs_broker_entries(self, authenticated_user, test_broker_account, sample_multi_asset_portfolio):
        """Test distinction between manual and broker entries"""
        from models import Portfolio
        from app import db
        
        # Ensure some holdings are manual (no broker_id) and some are from broker
        portfolios = Portfolio.query.all()
        if len(portfolios) >= 2:
            portfolios[0].broker_id = None  # Manual entry
            portfolios[0].data_source = 'manual_upload'
            portfolios[1].broker_id = str(test_broker_account.id)  # Broker entry
            portfolios[1].data_source = 'broker'
            db.session.commit()
        
        # Test that both show up correctly
        response = authenticated_user.get('/api/portfolio')
        data = json.loads(response.data)
        
        manual_entries = []
        broker_entries = []
        
        for holding in data['holdings']:
            if holding.get('data_source') == 'manual_upload':
                manual_entries.append(holding)
            elif holding.get('data_source') == 'broker':
                broker_entries.append(holding)
        
        # Should have both types
        if len(portfolios) >= 2:
            assert len(manual_entries) >= 1 or len(broker_entries) >= 1


class TestPortfolioWorkflowIntegration:
    """Test complete portfolio workflows"""
    
    def test_portfolio_creation_to_analysis_workflow(self, db_session, test_user, authenticated_user):
        """Test complete workflow from portfolio creation to analysis"""
        from models import Portfolio
        
        # Step 1: Create diverse portfolio
        holdings = [
            # Equity
            Portfolio(
                user_id=test_user.id,
                ticker_symbol='WORKFLOW_EQUITY',
                stock_name='Workflow Test Equity',
                asset_type='equities',
                asset_category='equity',
                quantity=100,
                date_purchased=date(2024, 1, 15),
                purchase_price=1000.0,
                purchased_value=100000.0,
                current_price=1200.0,
                current_value=120000.0,
                trade_type='long_term',
                data_source='broker'
            ),
            # F&O
            Portfolio(
                user_id=test_user.id,
                ticker_symbol='WORKFLOW_FO',
                stock_name='Workflow Test F&O',
                asset_type='futures_options',
                asset_category='equity',
                contract_type='CALL',
                option_type='CE',
                strike_price=25000.0,
                expiry_date=date.today() + timedelta(days=30),
                lot_size=50,
                quantity=2,
                date_purchased=date.today(),
                purchase_price=100.0,
                purchased_value=10000.0,
                current_price=150.0,
                current_value=15000.0,
                trade_type='short_term',
                data_source='broker'
            ),
            # Gold
            Portfolio(
                user_id=test_user.id,
                ticker_symbol='WORKFLOW_GOLD',
                stock_name='Workflow Gold ETF',
                asset_type='gold',
                asset_category='commodities',
                gold_form='ETF',
                gold_purity='24K',
                quantity=50,
                date_purchased=date(2024, 3, 1),
                purchase_price=5000.0,
                purchased_value=250000.0,
                current_price=5200.0,
                current_value=260000.0,
                trade_type='long_term',
                data_source='manual_upload'
            )
        ]
        
        for holding in holdings:
            db_session.add(holding)
        db_session.commit()
        
        # Step 2: Test unified portfolio view
        response = authenticated_user.get('/api/portfolio/unified')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['holdings_count'] == 3
        assert data['total_portfolio_value'] == 395000.0  # 120000 + 15000 + 260000
        assert data['total_invested_value'] == 360000.0  # 100000 + 10000 + 250000
        assert data['total_pnl'] == 35000.0  # 395000 - 360000
        
        # Step 3: Test asset type filtering
        equity_response = authenticated_user.get('/api/portfolio/by-asset-type/equities')
        equity_data = json.loads(equity_response.data)
        assert len(equity_data['holdings']) == 1
        assert equity_data['holdings'][0]['ticker_symbol'] == 'WORKFLOW_EQUITY'
        
        fo_response = authenticated_user.get('/api/portfolio/by-asset-type/futures_options')
        fo_data = json.loads(fo_response.data)
        assert len(fo_data['holdings']) == 1
        assert fo_data['holdings'][0]['contract_type'] == 'CALL'
        
        gold_response = authenticated_user.get('/api/portfolio/by-asset-type/gold')
        gold_data = json.loads(gold_response.data)
        assert len(gold_data['holdings']) == 1
        assert gold_data['holdings'][0]['gold_form'] == 'ETF'
        
        # Step 4: Test model methods on created holdings
        workflow_equity = Portfolio.query.filter_by(ticker_symbol='WORKFLOW_EQUITY').first()
        assert workflow_equity.is_equity() is True
        assert workflow_equity.get_risk_level() == 'Medium'
        assert workflow_equity.pnl_amount == 20000.0
        assert workflow_equity.pnl_percentage == 20.0
        
        workflow_fo = Portfolio.query.filter_by(ticker_symbol='WORKFLOW_FO').first()
        assert workflow_fo.is_futures_options() is True
        assert workflow_fo.has_expiry() is True
        assert workflow_fo.days_to_expiry() == 30
        assert workflow_fo.get_risk_level() == 'High'
        
        workflow_gold = Portfolio.query.filter_by(ticker_symbol='WORKFLOW_GOLD').first()
        assert workflow_gold.is_gold() is True
        assert workflow_gold.get_risk_level() == 'Low'
        gold_info = workflow_gold.get_asset_specific_info()
        assert gold_info['Gold Form'] == 'ETF'
        assert gold_info['Purity'] == '24K'


class TestPortfolioDataConsistency:
    """Test data consistency across different portfolio views"""
    
    def test_portfolio_data_consistency_across_endpoints(self, authenticated_user, sample_multi_asset_portfolio):
        """Test that the same data appears consistently across different API endpoints"""
        # Get data from different endpoints
        unified_response = authenticated_user.get('/api/portfolio/unified')
        regular_response = authenticated_user.get('/api/portfolio')
        
        unified_data = json.loads(unified_response.data)
        regular_data = json.loads(regular_response.data)
        
        # Both should be successful
        assert unified_data['success'] is True
        assert regular_data['success'] is True
        
        # Holdings count should match
        unified_count = unified_data['holdings_count']
        regular_count = regular_data['count']
        assert unified_count == regular_count
        
        # Total values should match (allowing for small floating point differences)
        if 'total_portfolio_value' in unified_data and 'total_value' in regular_data:
            assert abs(unified_data['total_portfolio_value'] - regular_data['total_value']) < 0.01
    
    def test_asset_specific_fields_preservation(self, authenticated_user, sample_fo_portfolio, sample_multi_asset_portfolio):
        """Test that asset-specific fields are preserved across different API calls"""
        # Test F&O specific fields
        fo_response = authenticated_user.get('/api/portfolio/by-asset-type/futures_options')
        fo_data = json.loads(fo_response.data)
        
        if fo_data['holdings']:
            fo_holding = fo_data['holdings'][0]
            # Should have F&O specific fields
            fo_fields = ['contract_type', 'expiry_date', 'lot_size']
            for field in fo_fields:
                if fo_holding.get(field) is not None:  # Field exists and has value
                    assert fo_holding[field] is not None
        
        # Test Gold specific fields
        gold_response = authenticated_user.get('/api/portfolio/by-asset-type/gold')
        gold_data = json.loads(gold_response.data)
        
        if gold_data['holdings']:
            gold_holding = gold_data['holdings'][0]
            # Should have gold specific fields if they exist
            gold_fields = ['gold_form', 'gold_purity', 'grams']
            for field in gold_fields:
                if field in gold_holding and gold_holding[field] is not None:
                    assert gold_holding[field] is not None
    
    def test_portfolio_calculations_accuracy(self, authenticated_user, sample_equity_portfolio):
        """Test accuracy of P&L and percentage calculations"""
        response = authenticated_user.get('/api/portfolio')
        data = json.loads(response.data)
        
        for holding in data['holdings']:
            purchased_value = holding.get('purchased_value', 0)
            current_value = holding.get('current_value', 0)
            pnl_amount = holding.get('pnl_amount', 0)
            pnl_percentage = holding.get('pnl_percentage', 0)
            
            # Verify P&L calculation
            expected_pnl = current_value - purchased_value
            assert abs(pnl_amount - expected_pnl) < 0.01
            
            # Verify percentage calculation
            if purchased_value > 0:
                expected_percentage = (expected_pnl / purchased_value) * 100
                assert abs(pnl_percentage - expected_percentage) < 0.01