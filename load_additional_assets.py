"""
Load Additional Asset Class Holdings for Test User
Loads: Fixed Deposits, Real Estate, Gold, Crypto, F&O
"""

import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    User,
    ManualFixedDepositHolding,
    ManualRealEstateHolding,
    ManualCommodityHolding,
    ManualCryptocurrencyHolding,
    ManualFuturesOptionsHolding
)

def load_fixed_deposits():
    """Load FD holdings"""
    print("\n🏦 LOADING FIXED DEPOSITS...")
    print("-" * 80)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            print("❌ Test user not found!")
            return
        
        ManualFixedDepositHolding.query.filter_by(user_id=user.id).delete()
        
        fds = [
            {
                'bank_name': 'HDFC Bank',
                'fd_number': 'FD123456',
                'account_number': '50100123456789',
                'branch_name': 'Mumbai Main Branch',
                'deposit_type': 'Regular',
                'principal_amount': 500000.00,
                'interest_rate': 7.25,
                'tenure_months': 24,
                'deposit_date': date(2023, 6, 1),
                'maturity_date': date(2025, 6, 1),
                'interest_frequency': 'Cumulative',
                'interest_payout': 'Cumulative',
                'tds_applicable': True,
                'nominee_name': 'Spouse Name',
                'nominee_relation': 'Spouse',
                'portfolio_name': 'Fixed Income'
            },
            {
                'bank_name': 'ICICI Bank',
                'fd_number': 'FD789012',
                'account_number': '60200987654321',
                'branch_name': 'Delhi Connaught Place',
                'deposit_type': 'Tax Saver',
                'principal_amount': 150000.00,
                'interest_rate': 7.00,
                'tenure_months': 60,
                'deposit_date': date(2024, 4, 1),
                'maturity_date': date(2029, 4, 1),
                'interest_frequency': 'Annual',
                'interest_payout': 'Payout',
                'tds_applicable': False,
                'nominee_name': 'Parent Name',
                'nominee_relation': 'Parent',
                'portfolio_name': 'Tax Saving'
            },
            {
                'bank_name': 'SBI',
                'fd_number': 'SBI345678',
                'account_number': '12345678901',
                'branch_name': 'Bangalore Koramangala',
                'deposit_type': 'Senior Citizen',
                'principal_amount': 300000.00,
                'interest_rate': 7.75,
                'tenure_months': 12,
                'deposit_date': date(2024, 1, 15),
                'maturity_date': date(2025, 1, 15),
                'interest_frequency': 'Quarterly',
                'interest_payout': 'Payout',
                'tds_applicable': True,
                'nominee_name': 'Child Name',
                'nominee_relation': 'Child',
                'portfolio_name': 'Senior Citizen FD'
            }
        ]
        
        for fd_data in fds:
            fd = ManualFixedDepositHolding(user_id=user.id, **fd_data)
            fd.calculate_maturity()
            db.session.add(fd)
            
            print(f"✅ {fd.bank_name:15} | ₹{fd.principal_amount:>10,.0f} @ {fd.interest_rate}% | "
                  f"Maturity: ₹{fd.maturity_amount:>10,.2f} | "
                  f"Current: ₹{fd.current_value:>10,.2f}")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(fds)} fixed deposits")


def load_real_estate():
    """Load real estate holdings"""
    print("\n🏠 LOADING REAL ESTATE...")
    print("-" * 80)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            return
        
        ManualRealEstateHolding.query.filter_by(user_id=user.id).delete()
        
        properties = [
            {
                'property_name': '3 BHK Apartment - Prestige Lakeside',
                'property_type': 'Residential',
                'property_subtype': 'Apartment',
                'address': 'Prestige Lakeside Habitat, Varthur Road',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560103',
                'area_sqft': 1650.0,
                'bedrooms': 3,
                'bathrooms': 3,
                'purchase_date': date(2020, 3, 15),
                'purchase_price': 12500000.00,
                'stamp_duty': 750000.00,
                'registration_charges': 50000.00,
                'brokerage': 125000.00,
                'other_charges': 75000.00,
                'loan_amount': 8500000.00,
                'loan_bank': 'HDFC Home Loans',
                'emi_amount': 75000.00,
                'loan_tenure_months': 240,
                'current_market_value': 16500000.00,
                'valuation_date': date(2024, 10, 1),
                'is_rented': True,
                'monthly_rent': 45000.00,
                'tenant_name': 'Corporate Tenant',
                'lease_start_date': date(2024, 6, 1),
                'lease_end_date': date(2026, 5, 31),
                'property_tax_annual': 18000.00,
                'maintenance_monthly': 8500.00,
                'portfolio_name': 'Real Estate'
            },
            {
                'property_name': 'Commercial Shop - Phoenix Market City',
                'property_type': 'Commercial',
                'property_subtype': 'Shop',
                'address': 'Phoenix Market City, Whitefield',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560066',
                'area_sqft': 450.0,
                'purchase_date': date(2019, 8, 1),
                'purchase_price': 8500000.00,
                'stamp_duty': 510000.00,
                'registration_charges': 35000.00,
                'brokerage': 85000.00,
                'other_charges': 50000.00,
                'loan_amount': 0.00,
                'current_market_value': 12000000.00,
                'valuation_date': date(2024, 9, 1),
                'is_rented': True,
                'monthly_rent': 85000.00,
                'tenant_name': 'Retail Store',
                'lease_start_date': date(2023, 1, 1),
                'lease_end_date': date(2026, 12, 31),
                'property_tax_annual': 42000.00,
                'maintenance_monthly': 12000.00,
                'portfolio_name': 'Commercial RE'
            }
        ]
        
        for prop_data in properties:
            prop = ManualRealEstateHolding(user_id=user.id, **prop_data)
            prop.total_investment = (
                prop.purchase_price + prop.stamp_duty + prop.registration_charges + 
                prop.brokerage + prop.other_charges
            )
            prop.calculate_values()
            db.session.add(prop)
            
            print(f"✅ {prop.property_name[:35]:35} | {prop.city:12} | "
                  f"Buy: ₹{prop.purchase_price/100000:>5.1f}L | "
                  f"Current: ₹{prop.current_market_value/100000:>5.1f}L | "
                  f"Gain: ₹{prop.unrealized_gain/100000:>5.1f}L ({prop.unrealized_gain_percentage:+.1f}%)")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(properties)} real estate holdings")


def load_gold_commodities():
    """Load gold and commodity holdings"""
    print("\n🪙 LOADING GOLD & COMMODITIES...")
    print("-" * 80)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            return
        
        ManualCommodityHolding.query.filter_by(user_id=user.id).delete()
        
        commodities = [
            {
                'commodity_type': 'Gold',
                'commodity_form': 'Physical',
                'sub_form': 'Jewelry',
                'item_name': '22K Gold Necklace Set',
                'purity': '22K',
                'weight_grams': 85.5,
                'purchase_date': date(2022, 11, 10),
                'quantity': 1,
                'purchase_rate_per_gram': 5200.00,
                'purchase_amount': 444600.00,
                'making_charges': 35000.00,
                'gst': 23988.00,
                'vendor_name': 'Tanishq',
                'bill_number': 'TAN123456',
                'hallmark_number': 'BIS916',
                'current_rate_per_gram': 6450.00,
                'valuation_date': date.today(),
                'storage_location': 'Bank Locker',
                'locker_number': 'L123',
                'locker_rent_annual': 3500.00,
                'insurance_annual': 2000.00,
                'portfolio_name': 'Gold Physical'
            },
            {
                'commodity_type': 'Gold',
                'commodity_form': 'Digital Gold',
                'sub_form': 'Digital',
                'item_name': 'Digital Gold - Paytm',
                'purity': '24K',
                'weight_grams': 25.0,
                'purchase_date': date(2024, 5, 15),
                'quantity': 25,
                'purchase_rate_per_gram': 6100.00,
                'purchase_amount': 152500.00,
                'digital_platform': 'Paytm',
                'digital_account_id': 'PTM987654321',
                'current_rate_per_gram': 6420.00,
                'valuation_date': date.today(),
                'portfolio_name': 'Digital Gold'
            },
            {
                'commodity_type': 'Gold',
                'commodity_form': 'Sovereign Gold Bond',
                'item_name': 'Sovereign Gold Bond 2023-24 Series IV',
                'weight_grams': 50.0,
                'purchase_date': date(2024, 2, 1),
                'quantity': 50,
                'purchase_rate_per_gram': 5950.00,
                'purchase_amount': 297500.00,
                'current_rate_per_gram': 6420.00,
                'valuation_date': date.today(),
                'portfolio_name': 'SGB'
            },
            {
                'commodity_type': 'Silver',
                'commodity_form': 'Physical',
                'sub_form': 'Coins',
                'item_name': '999 Silver Coins',
                'purity': '999',
                'weight_grams': 500.0,
                'purchase_date': date(2023, 6, 20),
                'quantity': 50,
                'purchase_rate_per_gram': 72.00,
                'purchase_amount': 36000.00,
                'gst': 1800.00,
                'vendor_name': 'MMTC-PAMP',
                'current_rate_per_gram': 85.00,
                'valuation_date': date.today(),
                'storage_location': 'Home Safe',
                'portfolio_name': 'Silver'
            }
        ]
        
        for commodity_data in commodities:
            commodity = ManualCommodityHolding(user_id=user.id, **commodity_data)
            commodity.total_investment = (
                commodity.purchase_amount + 
                (commodity.making_charges or 0) + 
                (commodity.gst or 0) + 
                (commodity.other_charges or 0)
            )
            commodity.calculate_values()
            db.session.add(commodity)
            
            print(f"✅ {commodity.commodity_type:8} | {commodity.commodity_form:18} | "
                  f"{commodity.weight_grams:>6.1f}g @ ₹{commodity.purchase_rate_per_gram:>6.0f}/g | "
                  f"Current: ₹{commodity.current_market_value:>10,.0f} | "
                  f"Gain: ₹{commodity.unrealized_gain:>8,.0f} ({commodity.unrealized_gain_percentage:+.1f}%)")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(commodities)} gold & commodity holdings")


def load_cryptocurrency():
    """Load cryptocurrency holdings"""
    print("\n₿ LOADING CRYPTOCURRENCY...")
    print("-" * 80)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            return
        
        ManualCryptocurrencyHolding.query.filter_by(user_id=user.id).delete()
        
        cryptos = [
            {
                'crypto_symbol': 'BTC',
                'crypto_name': 'Bitcoin',
                'platform': 'WazirX',
                'wallet_type': 'Exchange',
                'purchase_date': date(2023, 1, 15),
                'quantity': 0.15,
                'purchase_rate_inr': 1850000.00,
                'purchase_amount': 277500.00,
                'transaction_fee': 555.00,
                'current_rate_inr': 5600000.00,
                'valuation_date': date.today(),
                'is_staked': False,
                'portfolio_name': 'Crypto'
            },
            {
                'crypto_symbol': 'ETH',
                'crypto_name': 'Ethereum',
                'platform': 'CoinDCX',
                'wallet_type': 'Exchange',
                'purchase_date': date(2023, 5, 20),
                'quantity': 2.5,
                'purchase_rate_inr': 145000.00,
                'purchase_amount': 362500.00,
                'transaction_fee': 725.00,
                'gas_fee': 125.00,
                'current_rate_inr': 190000.00,
                'valuation_date': date.today(),
                'is_staked': True,
                'staking_platform': 'CoinDCX Earn',
                'staking_apy': 5.5,
                'staking_rewards_earned': 8500.00,
                'portfolio_name': 'Crypto'
            },
            {
                'crypto_symbol': 'BNB',
                'crypto_name': 'Binance Coin',
                'platform': 'WazirX',
                'wallet_type': 'Exchange',
                'purchase_date': date(2024, 3, 10),
                'quantity': 5.0,
                'purchase_rate_inr': 32000.00,
                'purchase_amount': 160000.00,
                'transaction_fee': 320.00,
                'current_rate_inr': 42000.00,
                'valuation_date': date.today(),
                'is_staked': False,
                'portfolio_name': 'Crypto'
            },
            {
                'crypto_symbol': 'SOL',
                'crypto_name': 'Solana',
                'platform': 'CoinDCX',
                'wallet_type': 'Hardware Wallet',
                'purchase_date': date(2024, 7, 5),
                'quantity': 15.0,
                'purchase_rate_inr': 12000.00,
                'purchase_amount': 180000.00,
                'transaction_fee': 360.00,
                'current_rate_inr': 11500.00,
                'valuation_date': date.today(),
                'is_staked': False,
                'portfolio_name': 'Crypto'
            }
        ]
        
        for crypto_data in cryptos:
            crypto = ManualCryptocurrencyHolding(user_id=user.id, **crypto_data)
            crypto.total_investment = (
                crypto.purchase_amount + 
                (crypto.transaction_fee or 0) + 
                (crypto.gas_fee or 0) + 
                (crypto.other_charges or 0)
            )
            crypto.calculate_values()
            db.session.add(crypto)
            
            staked_text = "⚡ Staked" if crypto.is_staked else ""
            print(f"✅ {crypto.crypto_symbol:5} | {crypto.quantity:>8.4f} coins @ ₹{crypto.purchase_rate_inr:>10,.0f} | "
                  f"Current: ₹{crypto.current_market_value:>10,.0f} | "
                  f"P&L: ₹{crypto.unrealized_gain:>9,.0f} ({crypto.unrealized_gain_percentage:+.1f}%) {staked_text}")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(cryptos)} cryptocurrency holdings")


def load_futures_options():
    """Load F&O holdings"""
    print("\n📊 LOADING FUTURES & OPTIONS...")
    print("-" * 80)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            return
        
        ManualFuturesOptionsHolding.query.filter_by(user_id=user.id).delete()
        
        # Calculate expiry dates (last Thursday of month)
        today = date.today()
        current_month_expiry = date(2024, 10, 31)
        next_month_expiry = date(2024, 11, 28)
        
        fno_positions = [
            {
                'contract_type': 'Future',
                'underlying_asset': 'NIFTY',
                'symbol': 'NIFTY24OCTFUT',
                'lot_size': 50,
                'quantity_lots': 2,
                'total_quantity': 100,
                'expiry_date': current_month_expiry,
                'trade_date': date(2024, 10, 15),
                'position_type': 'Long',
                'entry_price': 24500.00,
                'brokerage': 100.00,
                'stt': 122.50,
                'exchange_charges': 50.00,
                'gst': 30.60,
                'current_market_price': 24750.00,
                'position_status': 'Open',
                'portfolio_name': 'F&O Trading'
            },
            {
                'contract_type': 'Call Option',
                'underlying_asset': 'RELIANCE',
                'symbol': 'RELIANCE24OCT2700CE',
                'strike_price': 2700.00,
                'lot_size': 250,
                'quantity_lots': 1,
                'total_quantity': 250,
                'expiry_date': current_month_expiry,
                'trade_date': date(2024, 10, 18),
                'position_type': 'Long',
                'entry_price': 45.00,
                'premium_paid': 11250.00,
                'brokerage': 50.00,
                'stt': 28.13,
                'exchange_charges': 20.00,
                'gst': 17.66,
                'current_market_price': 62.00,
                'position_status': 'Open',
                'portfolio_name': 'Options'
            },
            {
                'contract_type': 'Put Option',
                'underlying_asset': 'BANKNIFTY',
                'symbol': 'BANKNIFTY24NOV51500PE',
                'strike_price': 51500.00,
                'lot_size': 15,
                'quantity_lots': 2,
                'total_quantity': 30,
                'expiry_date': next_month_expiry,
                'trade_date': date(2024, 10, 20),
                'position_type': 'Long',
                'entry_price': 180.00,
                'premium_paid': 5400.00,
                'brokerage': 40.00,
                'stt': 13.50,
                'exchange_charges': 15.00,
                'gst': 12.33,
                'current_market_price': 215.00,
                'position_status': 'Open',
                'portfolio_name': 'Options'
            },
            {
                'contract_type': 'Future',
                'underlying_asset': 'TCS',
                'symbol': 'TCS24OCTFUT',
                'lot_size': 125,
                'quantity_lots': 1,
                'total_quantity': 125,
                'expiry_date': current_month_expiry,
                'trade_date': date(2024, 10, 10),
                'position_type': 'Long',
                'entry_price': 3420.00,
                'brokerage': 75.00,
                'stt': 53.38,
                'exchange_charges': 25.00,
                'gst': 27.61,
                'current_market_price': 3475.00,
                'position_status': 'Open',
                'portfolio_name': 'Stock Futures'
            }
        ]
        
        for fno_data in fno_positions:
            fno = ManualFuturesOptionsHolding(user_id=user.id, **fno_data)
            fno.total_charges = (
                (fno.brokerage or 0) + (fno.stt or 0) + 
                (fno.exchange_charges or 0) + (fno.gst or 0) + 
                (fno.other_charges or 0)
            )
            
            if fno.contract_type == 'Future':
                fno.total_investment = (fno.entry_price * fno.total_quantity) + fno.total_charges
            else:  # Options
                fno.total_investment = fno.premium_paid + fno.total_charges
            
            fno.calculate_values()
            db.session.add(fno)
            
            contract_desc = f"{fno.contract_type[:4]:4}"
            if fno.strike_price:
                contract_desc += f" {fno.strike_price:.0f}"
            
            print(f"✅ {fno.underlying_asset:10} | {contract_desc:15} | "
                  f"{fno.quantity_lots:>2} Lot | "
                  f"Entry: ₹{fno.entry_price:>7.2f} → ₹{fno.current_market_price:>7.2f} | "
                  f"P&L: ₹{fno.unrealized_pnl:>8,.0f} ({fno.unrealized_pnl_percentage:+.1f}%)")
        
        db.session.commit()
        print(f"\n✅ Loaded {len(fno_positions)} F&O positions")


def show_complete_summary():
    """Show complete portfolio summary"""
    print("\n" + "=" * 100)
    print("📊 COMPLETE PORTFOLIO SUMMARY")
    print("=" * 100)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            return
        
        summary_data = []
        
        # FDs
        fds = ManualFixedDepositHolding.query.filter_by(user_id=user.id).all()
        fd_investment = sum(f.principal_amount for f in fds)
        fd_value = sum(f.current_value or 0 for f in fds)
        summary_data.append(('Fixed Deposits', len(fds), fd_investment, fd_value, fd_value - fd_investment))
        
        # Real Estate
        properties = ManualRealEstateHolding.query.filter_by(user_id=user.id).all()
        re_investment = sum(p.total_investment for p in properties)
        re_value = sum(p.current_market_value or 0 for p in properties)
        summary_data.append(('Real Estate', len(properties), re_investment, re_value, re_value - re_investment))
        
        # Gold
        commodities = ManualCommodityHolding.query.filter_by(user_id=user.id).all()
        gold_investment = sum(c.total_investment for c in commodities)
        gold_value = sum(c.current_market_value or 0 for c in commodities)
        summary_data.append(('Gold & Commodities', len(commodities), gold_investment, gold_value, gold_value - gold_investment))
        
        # Crypto
        cryptos = ManualCryptocurrencyHolding.query.filter_by(user_id=user.id).all()
        crypto_investment = sum(c.total_investment for c in cryptos)
        crypto_value = sum(c.current_market_value or 0 for c in cryptos)
        summary_data.append(('Cryptocurrency', len(cryptos), crypto_investment, crypto_value, crypto_value - crypto_investment))
        
        # F&O
        fnos = ManualFuturesOptionsHolding.query.filter_by(user_id=user.id).all()
        fno_investment = sum(f.total_investment for f in fnos)
        fno_value = sum(f.current_value or 0 for f in fnos)
        summary_data.append(('F&O Positions', len(fnos), fno_investment, fno_value, fno_value - fno_investment))
        
        print(f"\n{'Asset Class':<25} {'Count':>6} {'Investment':>18} {'Current Value':>18} {'P&L':>18}")
        print("-" * 100)
        
        total_investment = 0
        total_value = 0
        
        for asset_class, count, investment, value, pnl in summary_data:
            pnl_pct = (pnl / investment * 100) if investment > 0 else 0
            print(f"{asset_class:<25} {count:>6} ₹{investment:>16,.0f} ₹{value:>16,.0f} "
                  f"₹{pnl:>10,.0f} ({pnl_pct:+.1f}%)")
            total_investment += investment
            total_value += value
        
        print("-" * 100)
        total_pnl = total_value - total_investment
        total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        print(f"{'TOTAL':<25} {'':<6} ₹{total_investment:>16,.0f} ₹{total_value:>16,.0f} "
              f"₹{total_pnl:>10,.0f} ({total_pnl_pct:+.1f}%)")
        
        print("\n" + "=" * 100)


if __name__ == "__main__":
    print("\n🚀 LOADING ADDITIONAL ASSET CLASS HOLDINGS")
    print("=" * 100)
    
    try:
        load_fixed_deposits()
        load_real_estate()
        load_gold_commodities()
        load_cryptocurrency()
        load_futures_options()
        show_complete_summary()
        
        print("\n✅ ALL ADDITIONAL ASSET CLASS HOLDINGS LOADED SUCCESSFULLY!")
        print("\n👤 Login: test@targetcapital.com / test123")
        print("📂 View in: Dashboard → Portfolio Hub → [Select Asset Class]")
        print("\n🎯 Test Data Includes:")
        print("   • 3 Fixed Deposits (HDFC, ICICI, SBI)")
        print("   • 2 Real Estate Properties (Residential + Commercial)")
        print("   • 4 Gold/Commodity holdings (Physical Gold, Digital Gold, SGB, Silver)")
        print("   • 4 Cryptocurrency positions (BTC, ETH, BNB, SOL)")
        print("   • 4 F&O positions (NIFTY Future, RELIANCE Call, BANKNIFTY Put, TCS Future)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
