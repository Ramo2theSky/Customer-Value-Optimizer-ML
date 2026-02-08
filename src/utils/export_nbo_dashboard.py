"""
Export NBO Data to Dashboard JSON
==================================
Export CVO NBO results to JSON for dashboard
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class NBODataExporter:
    """Export NBO data to JSON format"""
    
    def __init__(self, data_path='laporan_nbo/CVO_NBO_Master.xlsx', output_dir='dashboard_data'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self):
        """Load NBO data from Excel"""
        print("[DATA] Loading NBO data...")
        self.df = pd.read_excel(self.data_path, engine='openpyxl')
        
        # Rename columns for easier access
        self.df.columns = [col.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_') 
                          for col in self.df.columns]
        
        print(f"[OK] Loaded {len(self.df):,} customers")
        print(f"   Columns: {list(self.df.columns)}")
        return self.df
    
    def export_summary_metrics(self):
        """Export summary metrics"""
        print("\n[CHART] Exporting summary metrics...")
        
        summary = {
            'total_customers': int(len(self.df)),
            'total_revenue': float(self.df['pendapatan_rp'].sum()),
            'avg_revenue': float(self.df['pendapatan_rp'].mean()),
            'median_revenue': float(self.df['pendapatan_rp'].median()),
            'avg_bandwidth': float(self.df['bandwidth_mbps'].mean()),
            'median_bandwidth': float(self.df['bandwidth_mbps'].median()),
            'avg_tenure': float(self.df['masa_berlangganan_bulan'].mean()),
            'total_potential': float(self.df['potensi_revenue_rp'].sum()),
            'generated_at': datetime.now().isoformat()
        }
        
        # Tier distribution
        tier_dist = self.df['tier_saat_ini'].value_counts().to_dict()
        summary['tier_distribution'] = {str(k): int(v) for k, v in tier_dist.items()}
        
        # Bandwidth cluster distribution
        cluster_dist = self.df['cluster_bandwidth'].value_counts().to_dict()
        summary['bandwidth_cluster_distribution'] = {str(k): int(v) for k, v in cluster_dist.items()}
        
        # Strategic category distribution
        cat_dist = self.df['kategori_strategis'].value_counts().to_dict()
        summary['strategic_category_distribution'] = {str(k): int(v) for k, v in cat_dist.items()}
        
        # Priority distribution
        priority_dist = self.df['prioritas'].value_counts().to_dict()
        summary['priority_distribution'] = {str(k): int(v) for k, v in priority_dist.items()}
        
        with open(f'{self.output_dir}/summary_metrics.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] summary_metrics.json")
        return summary
    
    def export_matrix_revenue_bandwidth(self):
        """Export Revenue vs Bandwidth matrix data"""
        print("\n[DATA] Exporting Revenue x Bandwidth matrix...")
        
        matrix_data = self.df[[
            'nama_pelanggan', 'pendapatan_rp', 'bandwidth_mbps', 
            'kategori_strategis', 'strategi', 'next_best_offer',
            'tier_saat_ini', 'cluster_bandwidth', 'prioritas',
            'potensi_revenue_rp', 'skor_upsell_0_1'
        ]].copy()
        
        # Convert to records
        records = []
        for _, row in matrix_data.iterrows():
            records.append({
                'customer': str(row['nama_pelanggan']),
                'revenue': float(row['pendapatan_rp']),
                'bandwidth': float(row['bandwidth_mbps']),
                'category': str(row['kategori_strategis']),
                'strategy': str(row['strategi']),
                'nbo': str(row['next_best_offer']),
                'tier': str(row['tier_saat_ini']),
                'cluster': str(row['cluster_bandwidth']),
                'priority': str(row['prioritas']),
                'potential': float(row['potensi_revenue_rp']),
                'upsell_score': float(row['skor_upsell_0_1'])
            })
        
        with open(f'{self.output_dir}/matrix_revenue_bandwidth.json', 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] matrix_revenue_bandwidth.json ({len(records)} records)")
    
    def export_matrix_revenue_tenure(self):
        """Export Revenue vs Tenure matrix data"""
        print("\n[DATA] Exporting Revenue x Tenure matrix...")
        
        matrix_data = self.df[[
            'nama_pelanggan', 'pendapatan_rp', 'masa_berlangganan_bulan',
            'kategori_strategis', 'tier_saat_ini', 'prioritas',
            'potensi_revenue_rp'
        ]].copy()
        
        records = []
        for _, row in matrix_data.iterrows():
            records.append({
                'customer': str(row['nama_pelanggan']),
                'revenue': float(row['pendapatan_rp']),
                'tenure': float(row['masa_berlangganan_bulan']),
                'category': str(row['kategori_strategis']),
                'tier': str(row['tier_saat_ini']),
                'priority': str(row['prioritas']),
                'potential': float(row['potensi_revenue_rp'])
            })
        
        with open(f'{self.output_dir}/matrix_revenue_tenure.json', 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] matrix_revenue_tenure.json ({len(records)} records)")
    
    def export_tier_roadmap(self):
        """Export tier progression roadmap"""
        print("\n[TARGET] Exporting tier roadmap...")
        
        # Group by current tier
        tier_stats = self.df.groupby('tier_saat_ini').agg({
            'nama_pelanggan': 'count',
            'pendapatan_rp': ['mean', 'sum'],
            'potensi_revenue_rp': 'sum',
            'bandwidth_mbps': 'mean'
        }).reset_index()
        
        roadmap = []
        for _, row in tier_stats.iterrows():
            current_tier = row['tier_saat_ini']
            
            roadmap.append({
                'tier': str(current_tier),
                'count': int(row['nama_pelanggan']),
                'avg_revenue': float(row['pendapatan_rp']['mean']),
                'total_revenue': float(row['pendapatan_rp']['sum']),
                'total_potential': float(row['potensi_revenue_rp']),
                'avg_bandwidth': float(row['bandwidth_mbps']),
                'next_tier': self._get_next_tier(str(current_tier)),
                'recommendation': self._get_tier_recommendation(str(current_tier))
            })
        
        # Sort by tier progression
        tier_order = [
            'DI Only', 'TS Only', 'SDS Only', 'GE Only',
            'DI-TS', 'DI-SDS', 'DI-GE', 'SDS-TS', 'GE-SDS', 'GE-TS',
            'DI-SDS-TS', 'DI-GE-TS', 'DI-GE-SDS', 'GE-SDS-TS', 'ALL NOMENKLATUR'
        ]
        roadmap.sort(key=lambda x: tier_order.index(x['tier']) if x['tier'] in tier_order else 999)
        
        with open(f'{self.output_dir}/tier_roadmap.json', 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] tier_roadmap.json ({len(roadmap)} tiers)")
    
    def _get_next_tier(self, current_tier):
        """Get next tier recommendation"""
        roadmap = {
            'DI Only': 'DI-TS',
            'TS Only': 'DI-TS',
            'SDS Only': 'DI-SDS-TS',
            'GE Only': 'DI-GE',
            'DI-TS': 'DI-SDS-TS',
            'DI-SDS': 'DI-SDS-TS',
            'DI-GE': 'DI-GE-TS',
            'SDS-TS': 'DI-SDS-TS',
            'GE-SDS': 'GE-SDS-TS',
            'GE-TS': 'DI-GE-TS',
            'DI-SDS-TS': 'ALL NOMENKLATUR',
            'DI-GE-TS': 'ALL NOMENKLATUR',
            'DI-GE-SDS': 'ALL NOMENKLATUR',
            'GE-SDS-TS': 'ALL NOMENKLATUR',
            'ALL NOMENKLATUR': None
        }
        return roadmap.get(current_tier, None)
    
    def _get_tier_recommendation(self, tier):
        """Get recommendation for tier"""
        recommendations = {
            'DI Only': 'Tambahkan Technology Services',
            'TS Only': 'Tambahkan Digital Infrastructure',
            'SDS Only': 'Tambahkan DI + TS',
            'GE Only': 'Tambahkan DI + SDS',
            'DI-TS': 'Tambahkan Smart Digital Solution',
            'DI-SDS': 'Tambahkan TS untuk lengkapi',
            'DI-GE': 'Tambahkan TS + SDS',
            'SDS-TS': 'Tambahkan DI untuk lengkapi',
            'GE-SDS': 'Tambahkan DI + TS',
            'GE-TS': 'Tambahkan DI + SDS',
            'DI-SDS-TS': 'Tambahkan Green Ecosystem',
            'DI-GE-TS': 'Tambahkan SDS untuk lengkapi',
            'DI-GE-SDS': 'Tambahkan TS untuk lengkapi',
            'GE-SDS-TS': 'Tambahkan DI untuk lengkapi',
            'ALL NOMENKLATUR': 'Retention & Premium Services'
        }
        return recommendations.get(tier, 'Analyze Further')
    
    def export_nbo_by_category(self):
        """Export NBO recommendations by strategic category"""
        print("\n Exporting NBO by category...")
        
        # SNIPER (High Priority Upsell)
        sniper_data = self.df[self.df['kategori_strategis'] == 'SNIPER']
        sniper_targets = sniper_data[[
            'nama_pelanggan', 'tier_saat_ini', 'kategori_strategis',
            'strategi', 'next_best_offer', 'bandwidth_mbps', 
            'pendapatan_rp', 'potensi_revenue_rp', 'prioritas'
        ]].to_dict('records')
        
        sniper_list = []
        for record in sniper_targets:
            sniper_list.append({
                'customer': str(record['nama_pelanggan']),
                'current_tier': str(record['tier_saat_ini']),
                'category': str(record['kategori_strategis']),
                'strategy': str(record['strategi']),
                'nbo': str(record['next_best_offer']),
                'bandwidth': float(record['bandwidth_mbps']),
                'revenue': float(record['pendapatan_rp']),
                'potential': float(record['potensi_revenue_rp']),
                'priority': str(record['prioritas'])
            })
        
        with open(f'{self.output_dir}/nbo_sniper.json', 'w', encoding='utf-8') as f:
            json.dump(sniper_list, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] nbo_sniper.json ({len(sniper_list)} targets)")
        
        # RISIKO (Retention Priority)
        risiko_data = self.df[self.df['kategori_strategis'] == 'RISIKO']
        risiko_targets = risiko_data[[
            'nama_pelanggan', 'tier_saat_ini', 'kategori_strategis',
            'strategi', 'next_best_offer', 'bandwidth_mbps',
            'pendapatan_rp', 'potensi_revenue_rp', 'prioritas'
        ]].to_dict('records')
        
        risiko_list = []
        for record in risiko_targets:
            risiko_list.append({
                'customer': str(record['nama_pelanggan']),
                'current_tier': str(record['tier_saat_ini']),
                'category': str(record['kategori_strategis']),
                'strategy': str(record['strategi']),
                'nbo': str(record['next_best_offer']),
                'bandwidth': float(record['bandwidth_mbps']),
                'revenue': float(record['pendapatan_rp']),
                'potential': float(record['potensi_revenue_rp']),
                'priority': str(record['prioritas'])
            })
        
        with open(f'{self.output_dir}/nbo_risiko.json', 'w', encoding='utf-8') as f:
            json.dump(risiko_list, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] nbo_risiko.json ({len(risiko_list)} targets)")
    
    def export_top_opportunities(self):
        """Export top opportunities"""
        print("\n[TROPHY] Exporting top opportunities...")
        
        # Get top 50 by potential
        top50 = self.df.nlargest(50, 'potensi_revenue_rp')
        
        opportunities = []
        for _, row in top50.iterrows():
            opportunities.append({
                'customer': str(row['nama_pelanggan']),
                'current_tier': str(row['tier_saat_ini']),
                'recommended_tier': str(row['rekomendasi_tier']),
                'category': str(row['kategori_strategis']),
                'strategy': str(row['strategi']),
                'nbo': str(row['next_best_offer']),
                'bandwidth': float(row['bandwidth_mbps']),
                'current_revenue': float(row['pendapatan_rp']),
                'potential_revenue': float(row['potensi_revenue_rp']),
                'priority': str(row['prioritas']),
                'upsell_score': float(row['skor_upsell_0_1']),
                'clv_prediction': float(row['clv_prediksi_rp']) if 'clv_prediksi_rp' in row else 0
            })
        
        with open(f'{self.output_dir}/top_50_opportunities.json', 'w', encoding='utf-8') as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] top_50_opportunities.json ({len(opportunities)} opportunities)")
    
    def export_all(self):
        """Export all data"""
        print("\n" + "="*60)
        print("EXPORTING NBO DASHBOARD DATA")
        print("="*60)
        
        self.load_data()
        self.export_summary_metrics()
        self.export_matrix_revenue_bandwidth()
        self.export_matrix_revenue_tenure()
        self.export_tier_roadmap()
        self.export_nbo_by_category()
        self.export_top_opportunities()
        
        print("\n" + "="*60)
        print("[OK] ALL DATA EXPORTED")
        print("="*60)
        print("\nFiles generated in 'dashboard_data/':")
        print("   [DATA] summary_metrics.json")
        print("   [DATA] matrix_revenue_bandwidth.json")
        print("   [DATA] matrix_revenue_tenure.json")
        print("   [DATA] tier_roadmap.json")
        print("   [DATA] nbo_sniper.json")
        print("   [DATA] nbo_risiko.json")
        print("   [DATA] top_50_opportunities.json")


if __name__ == "__main__":
    exporter = NBODataExporter()
    exporter.export_all()
