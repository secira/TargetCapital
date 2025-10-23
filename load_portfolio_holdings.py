"""
Load Portfolio Holdings for Test User
Populates ManualEquityHolding and ManualMutualFundHolding tables
"""

import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import ManualEquityHolding, ManualMutualFundHolding, User

def load_equity_holdings():
    """Load equity holdings for test user"""
    print("\n📈 LOADING EQUITY HOLDINGS...")
    print("-" * 60)
    
    with app.app_context():
        # Get test user
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            print("❌ Test user not found!")
            return
        
        # Clear existing holdings for fresh start
        ManualEquityHolding.query.filter_by(user_id=user.id).delete()
        
        equity_holdings = [
            {
                'symbol': 'RELIANCE',
                'company_name': 'Reliance Industries Ltd',
                'isin': 'INE002A01018',
                'purchase_date': date(2024, 6, 15),
                'quantity': 100,
                'purchase_price': 2500.50,
                'brokerage': 50.0,
                'stt': 25.0,
                'transaction_charges': 10.0,
                'gst': 8.50,
                'stamp_duty': 5.0,
                'current_price': 2650.00,
                'portfolio_name': 'Growth Portfolio'
            },
            {
                'symbol': 'TCS',
                'company_name': 'Tata Consultancy Services Ltd',
                'isin': 'INE467B01029',
                'purchase_date': date(2024, 7, 20),
                'quantity': 50,
                'purchase_price': 3200.00,
                'brokerage': 40.0,
                'stt': 16.0,
                'transaction_charges': 8.0,
                'gst': 6.40,
                'stamp_duty': 4.0,
                'current_price': 3450.00,
                'portfolio_name': 'Core Portfolio'
            },
            {
                'symbol': 'HDFCBANK',
                'company_name': 'HDFC Bank Ltd',
                'isin': 'INE040A01034',
                'purchase_date': date(2024, 5, 10),
                'quantity': 75,
                'purchase_price': 1550.00,
                'brokerage': 30.0,
                'stt': 11.63,
                'transaction_charges': 6.0,
                'gst': 4.75,
                'stamp_duty': 3.0,
                'current_price': 1620.00,
                'portfolio_name': 'Banking Portfolio'
            },
            {
                'symbol': 'INFY',
                'company_name': 'Infosys Ltd',
                'isin': 'INE009A01021',
                'purchase_date': date(2024, 8, 5),
                'quantity': 60,
                'purchase_price': 1450.00,
                'brokerage': 25.0,
                'stt': 8.70,
                'transaction_charges': 5.0,
                'gst': 4.00,
                'stamp_duty': 2.50,
                'current_price': 1480.00,
                'portfolio_name': 'IT Portfolio'
            },
            {
                'symbol': 'ICICIBANK',
                'company_name': 'ICICI Bank Ltd',
                'isin': 'INE090A01021',
                'purchase_date': date(2024, 4, 15),
                'quantity': 80,
                'purchase_price': 950.00,
                'brokerage': 28.0,
                'stt': 7.60,
                'transaction_charges': 5.50,
                'gst': 4.20,
                'stamp_duty': 2.80,
                'current_price': 1020.00,
                'portfolio_name': 'Banking Portfolio'
            }
        ]
        
        for holding_data in equity_holdings:
            holding = ManualEquityHolding(
                user_id=user.id,
                **holding_data
            )
            holding.calculate_totals()
            db.session.add(holding)
            
            print(f"✅ {holding.symbol:12} | Qty: {holding.quantity:6.0f} | "
                  f"Buy: ₹{holding.purchase_price:8.2f} | "
                  f"Current: ₹{holding.current_price:8.2f} | "
                  f"P&L: ₹{holding.unrealized_pnl:8.2f} ({holding.unrealized_pnl_percentage:+.2f}%)")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(equity_holdings)} equity holdings")


def load_mutual_fund_holdings():
    """Load mutual fund holdings for test user"""
    print("\n💰 LOADING MUTUAL FUND HOLDINGS...")
    print("-" * 60)
    
    with app.app_context():
        # Get test user
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            print("❌ Test user not found!")
            return
        
        # Clear existing holdings
        ManualMutualFundHolding.query.filter_by(user_id=user.id).delete()
        
        mf_holdings = [
            {
                'scheme_name': 'HDFC Equity Fund - Direct Plan - Growth',
                'fund_house': 'HDFC Asset Management Company',
                'isin': 'INF179KA1215',
                'folio_number': '12345/67',
                'fund_category': 'Equity',
                'transaction_date': date(2024, 1, 15),
                'units': 250.456,
                'nav': 718.50,
                'amount': 180000.00,
                'entry_load': 0.0,
                'exit_load': 0.0,
                'stamp_duty': 50.0,
                'stt': 0.0,
                'other_charges': 0.0,
                'current_nav': 850.50,
                'portfolio_name': 'Equity MF'
            },
            {
                'scheme_name': 'SBI Bluechip Fund - Direct Plan - Growth',
                'fund_house': 'SBI Mutual Fund',
                'isin': 'INF200KA1156',
                'folio_number': '98765/43',
                'fund_category': 'Equity',
                'transaction_date': date(2024, 2, 10),
                'units': 180.234,
                'nav': 888.00,
                'amount': 160000.00,
                'entry_load': 0.0,
                'exit_load': 0.0,
                'stamp_duty': 40.0,
                'stt': 0.0,
                'other_charges': 0.0,
                'current_nav': 975.25,
                'portfolio_name': 'Equity MF'
            },
            {
                'scheme_name': 'ICICI Prudential Technology Fund - Direct Plan - Growth',
                'fund_house': 'ICICI Prudential Mutual Fund',
                'isin': 'INF109KA1721',
                'folio_number': '54321/98',
                'fund_category': 'Equity',
                'transaction_date': date(2024, 3, 5),
                'units': 120.567,
                'nav': 912.50,
                'amount': 110000.00,
                'entry_load': 0.0,
                'exit_load': 0.0,
                'stamp_duty': 30.0,
                'stt': 0.0,
                'other_charges': 0.0,
                'current_nav': 1125.75,
                'portfolio_name': 'Sector MF'
            },
            {
                'scheme_name': 'Axis Long Term Equity Fund - Direct Plan - Growth',
                'fund_house': 'Axis Asset Management Company',
                'isin': 'INF846K01EW4',
                'folio_number': '11223/44',
                'fund_category': 'ELSS',
                'transaction_date': date(2024, 4, 1),
                'units': 95.234,
                'nav': 1050.00,
                'amount': 100000.00,
                'entry_load': 0.0,
                'exit_load': 0.0,
                'stamp_duty': 25.0,
                'stt': 0.0,
                'other_charges': 0.0,
                'current_nav': 1180.50,
                'portfolio_name': 'Tax Saver'
            }
        ]
        
        for mf_data in mf_holdings:
            mf = ManualMutualFundHolding(
                user_id=user.id,
                **mf_data
            )
            mf.calculate_totals()
            db.session.add(mf)
            
            print(f"✅ {mf.scheme_name[:40]:40} | Units: {mf.units:8.3f} | "
                  f"NAV: ₹{mf.nav:7.2f} → ₹{mf.current_nav:7.2f} | "
                  f"P&L: ₹{mf.unrealized_pnl:8.2f} ({mf.unrealized_pnl_percentage:+.2f}%)")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(mf_holdings)} mutual fund holdings")


def show_summary():
    """Show portfolio summary"""
    print("\n" + "=" * 80)
    print("📊 PORTFOLIO SUMMARY")
    print("=" * 80)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            return
        
        # Equity Summary
        equity_holdings = ManualEquityHolding.query.filter_by(user_id=user.id).all()
        total_equity_investment = sum(h.total_investment for h in equity_holdings)
        total_equity_value = sum(h.current_value or 0 for h in equity_holdings)
        total_equity_pnl = total_equity_value - total_equity_investment
        equity_pnl_pct = (total_equity_pnl / total_equity_investment * 100) if total_equity_investment > 0 else 0
        
        print(f"\n📈 EQUITIES:")
        print(f"   Holdings: {len(equity_holdings)}")
        print(f"   Investment: ₹{total_equity_investment:,.2f}")
        print(f"   Current Value: ₹{total_equity_value:,.2f}")
        print(f"   P&L: ₹{total_equity_pnl:,.2f} ({equity_pnl_pct:+.2f}%)")
        
        # Mutual Fund Summary
        mf_holdings = ManualMutualFundHolding.query.filter_by(user_id=user.id).all()
        total_mf_investment = sum(h.total_investment for h in mf_holdings)
        total_mf_value = sum(h.current_value or 0 for h in mf_holdings)
        total_mf_pnl = total_mf_value - total_mf_investment
        mf_pnl_pct = (total_mf_pnl / total_mf_investment * 100) if total_mf_investment > 0 else 0
        
        print(f"\n💰 MUTUAL FUNDS:")
        print(f"   Holdings: {len(mf_holdings)}")
        print(f"   Investment: ₹{total_mf_investment:,.2f}")
        print(f"   Current Value: ₹{total_mf_value:,.2f}")
        print(f"   P&L: ₹{total_mf_pnl:,.2f} ({mf_pnl_pct:+.2f}%)")
        
        # Total Portfolio
        total_investment = total_equity_investment + total_mf_investment
        total_value = total_equity_value + total_mf_value
        total_pnl = total_value - total_investment
        total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        print(f"\n📊 TOTAL PORTFOLIO:")
        print(f"   Total Investment: ₹{total_investment:,.2f}")
        print(f"   Current Value: ₹{total_value:,.2f}")
        print(f"   Total P&L: ₹{total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🚀 LOADING PORTFOLIO HOLDINGS FOR TEST USER")
    print("=" * 80)
    
    try:
        load_equity_holdings()
        load_mutual_fund_holdings()
        show_summary()
        
        print("\n✅ ALL PORTFOLIO HOLDINGS LOADED SUCCESSFULLY!")
        print("\n👤 Login with: test@targetcapital.com / test123")
        print("📂 Navigate to: Dashboard → Portfolio Hub → Equities / Mutual Funds")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
