"""
Test configuration and fixtures for the multi-asset portfolio system
"""

import pytest
import os
import tempfile
from datetime import datetime, date
from app import app, db
from models import User, Portfolio, PricingPlan, SubscriptionStatus
from models_broker import BrokerAccount, BrokerType, ConnectionStatus

@pytest.fixture(scope='session')
def test_app():
    """Create a test Flask app with in-memory database"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(test_app):
    """Create a test client"""
    return test_app.test_client()

@pytest.fixture
def app_context(test_app):
    """Create application context for tests"""
    with test_app.app_context():
        yield

@pytest.fixture
def db_session(app_context):
    """Create database session for tests"""
    yield db.session
    db.session.rollback()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        pricing_plan=PricingPlan.TARGET_PLUS,
        subscription_status=SubscriptionStatus.ACTIVE
    )
    user.set_password('testpass123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_broker_account(db_session, test_user):
    """Create a test broker account"""
    broker = BrokerAccount(
        user_id=test_user.id,
        broker_type='zerodha',
        broker_name='Zerodha',
        connection_status='connected',
        is_primary=True,
        account_balance=100000.0,
        margin_available=50000.0,
        is_active=True
    )
    db_session.add(broker)
    db_session.commit()
    return broker

@pytest.fixture
def sample_equity_portfolio(db_session, test_user):
    """Create sample equity portfolio holdings"""
    holdings = []
    
    # Regular equity stock
    equity = Portfolio(
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
    holdings.append(equity)
    
    # Mutual fund
    mutual_fund = Portfolio(
        user_id=test_user.id,
        ticker_symbol='HDFCTOP100',
        stock_name='HDFC Top 100 Fund',
        asset_type='mutual_funds',
        asset_category='equity',
        quantity=1000,
        date_purchased=date(2024, 2, 1),
        purchase_price=750.0,
        purchased_value=750000.0,
        current_price=825.0,
        current_value=825000.0,
        trade_type='long_term',
        data_source='manual_upload'
    )
    holdings.append(mutual_fund)
    
    for holding in holdings:
        db_session.add(holding)
    db_session.commit()
    return holdings

@pytest.fixture
def sample_fo_portfolio(db_session, test_user):
    """Create sample F&O portfolio holdings"""
    holdings = []
    
    # Call option
    call_option = Portfolio(
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
    holdings.append(call_option)
    
    # Future contract
    future = Portfolio(
        user_id=test_user.id,
        ticker_symbol='RELIANCE24DECFUT',
        stock_name='RELIANCE 24DEC Future',
        asset_type='futures_options',
        asset_category='equity',
        contract_type='FUTURE',
        expiry_date=date(2024, 12, 26),
        lot_size=250,
        quantity=1,
        date_purchased=date(2024, 11, 20),
        purchase_price=2600.0,
        purchased_value=650000.0,
        current_price=2750.0,
        current_value=687500.0,
        exchange='NSE',
        trade_type='short_term',
        data_source='broker'
    )
    holdings.append(future)
    
    for holding in holdings:
        db_session.add(holding)
    db_session.commit()
    return holdings

@pytest.fixture
def sample_multi_asset_portfolio(db_session, test_user):
    """Create comprehensive multi-asset portfolio"""
    holdings = []
    
    # Gold ETF
    gold_etf = Portfolio(
        user_id=test_user.id,
        ticker_symbol='GOLDIETF',
        stock_name='SBI Gold ETF',
        asset_type='gold',
        asset_category='commodities',
        gold_form='ETF',
        gold_purity='24K',
        quantity=100,
        date_purchased=date(2024, 3, 10),
        purchase_price=5500.0,
        purchased_value=550000.0,
        current_price=5750.0,
        current_value=575000.0,
        exchange='NSE',
        trade_type='long_term',
        data_source='broker'
    )
    holdings.append(gold_etf)
    
    # Fixed Deposit
    fd = Portfolio(
        user_id=test_user.id,
        ticker_symbol='HDFCFD2024',
        stock_name='HDFC Bank Fixed Deposit',
        asset_type='fixed_income',
        asset_category='debt',
        maturity_date=date(2025, 6, 15),
        interest_rate=7.5,
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
    holdings.append(fd)
    
    # Real Estate
    property_holding = Portfolio(
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
    holdings.append(property_holding)
    
    # NPS Investment
    nps = Portfolio(
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
    holdings.append(nps)
    
    for holding in holdings:
        db_session.add(holding)
    db_session.commit()
    return holdings

@pytest.fixture
def authenticated_user(client, test_user):
    """Login the test user and return authenticated client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client