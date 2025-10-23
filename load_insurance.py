"""
Load Insurance Holdings for Test User
Adds various types of insurance policies: Term, Life, Health, Motor, etc.
"""

import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, ManualInsuranceHolding

def load_insurance_policies():
    """Load various insurance policies"""
    print("\n🛡️ LOADING INSURANCE POLICIES...")
    print("-" * 100)
    
    with app.app_context():
        user = User.query.filter_by(email='test@targetcapital.com').first()
        if not user:
            print("❌ Test user not found!")
            return
        
        # Clear existing insurance policies
        ManualInsuranceHolding.query.filter_by(user_id=user.id).delete()
        
        policies = [
            {
                'insurance_type': 'Term Life',
                'policy_name': 'HDFC Life Click 2 Protect Plus',
                'policy_number': 'HDFC/TERM/12345678',
                'insurance_company': 'HDFC Life Insurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Test User',
                'sum_assured': 10000000.00,  # 1 Crore
                'policy_term_years': 30,
                'premium_amount': 12500.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 30,
                'total_premiums_paid': 62500.00,  # 5 years paid
                'policy_start_date': date(2019, 4, 1),
                'policy_end_date': date(2049, 3, 31),
                'maturity_date': date(2049, 3, 31),
                'next_premium_due_date': date(2025, 4, 1),
                'maturity_amount': 0.00,  # Term insurance - no maturity benefit
                'nominee_name': 'Spouse Name',
                'nominee_relation': 'Spouse',
                'agent_name': 'Rajesh Kumar',
                'agent_contact': '+91-9876543210',
                'policy_status': 'Active',
                'portfolio_name': 'Life Insurance'
            },
            {
                'insurance_type': 'Life (Endowment)',
                'policy_name': 'LIC Jeevan Anand',
                'policy_number': 'LIC/512345678',
                'insurance_company': 'LIC of India',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Test User',
                'sum_assured': 2000000.00,  # 20 Lakhs
                'policy_term_years': 25,
                'premium_amount': 45000.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 20,
                'total_premiums_paid': 450000.00,  # 10 years paid
                'policy_start_date': date(2014, 6, 15),
                'policy_end_date': date(2039, 6, 14),
                'maturity_date': date(2039, 6, 14),
                'next_premium_due_date': date(2025, 6, 15),
                'maturity_amount': 2500000.00,  # Includes bonus
                'bonus_accumulated': 350000.00,
                'surrender_value': 420000.00,
                'nominee_name': 'Parent Name',
                'nominee_relation': 'Parent',
                'agent_name': 'Suresh Sharma',
                'agent_contact': '+91-9765432109',
                'policy_status': 'Active',
                'portfolio_name': 'Endowment Plans'
            },
            {
                'insurance_type': 'Health',
                'policy_name': 'Star Health Comprehensive Insurance',
                'policy_number': 'STAR/HLT/987654321',
                'insurance_company': 'Star Health Insurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Self & Family (4 members)',
                'sum_assured': 1000000.00,  # 10 Lakhs family floater
                'policy_term_years': 1,
                'premium_amount': 28000.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 1,
                'total_premiums_paid': 84000.00,  # 3 years paid
                'policy_start_date': date(2024, 8, 1),
                'policy_end_date': date(2025, 7, 31),
                'next_premium_due_date': date(2025, 8, 1),
                'nominee_name': 'Spouse Name',
                'nominee_relation': 'Spouse',
                'agent_name': 'Priya Desai',
                'agent_contact': '+91-9654321098',
                'policy_status': 'Active',
                'portfolio_name': 'Health Insurance',
                'notes': 'Family Floater: Self, Spouse, 2 Children. Coverage includes pre and post hospitalization, room rent, ICU charges.'
            },
            {
                'insurance_type': 'Health (Critical Illness)',
                'policy_name': 'ICICI Lombard Cancer Care Plus',
                'policy_number': 'ICICI/CI/456789012',
                'insurance_company': 'ICICI Lombard General Insurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Test User',
                'sum_assured': 5000000.00,  # 50 Lakhs critical illness cover
                'policy_term_years': 10,
                'premium_amount': 18000.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 10,
                'total_premiums_paid': 54000.00,  # 3 years paid
                'policy_start_date': date(2022, 1, 10),
                'policy_end_date': date(2032, 1, 9),
                'next_premium_due_date': date(2025, 1, 10),
                'nominee_name': 'Spouse Name',
                'nominee_relation': 'Spouse',
                'agent_name': 'Amit Patel',
                'agent_contact': '+91-9543210987',
                'policy_status': 'Active',
                'portfolio_name': 'Critical Illness Cover',
                'notes': 'Covers 36+ critical illnesses including cancer, heart attack, stroke, organ failure.'
            },
            {
                'insurance_type': 'Motor (Car)',
                'policy_name': 'Bajaj Allianz Comprehensive Car Insurance',
                'policy_number': 'BAJAJ/CAR/123456789',
                'insurance_company': 'Bajaj Allianz General Insurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Honda City VX (KA-01-AB-1234)',
                'sum_assured': 1200000.00,  # IDV (Insured Declared Value)
                'policy_term_years': 1,
                'premium_amount': 18500.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 1,
                'total_premiums_paid': 18500.00,  # Current year
                'policy_start_date': date(2024, 9, 1),
                'policy_end_date': date(2025, 8, 31),
                'next_premium_due_date': date(2025, 9, 1),
                'agent_name': 'Auto Dealership',
                'agent_contact': '+91-9432109876',
                'policy_status': 'Active',
                'portfolio_name': 'Motor Insurance',
                'notes': 'Comprehensive coverage with zero depreciation add-on, engine protection, roadside assistance, NCB 35%'
            },
            {
                'insurance_type': 'Motor (Two Wheeler)',
                'policy_name': 'HDFC ERGO Bike Insurance',
                'policy_number': 'HDFC/BIKE/987654321',
                'insurance_company': 'HDFC ERGO General Insurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Honda Activa (KA-02-XY-5678)',
                'sum_assured': 75000.00,  # IDV
                'policy_term_years': 1,
                'premium_amount': 2800.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 1,
                'total_premiums_paid': 2800.00,
                'policy_start_date': date(2024, 7, 15),
                'policy_end_date': date(2025, 7, 14),
                'next_premium_due_date': date(2025, 7, 15),
                'agent_name': 'Online Purchase',
                'policy_status': 'Active',
                'portfolio_name': 'Motor Insurance',
                'notes': 'Comprehensive policy with personal accident cover ₹15 lakhs'
            },
            {
                'insurance_type': 'Home Insurance',
                'policy_name': 'New India Home Protect Plan',
                'policy_number': 'NIA/HOME/111222333',
                'insurance_company': 'New India Assurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': '3 BHK Apartment - Prestige Lakeside',
                'sum_assured': 5000000.00,  # Building + Contents
                'policy_term_years': 1,
                'premium_amount': 12000.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 1,
                'total_premiums_paid': 36000.00,  # 3 years
                'policy_start_date': date(2024, 3, 1),
                'policy_end_date': date(2025, 2, 28),
                'next_premium_due_date': date(2025, 3, 1),
                'agent_name': 'Insurance Broker',
                'agent_contact': '+91-9321098765',
                'policy_status': 'Active',
                'portfolio_name': 'Property Insurance',
                'notes': 'Covers: Building Structure ₹35L, Contents ₹15L, Burglary ₹5L, Public Liability ₹10L'
            },
            {
                'insurance_type': 'Personal Accident',
                'policy_name': 'TATA AIG Personal Accident Policy',
                'policy_number': 'TATA/PA/444555666',
                'insurance_company': 'TATA AIG General Insurance',
                'policy_holder_name': 'Test User',
                'insured_person_name': 'Test User',
                'sum_assured': 10000000.00,  # 1 Crore
                'policy_term_years': 1,
                'premium_amount': 3500.00,
                'premium_frequency': 'Annual',
                'premium_payment_term_years': 1,
                'total_premiums_paid': 7000.00,  # 2 years
                'policy_start_date': date(2024, 5, 1),
                'policy_end_date': date(2025, 4, 30),
                'next_premium_due_date': date(2025, 5, 1),
                'nominee_name': 'Spouse Name',
                'nominee_relation': 'Spouse',
                'agent_name': 'Online Purchase',
                'policy_status': 'Active',
                'portfolio_name': 'Accident Cover',
                'notes': 'Coverage: Accidental Death ₹1Cr, Permanent Total Disability ₹1Cr, Medical Expenses ₹10L'
            }
        ]
        
        total_sum_assured = 0
        total_premiums = 0
        
        for policy_data in policies:
            policy = ManualInsuranceHolding(user_id=user.id, **policy_data)
            db.session.add(policy)
            
            total_sum_assured += policy.sum_assured
            total_premiums += policy.total_premiums_paid
            
            # Display with proper formatting
            premium_text = f"₹{policy.premium_amount:>7,.0f}/{policy.premium_frequency[:3]}"
            status_icon = "✅" if policy.policy_status == "Active" else "⚠️"
            
            print(f"{status_icon} {policy.insurance_type:25} | {policy.insurance_company[:25]:25} | "
                  f"Cover: ₹{policy.sum_assured/100000:>5.1f}L | "
                  f"Premium: {premium_text:15} | Due: {policy.next_premium_due_date.strftime('%d-%b-%Y') if policy.next_premium_due_date else 'N/A':12}")
        
        db.session.commit()
        
        print("\n" + "-" * 100)
        print(f"✅ Loaded {len(policies)} insurance policies")
        print(f"\n📊 Insurance Portfolio Summary:")
        print(f"   Total Coverage: ₹{total_sum_assured/10000000:.2f} Crores")
        print(f"   Total Premiums Paid: ₹{total_premiums:,.0f}")
        
        # Group by type
        print(f"\n📋 Policies by Type:")
        policy_types = {}
        for policy in ManualInsuranceHolding.query.filter_by(user_id=user.id).all():
            policy_type = policy.insurance_type
            if policy_type not in policy_types:
                policy_types[policy_type] = {'count': 0, 'coverage': 0}
            policy_types[policy_type]['count'] += 1
            policy_types[policy_type]['coverage'] += policy.sum_assured
        
        for ptype, data in sorted(policy_types.items()):
            print(f"   {ptype:25} : {data['count']} policies | ₹{data['coverage']/100000:>7.1f}L coverage")
        
        print("\n" + "=" * 100)


if __name__ == "__main__":
    print("\n🚀 LOADING INSURANCE POLICIES FOR TEST USER")
    print("=" * 100)
    
    try:
        load_insurance_policies()
        
        print("\n✅ ALL INSURANCE POLICIES LOADED SUCCESSFULLY!")
        print("\n👤 Login: test@targetcapital.com / test123")
        print("📂 View in: Dashboard → Portfolio Hub → Insurance")
        print("\n🎯 Test Data Includes:")
        print("   • 1 Term Life Insurance (₹1 Crore cover)")
        print("   • 1 Life Endowment Plan (₹20 Lakhs)")
        print("   • 1 Family Health Insurance (₹10 Lakhs floater)")
        print("   • 1 Critical Illness Cover (₹50 Lakhs)")
        print("   • 1 Car Insurance (Honda City)")
        print("   • 1 Two Wheeler Insurance (Honda Activa)")
        print("   • 1 Home Insurance (₹50 Lakhs)")
        print("   • 1 Personal Accident Cover (₹1 Crore)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
