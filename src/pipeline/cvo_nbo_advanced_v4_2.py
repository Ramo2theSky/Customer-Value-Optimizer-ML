#!/usr/bin/env python3
"""
CVO NBO Advanced Engine v4.2 - Production Script
================================================
Multi-dimensional Product Recommendation System
with Data-Driven Corrections

Features:
- 8-Factor Scoring (ARPU-aware, realistic thresholds)
- Smart Bandwidth Parser (handles "5 IP", "Tidak Ada")
- Tenure Cleaning (handles "Berkontrak 2026", "Data Tidak Valid")
- Co-occurrence Analysis
- 3 NBOs per company with detailed reasoning

Author: ML Team PLN Icon+
Date: February 2026
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# ARPU Thresholds (Realistic for PLN Icon+ based on data analysis)
ARPU_THRESHOLDS = {
    'Entry': (0, 1_000_000),
    'Mid': (1_000_000, 3_500_000),
    'High': (3_500_000, 15_000_000),
    'Enterprise': (15_000_000, float('inf'))
}

# Tier Levels Mapping
TIER_LEVELS = {
    'DI-TS': 1,
    'DI-SDS-TS': 2,
    'DI-SDS-SDS': 3,
    'ALL NOMENKLATUR': 4
}

# Product Complexity Inference
COMPLEXITY_KEYWORDS = {
    'Simple': ['basic', 'starter', 'light', 'essential', 'entry', 'bronze'],
    'Medium': ['standard', 'professional', 'plus', 'advanced', 'silver', 'medium'],
    'Complex': ['enterprise', 'premium', 'ultimate', 'managed', 'gold', 'platinum', 'deluxe']
}

# Colors for strategies
STRATEGY_COLORS = {
    'Star': '#10B981',      # Green
    'Risk': '#F97316',      # Orange
    'Sniper': '#3B82F6',    # Blue
    'Incubator': '#6B7280'  # Gray
}

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_companies_data(filepath):
    """Load and initial cleaning of companies data"""
    print(f"[INFO] Loading companies data from {filepath}...")
    df = pd.read_excel(filepath)
    print(f"   Loaded {len(df):,} rows")
    return df

def load_validation_list(filepath):
    """Load list of 5,646 valid companies"""
    print(f"[INFO] Loading validation list from {filepath}...")
    df = pd.read_excel(filepath)
    # Extract company names
    company_names = df.iloc[:, 0].dropna().unique()
    print(f"   Found {len(company_names):,} valid companies")
    return set(company_names)

def load_product_catalog(filepath):
    """Load and process 247 products from catalog"""
    print(f"[INFO] Loading product catalog from {filepath}...")
    df = pd.read_excel(filepath)
    print(f"   Loaded {len(df):,} products")
    return df

# ============================================================================
# DATA CLEANING FUNCTIONS
# ============================================================================

def categorize_arpu_realistic(revenue):
    """
    Categorize ARPU based on realistic PLN Icon+ thresholds
    Median: Rp 975,000 | Q3: Rp 3.5jt | Top 5%: Rp 14jt
    """
    if pd.isna(revenue) or revenue == 0:
        return "Bundled/Free", 0
    elif revenue < 1_000_000:
        return "Entry", 1
    elif revenue < 3_500_000:
        return "Mid", 2
    elif revenue < 15_000_000:
        return "High", 3
    else:
        return "Enterprise", 4

def parse_bandwidth_smart(bandwidth_str):
    """
    Smart bandwidth parser handling:
    - "5 IP", "2 IP" → IP-Only (not bandwidth!)
    - "10 MBPS", "100 MBPS" → numeric
    - "Tidak Ada" → 0
    - "E1" → 2 MBPS
    """
    if pd.isna(bandwidth_str) or bandwidth_str == "Tidak Ada":
        return 0, "Non-Connectivity"
    
    bw = str(bandwidth_str).upper().strip()
    
    # Pattern 1: IP Address (NOT bandwidth!)
    if "IP" in bw and "MBPS" not in bw and "GBPS" not in bw:
        return 0, "IP-Only"
    
    # Pattern 2: Standard MBPS/GBPS
    match = re.search(r'(\d+)\s*(MBPS|GBPS)', bw)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        if unit == "GBPS":
            return number * 1000, "Connectivity"
        return number, "Connectivity"
    
    # Pattern 3: E1
    if "E1" in bw:
        return 2, "Connectivity"
    
    # Pattern 4: Just numbers (assume MBPS)
    if bw.isdigit():
        return int(bw), "Connectivity"
    
    return 0, "Unknown"

def clean_tenure_smart(tenure_value):
    """
    Clean tenure handling various formats:
    - '1', '2', '26' → integer
    - "Berkontrak di Tahun 2026" → 0 (new/renewal risk)
    - "Data Tidak Valid" → median (3)
    """
    if pd.isna(tenure_value):
        return 3  # Median default
    
    tenure_str = str(tenure_value).strip()
    
    # Pure number
    if tenure_str.isdigit():
        years = int(tenure_str)
        return min(years, 26)  # Cap at 26
    
    # Number with quotes
    if re.match(r"^'\d+'$", tenure_str):
        years = int(tenure_str.strip("'"))
        return min(years, 26)
    
    # "Berkontrak di Tahun XXXX" → Churn risk/New
    if "Berkontrak" in tenure_str:
        return 0
    
    # Invalid data
    if "Tidak Valid" in tenure_str or "Invalid" in tenure_str:
        return 3  # Median
    
    # Extract any number
    match = re.search(r'\d+', tenure_str)
    if match:
        return min(int(match.group()), 26)
    
    return 3  # Default median

def infer_product_complexity(product_name):
    """Infer complexity from product name"""
    name_lower = str(product_name).lower()
    
    for complexity, keywords in COMPLEXITY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return complexity
    
    return "Medium"  # Default

def estimate_cost_tier(nomenklatur):
    """Estimate cost tier from nomenklatur"""
    nom = str(nomenklatur).upper()
    
    if any(x in nom for x in ['DI-TS']):
        return 1  # Entry
    elif any(x in nom for x in ['DI-SDS-TS']):
        return 2  # Mid
    elif any(x in nom for x in ['DI-SDS-SDS']):
        return 3  # High
    else:
        return 2  # Default Mid

# ============================================================================
# CO-OCCURRENCE ANALYSIS
# ============================================================================

def build_cooccurrence_matrix(df):
    """Build co-occurrence matrix: which products appear together"""
    print("\n[SEARCH] Building co-occurrence matrix...")
    
    # Group by company, aggregate products
    company_products = df.groupby('Row Labels')['ProdukBaru'].apply(list).reset_index()
    
    # Build matrix
    co_occurrence = defaultdict(lambda: defaultdict(int))
    product_counts = Counter()
    
    for _, row in company_products.iterrows():
        products = row['ProdukBaru']
        product_counts.update(products)
        
        # Count pairs
        for i, p1 in enumerate(products):
            for p2 in products[i+1:]:
                co_occurrence[p1][p2] += 1
                co_occurrence[p2][p1] += 1
    
    print(f"   Analyzed {len(product_counts)} unique products")
    return co_occurrence, product_counts

def get_cooccurrence_boost(company_products, candidate_product, co_occurrence, total_companies):
    """Calculate co-occurrence score boost"""
    boost = 0
    
    for current_product in company_products:
        if current_product in co_occurrence and candidate_product in co_occurrence[current_product]:
            count = co_occurrence[current_product][candidate_product]
            # Normalize by total
            confidence = count / total_companies
            boost += confidence * 20  # Max 20 points
    
    return min(boost, 20)

# ============================================================================
# NBO SCORING ENGINE
# ============================================================================

def calculate_nbo_score_v4_2(company, product, co_occurrence, total_companies):
    """
    Calculate NBO score using 8 factors with data-driven corrections
    """
    score = 0
    
    # Factor 1: Tier Compatibility (15%)
    company_tier_level = TIER_LEVELS.get(company['tier'], 2)
    product_tier_level = product['tier_level']
    tier_diff = product_tier_level - company_tier_level
    
    if tier_diff == 0:
        score += 15
    elif tier_diff == 1:
        score += 12
    elif tier_diff == 2:
        score += 8
    else:
        score += 3
    
    # Factor 2: Category Match (15%)
    if product['category'] == company['category']:
        score += 15
    elif product['category'] in ['Technology Services', 'Digital Infrastructure'] and \
         company['category'] in ['Technology Services', 'Digital Infrastructure']:
        score += 10  # Adjacent
    else:
        score += 5
    
    # Factor 3: Bandwidth Suitability (15%)
    company_bw, bw_type = company['bandwidth_clean']
    product_min_bw = product['min_bandwidth']
    
    if bw_type == "IP-Only":
        # IP-only customers → offer connectivity bundles
        if product['category'] == 'Connectivity':
            score += 15  # Perfect - they need this!
        elif product_min_bw == 0:
            score += 15  # Non-connectivity OK
        else:
            score += 5
    elif product_min_bw == 0:
        # Non-connectivity product
        score += 15
    else:
        # Normal bandwidth comparison
        if company_bw >= product_min_bw * 1.5:
            score += 15
        elif company_bw >= product_min_bw:
            score += 10
        elif company_bw >= product_min_bw * 0.5:
            score += 5
        else:
            score += 2
    
    # Factor 4: Industry Fit (15%)
    industry = company['industry']
    if product['target_industries'] and industry in product['target_industries']:
        score += 15
    elif industry in ['BANKING & FINANCIAL', 'GOVERNMENT'] and 'Security' in product['name']:
        score += 12  # Security products for regulated industries
    elif industry in ['MANUFACTURE'] and 'IoT' in product['name']:
        score += 12
    else:
        score += 5
    
    # Factor 5: Current Product Gap/Co-occurrence (10%)
    current_products = company.get('current_products', [])
    if current_products:
        boost = get_cooccurrence_boost(current_products, product['name'], co_occurrence, total_companies)
        score += min(boost, 10)
    else:
        score += 5
    
    # Factor 6: Regional Availability (5%)
    score += 5  # Assume available for now (can be refined)
    
    # Factor 7: ARPU Affordability (15%) - DATA-DRIVEN
    company_arpu_cat, company_arpu_level = categorize_arpu_realistic(company['revenue'])
    product_cost_level = product['cost_tier']
    
    if company['revenue'] == 0:
        # Bundled/Free - offer add-ons
        score += 8 if product_cost_level == 1 else 3
    else:
        tier_diff = product_cost_level - company_arpu_level
        if tier_diff == 0:
            score += 15
        elif tier_diff == 1:
            score += 12  # One step up - realistic upsell
        elif tier_diff == 2:
            score += 7   # Stretch
        else:
            score += 2   # Too big gap
    
    # Factor 8: Tenure Strategy (10%)
    tenure = company['tenure_clean']
    complexity = product['complexity']
    
    if tenure == 0:  # Berkontarak/Churn risk
        score += 10 if complexity == 'Simple' else 3
        # Also boost retention products
        if 'Retention' in product.get('tags', []):
            score += 5
    elif tenure < 0.5:
        score += 10 if complexity == 'Simple' else 3
    elif tenure < 2:
        score += 10 if complexity in ['Simple', 'Medium'] else 6
    elif tenure <= 5:
        score += 10
    else:  # Loyal > 5 years
        score += 10 if complexity in ['Medium', 'Complex'] else 7
    
    return min(score, 100)

def assign_strategy(company):
    """Assign 4-quadrant strategy"""
    revenue = company['revenue']
    bandwidth = company['bandwidth_clean'][0]
    
    # Use median-based thresholds
    rev_threshold = 3_500_000  # Q3
    bw_threshold = 10  # 10 MBPS
    
    if revenue >= rev_threshold and bandwidth >= bw_threshold:
        return "Star", "RETAIN"
    elif revenue >= rev_threshold and bandwidth < bw_threshold:
        return "Risk", "CROSS-SELL"
    elif revenue < rev_threshold and bandwidth >= bw_threshold:
        return "Sniper", "UPSELL"
    else:
        return "Incubator", "AUTOMATE"

def assign_priority(company, nbo_score):
    """Assign priority based on multiple factors"""
    revenue = company['revenue']
    tenure = company['tenure_clean']
    
    # High priority conditions
    if nbo_score >= 80:
        return "High", "Perfect match - immediate action"
    elif revenue >= 15_000_000 or (revenue >= 3_500_000 and tenure == 0):
        # High revenue or churn risk
        return "High", "High-value or renewal risk"
    elif nbo_score >= 60:
        return "Medium", "Good opportunity"
    else:
        return "Low", "Monitor or automated campaign"

def generate_reasoning(company, product, score_factors):
    """Generate human-readable reasoning"""
    reasons = []
    
    # ARPU match
    if company['revenue'] > 0:
        arpu_cat, _ = categorize_arpu_realistic(company['revenue'])
        if arpu_cat == product.get('cost_category', 'Unknown'):
            reasons.append(f"Sesuai daya beli {arpu_cat}")
    
    # Bandwidth
    if company['bandwidth_clean'][1] == "IP-Only":
        reasons.append("Anda punya IP, segera bundling dengan Internet untuk SLA lebih baik")
    
    # Category
    if product['category'] == company['category']:
        reasons.append(f"Melengkapi layanan {company['category']}")
    
    # Industry
    if company['industry'] in ['BANKING & FINANCIAL', 'GOVERNMENT']:
        reasons.append(f"Compliance penting untuk sektor {company['industry']}")
    
    # Tenure/Churn risk
    if company['tenure_clean'] == 0:
        reasons.append("Prioritas renewal kontrak 2026")
    elif company['tenure_clean'] > 5:
        reasons.append("Customer loyal - layanan premium tersedia")
    
    # Co-occurrence
    if score_factors.get('has_complementary', False):
        reasons.append("Pelanggan serupa juga membeli produk ini")
    
    return " | ".join(reasons) if reasons else "Rekomendasi berdasarkan profil lengkap"

# ============================================================================
# MAIN PROCESSING PIPELINE
# ============================================================================

def process_data(df_companies, df_catalog, validation_set):
    """Main processing pipeline"""
    print("\n" + "="*80)
    print("PROCESSING PIPELINE")
    print("="*80)
    
    # Step 1: Filter only validation companies
    print("\n[1] Filtering validation companies...")
    df_filtered = df_companies[df_companies['Row Labels'].isin(validation_set)].copy()
    print(f"   Filtered: {len(df_filtered):,} rows")
    
    # Step 2: Clean data
    print("\n[2] Cleaning data...")
    
    # ARPU
    df_filtered['arpu_category'], df_filtered['arpu_level'] = zip(*
        df_filtered['hargaPelanggan'].apply(categorize_arpu_realistic)
    )
    print(f"   ARPU: {df_filtered['arpu_category'].value_counts().to_dict()}")
    
    # Bandwidth
    df_filtered['bandwidth_clean'] = df_filtered['Bandwidth Fix'].apply(parse_bandwidth_smart)
    df_filtered['bandwidth_mbps'] = df_filtered['bandwidth_clean'].apply(lambda x: x[0])
    df_filtered['bandwidth_type'] = df_filtered['bandwidth_clean'].apply(lambda x: x[1])
    print(f"   Bandwidth types: {df_filtered['bandwidth_type'].value_counts().to_dict()}")
    
    # Tenure
    df_filtered['tenure_clean'] = df_filtered['Lama_Langganan'].apply(clean_tenure_smart)
    tenure_2026 = (df_filtered['tenure_clean'] == 0).sum()
    print(f"   Tenure 2026 (Churn Risk): {tenure_2026} companies")
    
    # Step 3: Build co-occurrence matrix
    print("\n[3] Building co-occurrence matrix...")
    co_occurrence, product_counts = build_cooccurrence_matrix(df_filtered)
    total_companies = len(df_filtered['Row Labels'].unique())
    
    # Step 4: Process catalog
    print("\n[4] Processing product catalog...")
    products = []
    for _, row in df_catalog.iterrows():
        product = {
            'name': row.get('Produk', ''),
            'category': row.get('Kategori Produk', ''),
            'nomenklatur': row.get('Nomenklatur Baru', ''),
            'tier': row.get('Nomenklatur Baru', ''),
            'tier_level': estimate_cost_tier(row.get('Nomenklatur Baru', '')),
            'cost_tier': estimate_cost_tier(row.get('Nomenklatur Baru', '')),
            'min_bandwidth': 0,  # Will be set based on product type
            'complexity': infer_product_complexity(row.get('Produk', '')),
            'target_industries': [],  # Can be inferred
        }
        products.append(product)
    
    print(f"   Processed {len(products)} products")
    
    # Step 5: Aggregate per company
    print("\n[5] Aggregating per company...")
    company_groups = df_filtered.groupby('Row Labels').agg({
        'hargaPelanggan': 'sum',  # Total ARPU
        'bandwidth_mbps': 'max',
        'bandwidth_type': 'first',
        'Lama_Langganan': 'first',
        'tenure_clean': 'first',
        'segmenCustomer': 'first',
        'Kategori_Baru': 'first',
        'Kelompok Tier': 'first',
        'ProdukBaru': lambda x: list(x.unique()),  # All products
        'SBUOwner': 'first',
        'arpu_category': 'first',
        'arpu_level': 'first',
        'statusLayanan': 'first'
    }).reset_index()
    
    print(f"   Aggregated: {len(company_groups)} unique companies")
    
    # Step 6: Generate NBO for each company
    print("\n[6] Generating NBO recommendations...")
    recommendations = []
    
    for idx, company in company_groups.iterrows():
        if idx % 500 == 0:
            print(f"   Processing... {idx}/{len(company_groups)}")
        
        # Prepare company data
        company_data = {
            'nama': company['Row Labels'],
            'revenue': company['hargaPelanggan'],
            'bandwidth_clean': (company['bandwidth_mbps'], company['bandwidth_type']),
            'tenure_clean': company['tenure_clean'],
            'industry': company['segmenCustomer'],
            'category': company['Kategori_Baru'],
            'tier': company['Kelompok Tier'],
            'current_products': company['ProdukBaru'],
            'sbu': company['SBUOwner'],
            'arpu_category': company['arpu_category'],
            'arpu_level': company['arpu_level'],
            'status': company['statusLayanan']
        }
        
        # Calculate scores for all products
        product_scores = []
        for product in products:
            score = calculate_nbo_score_v4_2(company_data, product, co_occurrence, total_companies)
            product_scores.append((product, score))
        
        # Sort and get top 3
        product_scores.sort(key=lambda x: x[1], reverse=True)
        top3 = product_scores[:3]
        
        # Assign strategy and priority
        strategy, action = assign_strategy(company_data)
        priority, priority_reason = assign_priority(company_data, top3[0][1] if top3 else 0)
        
        # Generate reasoning
        reasoning = []
        for prod, score in top3:
            reasons = generate_reasoning(company_data, prod, {})
            reasoning.append(reasons)
        
        # Build recommendation record
        rec = {
            'ID': f"NBO_{idx+1:06d}",
            'Nama Pelanggan': company['Row Labels'],
            'Revenue': company['hargaPelanggan'],
            'ARPU_Category': company['arpu_category'],
            'Tenure_Tahun': company['tenure_clean'],
            'Tenure_Strategy': 'Renewal Risk' if company['tenure_clean'] == 0 else 
                              ('Growth' if company['tenure_clean'] < 2 else 'Loyalty'),
            'Bandwidth': company['bandwidth_mbps'],
            'Bandwidth_Type': company['bandwidth_type'],
            'Industry': company['segmenCustomer'],
            'Current_Tier': company['Kelompok Tier'],
            'Current_Products': ', '.join([str(p) for p in company['ProdukBaru'][:3] if pd.notna(p)]) + ('...' if len([p for p in company['ProdukBaru'] if pd.notna(p)]) > 3 else ''),
            'Product_Count': len([p for p in company['ProdukBaru'] if pd.notna(p)]),
            'Strategy': strategy,
            'Action': action,
            'Priority': priority,
            'SBU': company['SBUOwner'],
            'Status': company['statusLayanan'],
            # NBO 1
            'NBO_1_Product': top3[0][0]['name'] if len(top3) > 0 else '',
            'NBO_1_Score': top3[0][1] if len(top3) > 0 else 0,
            'NBO_1_Reasoning': reasoning[0] if len(reasoning) > 0 else '',
            # NBO 2
            'NBO_2_Product': top3[1][0]['name'] if len(top3) > 1 else '',
            'NBO_2_Score': top3[1][1] if len(top3) > 1 else 0,
            'NBO_2_Reasoning': reasoning[1] if len(reasoning) > 1 else '',
            # NBO 3
            'NBO_3_Product': top3[2][0]['name'] if len(top3) > 2 else '',
            'NBO_3_Score': top3[2][1] if len(top3) > 2 else 0,
            'NBO_3_Reasoning': reasoning[2] if len(reasoning) > 2 else '',
        }
        
        recommendations.append(rec)
    
    return recommendations

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_excel(recommendations, output_path):
    """Export to Excel format"""
    print(f"\n[INFO] Exporting to Excel: {output_path}")
    df = pd.DataFrame(recommendations)
    df.to_excel(output_path, index=False)
    print(f"   Saved {len(df)} rows")
    return df

def export_to_json(recommendations, output_path):
    """Export to JSON for API"""
    print(f"\n[SAVE] Exporting to JSON: {output_path}")
    
    # Convert to API-friendly format
    api_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '4.2',
            'total_companies': len(recommendations),
            'source_files': [
                'Data Penuh Pelanggan Aktif Clean.xlsx',
                'Mapping Seluruh Produk ICON+.xlsx',
                '20260204 List Pelanggan Aktif PLN Icon Plus.xlsx'
            ]
        },
        'data': recommendations
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved")

def generate_summary(recommendations):
    """Generate summary statistics"""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    df = pd.DataFrame(recommendations)
    
    print(f"\n[INFO] Total Companies: {len(df):,}")
    print(f"[MONEY] Total Revenue: Rp {df['Revenue'].sum():,.0f}")
    print(f"[STAT] Average Revenue: Rp {df['Revenue'].mean():,.0f}")
    
    print(f"\n[TARGET] Strategy Distribution:")
    print(df['Strategy'].value_counts())
    
    print(f"\n[PRIORITY] Priority Distribution:")
    print(df['Priority'].value_counts())
    
    print(f"\n[BIZ] ARPU Category Distribution:")
    print(df['ARPU_Category'].value_counts())
    
    print(f"\n[TIME] Tenure Strategy:")
    print(df['Tenure_Strategy'].value_counts())
    
    print(f"\n[NET] Bandwidth Type:")
    print(df['Bandwidth_Type'].value_counts())
    
    print(f"\n[MAP] Top 10 Industries:")
    print(df['Industry'].value_counts().head(10))

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main execution function"""
    print("="*80)
    print("CVO NBO ADVANCED ENGINE v4.2")
    print("Multi-dimensional Product Recommendation System")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    # File paths
    COMPANIES_FILE = 'Data Penuh Pelanggan Aktif Clean.xlsx'
    VALIDATION_FILE = '20260204 List Pelanggan Aktif PLN Icon Plus.xlsx'
    CATALOG_FILE = 'Mapping Seluruh Produk ICON+.xlsx'
    OUTPUT_EXCEL = 'CVO_NBO_Master_2026_Advanced.xlsx'
    OUTPUT_JSON = 'dashboard_data.json'
    
    try:
        # Load data
        df_companies = load_companies_data(COMPANIES_FILE)
        validation_set = load_validation_list(VALIDATION_FILE)
        df_catalog = load_product_catalog(CATALOG_FILE)
        
        # Process
        recommendations = process_data(df_companies, df_catalog, validation_set)
        
        # Export
        export_to_excel(recommendations, OUTPUT_EXCEL)
        export_to_json(recommendations, OUTPUT_JSON)
        
        # Summary
        generate_summary(recommendations)
        
        print("\n" + "="*80)
        print("[OK] COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Output Files:")
        print(f"  - {OUTPUT_EXCEL}")
        print(f"  - {OUTPUT_JSON}")
        print(f"Finished at: {datetime.now()}")
        
    except Exception as e:
        print(f"\n[ERROR] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
