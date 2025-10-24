#!/usr/bin/env python3
"""
Populate Vector Database with Sample Indian Stock Market Data
Generates embeddings using OpenAI and stores in PostgreSQL with pgvector
"""

import json
from datetime import datetime, timedelta
from app import app, db
from models import VectorDocument
from services.vector_service import VectorService

# Sample stock market data for Indian stocks
SAMPLE_DOCUMENTS = [
    # Reliance Industries
    {
        'document_type': 'stock_data',
        'symbol': 'RELIANCE',
        'title': 'Reliance Industries Limited - Company Overview',
        'content': '''Reliance Industries Limited (RIL) is India's largest private sector corporation with a market cap of over ₹17 lakh crore. 
        The company operates in four main business segments: Oil to Chemicals (O2C), Oil and Gas, Retail, and Digital Services (Jio). 
        RIL has shown consistent revenue growth with FY23 revenue at ₹8,92,000 crore. The company's debt-to-equity ratio is 0.52, 
        indicating healthy financial leverage. Recent expansion in renewable energy and telecom sectors positions RIL for long-term growth. 
        The stock trades at a P/E ratio of 28.5 and offers a dividend yield of 0.35%. Institutional ownership stands at 28%, 
        with strong promoter holding of 50.4%. The company has announced plans to invest ₹75,000 crore in green energy over the next 3 years.''',
        'sector': 'Conglomerate',
        'category': 'Large Cap',
        'source_url': 'https://www.ril.com',
        'published_date': datetime.now() - timedelta(days=2)
    },
    {
        'document_type': 'news',
        'symbol': 'RELIANCE',
        'title': 'Reliance Industries Announces Major Green Hydrogen Initiative',
        'content': '''Reliance Industries announced a ₹75,000 crore investment in green hydrogen and renewable energy projects. 
        The company aims to become carbon neutral by 2035. This strategic move aligns with India's 2070 net-zero carbon emissions target. 
        Analysts view this positively as it diversifies RIL's revenue streams beyond traditional oil and gas. 
        The project is expected to create over 100,000 jobs and position India as a global green hydrogen hub. 
        Market sentiment remains bullish with target prices ranging from ₹2,800 to ₹3,200.''',
        'sector': 'Conglomerate',
        'category': 'Market News',
        'source_url': 'https://economictimes.com',
        'published_date': datetime.now() - timedelta(days=1)
    },
    
    # TCS
    {
        'document_type': 'stock_data',
        'symbol': 'TCS',
        'title': 'Tata Consultancy Services - IT Services Leader',
        'content': '''TCS is India's largest IT services company with market cap of ₹13 lakh crore. 
        The company reported Q3 FY24 revenue of ₹59,162 crore with net profit of ₹11,058 crore, showing 4.1% YoY growth. 
        TCS maintains industry-leading operating margins of 25%+ and has a strong order book of $11.2 billion. 
        The company serves clients across BFSI, Retail, Manufacturing, and Healthcare sectors globally. 
        With 614,000+ employees, TCS has a strong talent retention rate of 92%. 
        The stock trades at P/E of 27.8 and offers consistent dividend yield of 1.2%. 
        Recent cloud transformation deals and AI/ML initiatives position TCS well for digital transformation demand.''',
        'sector': 'IT Services',
        'category': 'Large Cap',
        'source_url': 'https://www.tcs.com',
        'published_date': datetime.now() - timedelta(days=3)
    },
    {
        'document_type': 'earnings',
        'symbol': 'TCS',
        'title': 'TCS Q3 FY24 Earnings Report - Strong Growth Despite Global Headwinds',
        'content': '''TCS reported strong Q3 FY24 results with revenue at ₹59,162 crore (up 4.1% YoY) and net profit at ₹11,058 crore (up 7.8% YoY). 
        The company added 8 new clients in the $100 million+ bracket, taking the total to 62. 
        North America contributed 50% of revenue, Europe 31%, and India 5%. 
        BFSI vertical grew 6.2% while Retail faced headwinds with 2.1% decline. 
        Management guided for 14-16% revenue growth for FY24. 
        TCS announced ₹18 per share interim dividend. 
        The company is focusing on generative AI solutions with over 270 active AI projects. 
        Attrition rate improved to 11.2% from 17.8% last year.''',
        'sector': 'IT Services',
        'category': 'Earnings Report',
        'source_url': 'https://www.tcs.com/investor-relations',
        'published_date': datetime.now() - timedelta(days=15)
    },
    
    # HDFC Bank
    {
        'document_type': 'stock_data',
        'symbol': 'HDFCBANK',
        'title': 'HDFC Bank - India\'s Largest Private Sector Bank',
        'content': '''HDFC Bank is India's largest private sector bank with market cap of ₹12 lakh crore and asset base of ₹24 lakh crore. 
        The bank has 8,342 branches across India serving 85 million customers. 
        Q3 FY24 net profit stood at ₹16,372 crore with NII of ₹28,735 crore. 
        Asset quality remains strong with Gross NPA at 1.26% and Net NPA at 0.31%. 
        The bank maintains healthy CASA ratio of 40.8% and capital adequacy ratio of 18.9%. 
        HDFC Bank's digital banking platform has 73 million active users. 
        The stock trades at P/B of 2.8 and offers dividend yield of 1.1%. 
        Recent merger with HDFC Ltd creates one of the world's largest banks with improved liability franchise.''',
        'sector': 'Banking',
        'category': 'Large Cap',
        'source_url': 'https://www.hdfcbank.com',
        'published_date': datetime.now() - timedelta(days=5)
    },
    {
        'document_type': 'news',
        'symbol': 'HDFCBANK',
        'title': 'HDFC Bank Reports Record Quarterly Profit Post-Merger',
        'content': '''HDFC Bank reported record quarterly profit of ₹16,372 crore in Q3 FY24, marking strong growth post-merger with HDFC Ltd. 
        The merged entity now has total assets of ₹24 lakh crore, making it one of the largest banks globally by market capitalization. 
        Management highlighted improved cost-to-income ratio at 38.2% and strong credit growth of 16.8% YoY. 
        The bank added 1.2 crore new customers in the quarter, driven by digital banking initiatives. 
        Retail loans constitute 53% of total loan book while corporate and SME loans contribute 47%. 
        Analysts maintain 'Buy' rating with target price of ₹1,850-₹1,950.''',
        'sector': 'Banking',
        'category': 'Market News',
        'source_url': 'https://economictimes.com',
        'published_date': datetime.now() - timedelta(hours=18)
    },
    
    # Infosys
    {
        'document_type': 'stock_data',
        'symbol': 'INFY',
        'title': 'Infosys - Digital Transformation Leader',
        'content': '''Infosys is India's second-largest IT services company with market cap of ₹6.5 lakh crore. 
        Q3 FY24 revenue stood at ₹38,994 crore with net profit of ₹6,586 crore, representing 3.7% constant currency growth. 
        The company has a healthy order book with 73 large deals worth $17.7 billion signed in 9 months. 
        Infosys maintains operating margins of 21%+ and has strong presence in cloud, AI, and automation services. 
        The company employs 345,000+ professionals and serves 1,800+ clients globally. 
        Stock trades at P/E of 25.4 with dividend yield of 2.4%, making it attractive for income investors. 
        Recent partnerships with Microsoft Azure and Google Cloud strengthen its digital capabilities.''',
        'sector': 'IT Services',
        'category': 'Large Cap',
        'source_url': 'https://www.infosys.com',
        'published_date': datetime.now() - timedelta(days=4)
    },
    
    # ITC
    {
        'document_type': 'stock_data',
        'symbol': 'ITC',
        'title': 'ITC Limited - Diversified FMCG Conglomerate',
        'content': '''ITC is a diversified conglomerate with presence in FMCG, Hotels, Paperboards, Packaging, and Agri-Business. 
        Market cap stands at ₹5.2 lakh crore with consistent dividend-paying track record of 25+ years. 
        FY23 revenue was ₹68,951 crore with net profit of ₹19,332 crore, showing strong EBITDA margins of 38%. 
        FMCG segment contributes 53% of revenue while Hotels contribute 7% and Paperboards 13%. 
        The company has successfully reduced tobacco dependency to 42% of revenue from 65% a decade ago. 
        ITC offers attractive dividend yield of 3.8% and trades at P/E of 27.2. 
        Strong brand portfolio includes Aashirvaad, Sunfeast, Classmate, and Bingo. 
        The company is investing heavily in organic foods and wellness products.''',
        'sector': 'FMCG',
        'category': 'Large Cap',
        'source_url': 'https://www.itcportal.com',
        'published_date': datetime.now() - timedelta(days=6)
    },
    
    # Sector Analysis - Banking
    {
        'document_type': 'sector_analysis',
        'symbol': None,
        'title': 'Indian Banking Sector Analysis Q4 FY24',
        'content': '''The Indian banking sector is experiencing robust growth with credit growth at 16% YoY and deposit growth at 13% YoY. 
        Asset quality has improved significantly with system-level Gross NPA declining to 3.2% from 7.5% two years ago. 
        Private sector banks are gaining market share with HDFC Bank, ICICI Bank, and Axis Bank leading the growth. 
        RBI's focus on digital banking and UPI adoption has transformed the payment landscape with 12 billion UPI transactions monthly. 
        Net Interest Margins (NIM) for private banks average 4.2% while PSU banks maintain 2.8%. 
        Rising interest rates have improved profitability but may impact loan growth in coming quarters. 
        Banking sector valuations at 2.5x P/B appear reasonable given strong earnings growth and improved asset quality. 
        Key risks include global economic slowdown and potential credit quality deterioration in unsecured lending.''',
        'sector': 'Banking',
        'category': 'Sector Analysis',
        'source_url': 'https://www.rbi.org.in',
        'published_date': datetime.now() - timedelta(days=7)
    },
    
    # Sector Analysis - IT Services
    {
        'document_type': 'sector_analysis',
        'symbol': None,
        'title': 'Indian IT Sector Outlook 2024 - Navigating Global Challenges',
        'content': '''Indian IT sector faces mixed outlook for FY24 with expected revenue growth of 5-7% compared to 15%+ in previous years. 
        Global economic uncertainties, particularly in US and Europe, are leading to delayed deal closures and project postponements. 
        However, long-term structural trends remain strong with increased cloud adoption, AI/ML implementation, and digital transformation. 
        Top IT companies (TCS, Infosys, HCL Tech, Wipro, Tech Mahindra) collectively employ 1.6 million professionals. 
        BFSI vertical, contributing 35% of sector revenue, shows resilience while Retail and Telecom face headwinds. 
        Generative AI presents both opportunity and threat - IT companies investing heavily in AI capabilities. 
        Margins under pressure from wage inflation (8-10% annually) and increased travel costs post-pandemic. 
        Sector trades at 25x forward P/E, premium to global peers justified by better growth prospects and balance sheet strength.''',
        'sector': 'IT Services',
        'category': 'Sector Analysis',
        'source_url': 'https://nasscom.org',
        'published_date': datetime.now() - timedelta(days=10)
    },
    
    # Market Overview
    {
        'document_type': 'market_overview',
        'symbol': None,
        'title': 'Nifty 50 Market Analysis - January 2024',
        'content': '''Nifty 50 index trades at 21,500 levels with YTD returns of 2.3% after a strong 2023 which delivered 20% gains. 
        Market capitalization of NSE-listed companies stands at ₹325 lakh crore (USD 3.9 trillion). 
        FII flows turned positive with net inflows of $2.8 billion in January after selling pressure in Q4 2023. 
        DII flows remain consistently strong at $3.5 billion monthly, providing market stability. 
        Nifty 50 trades at P/E of 21.8x, slightly above 10-year average of 20.5x but justified by strong earnings growth of 16% expected in FY24. 
        Sectoral leadership has shifted from IT and Pharma to Banking, Auto, and Capital Goods. 
        Mid-cap and Small-cap indices have outperformed large-caps by 8% and 12% respectively in last 12 months. 
        Key risks include global interest rates, crude oil prices (currently $82/barrel), and geopolitical tensions. 
        Rupee stability at 83/USD provides comfort to equity markets.''',
        'sector': 'Market',
        'category': 'Market Overview',
        'source_url': 'https://www.nseindia.com',
        'published_date': datetime.now() - timedelta(hours=6)
    },
    
    # Investment Strategy
    {
        'document_type': 'investment_strategy',
        'symbol': None,
        'title': 'Strategic Portfolio Allocation for Indian Investors - 2024',
        'content': '''For Indian investors with moderate risk appetite, recommended allocation is: 60% Equity, 25% Debt, 10% Gold, 5% Alternatives. 
        Within equity allocation, suggest 40% Large Cap (Nifty 50 stocks), 35% Mid Cap, 20% Small Cap, and 5% International equity. 
        Sectoral allocation should favor: Banking & Financials (25%), IT Services (15%), Consumer Goods (15%), Auto & Ancillaries (12%), 
        Capital Goods & Infra (10%), Healthcare (8%), Energy (8%), Others (7%). 
        For debt allocation, prefer high-quality corporate bonds, government securities, and short-duration funds to protect from interest rate volatility. 
        Gold serves as hedge against inflation and currency depreciation - prefer Sovereign Gold Bonds for 2.5% additional return. 
        Rebalance portfolio quarterly to maintain target allocation. 
        Use SIP approach for equity investments to benefit from rupee cost averaging. 
        Tax optimization important: Utilize ₹1.25 lakh LTCG exemption and ₹1 lakh interest deduction under 80TTB for senior citizens.''',
        'sector': 'Market',
        'category': 'Investment Strategy',
        'source_url': 'https://www.sebi.gov.in',
        'published_date': datetime.now() - timedelta(days=12)
    },
]

def populate_vector_database():
    """Populate vector database with sample stock market data"""
    
    print("🚀 Starting Vector Database Population...")
    print(f"📊 Total documents to process: {len(SAMPLE_DOCUMENTS)}\n")
    
    with app.app_context():
        # Initialize vector service
        vector_service = VectorService()
        
        # Check if documents already exist
        existing_count = VectorDocument.query.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing documents in database")
            response = input("Do you want to clear existing documents? (yes/no): ")
            if response.lower() == 'yes':
                VectorDocument.query.delete()
                db.session.commit()
                print("✅ Cleared existing documents\n")
        
        success_count = 0
        error_count = 0
        
        # Process each document
        for idx, doc_data in enumerate(SAMPLE_DOCUMENTS, 1):
            try:
                print(f"[{idx}/{len(SAMPLE_DOCUMENTS)}] Processing: {doc_data['title'][:60]}...")
                
                # Generate embedding for the content
                print(f"  └─ Generating embedding (1536 dimensions)...")
                embedding = vector_service.generate_embedding(doc_data['content'])
                
                if not embedding:
                    print(f"  └─ ❌ Failed to generate embedding")
                    error_count += 1
                    continue
                
                # Create vector document
                vector_doc = VectorDocument(
                    document_type=doc_data['document_type'],
                    symbol=doc_data['symbol'],
                    title=doc_data['title'],
                    content=doc_data['content'],
                    embedding=json.dumps(embedding),  # Store as JSON string
                    sector=doc_data['sector'],
                    category=doc_data['category'],
                    source_url=doc_data['source_url'],
                    published_date=doc_data['published_date']
                )
                
                db.session.add(vector_doc)
                db.session.commit()
                
                print(f"  └─ ✅ Successfully stored with embedding")
                success_count += 1
                
            except Exception as e:
                print(f"  └─ ❌ Error: {str(e)}")
                error_count += 1
                db.session.rollback()
                continue
        
        # Summary
        print("\n" + "="*70)
        print("📊 POPULATION SUMMARY")
        print("="*70)
        print(f"✅ Successfully processed: {success_count} documents")
        print(f"❌ Failed: {error_count} documents")
        print(f"📈 Total in database: {VectorDocument.query.count()} documents")
        print("\n🎯 Vector database is now ready for RAG-powered research!")
        print("="*70)
        
        # Display sample statistics
        print("\n📊 Database Statistics:")
        print(f"  • Stock Data: {VectorDocument.query.filter_by(document_type='stock_data').count()}")
        print(f"  • News Articles: {VectorDocument.query.filter_by(document_type='news').count()}")
        print(f"  • Earnings Reports: {VectorDocument.query.filter_by(document_type='earnings').count()}")
        print(f"  • Sector Analysis: {VectorDocument.query.filter_by(document_type='sector_analysis').count()}")
        print(f"  • Market Overview: {VectorDocument.query.filter_by(document_type='market_overview').count()}")
        print(f"  • Investment Strategy: {VectorDocument.query.filter_by(document_type='investment_strategy').count()}")
        
        print("\n🔍 Top Symbols in Database:")
        symbols = db.session.query(VectorDocument.symbol).filter(
            VectorDocument.symbol.isnot(None)
        ).distinct().all()
        for symbol in symbols:
            count = VectorDocument.query.filter_by(symbol=symbol[0]).count()
            print(f"  • {symbol[0]}: {count} documents")

if __name__ == '__main__':
    populate_vector_database()
