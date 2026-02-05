"""
CVO Integrated System v6.0
==========================
Full ML Pipeline dengan JSON Export untuk Next.js Dashboard

Output: dashboard_data.json (format ramah frontend)
Kolom wajib: customer_name, revenue, bandwidth_segment, tenure, 
             strategy_label, recommended_product, reasoning, industry

PLN Icon+ - Full Stack Integration
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("CVO v6.0 - Integrated ML Pipeline for Next.js")
print("="*80)


class IntegratedCVOPipeline:
    """
    ML Pipeline yang terintegrasi penuh dengan Frontend
    """
    
    def __init__(self, data_path: str, output_dir: str = 'public/data'):
        self.data_path = data_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def load_and_clean(self):
        """Load dan clean data"""
        print("\n[1/5] Loading data...")
        df = pd.read_excel(self.data_path, engine='openpyxl')
        
        # Clean revenue
        df['revenue'] = pd.to_numeric(df.get('hargaPelanggan', 0), errors='coerce').fillna(0)
        
        # Clean tenure  
        df['tenure'] = pd.to_numeric(df.get('Lama_Langganan', 0), errors='coerce').fillna(0)
        
        # Clean bandwidth dengan parsing yang lebih baik
        df['bandwidth'] = 0
        if 'Bandwidth Fix' in df.columns:
            def parse_bw(val):
                if pd.isna(val) or val == 'Tidak Ada':
                    return 0
                import re
                val_str = str(val).upper().strip()
                
                # Cari angka
                match = re.search(r'(\d+)', val_str)
                if not match:
                    return 0
                
                num = int(match.group(1))
                
                # Handle satuan
                if 'KBPS' in val_str:
                    return num / 1000  # Convert ke Mbps
                elif 'GBPS' in val_str or 'G' in val_str:
                    return num * 1000  # Convert ke Mbps
                elif 'E1' in val_str:
                    return 2  # E1 = 2 Mbps
                elif 'MBPS' in val_str or 'M' in val_str:
                    return num  # Sudah Mbps
                else:
                    return num  # Default assume Mbps
            
            df['bandwidth'] = df['Bandwidth Fix'].apply(parse_bw)
            print(f"   Bandwidth stats: min={df['bandwidth'].min():.1f}, max={df['bandwidth'].max():.1f}, mean={df['bandwidth'].mean():.1f}")
        
        # Filter valid data
        df = df[df['revenue'] > 0]
        
        print(f"   Loaded {len(df):,} valid customers")
        return df
    
    def create_bandwidth_segment(self, bandwidth):
        """
        Create bandwidth segment untuk frontend:
        - Low: < 10 Mbps
        - Mid: 10 - 100 Mbps  
        - High: > 100 Mbps
        """
        if bandwidth < 10:
            return 'Low'
        elif bandwidth <= 100:
            return 'Mid'
        else:
            return 'High'
    
    def create_bandwidth_score(self, segment):
        """
        Convert segment ke score numerik untuk chart:
        Low -> 1, Mid -> 2, High -> 3
        """
        mapping = {'Low': 1, 'Mid': 2, 'High': 3}
        return mapping.get(segment, 1)
    
    def analyze_strategy(self, revenue, bandwidth_segment):
        """
        Analyze strategy berdasarkan Revenue × Bandwidth
        """
        # Thresholds
        rev_high = revenue >= 2000000
        bw_high = bandwidth_segment == 'High'
        
        if rev_high and bw_high:
            return {
                'label': 'Star',
                'color': '#4CAF50',
                'action': 'Retention'
            }
        elif rev_high and not bw_high:
            return {
                'label': 'Risk',
                'color': '#FF5722', 
                'action': 'Cross-sell'
            }
        elif not rev_high and bw_high:
            return {
                'label': 'Sniper',
                'color': '#2196F3',
                'action': 'Upsell'
            }
        else:
            return {
                'label': 'Incubator',
                'color': '#9E9E9E',
                'action': 'Automation'
            }
    
    def generate_recommendation(self, row):
        """
        Generate product recommendation berdasarkan industry
        """
        industry = str(row.get('segmenCustomer', 'Unknown'))
        
        # Industry mapping
        recommendations = {
            'BANKING & FINANCIAL': {
                'product': 'Managed Security + CCTV Analytics',
                'reasoning': 'Banking requires high security and compliance. Current setup needs security enhancement.'
            },
            'GOVERNMENT': {
                'product': 'Smart City Command Center',
                'reasoning': 'Government sector benefits from smart city solutions and centralized monitoring.'
            },
            'MANUFACTURING': {
                'product': 'IoT Energy Monitoring',
                'reasoning': 'Manufacturing needs Industry 4.0 solutions for efficiency and predictive maintenance.'
            },
            'EDUCATION': {
                'product': 'Campus WiFi + Digital Library',
                'reasoning': 'Education sector needs comprehensive connectivity and digital learning platforms.'
            },
            'RETAIL': {
                'product': 'SD-WAN + POS Integration',
                'reasoning': 'Retail requires reliable connectivity and point-of-sale integration across branches.'
            },
            'HEALTHCARE': {
                'product': 'Telemedicine Platform',
                'reasoning': 'Healthcare needs reliable infrastructure for telemedicine and patient data security.'
            }
        }
        
        # Get recommendation atau fallback
        rec = recommendations.get(industry, {
            'product': 'Managed WiFi Enterprise',
            'reasoning': 'Standard enterprise solution for improved connectivity and management.'
        })
        
        return rec
    
    def process_data(self, df):
        """Process data untuk frontend"""
        print("\n[2/5] Processing data...")
        
        # Create bandwidth segment
        df['bandwidth_segment'] = df['bandwidth'].apply(self.create_bandwidth_segment)
        df['bandwidth_score'] = df['bandwidth_segment'].apply(self.create_bandwidth_score)
        
        # Analyze strategy untuk setiap row
        strategy_data = df.apply(
            lambda row: self.analyze_strategy(row['revenue'], row['bandwidth_segment']),
            axis=1
        )
        df['strategy_label'] = [s['label'] for s in strategy_data]
        df['strategy_color'] = [s['color'] for s in strategy_data]
        df['strategy_action'] = [s['action'] for s in strategy_data]
        
        # Generate recommendations
        rec_data = df.apply(self.generate_recommendation, axis=1)
        df['recommended_product'] = [r['product'] for r in rec_data]
        df['reasoning'] = [r['reasoning'] for r in rec_data]
        
        print(f"   Processed {len(df)} customers")
        print(f"   Strategy distribution: {df['strategy_label'].value_counts().to_dict()}")
        
        return df
    
    def export_for_frontend(self, df):
        """
        Export data ke JSON format yang dibutuhkan Next.js
        """
        print("\n[3/5] Exporting for frontend...")
        
        # Select dan rename kolom sesuai requirement
        export_df = pd.DataFrame({
            'customer_name': df['namaPelanggan'],
            'revenue': df['revenue'],
            'bandwidth_segment': df['bandwidth_segment'],
            'bandwidth_score': df['bandwidth_score'],
            'tenure': df['tenure'],
            'strategy_label': df['strategy_label'],
            'strategy_color': df['strategy_color'],
            'strategy_action': df['strategy_action'],
            'recommended_product': df['recommended_product'],
            'reasoning': df['reasoning'],
            'industry': df['segmenCustomer'],
            'id': df['idPelanggan'].astype(str)
        })
        
        # Export ke JSON (format yang dibutuhkan Next.js)
        json_path = os.path.join(self.output_dir, 'dashboard_data.json')
        export_df.to_json(json_path, orient='records', force_ascii=False, indent=2)
        
        print(f"   [OK] Exported: {json_path}")
        print(f"   Total records: {len(export_df)}")
        
        # Also export summary untuk stats
        summary = {
            'total_customers': int(len(export_df)),
            'total_revenue': int(export_df['revenue'].sum()),
            'avg_revenue': int(export_df['revenue'].mean()),
            'risk_clients': int(len(export_df[export_df['strategy_label'] == 'Risk'])),
            'star_clients': int(len(export_df[export_df['strategy_label'] == 'Star'])),
            'sniper_targets': int(len(export_df[export_df['strategy_label'] == 'Sniper'])),
            'generated_at': datetime.now().isoformat()
        }
        
        summary_path = os.path.join(self.output_dir, 'summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"   [OK] Summary: {summary_path}")
        
        return export_df, summary
    
    def run_pipeline(self):
        """Run full pipeline"""
        print("\n" + "="*80)
        print("RUNNING INTEGRATED PIPELINE")
        print("="*80)
        
        # Load
        df = self.load_and_clean()
        
        # Process
        df = self.process_data(df)
        
        # Export
        export_df, summary = self.export_for_frontend(df)
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETE - DATA READY FOR NEXT.JS")
        print("="*80)
        print(f"\nFiles generated in: {self.output_dir}/")
        print("   - dashboard_data.json (Main data for frontend)")
        print("   - summary.json (Stats for dashboard)")
        print(f"\nTotal customers: {summary['total_customers']:,}")
        print(f"Total revenue: Rp {summary['total_revenue']:,}")
        
        return export_df, summary


if __name__ == "__main__":
    # Run integrated pipeline
    pipeline = IntegratedCVOPipeline(
        data_path='Data Penuh Pelanggan Aktif.xlsx',
        output_dir='cvo-dashboard/public/data'  # Langsung ke folder Next.js
    )
    
    df, summary = pipeline.run_pipeline()
