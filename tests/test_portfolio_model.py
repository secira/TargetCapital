"""
Test Portfolio model methods and asset-specific functionality
"""

import pytest
from datetime import date, timedelta
from models import Portfolio


class TestPortfolioModelMethods:
    """Test Portfolio model methods"""
    
    def test_get_asset_type_display(self, app_context):
        """Test asset type display names"""
        test_cases = [
            ('equities', 'Equities'),
            ('mutual_funds', 'Mutual Funds'),
            ('fixed_income', 'Fixed Income'),
            ('futures_options', 'Futures & Options'),
            ('nps', 'National Pension System'),
            ('real_estate', 'Real Estate'),
            ('gold', 'Gold'),
            ('etf', 'ETFs'),
            ('crypto', 'Cryptocurrency'),
            ('esop', 'ESOP'),
            ('private_equity', 'Private Equity'),
            ('unknown_type', 'Unknown_Type'),
            (None, 'Unknown')
        ]
        
        for asset_type, expected_display in test_cases:
            portfolio = Portfolio(asset_type=asset_type)
            assert portfolio.get_asset_type_display() == expected_display

    def test_get_asset_category_display(self, app_context):
        """Test asset category display names"""
        test_cases = [
            ('equity', 'Equity'),
            ('debt', 'Debt'),
            ('commodities', 'Commodities'),
            ('alternative', 'Alternative'),
            ('hybrid', 'Hybrid'),
            ('unknown_category', 'Unknown_Category'),
            (None, 'Unknown')
        ]
        
        for category, expected_display in test_cases:
            portfolio = Portfolio(asset_category=category)
            assert portfolio.get_asset_category_display() == expected_display

    def test_asset_type_checkers(self, app_context):
        """Test asset type checker methods"""
        test_cases = [
            ('equities', 'is_equity', True),
            ('esop', 'is_equity', True),
            ('mutual_funds', 'is_equity', False),
            ('futures_options', 'is_futures_options', True),
            ('equities', 'is_futures_options', False),
            ('fixed_income', 'is_fixed_income', True),
            ('equities', 'is_fixed_income', False),
            ('real_estate', 'is_real_estate', True),
            ('equities', 'is_real_estate', False),
            ('gold', 'is_gold', True),
            ('equities', 'is_gold', False),
            ('nps', 'is_nps', True),
            ('equities', 'is_nps', False),
        ]
        
        for asset_type, method_name, expected in test_cases:
            portfolio = Portfolio(asset_type=asset_type)
            assert getattr(portfolio, method_name)() == expected

    def test_pnl_calculations(self, app_context):
        """Test P&L calculation properties"""
        # Profitable holding
        portfolio_profit = Portfolio(
            purchased_value=100000.0,
            current_value=120000.0
        )
        assert portfolio_profit.pnl_amount == 20000.0
        assert portfolio_profit.pnl_percentage == 20.0
        assert portfolio_profit.get_pnl_class() == 'text-success'
        
        # Loss-making holding
        portfolio_loss = Portfolio(
            purchased_value=100000.0,
            current_value=80000.0
        )
        assert portfolio_loss.pnl_amount == -20000.0
        assert portfolio_loss.pnl_percentage == -20.0
        assert portfolio_loss.get_pnl_class() == 'text-danger'
        
        # Break-even holding
        portfolio_even = Portfolio(
            purchased_value=100000.0,
            current_value=100000.0
        )
        assert portfolio_even.pnl_amount == 0.0
        assert portfolio_even.pnl_percentage == 0.0
        assert portfolio_even.get_pnl_class() == 'text-muted'
        
        # Missing current_value
        portfolio_missing = Portfolio(
            purchased_value=100000.0,
            current_value=None
        )
        assert portfolio_missing.pnl_amount == 0
        assert portfolio_missing.pnl_percentage == 0.0

    def test_risk_level_assignment(self, app_context):
        """Test risk level based on asset type"""
        risk_test_cases = [
            ('equities', 'Medium'),
            ('futures_options', 'High'),
            ('fixed_income', 'Low'),
            ('real_estate', 'Medium'),
            ('gold', 'Low'),
            ('nps', 'Low'),
            ('mutual_funds', 'Medium'),
            ('etf', 'Medium'),
            ('crypto', 'Very High'),
            ('esop', 'High'),
            ('private_equity', 'Very High'),
            ('unknown_asset', 'Unknown')
        ]
        
        for asset_type, expected_risk in risk_test_cases:
            portfolio = Portfolio(asset_type=asset_type)
            assert portfolio.get_risk_level() == expected_risk


class TestFuturesOptionsSpecific:
    """Test F&O specific functionality"""
    
    def test_fo_asset_specific_info(self, app_context):
        """Test F&O asset specific information"""
        fo_portfolio = Portfolio(
            asset_type='futures_options',
            contract_type='CALL',
            option_type='CE',
            strike_price=27000.0,
            expiry_date=date(2024, 12, 26),
            lot_size=25
        )
        
        info = fo_portfolio.get_asset_specific_info()
        expected_info = {
            'Contract Type': 'CALL',
            'Strike Price': 27000.0,
            'Expiry Date': '26-12-2024',
            'Lot Size': 25,
            'Option Type': 'CE'
        }
        assert info == expected_info
    
    def test_expiry_functionality(self, app_context):
        """Test expiry-related methods for F&O"""
        # Contract expiring tomorrow
        tomorrow = date.today() + timedelta(days=1)
        fo_expiring = Portfolio(
            asset_type='futures_options',
            expiry_date=tomorrow
        )
        
        assert fo_expiring.has_expiry() is True
        assert fo_expiring.days_to_expiry() == 1
        assert fo_expiring.is_expiring_soon() is True
        assert fo_expiring.is_expiring_soon(days=3) is True
        
        # Contract expiring in 10 days
        future_date = date.today() + timedelta(days=10)
        fo_future = Portfolio(
            asset_type='futures_options',
            expiry_date=future_date
        )
        
        assert fo_future.days_to_expiry() == 10
        assert fo_future.is_expiring_soon() is False
        assert fo_future.is_expiring_soon(days=15) is True
        
        # Contract with no expiry
        fo_no_expiry = Portfolio(asset_type='equities')
        assert fo_no_expiry.has_expiry() is False
        assert fo_no_expiry.days_to_expiry() is None
        assert fo_no_expiry.is_expiring_soon() is False
    
    def test_fo_validation(self, app_context):
        """Test F&O validation requirements"""
        # Valid F&O contract
        valid_fo = Portfolio(
            asset_type='futures_options',
            contract_type='CALL',
            expiry_date=date(2024, 12, 26)
        )
        assert valid_fo.validate_required_fields() == []
        
        # Missing contract type
        invalid_fo1 = Portfolio(
            asset_type='futures_options',
            expiry_date=date(2024, 12, 26)
        )
        errors = invalid_fo1.validate_required_fields()
        assert 'Contract type is required for F&O assets' in errors
        
        # Missing expiry date
        invalid_fo2 = Portfolio(
            asset_type='futures_options',
            contract_type='CALL'
        )
        errors = invalid_fo2.validate_required_fields()
        assert 'Expiry date is required for F&O assets' in errors


class TestRealEstateSpecific:
    """Test Real Estate specific functionality"""
    
    def test_real_estate_asset_specific_info(self, app_context):
        """Test Real Estate asset specific information"""
        property_portfolio = Portfolio(
            asset_type='real_estate',
            property_type='Residential',
            property_location='Mumbai, Andheri East',
            area_sqft=1200.0
        )
        
        info = property_portfolio.get_asset_specific_info()
        expected_info = {
            'Property Type': 'Residential',
            'Location': 'Mumbai, Andheri East',
            'Area (sq ft)': 1200.0
        }
        assert info == expected_info
    
    def test_real_estate_validation(self, app_context):
        """Test Real Estate validation requirements"""
        # Valid property
        valid_property = Portfolio(
            asset_type='real_estate',
            property_type='Commercial'
        )
        assert valid_property.validate_required_fields() == []
        
        # Missing property type
        invalid_property = Portfolio(asset_type='real_estate')
        errors = invalid_property.validate_required_fields()
        assert 'Property type is required for real estate assets' in errors


class TestGoldSpecific:
    """Test Gold specific functionality"""
    
    def test_gold_asset_specific_info(self, app_context):
        """Test Gold asset specific information"""
        gold_portfolio = Portfolio(
            asset_type='gold',
            gold_form='ETF',
            gold_purity='24K',
            grams=100.5
        )
        
        info = gold_portfolio.get_asset_specific_info()
        expected_info = {
            'Gold Form': 'ETF',
            'Purity': '24K',
            'Weight (grams)': 100.5
        }
        assert info == expected_info
    
    def test_gold_validation(self, app_context):
        """Test Gold validation requirements"""
        # Valid gold investment
        valid_gold = Portfolio(
            asset_type='gold',
            gold_form='Physical'
        )
        assert valid_gold.validate_required_fields() == []
        
        # Missing gold form
        invalid_gold = Portfolio(asset_type='gold')
        errors = invalid_gold.validate_required_fields()
        assert 'Gold form is required for gold assets' in errors


class TestNPSSpecific:
    """Test NPS specific functionality"""
    
    def test_nps_asset_specific_info(self, app_context):
        """Test NPS asset specific information"""
        nps_portfolio = Portfolio(
            asset_type='nps',
            nps_scheme='Aggressive Hybrid Fund',
            pension_fund_manager='HDFC Pension Fund',
            tier='Tier 1'
        )
        
        info = nps_portfolio.get_asset_specific_info()
        expected_info = {
            'NPS Scheme': 'Aggressive Hybrid Fund',
            'Pension Fund Manager': 'HDFC Pension Fund',
            'Tier': 'Tier 1'
        }
        assert info == expected_info
    
    def test_nps_validation(self, app_context):
        """Test NPS validation requirements"""
        # Valid NPS investment
        valid_nps = Portfolio(
            asset_type='nps',
            nps_scheme='Conservative Fund'
        )
        assert valid_nps.validate_required_fields() == []
        
        # Missing NPS scheme
        invalid_nps = Portfolio(asset_type='nps')
        errors = invalid_nps.validate_required_fields()
        assert 'NPS scheme is required for NPS assets' in errors


class TestFixedIncomeSpecific:
    """Test Fixed Income specific functionality"""
    
    def test_fixed_income_asset_specific_info(self, app_context):
        """Test Fixed Income asset specific information"""
        bond_portfolio = Portfolio(
            asset_type='fixed_income',
            maturity_date=date(2025, 6, 15),
            interest_rate=7.5,
            coupon_rate=8.0,
            face_value=100000.0
        )
        
        info = bond_portfolio.get_asset_specific_info()
        expected_info = {
            'Maturity Date': '15-06-2025',
            'Interest Rate': '7.5%',
            'Coupon Rate': '8.0%',
            'Face Value': 100000.0
        }
        assert info == expected_info
    
    def test_fixed_income_validation(self, app_context):
        """Test Fixed Income validation requirements"""
        # Valid fixed income
        valid_bond = Portfolio(
            asset_type='fixed_income',
            maturity_date=date(2025, 12, 31)
        )
        assert valid_bond.validate_required_fields() == []
        
        # Missing maturity date
        invalid_bond = Portfolio(asset_type='fixed_income')
        errors = invalid_bond.validate_required_fields()
        assert 'Maturity date is required for fixed income assets' in errors


class TestPortfolioHelperMethods:
    """Test additional Portfolio helper methods"""
    
    def test_get_broker_name(self, app_context):
        """Test broker name getter"""
        # Portfolio with broker
        portfolio_with_broker = Portfolio(broker_id='zerodha')
        assert portfolio_with_broker.get_broker_name() == 'zerodha'
        
        # Portfolio without broker (manual entry)
        portfolio_manual = Portfolio(broker_id=None)
        assert portfolio_manual.get_broker_name() == 'Manual Entry'
        
        portfolio_empty = Portfolio(broker_id='')
        assert portfolio_empty.get_broker_name() == 'Manual Entry'
    
    def test_asset_specific_info_filters_none_values(self, app_context):
        """Test that asset specific info filters out None values"""
        portfolio = Portfolio(
            asset_type='futures_options',
            contract_type='CALL',
            strike_price=None,  # This should be filtered out
            expiry_date=date(2024, 12, 26),
            lot_size=25,
            option_type=None  # This should be filtered out
        )
        
        info = portfolio.get_asset_specific_info()
        expected_info = {
            'Contract Type': 'CALL',
            'Expiry Date': '26-12-2024',
            'Lot Size': 25
        }
        assert info == expected_info
        assert 'Strike Price' not in info
        assert 'Option Type' not in info
    
    def test_portfolio_repr(self, app_context):
        """Test Portfolio string representation"""
        portfolio = Portfolio(
            ticker_symbol='RELIANCE',
            quantity=100
        )
        expected_repr = '<Portfolio RELIANCE - 100 units>'
        assert repr(portfolio) == expected_repr


class TestPortfolioValidation:
    """Test comprehensive portfolio validation"""
    
    def test_multiple_asset_validation_errors(self, app_context):
        """Test that validation can return multiple errors"""
        invalid_fo = Portfolio(asset_type='futures_options')
        errors = invalid_fo.validate_required_fields()
        
        assert len(errors) == 2
        assert 'Contract type is required for F&O assets' in errors
        assert 'Expiry date is required for F&O assets' in errors
    
    def test_equity_validation_no_errors(self, app_context):
        """Test that equity assets don't require additional fields"""
        equity = Portfolio(asset_type='equities')
        assert equity.validate_required_fields() == []
        
        esop = Portfolio(asset_type='esop')
        assert esop.validate_required_fields() == []
    
    def test_unknown_asset_type_validation(self, app_context):
        """Test validation for unknown asset types"""
        unknown = Portfolio(asset_type='unknown_asset')
        assert unknown.validate_required_fields() == []