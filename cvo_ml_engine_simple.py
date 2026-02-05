"""
CUSTOMER VALUE OPTIMIZER (CVO) - ML Pipeline v2.1 (No XGBoost Version)
==============================================
PLN Icon+ Marketing Planning & Analysis Division

This version uses only scikit-learn (no XGBoost required)
Works immediately without installing extra packages
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import warnings
from datetime import datetime
import re
import os
import json

warnings.filterwarnings('ignore')

print("✅ Using scikit-learn only (no XGBoost required)")


class CustomerValueOptimizer:
    """Main class for Customer Value Optimization"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df_raw = None
        self.df_processed = None
        self.df_features = None
        self.df_final = None
        self.upsell_model = None
        self.crosssell_model = None
        self.clv_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.metrics = {'upsell': {}, 'crosssell': {}, 'clv': {}}
        self.thresholds = {}
    
    def load_data(self):
        """Load data from Excel or CSV file"""
        print("\n📊 Loading data...")
        try:
            file_size = os.path.getsize(self.data_path) / (1024 * 1024)
            print(f"   File size: {file_size:.1f} MB")
            
            if self.data_path.endswith('.xlsx') or self.data_path.endswith('.xls'):
                if file_size > 50:
                    print("   ⚡ Large file detected - using optimized loading...")
                self.df_raw = pd.read_excel(self.data_path, engine='openpyxl')
                print(f"   Loaded Excel file: {self.data_path}")
            elif self.data_path.endswith('.csv'):
                try:
                    self.df_raw = pd.read_csv(self.data_path, sep=None, engine='python')
                except:
                    self.df_raw = pd.read_csv(self.data_path, sep=';', engine='python')
                print(f"   Loaded CSV file: {self.data_path}")
            else:
                raise ValueError("❌ Unsupported file format. Use .xlsx or .csv")
            
            if len(self.df_raw) > 50000:
                print(f"   ⚡ Optimizing memory for {len(self.df_raw):,} rows...")
                self._optimize_memory()
            
            print(f"✅ Data loaded: {len(self.df_raw):,} rows, {len(self.df_raw.columns)} columns")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _optimize_memory(self):
        """Optimize memory for large datasets"""
        for col in self.df_raw.select_dtypes(include=['object']).columns:
            num_unique = self.df_raw[col].nunique()
            num_total = len(self.df_raw)
            if num_unique / num_total < 0.5:
                self.df_raw[col] = self.df_raw[col].astype('category')
        
        for col in self.df_raw.select_dtypes(include=['int']).columns:
            self.df_raw[col] = pd.to_numeric(self.df_raw[col], downcast='integer')
        
        for col in self.df_raw.select_dtypes(include=['float']).columns:
            self.df_raw[col] = pd.to_numeric(self.df_raw[col], downcast='float')
    
    def clean_and_standardize(self):
        """Clean and standardize data"""
        print("\n🧹 Cleaning data...")
        df = self.df_raw.copy()
        initial_rows = len(df)
        
        column_mapping = {
            'namaPelanggan': 'customer_name',
            'hargaPelanggan': 'revenue',
            'hargaPelangganLalu': 'revenue_previous',
            'bandwidth': 'bandwidth',
            'Lama_Langganan': 'tenure_months',
            'segmenIcon': 'segment',
            'WILAYAH': 'region',
            'Kategori_Baru': 'category',
            'namaLayanan': 'product_name',
            'statusLayanan': 'status'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Clean revenue
        for col in ['revenue', 'revenue_previous']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[^\d]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Clean bandwidth
        if 'bandwidth' in df.columns:
            def convert_bw(val):
                if pd.isna(val): return 0
                val_str = str(val).lower()
                nums = re.findall(r"\d+\.?\d*", val_str.replace(',', '.'))
                if not nums: return 0
                num = float(nums[0])
                if 'gb' in val_str: return num * 1000
                elif 'kb' in val_str: return num / 1000
                return num
            df['bandwidth_mbps'] = df['bandwidth'].apply(convert_bw)
        
        # Clean tenure
        df['tenure_months'] = pd.to_numeric(df.get('tenure_months', 0), errors='coerce').fillna(0)
        
        # Filter active only
        if 'status' in df.columns:
            df = df[df['status'].str.contains('AKTIF|Aktif|Active', case=False, na=False)]
        
        # Remove duplicates
        if 'customer_name' in df.columns:
            df = df.drop_duplicates(subset=['customer_name'], keep='first')
        
        self.df_processed = df
        print(f"✅ Cleaned: {len(df)} active customers")
        return df
    
    def engineer_features(self):
        """Create ML features"""
        print("\n🔧 Engineering features...")
        df = self.df_processed.copy()
        
        # Revenue features
        df['revenue_per_mbps'] = np.where(df['bandwidth_mbps'] > 0, df['revenue'] / df['bandwidth_mbps'], 0)
        
        if 'revenue_previous' in df.columns:
            df['revenue_growth'] = np.where(df['revenue_previous'] > 0,
                                           (df['revenue'] - df['revenue_previous']) / df['revenue_previous'], 0)
        else:
            df['revenue_growth'] = 0
        
        # Value score
        df['value_score'] = (
            (df['revenue'] / df['revenue'].max()) * 0.4 +
            (df['tenure_months'] / df['tenure_months'].max()) * 0.3 +
            (df['bandwidth_mbps'] / df['bandwidth_mbps'].max()) * 0.3
        )
        
        # Indicators
        df['is_high_value'] = (df['revenue'] >= df['revenue'].quantile(0.75)).astype(int)
        df['is_high_bandwidth'] = (df['bandwidth_mbps'] >= df['bandwidth_mbps'].quantile(0.75)).astype(int)
        df['is_low_revenue'] = (df['revenue'] < df['revenue'].quantile(0.25)).astype(int)
        
        # Encode categoricals
        for col in ['segment', 'region', 'category']:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        self.df_features = df
        print(f"✅ Features ready: {df.shape[1]} columns")
        return df
    
    def create_strategic_matrices(self):
        """Create 2x2 strategic matrices"""
        print("\n📊 Creating strategic matrices...")
        df = self.df_features.copy()
        
        self.thresholds['median_revenue'] = df['revenue'].median()
        self.thresholds['median_bandwidth'] = df['bandwidth_mbps'].median()
        self.thresholds['median_tenure'] = df['tenure_months'].median()
        
        print(f"   Thresholds: Revenue Rp {self.thresholds['median_revenue']:,.0f}, BW {self.thresholds['median_bandwidth']:.0f} Mbps")
        
        # Matrix 1: Revenue vs Bandwidth
        def classify_bw(row):
            if row['revenue'] >= self.thresholds['median_revenue'] and row['bandwidth_mbps'] >= self.thresholds['median_bandwidth']:
                return '🌟 STAR CLIENT', 'RETENTION'
            elif row['revenue'] >= self.thresholds['median_revenue'] and row['bandwidth_mbps'] < self.thresholds['median_bandwidth']:
                return '🎯 RISK AREA', 'CROSS-SELL'
            elif row['revenue'] < self.thresholds['median_revenue'] and row['bandwidth_mbps'] >= self.thresholds['median_bandwidth']:
                return '🔫 SNIPER ZONE', 'UPSELL'
            else:
                return '🥚 INCUBATOR', 'NURTURE'
        
        results = df.apply(classify_bw, axis=1)
        df['matrix_1_quadrant'] = results.apply(lambda x: x[0])
        df['matrix_1_strategy'] = results.apply(lambda x: x[1])
        
        # Matrix 2: Revenue vs Tenure
        def classify_tenure(row):
            if row['revenue'] >= self.thresholds['median_revenue'] and row['tenure_months'] >= self.thresholds['median_tenure']:
                return '💎 CHAMPION', 'ADVOCACY'
            elif row['revenue'] >= self.thresholds['median_revenue'] and row['tenure_months'] < self.thresholds['median_tenure']:
                return '⚡ HIGH POTENTIAL', 'LOCK-IN'
            elif row['revenue'] < self.thresholds['median_revenue'] and row['tenure_months'] >= self.thresholds['median_tenure']:
                return '🎁 LOYAL', 'GRADUAL UPSELL'
            else:
                return '🌱 NEWBIE', 'EDUCATION'
        
        results2 = df.apply(classify_tenure, axis=1)
        df['matrix_2_quadrant'] = results2.apply(lambda x: x[0])
        df['matrix_2_strategy'] = results2.apply(lambda x: x[1])
        
        self.df_features = df
        
        print("\n   Matrix 1 Distribution:")
        for quad, count in df['matrix_1_quadrant'].value_counts().items():
            print(f"      {quad}: {count} customers ({count/len(df)*100:.1f}%)")
        
        return df
    
    def train_models(self):
        """Train ML models using scikit-learn only"""
        print("\n🎯 Training ML models (scikit-learn)...")
        df = self.df_features.copy()
        
        # Prepare features
        feature_cols = ['revenue', 'bandwidth_mbps', 'tenure_months', 'revenue_per_mbps',
                       'revenue_growth', 'value_score', 'is_high_value', 'is_high_bandwidth']
        encoded_cols = [c for c in df.columns if c.endswith('_encoded')]
        feature_cols.extend(encoded_cols)
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Targets
        y_upsell = (df['matrix_1_quadrant'] == '🔫 SNIPER ZONE').astype(int)
        y_crosssell = (df['matrix_1_quadrant'] == '🎯 RISK AREA').astype(int)
        
        # Split data
        X_train, X_test, y_up_train, y_up_test = train_test_split(
            X_scaled, y_upsell, test_size=0.2, random_state=42, stratify=y_upsell)
        
        _, _, y_cs_train, y_cs_test = train_test_split(
            X_scaled, y_crosssell, test_size=0.2, random_state=42, stratify=y_crosssell)
        
        # 1. Upsell Model (GradientBoostingClassifier)
        print("\n   🚀 Training GradientBoosting (Upsell)...")
        self.upsell_model = GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        )
        self.upsell_model.fit(X_train, y_up_train)
        
        y_up_pred = self.upsell_model.predict(X_test)
        y_up_prob = self.upsell_model.predict_proba(X_test)[:, 1]
        
        self.metrics['upsell'] = {
            'accuracy': self.upsell_model.score(X_test, y_up_test),
            'roc_auc': roc_auc_score(y_up_test, y_up_prob)
        }
        
        print(f"      ✅ Accuracy: {self.metrics['upsell']['accuracy']:.1%}")
        print(f"      ✅ ROC-AUC: {self.metrics['upsell']['roc_auc']:.3f}")
        
        # 2. Cross-sell Model (Random Forest)
        print("\n   🌲 Training Random Forest (Cross-sell)...")
        self.crosssell_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        self.crosssell_model.fit(X_train, y_cs_train)
        
        y_cs_pred = self.crosssell_model.predict(X_test)
        y_cs_prob = self.crosssell_model.predict_proba(X_test)[:, 1]
        
        self.metrics['crosssell'] = {
            'accuracy': self.crosssell_model.score(X_test, y_cs_test),
            'roc_auc': roc_auc_score(y_cs_test, y_cs_prob)
        }
        
        print(f"      ✅ Accuracy: {self.metrics['crosssell']['accuracy']:.1%}")
        print(f"      ✅ ROC-AUC: {self.metrics['crosssell']['roc_auc']:.3f}")
        
        # 3. CLV Model
        print("\n   💰 Training CLV Model...")
        y_clv = df['revenue']
        X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_clv, test_size=0.2, random_state=42)
        
        self.clv_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
        )
        self.clv_model.fit(X_tr, y_tr)
        y_clv_pred = self.clv_model.predict(X_te)
        
        self.metrics['clv'] = {
            'mae': np.mean(np.abs(y_te - y_clv_pred)),
            'mape': np.mean(np.abs((y_te - y_clv_pred) / (y_te + 1))) * 100
        }
        
        print(f"      ✅ MAE: Rp {self.metrics['clv']['mae']:,.0f}, MAPE: {self.metrics['clv']['mape']:.2f}%")
        print("\n✅ All models trained!")
        return self.metrics
    
    def generate_predictions(self):
        """Generate predictions for all customers"""
        print("\n🔮 Generating predictions...")
        df = self.df_features.copy()
        
        feature_cols = ['revenue', 'bandwidth_mbps', 'tenure_months', 'revenue_per_mbps',
                       'revenue_growth', 'value_score', 'is_high_value', 'is_high_bandwidth']
        encoded_cols = [c for c in df.columns if c.endswith('_encoded')]
        feature_cols.extend(encoded_cols)
        available_features = [c for c in feature_cols if c in df.columns]
        
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predictions
        df['upsell_propensity'] = self.upsell_model.predict_proba(X_scaled)[:, 1]
        df['crosssell_propensity'] = self.crosssell_model.predict_proba(X_scaled)[:, 1]
        df['predicted_clv_12m'] = self.clv_model.predict(X_scaled)
        
        # Priority buckets
        df['upsell_priority'] = pd.cut(df['upsell_propensity'], bins=[0, 0.3, 0.6, 1.0], labels=['Low', 'Medium', 'High'])
        df['crosssell_priority'] = pd.cut(df['crosssell_propensity'], bins=[0, 0.3, 0.6, 1.0], labels=['Low', 'Medium', 'High'])
        
        # Revenue potential
        df['upsell_potential'] = np.where(df['upsell_propensity'] > 0.5, df['predicted_clv_12m'] * 0.3, 0)
        df['crosssell_potential'] = np.where(df['crosssell_propensity'] > 0.5, df['predicted_clv_12m'] * 0.25, 0)
        
        self.df_final = df
        
        print(f"\n   High Upsell Propensity: {len(df[df['upsell_propensity'] > 0.7])} customers")
        print(f"   High Cross-sell Propensity: {len(df[df['crosssell_propensity'] > 0.7])} customers")
        print(f"   Total Upsell Potential: Rp {df['upsell_potential'].sum():,.0f}")
        print(f"   Total Cross-sell Potential: Rp {df['crosssell_potential'].sum():,.0f}")
        
        return df
    
    def generate_excel_reports(self, output_dir='reports'):
        """Generate Excel reports"""
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n📑 Generating reports in '{output_dir}/'...")
        
        df = self.df_final.copy()
        
        cols = ['customer_name', 'revenue', 'bandwidth_mbps', 'tenure_months',
                'matrix_1_quadrant', 'matrix_1_strategy', 'matrix_2_quadrant', 'matrix_2_strategy',
                'upsell_propensity', 'upsell_priority', 'upsell_potential',
                'crosssell_propensity', 'crosssell_priority', 'crosssell_potential',
                'predicted_clv_12m', 'value_score']
        cols = [c for c in cols if c in df.columns]
        
        # Master report
        master = df[cols].sort_values('upsell_propensity', ascending=False)
        master.to_excel(f'{output_dir}/CVO_Master_Report.xlsx', index=False)
        print(f"   ✅ CVO_Master_Report.xlsx ({len(master)} customers)")
        
        # Upsell opportunities
        upsell = df[df['upsell_propensity'] > 0.5][cols].sort_values('upsell_potential', ascending=False)
        upsell.to_excel(f'{output_dir}/CVO_Upsell_Opportunities.xlsx', index=False)
        print(f"   ✅ CVO_Upsell_Opportunities.xlsx ({len(upsell)} targets)")
        
        # Cross-sell opportunities
        crosssell = df[df['crosssell_propensity'] > 0.5][cols].sort_values('crosssell_potential', ascending=False)
        crosssell.to_excel(f'{output_dir}/CVO_Crosssell_Opportunities.xlsx', index=False)
        print(f"   ✅ CVO_Crosssell_Opportunities.xlsx ({len(crosssell)} targets)")
        
        # Strategic matrices
        with pd.ExcelWriter(f'{output_dir}/CVO_Strategic_Matrices.xlsx') as writer:
            for quad in df['matrix_1_quadrant'].unique():
                df[df['matrix_1_quadrant'] == quad][cols].to_excel(writer, sheet_name=quad[:31], index=False)
        print(f"   ✅ CVO_Strategic_Matrices.xlsx")
        
        # Top 50
        df['total_potential'] = df['upsell_potential'] + df['crosssell_potential']
        top50 = df.nlargest(50, 'total_potential')[cols + ['total_potential']]
        top50.to_excel(f'{output_dir}/CVO_Top_50_Opportunities.xlsx', index=False)
        print(f"   ✅ CVO_Top_50_Opportunities.xlsx")
        
        return output_dir
    
    def generate_executive_summary(self, output_dir='reports'):
        """Generate executive summary"""
        df = self.df_final.copy()
        
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║        CUSTOMER VALUE OPTIMIZER (CVO) - EXECUTIVE SUMMARY      ║
║                     PLN Icon+ Division                         ║
╚════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Marketing Planning & Analysis Division

KEY METRICS
-----------
Total Active Customers: {len(df):,}
Total Current Revenue: Rp {df['revenue'].sum():,.0f}
Avg Revenue per Customer: Rp {df['revenue'].mean():,.0f}
Avg CLV (12M): Rp {df['predicted_clv_12m'].mean():,.0f}

STRATEGIC MATRIX DISTRIBUTION
-----------------------------
"""
        for quad, count in df['matrix_1_quadrant'].value_counts().items():
            pct = count / len(df) * 100
            rev = df[df['matrix_1_quadrant'] == quad]['revenue'].sum()
            summary += f"{quad}: {count} customers ({pct:.1f}%) - Rp {rev:,.0f} revenue\n"
        
        summary += f"""
ML PREDICTIONS
--------------
High Upsell Propensity (>70%): {len(df[df['upsell_propensity'] > 0.7])} customers
  Potential: Rp {df[df['upsell_propensity'] > 0.7]['upsell_potential'].sum():,.0f}

High Cross-sell Propensity (>70%): {len(df[df['crosssell_propensity'] > 0.7])} customers
  Potential: Rp {df[df['crosssell_propensity'] > 0.7]['crosssell_potential'].sum():,.0f}

Total Opportunity: Rp {df['upsell_potential'].sum() + df['crosssell_potential'].sum():,.0f}

MODEL PERFORMANCE
-----------------
Upsell Model (GradientBoosting): {self.metrics['upsell']['accuracy']:.1%} accuracy, {self.metrics['upsell']['roc_auc']:.3f} ROC-AUC
Cross-sell Model (Random Forest): {self.metrics['crosssell']['accuracy']:.1%} accuracy, {self.metrics['crosssell']['roc_auc']:.3f} ROC-AUC
CLV Model: Rp {self.metrics['clv']['mae']:,.0f} MAE

TOP 5 UPSELL OPPORTUNITIES
--------------------------
"""
        top5 = df.nlargest(5, 'upsell_potential')[['customer_name', 'upsell_propensity', 'upsell_potential']]
        for _, row in top5.iterrows():
            summary += f"{row['customer_name'][:40]:40s} | {row['upsell_propensity']:.1%} | Rp {row['upsell_potential']:,.0f}\n"
        
        summary += f"""
ROI PROJECTIONS
---------------
Conservative (20%): Rp {(df['upsell_potential'].sum() + df['crosssell_potential'].sum()) * 0.20:,.0f}
Optimistic (40%): Rp {(df['upsell_potential'].sum() + df['crosssell_potential'].sum()) * 0.40:,.0f}

Generated by CVO v2.1 (Scikit-learn Edition)
"""
        
        with open(f'{output_dir}/Executive_Summary.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n📊 Executive Summary: {output_dir}/Executive_Summary.txt")
        print(summary)
        return summary
    
    def generate_json_for_dashboard(self, output_dir='dashboard_data'):
        """Generate JSON data for dashboard"""
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n📊 Generating dashboard data...")
        
        df = self.df_final.copy()
        
        # Summary metrics
        summary_metrics = {
            'total_customers': len(df),
            'total_revenue': float(df['revenue'].sum()),
            'avg_revenue': float(df['revenue'].mean()),
            'high_upsell_count': int((df['upsell_propensity'] > 0.7).sum()),
            'high_crosssell_count': int((df['crosssell_propensity'] > 0.7).sum()),
            'total_opportunity': float(df['upsell_potential'].sum() + df['crosssell_potential'].sum()),
            'model_accuracy_upsell': float(self.metrics['upsell']['accuracy']),
            'model_accuracy_crosssell': float(self.metrics['crosssell']['accuracy'])
        }
        
        with open(f'{output_dir}/summary_metrics.json', 'w') as f:
            json.dump(summary_metrics, f, indent=2)
        
        # Matrix distributions
        matrix1_dist = []
        for quadrant in df['matrix_1_quadrant'].unique():
            quadrant_df = df[df['matrix_1_quadrant'] == quadrant]
            matrix1_dist.append({
                'quadrant': quadrant,
                'count': len(quadrant_df),
                'percentage': float(len(quadrant_df) / len(df) * 100),
                'total_revenue': float(quadrant_df['revenue'].sum())
            })
        
        with open(f'{output_dir}/matrix1_distribution.json', 'w') as f:
            json.dump(matrix1_dist, f, indent=2)
        
        # Top opportunities
        top_upsell = df.nlargest(20, 'upsell_potential')[['customer_name', 'revenue', 'upsell_propensity', 'upsell_potential']].to_dict('records')
        top_crosssell = df.nlargest(20, 'crosssell_potential')[['customer_name', 'revenue', 'crosssell_propensity', 'crosssell_potential']].to_dict('records')
        
        with open(f'{output_dir}/top_opportunities.json', 'w') as f:
            json.dump({'top_upsell': top_upsell, 'top_crosssell': top_crosssell}, f, indent=2)
        
        # Scatter data (sample for performance)
        scatter_sample = df[['customer_name', 'revenue', 'bandwidth_mbps', 'upsell_propensity', 'crosssell_propensity', 'matrix_1_quadrant']].sample(min(1000, len(df))).to_dict('records')
        
        with open(f'{output_dir}/customer_scatter_data.json', 'w') as f:
            json.dump(scatter_sample, f, indent=2)
        
        print("   ✅ Dashboard data generated")
        return output_dir
    
    def run_pipeline(self):
        """Run complete pipeline"""
        print("\n" + "="*70)
        print("CUSTOMER VALUE OPTIMIZER (CVO) v2.1")
        print("PLN Icon+ - Scikit-learn Edition (No XGBoost Required)")
        print("="*70)
        
        if not self.load_data():
            return False
        
        self.clean_and_standardize()
        self.engineer_features()
        self.create_strategic_matrices()
        self.train_models()
        self.generate_predictions()
        self.generate_excel_reports()
        self.generate_executive_summary()
        self.generate_json_for_dashboard()
        
        print("\n" + "="*70)
        print("✅ CVO PIPELINE COMPLETED!")
        print("="*70)
        print("\n📁 Generated:")
        print("   - reports/CVO_Master_Report.xlsx")
        print("   - reports/CVO_Upsell_Opportunities.xlsx")
        print("   - reports/CVO_Crosssell_Opportunities.xlsx")
        print("   - reports/CVO_Strategic_Matrices.xlsx")
        print("   - reports/CVO_Top_50_Opportunities.xlsx")
        print("   - reports/Executive_Summary.txt")
        print("   - dashboard_data/*.json")
        print("\n✨ Ready for business!")
        
        return True


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n🎯 CVO v2.1 - Customer Value Optimizer")
    print("Using scikit-learn (no XGBoost required)\n")
    
    # Auto-detect data file
    full_data = "Data Penuh Pelanggan Aktif.xlsx"
    sample_data = "Data Sampel Machine Learning.xlsx"
    
    if os.path.exists(full_data):
        data_file = full_data
        print(f"📊 Using FULL DATA: {data_file}")
    elif os.path.exists(sample_data):
        data_file = sample_data
        print(f"📊 Using SAMPLE DATA: {data_file}")
    else:
        import glob
        files = glob.glob("*.xlsx") + glob.glob("*.csv")
        if files:
            data_file = files[0]
            print(f"📊 Using: {data_file}")
        else:
            print("❌ No data files found!")
            exit(1)
    
    cvo = CustomerValueOptimizer(data_file)
    success = cvo.run_pipeline()
    
    if success:
        print("\n🎉 Success! Check the 'reports/' folder.")
    else:
        print("\n❌ Failed. Check error messages above.")
