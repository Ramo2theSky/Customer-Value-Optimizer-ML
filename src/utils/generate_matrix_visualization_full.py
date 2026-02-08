"""
CVO Matrix Visualization Generator - FULL DATA
==============================================
Generate side-by-side matrix visualizations with ALL customers:
1. Revenue × Bandwidth Matrix
2. Revenue × Tenure (Lama Berlangganan) Matrix

PLN Icon+ - Dashboard Visualization (Full Dataset)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from datetime import datetime
import os

# Set style
plt.style.use('default')
sns.set_palette("husl")

def load_data():
    """Load FULL data from Excel"""
    print("[DATA] Loading FULL data...")
    df = pd.read_excel('Data Penuh Pelanggan Aktif.xlsx', engine='openpyxl')
    
    # Clean and prepare
    df['revenue'] = pd.to_numeric(df['hargaPelanggan'], errors='coerce').fillna(0)
    df['tenure'] = pd.to_numeric(df['Lama_Langganan'], errors='coerce').fillna(0)
    
    # Bandwidth
    df['bandwidth'] = 0
    if 'bandwidth' in df.columns:
        df['bandwidth'] = pd.to_numeric(df['bandwidth'], errors='coerce').fillna(0)
    elif 'Bandwidth Fix' in df.columns:
        def parse_bw(val):
            if pd.isna(val) or val == 'Tidak Ada':
                return 0
            import re
            match = re.search(r'(\d+)', str(val))
            return int(match.group(1)) if match else 0
        df['bandwidth'] = df['Bandwidth Fix'].apply(parse_bw)
    
    # Filter customers with meaningful data
    df = df[df['revenue'] > 0]
    
    print(f"[OK] Loaded {len(df):,} customers (FULL DATA)")
    return df

def create_dual_matrix_full(df, output_path='cvo_dual_matrix_full.png'):
    """Create side-by-side matrices with FULL data"""
    
    print(f"[MATRIX] Processing {len(df):,} customers for visualization...")
    
    # Use ALL data (not sampling)
    df_all = df.copy()
    
    # Calculate thresholds based on ALL data
    revenue_median = df_all['revenue'].median()
    bandwidth_median = df_all['bandwidth'].median() if df_all['bandwidth'].median() > 0 else 100
    tenure_median = df_all['tenure'].median() if df_all['tenure'].median() > 0 else 3
    
    print(f"   Revenue Median: Rp {revenue_median:,.0f}")
    print(f"   Bandwidth Median: {bandwidth_median:.1f} Mbps")
    print(f"   Tenure Median: {tenure_median:.1f} years")
    
    # Create figure with 2 subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
    fig.suptitle('CVO DUAL MATRIX ANALYSIS - FULL DATASET\nPLN Icon+ Customer Value Optimizer (All Active Customers)', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # ==================== MATRIX 1: REVENUE × BANDWIDTH ====================
    ax1.set_title(f'MATRIX 1: REVENUE × BANDWIDTH\n{len(df_all):,} Pelanggan - Pendapatan vs Penggunaan Bandwidth', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Classify all customers
    star_clients = df_all[(df_all['revenue'] >= revenue_median) & 
                          (df_all['bandwidth'] >= bandwidth_median)]
    risk_area = df_all[(df_all['revenue'] >= revenue_median) & 
                       (df_all['bandwidth'] < bandwidth_median)]
    sniper_zone = df_all[(df_all['revenue'] < revenue_median) & 
                         (df_all['bandwidth'] >= bandwidth_median)]
    incubator = df_all[(df_all['revenue'] < revenue_median) & 
                       (df_all['bandwidth'] < bandwidth_median)]
    
    print(f"   Star Clients: {len(star_clients):,}")
    print(f"   Risk Area: {len(risk_area):,}")
    print(f"   Sniper Zone: {len(sniper_zone):,}")
    print(f"   Incubator: {len(incubator):,}")
    
    # Plot with density-appropriate sizing
    # Incubator (gray) - largest group, smallest points
    ax1.scatter(incubator['bandwidth'], incubator['revenue']/1000000, 
               c='#BDBDBD', s=15, alpha=0.4, edgecolors='none',
               label=f'INVEST/INCUBATOR ({len(incubator):,})', zorder=1)
    
    # Risk Area (orange)
    ax1.scatter(risk_area['bandwidth'], risk_area['revenue']/1000000, 
               c='#FF9800', s=25, alpha=0.6, edgecolors='darkorange', linewidth=0.5,
               label=f'RISK AREA ({len(risk_area):,})', zorder=3)
    
    # Star Clients (green)
    ax1.scatter(star_clients['bandwidth'], star_clients['revenue']/1000000, 
               c='#4CAF50', s=30, alpha=0.7, edgecolors='darkgreen', linewidth=0.5, 
               label=f'STAR CLIENTS ({len(star_clients):,})', zorder=4)
    
    # Sniper Zone (red) - TARGET, highlighted
    ax1.scatter(sniper_zone['bandwidth'], sniper_zone['revenue']/1000000, 
               c='#F44336', s=35, alpha=0.8, edgecolors='darkred', linewidth=1,
               marker='o', label=f'SNIPER ZONE ({len(sniper_zone):,})', zorder=5)
    
    # Add quadrant lines
    ax1.axhline(y=revenue_median/1000000, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    ax1.axvline(x=bandwidth_median, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    
    # Add annotations
    ax1.text(0.97, 0.97, f'STAR CLIENTS\n(High Revenue, High BW)\n{len(star_clients):,} pelanggan\nPertahankan!', 
             transform=ax1.transAxes, fontsize=10, fontweight='bold',
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='#C8E6C9', alpha=0.9, edgecolor='green', linewidth=2))
    
    ax1.text(0.03, 0.97, f'RISK AREA\n(High Revenue, Low BW)\n{len(risk_area):,} pelanggan\nRawan Komplain', 
             transform=ax1.transAxes, fontsize=10, fontweight='bold',
             verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.9, edgecolor='orange', linewidth=2))
    
    ax1.text(0.97, 0.03, f'[TARGET] SNIPER ZONE\n{len(sniper_zone):,} Klien Undervalued\nHigh Usage, Low Price\n\nACTION: TAWARKAN UPGRADE!', 
             transform=ax1.transAxes, fontsize=11, fontweight='bold', color='darkred',
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFCDD2', alpha=0.95, 
                      edgecolor='red', linewidth=3))
    
    ax1.set_xlabel('Penggunaan Bandwidth (Mbps) - Semakin Kanan Semakin Tinggi', fontsize=11)
    ax1.set_ylabel('Revenue (Juta Rupiah) - Semakin Atas Semakin Mahal', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.95, markerscale=1.5)
    
    # Format y-axis
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x:.0f} Jt'))
    
    # ==================== MATRIX 2: REVENUE × TENURE ====================
    ax2.set_title(f'MATRIX 2: REVENUE × LAMA BERLANGGANAN\n{len(df_all):,} Pelanggan - Pendapatan vs Masa Langganan', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Classify by tenure
    sultan_loyal = df_all[(df_all['revenue'] >= revenue_median) & 
                          (df_all['tenure'] >= tenure_median)]
    orang_kaya_baru = df_all[(df_all['revenue'] >= revenue_median) & 
                             (df_all['tenure'] < tenure_median)]
    sahabat_hemat = df_all[(df_all['revenue'] < revenue_median) & 
                           (df_all['tenure'] >= tenure_median)]
    pemula = df_all[(df_all['revenue'] < revenue_median) & 
                    (df_all['tenure'] < tenure_median)]
    
    print(f"   Sultan Loyal: {len(sultan_loyal):,}")
    print(f"   Orang Kaya Baru: {len(orang_kaya_baru):,}")
    print(f"   Sahabat Hemat: {len(sahabat_hemat):,}")
    print(f"   Pemula: {len(pemula):,}")
    
    # Plot dengan density-appropriate sizing
    # Pemula (gray)
    ax2.scatter(pemula['tenure'], pemula['revenue']/1000000, 
               c='#9E9E9E', s=15, alpha=0.4, edgecolors='none',
               label=f'PEMULA ({len(pemula):,})', zorder=1)
    
    # Sahabat Hemat (orange)
    ax2.scatter(sahabat_hemat['tenure'], sahabat_hemat['revenue']/1000000, 
               c='#FF9800', s=25, alpha=0.6, edgecolors='darkorange', linewidth=0.5,
               label=f'SAHABAT HEMAT ({len(sahabat_hemat):,})', zorder=3)
    
    # Orang Kaya Baru (blue)
    ax2.scatter(orang_kaya_baru['tenure'], orang_kaya_baru['revenue']/1000000, 
               c='#2196F3', s=30, alpha=0.7, edgecolors='darkblue', linewidth=0.5,
               label=f'ORANG KAYA BARU ({len(orang_kaya_baru):,})', zorder=4)
    
    # Sultan Loyal (green)
    ax2.scatter(sultan_loyal['tenure'], sultan_loyal['revenue']/1000000, 
               c='#4CAF50', s=35, alpha=0.8, edgecolors='darkgreen', linewidth=1,
               label=f'SULTAN LOYAL ({len(sultan_loyal):,})', zorder=5)
    
    # Add quadrant lines
    ax2.axhline(y=revenue_median/1000000, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    ax2.axvline(x=tenure_median, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    
    # Add annotations dengan count
    ax2.text(0.97, 0.97, f'SULTAN LOYAL\n(High Revenue + Long Tenure)\n{len(sultan_loyal):,} pelanggan\nStrategi: High-Value Cross-Sell\nTawarkan: PV Rooftop, Smart Office', 
             transform=ax2.transAxes, fontsize=9, fontweight='bold',
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='#C8E6C9', alpha=0.9, edgecolor='green', linewidth=2))
    
    ax2.text(0.03, 0.97, f'ORANG KAYA BARU\n(High Revenue + Short Tenure)\n{len(orang_kaya_baru):,} pelanggan\nStrategi: Onboarding\nTawarkan: Bundling Sederhana', 
             transform=ax2.transAxes, fontsize=9, fontweight='bold',
             verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='#BBDEFB', alpha=0.9, edgecolor='blue', linewidth=2))
    
    ax2.text(0.97, 0.03, f'SAHABAT HEMAT\n(Low Revenue + Long Tenure)\n{len(sahabat_hemat):,} pelanggan\nStrategi: Nudging / Trial\nTawarkan: Trial 1 Minggu', 
             transform=ax2.transAxes, fontsize=9, fontweight='bold',
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.9, edgecolor='orange', linewidth=2))
    
    ax2.text(0.03, 0.03, f'PEMULA\n(Low Revenue + Short Tenure)\n{len(pemula):,} pelanggan\nStrategi: Observation\nAction: Program Incubator', 
             transform=ax2.transAxes, fontsize=9, fontweight='bold',
             verticalalignment='bottom', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.9, edgecolor='gray', linewidth=2))
    
    ax2.set_xlabel('Lama Berlangganan (Tahun) - Semakin Kanan Semakin Lama', fontsize=11)
    ax2.set_ylabel('Revenue (Juta Rupiah) - Semakin Atas Semakin Mahal', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle=':')
    ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=9, framealpha=0.95, markerscale=1.5)
    
    # Format y-axis
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x:.0f} Jt'))
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n[OK] Full dual matrix saved to: {output_path}")
    
    plt.close()
    return output_path

def create_sample_visualization():
    """Create sample data for demonstration if Excel not available"""
    np.random.seed(42)
    n = 1000  # Sample with 1000 for demo
    
    df = pd.DataFrame({
        'namaPelanggan': [f'Pelanggan {i+1}' for i in range(n)],
        'revenue': np.random.lognormal(15, 1.2, n),
        'bandwidth': np.random.exponential(100, n),
        'tenure': np.random.gamma(2, 3, n),
    })
    
    # Clean up
    df['bandwidth'] = df['bandwidth'].clip(0, 500)
    df['tenure'] = df['tenure'].clip(0, 20)
    
    return df

if __name__ == "__main__":
    try:
        # Try to load real data
        df = load_data()
    except Exception as e:
        print(f"[WARN] Could not load Excel: {e}")
        print("[INFO] Using sample data for demonstration")
        df = create_sample_visualization()
    
    # Generate dual matrix with FULL data
    output_file = create_dual_matrix_full(df, 'cvo_dual_matrix_full.png')
    
    print("\n" + "="*70)
    print("VISUALIZATION COMPLETE - FULL DATASET!")
    print("="*70)
    print(f"\nFile generated: {output_file}")
    print(f"Total customers visualized: {len(df):,}")
    print("\nMatrices created:")
    print("  1. Revenue × Bandwidth (with SNIPER ZONE - ALL customers)")
    print("  2. Revenue × Lama Berlangganan (4 Indonesian quadrants - ALL customers)")
    print("\nThis visualization includes EVERY active customer in the dataset!")
