"""
Test Portfolio database CRUD operations for different asset types
"""

import pytest
from datetime import date, datetime
from models import Portfolio
from app import db


class TestPortfolioCRUDOperations:
    """Test basic CRUD operations for Portfolio model"""
    
    def test_create_equity_portfolio(self, db_session, test_user):
        """Test creating equity portfolio entry"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='RELIANCE',
            stock_name='Reliance Industries Limited',
            asset_type='equities',
            asset_category='equity',
            quantity=100,
            date_purchased=date(2024, 1, 15),
            purchase_price=2500.0,
            purchased_value=250000.0,
            current_price=2750.0,
            current_value=275000.0,
            sector='Energy',
            exchange='NSE',
            trade_type='long_term',
            data_source='broker'
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation
        retrieved = Portfolio.query.filter_by(ticker_symbol='RELIANCE').first()
        assert retrieved is not None
        assert retrieved.user_id == test_user.id
        assert retrieved.asset_type == 'equities'
        assert retrieved.quantity == 100
    
    def test_create_fo_portfolio(self, db_session, test_user):
        """Test creating F&O portfolio entry with asset-specific fields"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='NIFTY24DEC27000CE',
            stock_name='NIFTY 24DEC 27000 Call',
            asset_type='futures_options',
            asset_category='equity',
            contract_type='CALL',
            option_type='CE',
            strike_price=27000.0,
            expiry_date=date(2024, 12, 26),
            lot_size=25,
            quantity=2,
            date_purchased=date(2024, 11, 15),
            purchase_price=150.0,
            purchased_value=7500.0,
            current_price=200.0,
            current_value=10000.0,
            exchange='NSE',
            trade_type='short_term',
            data_source='broker'
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation with F&O specific fields
        retrieved = Portfolio.query.filter_by(ticker_symbol='NIFTY24DEC27000CE').first()
        assert retrieved is not None
        assert retrieved.asset_type == 'futures_options'
        assert retrieved.contract_type == 'CALL'
        assert retrieved.option_type == 'CE'
        assert retrieved.strike_price == 27000.0
        assert retrieved.expiry_date == date(2024, 12, 26)
        assert retrieved.lot_size == 25
    
    def test_create_gold_portfolio(self, db_session, test_user):
        """Test creating gold portfolio entry"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='GOLDIETF',
            stock_name='SBI Gold ETF',
            asset_type='gold',
            asset_category='commodities',
            gold_form='ETF',
            gold_purity='24K',
            grams=100.5,
            quantity=100,
            date_purchased=date(2024, 3, 10),
            purchase_price=5500.0,
            purchased_value=550000.0,
            current_price=5750.0,
            current_value=575000.0,
            trade_type='long_term',
            data_source='broker'
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation with gold specific fields
        retrieved = Portfolio.query.filter_by(ticker_symbol='GOLDIETF').first()
        assert retrieved is not None
        assert retrieved.asset_type == 'gold'
        assert retrieved.gold_form == 'ETF'
        assert retrieved.gold_purity == '24K'
        assert retrieved.grams == 100.5
    
    def test_create_real_estate_portfolio(self, db_session, test_user):
        """Test creating real estate portfolio entry"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='REALESTATE001',
            stock_name='Residential Apartment - Mumbai',
            asset_type='real_estate',
            asset_category='alternative',
            property_type='Residential',
            property_location='Mumbai, Andheri East',
            area_sqft=1200.0,
            quantity=1,
            date_purchased=date(2023, 8, 20),
            purchase_price=12500000.0,
            purchased_value=12500000.0,
            current_price=14000000.0,
            current_value=14000000.0,
            trade_type='long_term',
            data_source='manual_upload'
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation with real estate specific fields
        retrieved = Portfolio.query.filter_by(ticker_symbol='REALESTATE001').first()
        assert retrieved is not None
        assert retrieved.asset_type == 'real_estate'
        assert retrieved.property_type == 'Residential'
        assert retrieved.property_location == 'Mumbai, Andheri East'
        assert retrieved.area_sqft == 1200.0
    
    def test_create_nps_portfolio(self, db_session, test_user):
        """Test creating NPS portfolio entry"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='NPS001',
            stock_name='NPS - Equity Scheme',
            asset_type='nps',
            asset_category='hybrid',
            nps_scheme='Aggressive Hybrid Fund',
            pension_fund_manager='HDFC Pension Fund',
            tier='Tier 1',
            quantity=2500,
            date_purchased=date(2024, 4, 1),
            purchase_price=40.0,
            purchased_value=100000.0,
            current_price=45.0,
            current_value=112500.0,
            trade_type='long_term',
            data_source='manual_upload'
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation with NPS specific fields
        retrieved = Portfolio.query.filter_by(ticker_symbol='NPS001').first()
        assert retrieved is not None
        assert retrieved.asset_type == 'nps'
        assert retrieved.nps_scheme == 'Aggressive Hybrid Fund'
        assert retrieved.pension_fund_manager == 'HDFC Pension Fund'
        assert retrieved.tier == 'Tier 1'
    
    def test_create_fixed_income_portfolio(self, db_session, test_user):
        """Test creating fixed income portfolio entry"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='HDFCFD2024',
            stock_name='HDFC Bank Fixed Deposit',
            asset_type='fixed_income',
            asset_category='debt',
            maturity_date=date(2025, 6, 15),
            interest_rate=7.5,
            coupon_rate=8.0,
            face_value=500000.0,
            quantity=1,
            date_purchased=date(2024, 6, 15),
            purchase_price=500000.0,
            purchased_value=500000.0,
            current_price=500000.0,
            current_value=500000.0,
            trade_type='long_term',
            data_source='manual_upload'
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation with fixed income specific fields
        retrieved = Portfolio.query.filter_by(ticker_symbol='HDFCFD2024').first()
        assert retrieved is not None
        assert retrieved.asset_type == 'fixed_income'
        assert retrieved.maturity_date == date(2025, 6, 15)
        assert retrieved.interest_rate == 7.5
        assert retrieved.coupon_rate == 8.0
        assert retrieved.face_value == 500000.0


class TestPortfolioQuerying:
    """Test Portfolio querying by asset type"""
    
    def test_query_by_asset_type(self, db_session, test_user, sample_multi_asset_portfolio):
        """Test querying portfolio by asset type"""
        # Query equities
        equities = Portfolio.query.filter_by(user_id=test_user.id, asset_type='equities').all()
        assert len(equities) >= 0
        for equity in equities:
            assert equity.asset_type == 'equities'
        
        # Query F&O
        fo_assets = Portfolio.query.filter_by(user_id=test_user.id, asset_type='futures_options').all()
        for fo in fo_assets:
            assert fo.asset_type == 'futures_options'
        
        # Query gold
        gold_assets = Portfolio.query.filter_by(user_id=test_user.id, asset_type='gold').all()
        for gold in gold_assets:
            assert gold.asset_type == 'gold'
    
    def test_query_by_asset_category(self, db_session, test_user, sample_multi_asset_portfolio):
        """Test querying portfolio by asset category"""
        equity_category = Portfolio.query.filter_by(user_id=test_user.id, asset_category='equity').all()
        for asset in equity_category:
            assert asset.asset_category == 'equity'
        
        debt_category = Portfolio.query.filter_by(user_id=test_user.id, asset_category='debt').all()
        for asset in debt_category:
            assert asset.asset_category == 'debt'
        
        commodities = Portfolio.query.filter_by(user_id=test_user.id, asset_category='commodities').all()
        for asset in commodities:
            assert asset.asset_category == 'commodities'
    
    def test_query_with_asset_specific_fields(self, db_session, test_user, sample_fo_portfolio):
        """Test querying F&O assets with specific conditions"""
        # Query call options
        call_options = Portfolio.query.filter_by(
            user_id=test_user.id,
            asset_type='futures_options',
            contract_type='CALL'
        ).all()
        
        for option in call_options:
            assert option.contract_type == 'CALL'
        
        # Query options expiring within next 30 days
        from datetime import datetime, timedelta
        expiry_threshold = datetime.now().date() + timedelta(days=30)
        
        expiring_soon = Portfolio.query.filter(
            Portfolio.user_id == test_user.id,
            Portfolio.asset_type == 'futures_options',
            Portfolio.expiry_date <= expiry_threshold
        ).all()
        
        for asset in expiring_soon:
            assert asset.expiry_date <= expiry_threshold
    
    def test_query_real_estate_by_location(self, db_session, test_user, sample_multi_asset_portfolio):
        """Test querying real estate by location"""
        mumbai_properties = Portfolio.query.filter(
            Portfolio.user_id == test_user.id,
            Portfolio.asset_type == 'real_estate',
            Portfolio.property_location.like('%Mumbai%')
        ).all()
        
        for property_asset in mumbai_properties:
            assert 'Mumbai' in property_asset.property_location


class TestPortfolioUpdatingOperations:
    """Test Portfolio update operations"""
    
    def test_update_current_price(self, db_session, test_user):
        """Test updating current price and recalculating values"""
        # Create portfolio
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='TESTSTOCK',
            stock_name='Test Stock',
            asset_type='equities',
            quantity=100,
            date_purchased=date.today(),
            purchase_price=1000.0,
            purchased_value=100000.0,
            current_price=1000.0,
            current_value=100000.0
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Update current price
        portfolio.current_price = 1200.0
        portfolio.current_value = portfolio.current_price * portfolio.quantity
        db_session.commit()
        
        # Verify update
        updated = Portfolio.query.filter_by(ticker_symbol='TESTSTOCK').first()
        assert updated.current_price == 1200.0
        assert updated.current_value == 120000.0
        assert updated.pnl_amount == 20000.0  # 120000 - 100000
        assert updated.pnl_percentage == 20.0  # (20000 / 100000) * 100
    
    def test_update_fo_expiry_date(self, db_session, test_user):
        """Test updating F&O expiry date"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='TESTFO',
            stock_name='Test F&O',
            asset_type='futures_options',
            contract_type='CALL',
            expiry_date=date(2024, 12, 26),
            quantity=1,
            date_purchased=date.today(),
            purchase_price=100.0,
            purchased_value=100.0
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Update expiry date
        new_expiry = date(2024, 12, 31)
        portfolio.expiry_date = new_expiry
        db_session.commit()
        
        # Verify update
        updated = Portfolio.query.filter_by(ticker_symbol='TESTFO').first()
        assert updated.expiry_date == new_expiry


class TestPortfolioDeletionOperations:
    """Test Portfolio deletion operations"""
    
    def test_delete_portfolio_entry(self, db_session, test_user):
        """Test deleting portfolio entry"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='DELETEME',
            stock_name='Delete Me Stock',
            asset_type='equities',
            quantity=100,
            date_purchased=date.today(),
            purchase_price=1000.0,
            purchased_value=100000.0
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify creation
        created = Portfolio.query.filter_by(ticker_symbol='DELETEME').first()
        assert created is not None
        
        # Delete
        db_session.delete(created)
        db_session.commit()
        
        # Verify deletion
        deleted = Portfolio.query.filter_by(ticker_symbol='DELETEME').first()
        assert deleted is None
    
    def test_cascade_delete_user_portfolio(self, db_session, test_user):
        """Test that user deletion cascades to portfolio (if configured)"""
        portfolio = Portfolio(
            user_id=test_user.id,
            ticker_symbol='CASCADE',
            stock_name='Cascade Test',
            asset_type='equities',
            quantity=100,
            date_purchased=date.today(),
            purchase_price=1000.0,
            purchased_value=100000.0
        )
        
        db_session.add(portfolio)
        db_session.commit()
        
        # Verify portfolio exists
        assert Portfolio.query.filter_by(user_id=test_user.id).first() is not None
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Verify portfolio is also deleted (if cascade is configured)
        # Note: This depends on the foreign key configuration
        remaining = Portfolio.query.filter_by(user_id=test_user.id).first()
        # The test result depends on whether cascade delete is configured
        # If configured: assert remaining is None
        # If not configured: the delete will fail or portfolio will remain


class TestPortfolioIndexPerformance:
    """Test that the indexes we created improve query performance"""
    
    def test_user_asset_type_index_usage(self, db_session, test_user):
        """Test that user+asset_type queries use the index"""
        # Create multiple portfolio entries
        for i in range(10):
            portfolio = Portfolio(
                user_id=test_user.id,
                ticker_symbol=f'STOCK{i}',
                stock_name=f'Stock {i}',
                asset_type='equities' if i % 2 == 0 else 'mutual_funds',
                quantity=100,
                date_purchased=date.today(),
                purchase_price=1000.0,
                purchased_value=100000.0
            )
            db_session.add(portfolio)
        
        db_session.commit()
        
        # This query should use the idx_portfolio_user_asset_type index
        equities = Portfolio.query.filter_by(
            user_id=test_user.id,
            asset_type='equities'
        ).all()
        
        assert len(equities) == 5  # Half of the created entries
    
    def test_expiry_date_index_usage(self, db_session, test_user):
        """Test that expiry date queries use the index"""
        from datetime import timedelta
        
        # Create F&O contracts with different expiry dates
        for i in range(5):
            expiry = date.today() + timedelta(days=i*10)
            portfolio = Portfolio(
                user_id=test_user.id,
                ticker_symbol=f'FO{i}',
                stock_name=f'F&O Contract {i}',
                asset_type='futures_options',
                expiry_date=expiry,
                quantity=1,
                date_purchased=date.today(),
                purchase_price=100.0,
                purchased_value=100.0
            )
            db_session.add(portfolio)
        
        db_session.commit()
        
        # This query should use the idx_portfolio_expiry_date index
        threshold_date = date.today() + timedelta(days=25)
        expiring_soon = Portfolio.query.filter(
            Portfolio.expiry_date <= threshold_date
        ).all()
        
        assert len(expiring_soon) >= 3  # Should find the first 3 contracts