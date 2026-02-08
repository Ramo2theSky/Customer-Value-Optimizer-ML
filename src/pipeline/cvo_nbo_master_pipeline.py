"""
CVO NBO MASTER PIPELINE v1.0
==============================
Pipeline untuk membaca CVO_NBO_Master.xlsx (5,663 rows) dan convert ke JSON

Struktur Input (17 kolom):
- Nama Pelanggan
- Tier Saat Ini
- Rekomendasi Tier
- Prioritas Tier
- Bandwidth (Asli)
- Bandwidth (MBPS)
- Cluster Bandwidth
- Kategori Strategis
- Strategi
- Next Best Offer
- Pendapatan (Rp)
- Masa Berlangganan (Bulan)
- Skor Upsell (0-1)
- Prioritas
- Potensi Revenue (Rp)
- Produk Saat Ini
- CLV Prediksi (Rp)

Output: dashboard_data.json untuk API
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("="*80)
print("CVO NBO MASTER PIPELINE v1.0")
print("Memproses CVO_NBO_Master.xlsx (5,663 high-quality customers)")
print("="*80)

# Read Excel file
input_file = 'laporan_nbo/CVO_NBO_Master.xlsx'
output_file = 'cvo-dashboard/public/data/dashboard_data.json'

print(f"\n[1/4] Membaca {input_file}...")
df = pd.read_excel(input_file)

print(f"      Total rows: {len(df):,}")
print(f"      Columns: {len(df.columns)}")

# Clean column names (remove spaces, lowercase)
df.columns = df.columns.str.strip()

# Map Indonesian columns to English/API format
print("\n[2/4] Mapping columns...")

column_mapping = {
    'Nama Pelanggan': 'customer_name',
    'Tier Saat Ini': 'current_tier',
    'Rekomendasi Tier': 'recommended_tier',
    'Prioritas Tier': 'tier_priority',
    'Bandwidth (Asli)': 'bandwidth_original',
    'Bandwidth (MBPS)': 'bandwidth_mbps',
    'Cluster Bandwidth': 'bandwidth_segment',  # Low/Mid/High
    'Kategori Strategis': 'strategy_label',  # Star/Risk/Sniper/Incubator
    'Strategi': 'strategy_action',  # Retention/Cross-sell/Upsell/Automation
    'Next Best Offer': 'recommended_product',
    'Pendapatan (Rp)': 'revenue',
    'Masa Berlangganan (Bulan)': 'tenure_months',
    'Skor Upsell (0-1)': 'upsell_score',
    'Prioritas': 'priority',  # High/Medium/Low
    'Potensi Revenue (Rp)': 'potential_revenue',
    'Produk Saat Ini': 'current_product',
    'CLV Prediksi (Rp)': 'clv_predicted'
}

# Rename columns
df = df.rename(columns=column_mapping)

# Add calculated fields
print("\n[3/4] Calculating additional fields...")

# Generate unique ID
df['id'] = ['NBO_' + str(i+1).zfill(6) for i in range(len(df))]

# Calculate tenure in years
df['tenure'] = df['tenure_months'] / 12

# Calculate bandwidth score (1/2/3)
df['bandwidth_score'] = df['bandwidth_segment'].map({
    'Low': 1,
    'Mid': 2,
    'High': 3
}).fillna(1).astype(int)

# Determine industry from context (simplified)
def determine_industry(row):
    """Simple industry detection based on customer name"""
    name = str(row['customer_name']).upper()
    
    if any(bank in name for bank in ['BANK', 'BPR', 'KOPERASI', 'KSP']):
        return 'BANKING & FINANCIAL'
    elif any(mfg in name for mfg in ['INDUSTRI', 'MANUFACT', 'MOTOR', 'FACTORY']):
        return 'MANUFACTURE'
    elif any(edu in name for edu in ['UNIVERSITAS', 'SEKOLAH', 'INSTITUT', 'AKADEMI']):
        return 'EDUCATION'
    elif any(gov in name for gov in ['KABUPATEN', 'KOTA', 'PROVINSI', 'KECAMATAN', 'DESA']):
        return 'GOVERNMENT'
    elif any(retail in name for retail in ['RETAIL', 'DISTRIBUTION', 'MART', 'STORE']):
        return 'RETAIL DISTRIBUTION'
    elif any(health in name for health in ['HOSPITAL', 'KLINIK', 'MEDIC', 'HEALTH']):
        return 'HEALTHCARE'
    else:
        return 'OTHERS'

print("      Detecting industries...")
df['industry'] = df.apply(determine_industry, axis=1)

# Add strategy color
df['strategy_color'] = df['strategy_label'].map({
    'Star': '#4CAF50',
    'Risk': '#FF5722',
    'Sniper': '#2196F3',
    'Incubator': '#9E9E9E'
}).fillna('#9E9E9E')

# Generate reasoning based on strategy
def generate_reasoning(row):
    """Generate AI reasoning text"""
    strategy = row['strategy_label']
    tier_current = row['current_tier']
    tier_rec = row['recommended_tier']
    nbo = row['recommended_product']
    
    if strategy == 'Star':
        return f"High-value customer. Currently on {tier_current}. Recommended to maintain with {nbo}."
    elif strategy == 'Risk':
        return f"High revenue but {tier_current} tier. Upgrade to {tier_rec} with {nbo} to prevent churn."
    elif strategy == 'Sniper':
        return f"High usage detected. Upsell opportunity to {tier_rec} with {nbo}. Score: {row['upsell_score']:.0%}"
    else:  # Incubator
        return f"Entry-level customer. Automate engagement for future growth. Current: {tier_current}."

df['reasoning'] = df.apply(generate_reasoning, axis=1)

# Convert to API format
print("\n[4/4] Converting to API format...")

# Select and order columns for API
columns_for_api = [
    'id', 'customer_name', 'industry', 'revenue', 
    'current_tier', 'recommended_tier', 'tier_priority',
    'bandwidth_original', 'bandwidth_mbps', 'bandwidth_segment', 'bandwidth_score',
    'strategy_label', 'strategy_color', 'strategy_action',
    'recommended_product', 'reasoning',
    'tenure', 'tenure_months', 'upsell_score', 'priority',
    'potential_revenue', 'current_product', 'clv_predicted'
]

# Create output dataframe
df_output = df[columns_for_api].copy()

# Convert to records
data_records = df_output.to_dict('records')

# Save to JSON
print(f"\n[SAVE] Writing to {output_file}...")

# Ensure directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data_records, f, indent=2, ensure_ascii=False)

print(f"       Successfully saved {len(data_records):,} customers")

# Print summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Input file: {input_file}")
print(f"Output file: {output_file}")
print(f"Total customers processed: {len(df):,}")
print(f"\nStrategy breakdown:")
print(df['strategy_label'].value_counts().to_string())
print(f"\nTop 5 industries:")
print(df['industry'].value_counts().head().to_string())
print(f"\nTotal revenue: Rp {df['revenue'].sum():,.0f}")
print(f"Total potential revenue: Rp {df['potential_revenue'].sum():,.0f}")
print(f"\n[OK] Pipeline completed successfully!")
print("="*80)
