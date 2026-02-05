"""
CVO Dashboard Data Exporter
============================
Export all CVO results to dashboard-ready JSON format
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class DashboardDataExporter:
    """Export all CVO data to JSON for Next.js dashboard"""
    
    def __init__(self, data_path, output_dir='dashboard_data'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self):
        """Load data from Excel"""
        print("[DATA] Loading data...")
        self.df = pd.read_excel(self.data_path, engine='openpyxl')
        print(f"[OK] Loaded {len(self.df):,} customers")
        return self.df
    
    def export_summary_metrics(self):
        """Export summary metrics"""
        print("\n[CHART] Exporting summary metrics...")
        
        summary = {
            'total_customers': int(len(self.df)),
            'total_revenue': float(self.df['pendapatan'].sum()),
            'avg_revenue': float(self.df['pendapatan'].mean()),
            'median_revenue': float(self.df['pendapatan'].median()),
            'avg_bandwidth': float(self.df['bandwidth_mbps'].mean()),
            'median_bandwidth': float(self.df['bandwidth_mbps'].median()),
            'avg_tenure': float(self.df['masa_berlangganan'].mean()),
            'generated_at': datetime.now().isoformat()
        }
        
        # Add segment distribution
        segmen_dist = self.df['segmen_final'].value_counts().to_dict()
        summary['segmen_distribution'] = {k: int(v) for k, v in segmen_dist.items()}
        
        # Add bandwidth cluster distribution
        cluster_dist = self.df['bandwidth_cluster'].value_counts().to_dict()
        summary['bandwidth_cluster_distribution'] = {k: int(v) for k, v in cluster_dist.items()}
        
        # Add quadrants
        quadrants = self.df['kuadran'].value_counts().to_dict()
        summary['quadrants'] = {k: int(v) for k, v in quadrants.items()}
        
        # Add tier distribution
        if 'tier' in self.df.columns:
            tier_dist = self.df['tier'].value_counts().to_dict()
            summary['tier_distribution'] = {k: int(v) for k, v in tier_dist.items()}
        
        with open(f'{self.output_dir}/summary_metrics.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print("   [OK] summary_metrics.json")
        return summary
    
    def export_matrix_data(self):
        """Export data for strategic matrices"""
        print("\n[DATA] Exporting matrix data...")
        
        # Matrix 1: Revenue vs Bandwidth
        matrix1_data = self.df[['nama_pelanggan', 'pendapatan', 'bandwidth_mbps', 
                                'kuadran', 'segmen_final', 'strategi', 'nbo']].to_dict('records')
        
        with open(f'{self.output_dir}/matrix_revenue_bandwidth.json', 'w', encoding='utf-8') as f:
            json.dump(matrix1_data, f, indent=2)
        
        print("   [OK] matrix_revenue_bandwidth.json")
        
        # Matrix 2: Revenue vs Tenure
        matrix2_data = self.df[['nama_pelanggan', 'pendapatan', 'masa_berlangganan',
                                'segmen_final', 'tier']].to_dict('records')
        
        with open(f'{self.output_dir}/matrix_revenue_tenure.json', 'w', encoding='utf-8') as f:
            json.dump(matrix2_data, f, indent=2)
        
        print("   [OK] matrix_revenue_tenure.json")
    
    def export_tier_roadmap(self):
        """Export tier roadmap data"""
        print("\n[TARGET] Exporting tier roadmap...")
        
        if 'tier' not in self.df.columns:
            print("   [WARN] No tier column found")
            return
        
        tier_progression = [
            'DI Only', 'TS Only', 'SDS Only', 'GE Only',
            'DI-TS', 'DI-SDS', 'DI-GE', 'SDS-TS', 'GE-SDS', 'GE-TS',
            'DI-SDS-TS', 'DI-GE-TS', 'DI-GE-SDS', 'GE-SDS-TS', 'ALL NOMENKLATUR'
        ]
        
        roadmap = []
        for tier in tier_progression:
            tier_data = self.df[self.df['tier'] == tier]
            if len(tier_data) > 0:
                roadmap.append({
                    'tier': tier,
                    'count': int(len(tier_data)),
                    'avg_revenue': float(tier_data['pendapatan'].mean()),
                    'total_revenue': float(tier_data['pendapatan'].sum()),
                    'next_tier': self._get_next_tier(tier),
                    'recommendation': self._get_tier_recommendation(tier)
                })
        
        with open(f'{self.output_dir}/tier_roadmap.json', 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2)
        
        print("   [OK] tier_roadmap.json")
    
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
            'DI-SDS-TS': 'DI-GE-SDS-TS',
            'DI-GE-TS': 'ALL NOMENKLATUR',
            'DI-GE-SDS': 'ALL NOMENKLATUR',
            'GE-SDS-TS': 'ALL NOMENKLATUR'
        }
        return roadmap.get(current_tier, None)
    
    def _get_tier_recommendation(self, tier):
        """Get recommendation for tier"""
        recommendations = {
            'DI Only': 'Tambahkan Technology Services',
            'TS Only': 'Tambahkan Digital Infrastructure',
            'SDS Only': 'Tambahkan DI + TS',
            'DI-TS': 'Tambahkan Smart Digital Solution',
            'DI-SDS-TS': 'Tambahkan Green Ecosystem',
            'ALL NOMENKLATUR': 'Retention & Premium Services'
        }
        return recommendations.get(tier, 'Analyze Further')
    
    def export_nbo_recommendations(self):
        """Export NBO recommendations"""
        print("\n Exporting NBO recommendations...")
        
        # Upsell targets
        upsell_targets = self.df[
            (self.df['kuadran'].str.contains('SNIPER', na=False)) |
            (self.df['kuadran'].str.contains('UPSELL', na=False))
        ][['nama_pelanggan', 'segmen_final', 'tier', 'kuadran', 'strategi', 
           'nbo', 'bandwidth_mbps', 'pendapatan']].to_dict('records')
        
        with open(f'{self.output_dir}/nbo_upsell.json', 'w', encoding='utf-8') as f:
            json.dump(upsell_targets, f, indent=2)
        
        print("   [OK] nbo_upsell.json")
        
        # Cross-sell targets
        crosssell_targets = self.df[
            (self.df['kuadran'].str.contains('RISIKO', na=False)) |
            (self.df['kuadran'].str.contains('CROSS-SELL', na=False))
        ][['nama_pelanggan', 'segmen_final', 'tier', 'kuadran', 'strategi',
           'nbo', 'bandwidth_mbps', 'pendapatan']].to_dict('records')
        
        with open(f'{self.output_dir}/nbo_crosssell.json', 'w', encoding='utf-8') as f:
            json.dump(crosssell_targets, f, indent=2)
        
        print("   [OK] nbo_crosssell.json")
    
    def export_top_opportunities(self):
        """Export top opportunities"""
        print("\n[TROPHY] Exporting top opportunities...")
        
        # Calculate potential
        self.df['potential'] = self.df['pendapatan'] * 0.3  # Assume 30% upsell potential
        
        top50 = self.df.nlargest(50, 'potential')[
            ['nama_pelanggan', 'segmen_final', 'tier', 'kuadran', 'nbo',
             'bandwidth_mbps', 'pendapatan', 'potential', 'confidence']
        ].to_dict('records')
        
        with open(f'{self.output_dir}/top_50_opportunities.json', 'w', encoding='utf-8') as f:
            json.dump(top50, f, indent=2)
        
        print("   [OK] top_50_opportunities.json")
    
    def export_all(self):
        """Export all data"""
        print("\n" + "="*60)
        print("EXPORTING DASHBOARD DATA")
        print("="*60)
        
        self.load_data()
        self.export_summary_metrics()
        self.export_matrix_data()
        self.export_tier_roadmap()
        self.export_nbo_recommendations()
        self.export_top_opportunities()
        
        print("\n" + "="*60)
        print("[OK] ALL DATA EXPORTED TO 'dashboard_data/'")
        print("="*60)
        print("\nFiles generated:")
        print("   [DATA] summary_metrics.json")
        print("   [DATA] matrix_revenue_bandwidth.json")
        print("   [DATA] matrix_revenue_tenure.json")
        print("   [DATA] tier_roadmap.json")
        print("   [DATA] nbo_upsell.json")
        print("   [DATA] nbo_crosssell.json")
        print("   [DATA] top_50_opportunities.json")


if __name__ == "__main__":
    # Export from latest results
    exporter = DashboardDataExporter(
        'laporan_smart/CVO_Smart_Master.xlsx',
        'dashboard_data'
    )
    exporter.export_all()
