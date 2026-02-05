"""
CVO Matrix Visualization Generator
===================================
Generate side-by-side matrix visualizations:
1. Revenue × Bandwidth Matrix
2. Revenue × Tenure (Lama Berlangganan) Matrix

PLN Icon+ - Dashboard Visualization
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
    """Load data from Excel"""
    print("[DATA] Loading data...")
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
    
    print(f"[OK] Loaded {len(df)} customers")
    return df

def create_dual_matrix(df, output_path='cvo_dual_matrix.png'):
    """Create side-by-side matrices"""
    
    # Sample data for visualization (top 100 by revenue)
    df_sample = df.nlargest(100, 'revenue')
    
    # Calculate thresholds
    revenue_median = df_sample['revenue'].median()
    bandwidth_median = df_sample['bandwidth'].median() if df_sample['bandwidth'].median() > 0 else 100
    tenure_median = df_sample['tenure'].median() if df_sample['tenure'].median() > 0 else 3
    
    # Create figure with 2 subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle('CVO DUAL MATRIX ANALYSIS\nPLN Icon+ Customer Value Optimizer', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # ==================== MATRIX 1: REVENUE × BANDWIDTH ====================
    ax1.set_title('MATRIX 1: REVENUE × BANDWIDTH\nPendapatan vs Penggunaan Bandwidth', 
                  fontsize=14, fontweight='bold', pad=20)
    
    # Plot all points
    scatter1 = ax1.scatter(df_sample['bandwidth'], df_sample['revenue']/1000000, 
                          c='lightgray', s=150, alpha=0.6, edgecolors='black', linewidth=1)
    
    # Add quadrant lines
    ax1.axhline(y=revenue_median/1000000, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    ax1.axvline(x=bandwidth_median, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    
    # Color code quadrants
    # Q1: High Revenue, High Bandwidth (STAR CLIENTS - Green)
    star_clients = df_sample[(df_sample['revenue'] >= revenue_median) & 
                             (df_sample['bandwidth'] >= bandwidth_median)]
    ax1.scatter(star_clients['bandwidth'], star_clients['revenue']/1000000, 
               c='#2E7D32', s=200, alpha=0.8, edgecolors='darkgreen', linewidth=2, 
               label=f'STAR CLIENTS ({len(star_clients)})', zorder=5)
    
    # Q2: High Revenue, Low Bandwidth (RISK AREA - Red/Orange)
    risk_area = df_sample[(df_sample['revenue'] >= revenue_median) & 
                          (df_sample['bandwidth'] < bandwidth_median)]
    ax1.scatter(risk_area['bandwidth'], risk_area['revenue']/1000000, 
               c='#FF6F00', s=200, alpha=0.8, edgecolors='darkorange', linewidth=2,
               label=f'RISK AREA ({len(risk_area)})', zorder=5)
    
    # Q3: Low Revenue, High Bandwidth (SNIPER ZONE - Blue/Red)
    sniper_zone = df_sample[(df_sample['revenue'] < revenue_median) & 
                            (df_sample['bandwidth'] >= bandwidth_median)]
    ax1.scatter(sniper_zone['bandwidth'], sniper_zone['revenue']/1000000, 
               c='#C62828', s=250, alpha=0.9, edgecolors='darkred', linewidth=3,
               marker='X', label=f'SNIPER ZONE ({len(sniper_zone)})', zorder=6)
    
    # Q4: Low Revenue, Low Bandwidth (INVEST/INCUBATOR - Gray)
    incubator = df_sample[(df_sample['revenue'] < revenue_median) & 
                          (df_sample['bandwidth'] < bandwidth_median)]
    ax1.scatter(incubator['bandwidth'], incubator['revenue']/1000000, 
               c='#757575', s=150, alpha=0.5, edgecolors='gray', linewidth=1,
               label=f'INVEST/INCUBATOR ({len(incubator)})', zorder=4)
    
    # Add annotations
    ax1.text(0.95, 0.95, 'STAR CLIENTS\n(High Revenue, High Bandwidth)\nPertahankan!', 
             transform=ax1.transAxes, fontsize=11, fontweight='bold',
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8, edgecolor='green', linewidth=2))
    
    ax1.text(0.05, 0.95, 'RISK AREA\n(High Revenue, Low Bandwidth)\nRawan Komplain', 
             transform=ax1.transAxes, fontsize=11, fontweight='bold',
             verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8, edgecolor='orange', linewidth=2))
    
    ax1.text(0.95, 0.05, '🎯 SNIPER ZONE (TARGET)\n10 Klien Undervalued\nHigh Usage, Low Price\n\nACTION: TAWARKAN UPGRADE!', 
             transform=ax1.transAxes, fontsize=12, fontweight='bold', color='darkred',
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEBEE', alpha=0.95, 
                      edgecolor='red', linewidth=3))
    
    ax1.set_xlabel('Penggunaan Bandwidth (Mbps) - Semakin Kanan Semakin Tinggi', fontsize=11)
    ax1.set_ylabel('Revenue (Juta Rupiah) - Semakin Atas Semakin Mahal', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.9)
    
    # Format y-axis to show "Rp X Jt"
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x:.0f} Jt'))
    
    # ==================== MATRIX 2: REVENUE × TENURE ====================
    ax2.set_title('MATRIX 2: REVENUE × LAMA BERLANGGANAN\nPendapatan vs Masa Langganan', 
                  fontsize=14, fontweight='bold', pad=20)
    
    # Plot all points
    scatter2 = ax2.scatter(df_sample['tenure'], df_sample['revenue']/1000000, 
                          c='lightgray', s=150, alpha=0.6, edgecolors='black', linewidth=1)
    
    # Add quadrant lines
    ax2.axhline(y=revenue_median/1000000, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    ax2.axvline(x=tenure_median, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    
    # Color code quadrants dengan nama Indonesia
    # Q1: High Revenue, Long Tenure (SULTAN LOYAL - Green)
    sultan_loyal = df_sample[(df_sample['revenue'] >= revenue_median) & 
                             (df_sample['tenure'] >= tenure_median)]
    ax2.scatter(sultan_loyal['tenure'], sultan_loyal['revenue']/1000000, 
               c='#2E7D32', s=200, alpha=0.8, edgecolors='darkgreen', linewidth=2, 
               label=f'SULTAN LOYAL ({len(sultan_loyal)})', zorder=5)
    
    # Q2: High Revenue, Short Tenure (ORANG KAYA BARU - Blue)
    orang_kaya_baru = df_sample[(df_sample['revenue'] >= revenue_median) & 
                                (df_sample['tenure'] < tenure_median)]
    ax2.scatter(orang_kaya_baru['tenure'], orang_kaya_baru['revenue']/1000000, 
               c='#1565C0', s=200, alpha=0.8, edgecolors='darkblue', linewidth=2,
               label=f'ORANG KAYA BARU ({len(orang_kaya_baru)})', zorder=5)
    
    # Q3: Low Revenue, Long Tenure (SAHABAT HEMAT - Orange)
    sahabat_hemat = df_sample[(df_sample['revenue'] < revenue_median) & 
                              (df_sample['tenure'] >= tenure_median)]
    ax2.scatter(sahabat_hemat['tenure'], sahabat_hemat['revenue']/1000000, 
               c='#EF6C00', s=200, alpha=0.8, edgecolors='darkorange', linewidth=2,
               label=f'SAHABAT HEMAT ({len(sahabat_hemat)})', zorder=5)
    
    # Q4: Low Revenue, Short Tenure (PEMULA - Gray)
    pemula = df_sample[(df_sample['revenue'] < revenue_median) & 
                       (df_sample['tenure'] < tenure_median)]
    ax2.scatter(pemula['tenure'], pemula['revenue']/1000000, 
               c='#757575', s=150, alpha=0.5, edgecolors='gray', linewidth=1,
               label=f'PEMULA ({len(pemula)})', zorder=4)
    
    # Add annotations dengan nama Indonesia
    ax2.text(0.95, 0.95, '💚 SULTAN LOYAL\n(High Revenue + Long Tenure)\nStrategi: High-Value Cross-Sell\nTawarkan: PV Rooftop, Smart Office', 
             transform=ax2.transAxes, fontsize=10, fontweight='bold',
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.9, edgecolor='green', linewidth=2))
    
    ax2.text(0.05, 0.95, '💙 ORANG KAYA BARU\n(High Revenue + Short Tenure)\nStrategi: Onboarding & Satisfaction\nTawarkan: Bundling Sederhana', 
             transform=ax2.transAxes, fontsize=10, fontweight='bold',
             verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='#E3F2FD', alpha=0.9, edgecolor='blue', linewidth=2))
    
    ax2.text(0.95, 0.05, '🧡 SAHABAT HEMAT\n(Low Revenue + Long Tenure)\nStrategi: Nudging / Trial\nTawarkan: Trial 1 Minggu, Add-on Kecil', 
             transform=ax2.transAxes, fontsize=10, fontweight='bold',
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='#FFF3E0', alpha=0.9, edgecolor='orange', linewidth=2))
    
    ax2.text(0.05, 0.05, '🤍 PEMULA\n(Low Revenue + Short Tenure)\nStrategi: Observation\nAction: Program Incubator', 
             transform=ax2.transAxes, fontsize=10, fontweight='bold',
             verticalalignment='bottom', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.9, edgecolor='gray', linewidth=2))
    
    ax2.set_xlabel('Lama Berlangganan (Tahun) - Semakin Kanan Semakin Lama', fontsize=11)
    ax2.set_ylabel('Revenue (Juta Rupiah) - Semakin Atas Semakin Mahal', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=9, framealpha=0.9)
    
    # Format y-axis
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x:.0f} Jt'))
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"[OK] Dual matrix saved to: {output_path}")
    
    plt.close()
    return output_path

def create_sample_visualization():
    """Create sample data for demonstration if Excel not available"""
    np.random.seed(42)
    n = 100
    
    df = pd.DataFrame({
        'namaPelanggan': [f'Pelanggan {i+1}' for i in range(n)],
        'revenue': np.random.lognormal(15, 1.2, n),  # Log-normal for realistic revenue
        'bandwidth': np.random.exponential(100, n),  # Exponential for bandwidth
        'tenure': np.random.gamma(2, 3, n),  # Gamma for tenure (years)
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
    
    # Generate dual matrix
    output_file = create_dual_matrix(df, 'cvo_dual_matrix.png')
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE!")
    print("="*60)
    print(f"\nFile generated: {output_file}")
    print("\nMatrices created:")
    print("  1. Revenue × Bandwidth (with SNIPER ZONE)")
    print("  2. Revenue × Lama Berlangganan (4 Indonesian quadrants)")
