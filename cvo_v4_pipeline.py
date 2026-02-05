"""
CVO v4.0 - Customer Value Optimizer with Revenue × Tenure Matrix
===============================================================
Sistem CVO dengan:
- Revenue × Tenure Matrix (4 kuadran strategis)
- Simplified bandwidth clustering (NO_BANDWIDTH, ATM_IOT)
- Cross-sell product recommendations
- Multi-filter support

PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("CVO v4.0 - Revenue × Tenure Matrix & Cross-sell Engine")
print("="*80)


class CVORevenueTenureAnalyzer:
    """
    Analisis CVO dengan fokus Revenue × Tenure Matrix
    """
    
    def __init__(self, data_path: str, output_dir: str = 'cvo_v4_results'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        self.df_processed = None
        os.makedirs(output_dir, exist_ok=True)
        
    def load_data(self):
        """Load data penuh"""
        print("\n[DATA] Memuat data...")
        self.df = pd.read_excel(self.data_path, engine='openpyxl')
        print(f"[OK] {len(self.df):,} pelanggan dimuat")
        print(f"   Kolom: {len(self.df.columns)}")
        return self.df
    
    def clean_and_prepare(self):
        """Bersihkan dan siapkan data"""
        print("\n[CLEAN] Membersihkan data...")
        
        # Hanya pelanggan aktif
        if 'statusLayanan' in self.df.columns:
            self.df = self.df[self.df['statusLayanan'] == 'AKTIF']
        
        # Konversi lama_langganan ke numeric (dari object/string)
        if 'Lama_Langganan' in self.df.columns:
            self.df['tenure_years'] = pd.to_numeric(self.df['Lama_Langganan'], errors='coerce')
        elif 'lama_langganan' in self.df.columns:
            self.df['tenure_years'] = pd.to_numeric(self.df['lama_langganan'], errors='coerce')
        else:
            # Hitung dari tanggal aktivasi
            if 'tanggalAktivasi' in self.df.columns:
                self.df['tanggalAktivasi'] = pd.to_datetime(self.df['tanggalAktivasi'], errors='coerce')
                current_year = datetime.now().year
                self.df['tenure_years'] = current_year - self.df['tanggalAktivasi'].dt.year
        
        # Pendapatan
        if 'hargaPelanggan' in self.df.columns:
            self.df['revenue'] = pd.to_numeric(self.df['hargaPelanggan'], errors='coerce')
        elif 'pendapatan' in self.df.columns:
            self.df['revenue'] = pd.to_numeric(self.df['pendapatan'], errors='coerce')
        
        # Bandwidth
        self.df['bandwidth_mbps'] = 0
        if 'bandwidth' in self.df.columns:
            self.df['bandwidth_mbps'] = pd.to_numeric(self.df['bandwidth'], errors='coerce').fillna(0)
        elif 'Bandwidth Fix' in self.df.columns:
            # Parse bandwidth fix
            def parse_bandwidth(val):
                if pd.isna(val) or val == 'Tidak Ada':
                    return 0
                try:
                    # Extract number from strings like "20 MBPS"
                    import re
                    match = re.search(r'(\d+)', str(val))
                    return int(match.group(1)) if match else 0
                except:
                    return 0
            self.df['bandwidth_mbps'] = self.df['Bandwidth Fix'].apply(parse_bandwidth)
        
        # Simplified bandwidth cluster
        def get_bandwidth_cluster(row):
            bw = row['bandwidth_mbps']
            if bw == 0:
                return 'NO_BANDWIDTH'
            elif bw < 1:  # KBPS or very low
                return 'ATM_IOT'
            else:
                return 'HAS_BANDWIDTH'  # Will be mapped to segmen
        
        self.df['bandwidth_cluster'] = self.df.apply(get_bandwidth_cluster, axis=1)
        
        # Fill missing values
        self.df['tenure_years'] = self.df['tenure_years'].fillna(0)
        self.df['revenue'] = self.df['revenue'].fillna(0)
        
        print(f"[OK] {len(self.df):,} pelanggan aktif")
        print(f"   Rata-rata tenure: {self.df['tenure_years'].mean():.1f} tahun")
        print(f"   Rata-rata revenue: Rp {self.df['revenue'].mean():,.0f}")
        print(f"\n   Distribusi Bandwidth:")
        print(self.df['bandwidth_cluster'].value_counts())
        
        return self.df
    
    def create_revenue_tenure_matrix(self) -> pd.DataFrame:
        """
        Buat matriks Revenue × Tenure dengan 4 kuadran:
        - SULTAN LOYAL (High Revenue + Long Tenure)
        - ORANG KAYA BARU (High Revenue + Short Tenure)
        - SAHABAT HEMAT (Low Revenue + Long Tenure)
        - PEMULA (Low Revenue + Short Tenure)
        """
        print("\n[MATRIX] Membuat Revenue × Tenure Matrix...")
        
        # Hitung median untuk pemisah
        revenue_median = self.df['revenue'].median()
        tenure_median = self.df['tenure_years'].median()
        
        print(f"   Median Revenue: Rp {revenue_median:,.0f}")
        print(f"   Median Tenure: {tenure_median:.1f} tahun")
        
        # Definisikan kuadran
        def get_quadrant(row):
            revenue = row['revenue']
            tenure = row['tenure_years']
            
            if revenue >= revenue_median and tenure >= tenure_median:
                return 'SULTAN LOYAL'
            elif revenue >= revenue_median and tenure < tenure_median:
                return 'ORANG KAYA BARU'
            elif revenue < revenue_median and tenure >= tenure_median:
                return 'SAHABAT HEMAT'
            else:
                return 'PEMULA'
        
        self.df['revenue_tenure_quadrant'] = self.df.apply(get_quadrant, axis=1)
        
        # Strategi per kuadran
        strategies = {
            'SULTAN LOYAL': {
                'strategy': 'High-Value Cross-Sell',
                'action': 'Tawarkan produk premium: PV Rooftop, Full Smart Office Solution, Green Energy',
                'priority': 'HIGH',
                'color': '#10B981'  # Green
            },
            'ORANG KAYA BARU': {
                'strategy': 'Onboarding & Satisfaction',
                'action': 'Pastikan layanan stabil. Bundling sederhana: Internet + 1 CCTV',
                'priority': 'MEDIUM',
                'color': '#3B82F6'  # Blue
            },
            'SAHABAT HEMAT': {
                'strategy': 'Nudging / Trial',
                'action': 'Trial kecepatan tinggi 1 minggu. Add-on kecil untuk naikkan tagihan pelan-pelan',
                'priority': 'MEDIUM',
                'color': '#F59E0B'  # Orange
            },
            'PEMULA': {
                'strategy': 'Observation & Incubator',
                'action': 'Pastikan layanan standar baik. Masukkan program Incubator',
                'priority': 'LOW',
                'color': '#6B7280'  # Gray
            }
        }
        
        # Add strategy columns
        self.df['strategy'] = self.df['revenue_tenure_quadrant'].map(lambda x: strategies[x]['strategy'])
        self.df['action'] = self.df['revenue_tenure_quadrant'].map(lambda x: strategies[x]['action'])
        self.df['priority'] = self.df['revenue_tenure_quadrant'].map(lambda x: strategies[x]['priority'])
        self.df['quadrant_color'] = self.df['revenue_tenure_quadrant'].map(lambda x: strategies[x]['color'])
        
        # Print summary
        print("\n   Distribusi Kuadran:")
        quadrant_summary = self.df.groupby('revenue_tenure_quadrant').agg({
            'idPelanggan': 'count',
            'revenue': 'sum'
        }).round(0)
        quadrant_summary.columns = ['Jumlah', 'Total Revenue']
        print(quadrant_summary)
        
        return self.df
    
    def generate_cross_sell_recommendations(self):
        """
        Generate rekomendasi cross-sell berdasarkan:
        - Kategori_Baru (DI, TS, SDS, GE)
        - Kelompok Tier
        - segmenCustomer
        """
        print("\n[CROSS-SELL] Generate rekomendasi produk...")
        
        # Mapping kategori ke produk rekomendasi
        cross_sell_map = {
            'Digital Infrastructure': {
                'target': 'Technology Services',
                'products': [
                    'Managed WiFi Enterprise',
                    'CCTV Cloud',
                    'Video Conference',
                    'LAN Management'
                ]
            },
            'Technology Services': {
                'target': 'Digital Infrastructure',
                'products': [
                    'Internet Dedicated',
                    'METRONET',
                    'IPVPN',
                    'Dark Fiber'
                ]
            },
            'Smart & Digital Solution': {
                'target': 'DI + TS',
                'products': [
                    'Smart Building',
                    'IoT Platform',
                    'Digital Signage',
                    'Access Control'
                ]
            },
            'Green Ecosystem': {
                'target': 'All Categories',
                'products': [
                    'PV Rooftop',
                    'Energy Monitoring',
                    'Smart Grid',
                    'Green Data Center'
                ]
            }
        }
        
        def get_cross_sell_recommendation(row):
            kategori = row.get('Kategori_Baru', 'Digital Infrastructure')
            segmen = row.get('segmenCustomer', 'RETAIL DISTRIBUTION')
            
            # Default recommendation
            base_rec = cross_sell_map.get(kategori, cross_sell_map['Digital Infrastructure'])
            
            # Customize based on segmen
            segmen_products = {
                'GOVERNMENT': ['e-Government', 'Command Center', 'Disaster Recovery'],
                'BANKING & FINANCIAL': ['SDWAN', 'Managed Security', 'Backup Connectivity'],
                'RETAIL DISTRIBUTION': ['POS System', 'Inventory Management', 'Digital Payment'],
                'HEALTHCARE': ['Telemedicine', 'Medical IoT', 'Hospital Information System'],
                'EDUCATION': ['E-Learning', 'Digital Library', 'Smart Campus'],
                'MANUFACTURING': ['Industry 4.0', 'Predictive Maintenance', 'Smart Factory']
            }
            
            # Add segmen-specific products
            specific_products = segmen_products.get(segmen, [])
            all_products = base_rec['products'] + specific_products
            
            return {
                'target_category': base_rec['target'],
                'recommended_products': ' | '.join(all_products[:3]),
                'upsell_potential': row['revenue'] * 0.3  # Assume 30% upsell
            }
        
        # Apply recommendations
        recommendations = self.df.apply(get_cross_sell_recommendation, axis=1)
        self.df['cross_sell_target'] = recommendations.apply(lambda x: x['target_category'])
        self.df['cross_sell_products'] = recommendations.apply(lambda x: x['recommended_products'])
        self.df['upsell_potential'] = recommendations.apply(lambda x: x['upsell_potential'])
        
        print("[OK] Rekomendasi cross-sell dibuat")
        
        return self.df
    
    def export_dashboard_data(self):
        """
        Export data untuk dashboard dengan filter lengkap
        """
        print("\n[EXPORT] Export data untuk dashboard...")
        
        dashboard_dir = os.path.join(self.output_dir, 'dashboard_data')
        os.makedirs(dashboard_dir, exist_ok=True)
        
        # 1. Summary Metrics
        summary = {
            'total_customers': int(len(self.df)),
            'total_revenue': float(self.df['revenue'].sum()),
            'avg_revenue': float(self.df['revenue'].mean()),
            'median_revenue': float(self.df['revenue'].median()),
            'avg_tenure': float(self.df['tenure_years'].mean()),
            'median_tenure': float(self.df['tenure_years'].median()),
            'generated_at': datetime.now().isoformat()
        }
        
        # Filter distributions
        filter_columns = {
            'segmen_distribution': 'segmenCustomer',
            'wilayah_distribution': 'WILAYAH',
            'kategori_distribution': 'Kategori_Baru',
            'tier_distribution': 'Kelompok Tier',
            'produk_distribution': 'ProdukBaru'
        }
        
        for key, col in filter_columns.items():
            if col in self.df.columns:
                dist = self.df[col].value_counts().head(20).to_dict()
                summary[key] = {str(k): int(v) for k, v in dist.items()}
        
        # Quadrant distribution
        quad_dist = self.df['revenue_tenure_quadrant'].value_counts().to_dict()
        summary['quadrant_distribution'] = {str(k): int(v) for k, v in quad_dist.items()}
        
        with open(f'{dashboard_dir}/summary_metrics.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print("   [OK] summary_metrics.json")
        
        # 2. Revenue × Tenure Matrix Data
        matrix_columns = [
            'idPelanggan', 'namaPelanggan', 'revenue', 'tenure_years',
            'revenue_tenure_quadrant', 'strategy', 'action', 'priority',
            'quadrant_color', 'bandwidth_cluster', 'upsell_potential'
        ]
        
        # Add filter columns if exist
        for col in ['segmenCustomer', 'WILAYAH', 'Kategori_Baru', 'Kelompok Tier', 'ProdukBaru']:
            if col in self.df.columns:
                matrix_columns.append(col)
        
        matrix_data = self.df[matrix_columns].copy()
        matrix_data.columns = [col.lower().replace(' ', '_') for col in matrix_data.columns]
        
        # Convert to records
        records = matrix_data.to_dict('records')
        
        with open(f'{dashboard_dir}/revenue_tenure_matrix.json', 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"   [OK] revenue_tenure_matrix.json ({len(records)} records)")
        
        # 3. Top Opportunities
        top_opportunities = self.df.nlargest(100, 'upsell_potential')[
            ['idPelanggan', 'namaPelanggan', 'revenue', 'tenure_years',
             'revenue_tenure_quadrant', 'strategy', 'cross_sell_products',
             'upsell_potential', 'priority'] + 
            [col for col in ['segmenCustomer', 'WILAYAH', 'Kategori_Baru', 'Kelompok Tier'] if col in self.df.columns]
        ].to_dict('records')
        
        with open(f'{dashboard_dir}/top_100_opportunities.json', 'w', encoding='utf-8') as f:
            json.dump(top_opportunities, f, indent=2, ensure_ascii=False)
        print(f"   [OK] top_100_opportunities.json ({len(top_opportunities)} records)")
        
        # 4. Quadrant Analysis
        quadrant_analysis = []
        for quadrant in ['SULTAN LOYAL', 'ORANG KAYA BARU', 'SAHABAT HEMAT', 'PEMULA']:
            quad_data = self.df[self.df['revenue_tenure_quadrant'] == quadrant]
            if len(quad_data) > 0:
                quadrant_analysis.append({
                    'quadrant': quadrant,
                    'count': int(len(quad_data)),
                    'avg_revenue': float(quad_data['revenue'].mean()),
                    'avg_tenure': float(quad_data['tenure_years'].mean()),
                    'total_revenue': float(quad_data['revenue'].sum()),
                    'total_potential': float(quad_data['upsell_potential'].sum()),
                    'strategy': quad_data['strategy'].iloc[0],
                    'action': quad_data['action'].iloc[0],
                    'color': quad_data['quadrant_color'].iloc[0]
                })
        
        with open(f'{dashboard_dir}/quadrant_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(quadrant_analysis, f, indent=2, ensure_ascii=False)
        print(f"   [OK] quadrant_analysis.json ({len(quadrant_analysis)} quadrants)")
        
        # 5. Filter Options (for dropdowns)
        filter_options = {}
        for col in ['segmenCustomer', 'WILAYAH', 'Kategori_Baru', 'Kelompok Tier', 'ProdukBaru']:
            if col in self.df.columns:
                values = self.df[col].dropna().unique().tolist()
                filter_options[col] = sorted([str(v) for v in values])
        
        with open(f'{dashboard_dir}/filter_options.json', 'w', encoding='utf-8') as f:
            json.dump(filter_options, f, indent=2, ensure_ascii=False)
        print(f"   [OK] filter_options.json ({len(filter_options)} filters)")
        
        # 6. Excel Export for Sales Team
        excel_path = os.path.join(self.output_dir, 'CVO_v4_Master_Results.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Sheet 1: All customers
            export_cols = [
                'idPelanggan', 'namaPelanggan', 'revenue', 'tenure_years',
                'revenue_tenure_quadrant', 'strategy', 'action', 'priority',
                'bandwidth_cluster', 'cross_sell_target', 'cross_sell_products',
                'upsell_potential'
            ]
            for col in ['segmenCustomer', 'WILAYAH', 'Kategori_Baru', 'Kelompok Tier', 'ProdukBaru']:
                if col in self.df.columns:
                    export_cols.append(col)
            
            self.df[export_cols].to_excel(writer, sheet_name='All Customers', index=False)
            
            # Sheet 2: Per Quadrant
            for quadrant in ['SULTAN LOYAL', 'ORANG KAYA BARU', 'SAHABAT HEMAT', 'PEMULA']:
                quad_data = self.df[self.df['revenue_tenure_quadrant'] == quadrant]
                if len(quad_data) > 0:
                    sheet_name = quadrant[:31]  # Excel sheet name max 31 chars
                    quad_data[export_cols].to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Sheet 3: Top 100 Opportunities
            top100 = self.df.nlargest(100, 'upsell_potential')
            top100[export_cols].to_excel(writer, sheet_name='Top 100 Opportunities', index=False)
        
        print(f"   [OK] Excel: {excel_path}")
        
        print(f"\n[OK] SEMUA DATA DIEXPORT ke '{dashboard_dir}/'")
        
        return dashboard_dir
    
    def run_pipeline(self):
        """Jalankan full pipeline"""
        print("\n" + "="*80)
        print("MENJALANKAN CVO v4.0 PIPELINE")
        print("="*80)
        
        self.load_data()
        self.clean_and_prepare()
        self.create_revenue_tenure_matrix()
        self.generate_cross_sell_recommendations()
        dashboard_dir = self.export_dashboard_data()
        
        print("\n" + "="*80)
        print("PIPELINE SELESAI!")
        print("="*80)
        print(f"\nDashboard data tersedia di: {dashboard_dir}")
        print("\nFiles generated:")
        print("   - summary_metrics.json")
        print("   - revenue_tenure_matrix.json")
        print("   - top_100_opportunities.json")
        print("   - quadrant_analysis.json")
        print("   - filter_options.json")
        print("   - CVO_v4_Master_Results.xlsx")
        
        return dashboard_dir


if __name__ == "__main__":
    # Run pipeline
    analyzer = CVORevenueTenureAnalyzer(
        'Data Penuh Pelanggan Aktif.xlsx',
        'cvo_v4_results'
    )
    analyzer.run_pipeline()
