"""
CVO - Customer Value Optimizer v5.0
Full End-to-End System (Backend)
================================

Features:
- Advanced Clustering (Micro/Low/Mid/High)
- 2 Strategic Matrices (Sales Matrix & Trust Matrix)
- Hybrid Recommendation Engine (Rule-based + ML)
- Export untuk Dashboard Next.js

PLN Icon+ - ML Division
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("CVO v5.0 - End-to-End Customer Value Optimizer")
print("="*80)


class DataCleaner:
    """
    FASE 1: Data Cleaning & Feature Engineering
    ============================================
    """
    
    @staticmethod
    def clean_bandwidth(bandwidth_value):
        """
        Cluster bandwidth berdasarkan kegunaan bisnis:
        - Micro (< 10 Mbps): ATM/IoT
        - Low (10 - 100 Mbps): Retail/SOHO
        - Mid (100 - 500 Mbps): Corporate
        - High (> 500 Mbps): Backbone/Data Center
        """
        if pd.isna(bandwidth_value) or bandwidth_value == 0:
            return 'NO_BANDWIDTH'
        elif bandwidth_value < 10:
            return 'MICRO'  # ATM/IoT
        elif bandwidth_value < 100:
            return 'LOW'    # Retail/SOHO
        elif bandwidth_value < 500:
            return 'MID'    # Corporate
        else:
            return 'HIGH'   # Backbone/Data Center
    
    @staticmethod
    def clean_revenue(revenue_value):
        """
        Cluster revenue berdasarkan paket harga:
        - Zero/Free: 0 (Free Trial/Internal)
        - Standard: ~1.4 Juta (Bread & Butter)
        - High: > 2 Juta (Sultan)
        """
        if pd.isna(revenue_value) or revenue_value == 0:
            return 'ZERO'
        elif revenue_value < 500000:
            return 'LOW'
        elif revenue_value < 2000000:
            return 'STANDARD'
        else:
            return 'HIGH'
    
    @staticmethod
    def clean_tenure(tenure_value):
        """
        Cluster tenure berdasarkan loyalitas:
        - New: < 5 Tahun (Bulan madu)
        - Established: 5 - 10 Tahun (Stabil)
        - Loyal: > 10 Tahun (Abadi)
        """
        if pd.isna(tenure_value):
            return 'NEW'
        elif tenure_value < 5:
            return 'NEW'
        elif tenure_value <= 10:
            return 'ESTABLISHED'
        else:
            return 'LOYAL'
    
    @staticmethod
    def calculate_ltv(monthly_revenue, tenure):
        """Calculate Lifetime Value"""
        if pd.isna(monthly_revenue) or pd.isna(tenure):
            return 0
        return monthly_revenue * 12 * tenure
    
    @staticmethod
    def tag_product_role(kategori_baru):
        """
        Tag produk berdasarkan role:
        - Smart & Digital / Green Eco -> High_Margin
        - Digital Infra -> Core_Retention
        - Technology Services -> Add_On
        """
        if pd.isna(kategori_baru):
            return 'UNKNOWN'
        
        kategori = str(kategori_baru).upper()
        
        if 'SMART' in kategori or 'GREEN' in kategori or 'DIGITAL SOLUTION' in kategori:
            return 'HIGH_MARGIN'
        elif 'INFRA' in kategori or 'CONNECTIVITY' in kategori:
            return 'CORE_RETENTION'
        elif 'TECHNOLOGY' in kategori or 'SERVICE' in kategori or 'MANAGED' in kategori:
            return 'ADD_ON'
        else:
            return 'UNKNOWN'


class StrategicMatrixAnalyzer:
    """
    FASE 2: Logic Pembentukan 2 Matrix Strategis
    =============================================
    """
    
    @staticmethod
    def analyze_sales_matrix(revenue, bandwidth_cluster):
        """
        MATRIX 1: The Sales Matrix (Monthly Rev vs Bandwidth Segment)
        
        Risk Area (High Rev + Low Bandwidth): CROSS-SELL
        Sniper Zone (Low Rev + High Usage): UPSELL
        Star Clients (High Rev + High Bandwidth): RETENTION
        Incubator (Low Rev + Low Bandwidth): LOW COST AUTOMATION
        """
        rev_high = revenue >= 2000000  # Threshold High Revenue
        bw_high = bandwidth_cluster in ['MID', 'HIGH']
        
        if rev_high and bw_high:
            return {
                'quadrant': 'STAR_CLIENTS',
                'strategy': 'RETENTION',
                'color': '#4CAF50',
                'action': 'Jaga kepuasan, offer premium support'
            }
        elif rev_high and not bw_high:
            return {
                'quadrant': 'RISK_AREA',
                'strategy': 'CROSS_SELL',
                'color': '#FF5722',
                'action': 'Tawarkan produk value-add (security, managed svc)'
            }
        elif not rev_high and bw_high:
            return {
                'quadrant': 'SNIPER_ZONE',
                'strategy': 'UPSELL',
                'color': '#2196F3',
                'action': 'Tawarkan upgrade bandwidth dengan harga lebih tinggi'
            }
        else:
            return {
                'quadrant': 'INCUBATOR',
                'strategy': 'AUTOMATION',
                'color': '#9E9E9E',
                'action': 'Program incubator, low-touch automation'
            }
    
    @staticmethod
    def analyze_trust_matrix(ltv, tenure_cluster):
        """
        MATRIX 2: The Trust Matrix (Lifetime Value vs Tenure)
        
        Sultan Loyal (High LTV + Loyal): BIG TICKET CROSS-SELL
        New Potential (High Monthly + New): ONBOARDING
        """
        ltv_high = ltv >= 500000000  # > 500M LTV
        loyal = tenure_cluster == 'LOYAL'
        
        if ltv_high and loyal:
            return {
                'quadrant': 'SULTAN_LOYAL',
                'strategy': 'BIG_TICKET_CROSS_SELL',
                'color': '#2E7D32',
                'action': 'Tawarkan produk big ticket: PV Rooftop, Smart Building'
            }
        elif ltv_high and not loyal:
            return {
                'quadrant': 'NEW_POTENTIAL',
                'strategy': 'ONBOARDING',
                'color': '#1565C0',
                'action': 'Fokus kepuasan awal, bundling sederhana'
            }
        elif not ltv_high and loyal:
            return {
                'quadrant': 'LOYAL_BUT_LOW',
                'strategy': 'NUDGING',
                'color': '#F57C00',
                'action': 'Trial produk baru, loyalty rewards'
            }
        else:
            return {
                'quadrant': 'NEW_LOW',
                'strategy': 'INCUBATOR',
                'color': '#757575',
                'action': 'Program incubator, monitoring'
            }


class HybridRecommendationEngine:
    """
    FASE 3: Advanced Recommendation Engine (Hybrid Logic)
    ======================================================
    """
    
    def __init__(self, product_catalog_path: str):
        """Initialize dengan product catalog"""
        self.product_catalog = self._load_product_catalog(product_catalog_path)
        self.industry_priorities = self._setup_industry_priorities()
        
    def _load_product_catalog(self, path: str) -> pd.DataFrame:
        """Load master produk dari Excel"""
        if os.path.exists(path):
            return pd.read_excel(path, engine='openpyxl')
        else:
            print(f"[WARN] Product catalog not found: {path}")
            return pd.DataFrame()
    
    def _setup_industry_priorities(self) -> Dict:
        """Setup industry-specific priorities"""
        return {
            'BANKING & FINANCIAL': {
                'priority_products': ['IP VPN', 'Managed Security', 'CCTV Analytics', 'Backup Link'],
                'reasoning': 'Banking requires high security and compliance'
            },
            'GOVERNMENT': {
                'priority_products': ['Smart City', 'PV Rooftop', 'Command Center', 'e-Government'],
                'reasoning': 'Government needs public service and green energy'
            },
            'MANUFACTURING': {
                'priority_products': ['IoT Platform', 'Green Eco', 'Smart Factory', 'Predictive Maintenance'],
                'reasoning': 'Manufacturing needs efficiency and Industry 4.0'
            },
            'EDUCATION': {
                'priority_products': ['WiFi Campus', 'Video Conference', 'Digital Library', 'E-Learning'],
                'reasoning': 'Education needs connectivity and digital learning'
            },
            'RETAIL': {
                'priority_products': ['SD-WAN', 'POS System', 'CCTV', 'Managed WiFi'],
                'reasoning': 'Retail needs connectivity and customer analytics'
            },
            'HEALTHCARE': {
                'priority_products': ['Telemedicine', 'Medical IoT', 'Backup Connectivity', 'Secure Network'],
                'reasoning': 'Healthcare needs reliability and patient data security'
            }
        }
    
    def generate_recommendation(self, customer_data: Dict) -> Dict:
        """
        Generate hybrid recommendation menggunakan:
        Logic 1: Direct Mapping dari product catalog
        Logic 2: Industry Priorities
        Logic 3: Portfolio Gap Analysis
        Logic 4: Product Hierarchy (Bronze->Gold)
        """
        segmen = customer_data.get('segmen', 'UNKNOWN')
        current_tier = customer_data.get('tier', '')
        current_products = customer_data.get('produk', [])
        strategy = customer_data.get('strategy', '')
        
        recommendations = []
        reasoning_parts = []
        
        # Logic 1 & 2: Industry-based recommendation
        if segmen in self.industry_priorities:
            industry_rec = self.industry_priorities[segmen]
            for product in industry_rec['priority_products'][:2]:  # Top 2
                if product not in str(current_products):
                    recommendations.append(product)
                    reasoning_parts.append(f"{segmen} needs {product} ({industry_rec['reasoning']})")
        
        # Logic 3: Portfolio Gap
        if 'DI Only' in str(current_tier):
            if strategy == 'CROSS_SELL':
                recommendations.append('Managed Services')
                reasoning_parts.append("Portfolio Gap: Has DI but missing Managed Services")
            elif strategy == 'UPSELL':
                recommendations.append('Higher Tier DI')
                reasoning_parts.append("Upsell opportunity: Upgrade DI tier")
        
        # Logic 4: Product Hierarchy (Bronze->Gold)
        if 'Bronze' in str(current_products) or 'Basic' in str(current_products):
            recommendations.append('Upgrade to Gold/Premium')
            reasoning_parts.append("Product Hierarchy: Bronze user ready for Gold upgrade")
        
        # Final recommendation
        if not recommendations:
            recommendations = ['Managed WiFi', 'CCTV Cloud']  # Default
            reasoning_parts.append("Standard cross-sell for general segment")
        
        return {
            'primary_recommendation': recommendations[0] if recommendations else 'Consult Sales Team',
            'secondary_recommendation': recommendations[1] if len(recommendations) > 1 else None,
            'reasoning': ' | '.join(reasoning_parts[:2]),  # Top 2 reasons
            'confidence_score': min(0.95, 0.6 + (0.1 * len(recommendations)))
        }


class CVOPipeline:
    """
    Main Pipeline - End to End
    ==========================
    """
    
    def __init__(self, data_path: str, product_catalog_path: str, output_dir: str = 'cvo_v5_output'):
        self.data_path = data_path
        self.product_catalog_path = product_catalog_path
        self.output_dir = output_dir
        self.cleaner = DataCleaner()
        self.matrix_analyzer = StrategicMatrixAnalyzer()
        self.recommender = HybridRecommendationEngine(product_catalog_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
    def run_pipeline(self):
        """Execute full pipeline"""
        print("\n" + "="*80)
        print("RUNNING CVO v5.0 FULL PIPELINE")
        print("="*80)
        
        # 1. Load Data
        print("\n[1/5] Loading data...")
        df = pd.read_excel(self.data_path, engine='openpyxl')
        print(f"   Loaded {len(df):,} customers")
        
        # 2. Data Cleaning & Feature Engineering
        print("\n[2/5] Data cleaning & feature engineering...")
        
        # Revenue
        df['monthly_revenue'] = pd.to_numeric(df.get('hargaPelanggan', 0), errors='coerce').fillna(0)
        df['revenue_cluster'] = df['monthly_revenue'].apply(self.cleaner.clean_revenue)
        
        # Bandwidth
        df['bandwidth_mbps'] = 0
        if 'bandwidth' in df.columns:
            df['bandwidth_mbps'] = pd.to_numeric(df['bandwidth'], errors='coerce').fillna(0)
        elif 'Bandwidth Fix' in df.columns:
            def parse_bw(val):
                if pd.isna(val) or val == 'Tidak Ada':
                    return 0
                import re
                match = re.search(r'(\d+)', str(val))
                return int(match.group(1)) if match else 0
            df['bandwidth_mbps'] = df['Bandwidth Fix'].apply(parse_bw)
        
        df['bandwidth_cluster'] = df['bandwidth_mbps'].apply(self.cleaner.clean_bandwidth)
        
        # Tenure
        df['tenure_years'] = pd.to_numeric(df.get('Lama_Langganan', 0), errors='coerce').fillna(0)
        df['tenure_cluster'] = df['tenure_years'].apply(self.cleaner.clean_tenure)
        
        # LTV
        df['ltv'] = df.apply(lambda x: self.cleaner.calculate_ltv(x['monthly_revenue'], x['tenure_years']), axis=1)
        
        # Product Role
        df['product_role'] = df.get('Kategori_Baru', '').apply(self.cleaner.tag_product_role)
        
        print(f"   Revenue clusters: {df['revenue_cluster'].value_counts().to_dict()}")
        print(f"   Bandwidth clusters: {df['bandwidth_cluster'].value_counts().to_dict()}")
        print(f"   Tenure clusters: {df['tenure_cluster'].value_counts().to_dict()}")
        
        # 3. Strategic Matrix Analysis
        print("\n[3/5] Analyzing strategic matrices...")
        
        sales_matrix_results = df.apply(
            lambda x: self.matrix_analyzer.analyze_sales_matrix(x['monthly_revenue'], x['bandwidth_cluster']), 
            axis=1
        )
        df['sales_quadrant'] = [r['quadrant'] for r in sales_matrix_results]
        df['sales_strategy'] = [r['strategy'] for r in sales_matrix_results]
        df['sales_action'] = [r['action'] for r in sales_matrix_results]
        df['sales_color'] = [r['color'] for r in sales_matrix_results]
        
        trust_matrix_results = df.apply(
            lambda x: self.matrix_analyzer.analyze_trust_matrix(x['ltv'], x['tenure_cluster']),
            axis=1
        )
        df['trust_quadrant'] = [r['quadrant'] for r in trust_matrix_results]
        df['trust_strategy'] = [r['strategy'] for r in trust_matrix_results]
        df['trust_action'] = [r['action'] for r in trust_matrix_results]
        df['trust_color'] = [r['color'] for r in trust_matrix_results]
        
        print(f"   Sales Matrix: {df['sales_quadrant'].value_counts().to_dict()}")
        print(f"   Trust Matrix: {df['trust_quadrant'].value_counts().to_dict()}")
        
        # 4. Hybrid Recommendation
        print("\n[4/5] Generating hybrid recommendations...")
        
        recommendations = []
        for idx, row in df.iterrows():
            customer_data = {
                'segmen': row.get('segmenCustomer', 'UNKNOWN'),
                'tier': row.get('Kelompok Tier', ''),
                'produk': str(row.get('ProdukBaru', '')).split(','),
                'strategy': row['sales_strategy']
            }
            rec = self.recommender.generate_recommendation(customer_data)
            recommendations.append(rec)
        
        df['recommendation_primary'] = [r['primary_recommendation'] for r in recommendations]
        df['recommendation_secondary'] = [r['secondary_recommendation'] for r in recommendations]
        df['recommendation_reasoning'] = [r['reasoning'] for r in recommendations]
        df['confidence_score'] = [r['confidence_score'] for r in recommendations]
        
        # 5. Export Results
        print("\n[5/5] Exporting results...")
        self._export_results(df)
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETE!")
        print("="*80)
        
        return df
    
    def _export_results(self, df: pd.DataFrame):
        """Export hasil untuk dashboard"""
        
        # Excel Master
        excel_path = os.path.join(self.output_dir, 'CVO_v5_Master_Analysis.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # All customers
            df.to_excel(writer, sheet_name='All Customers', index=False)
            
            # Per quadrant
            for quadrant in df['sales_quadrant'].unique():
                quad_df = df[df['sales_quadrant'] == quadrant]
                sheet_name = quadrant[:31]
                quad_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Top opportunities
            top_opp = df.nlargest(100, 'confidence_score')
            top_opp.to_excel(writer, sheet_name='Top 100 Opportunities', index=False)
        
        print(f"   Excel: {excel_path}")
        
        # JSON untuk Dashboard
        dashboard_dir = os.path.join(self.output_dir, 'dashboard_data')
        os.makedirs(dashboard_dir, exist_ok=True)
        
        # Summary
        summary = {
            'total_customers': int(len(df)),
            'total_revenue': float(df['monthly_revenue'].sum()),
            'total_ltv': float(df['ltv'].sum()),
            'avg_revenue': float(df['monthly_revenue'].mean()),
            'avg_ltv': float(df['ltv'].mean()),
            'sales_matrix': df['sales_quadrant'].value_counts().to_dict(),
            'trust_matrix': df['trust_quadrant'].value_counts().to_dict(),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(f'{dashboard_dir}/summary_v5.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Customers data
        customers_export = df[[
            'idPelanggan', 'namaPelanggan', 'segmenCustomer', 'monthly_revenue', 
            'bandwidth_mbps', 'bandwidth_cluster', 'tenure_years', 'tenure_cluster',
            'ltv', 'sales_quadrant', 'sales_strategy', 'trust_quadrant', 'trust_strategy',
            'recommendation_primary', 'recommendation_secondary', 'recommendation_reasoning',
            'confidence_score', 'sales_color'
        ]].to_dict('records')
        
        with open(f'{dashboard_dir}/customers_v5.json', 'w', encoding='utf-8') as f:
            json.dump(customers_export, f, indent=2, ensure_ascii=False)
        
        print(f"   JSON files in: {dashboard_dir}")


if __name__ == "__main__":
    # Run pipeline
    pipeline = CVOPipeline(
        data_path='Data Penuh Pelanggan Aktif.xlsx',
        product_catalog_path='Mapping Seluruh Produk ICON+.xlsx',
        output_dir='cvo_v5_output'
    )
    
    result_df = pipeline.run_pipeline()
