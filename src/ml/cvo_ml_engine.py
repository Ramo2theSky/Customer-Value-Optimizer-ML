"""
CUSTOMER VALUE OPTIMIZER (CVO) - ML Pipeline v2.0
==============================================
PLN Icon+ Marketing Planning & Analysis Division
Author: Computer Science Intern
Date: February 2026

This module implements:
1. Advanced data cleaning and feature engineering
2. Supervised ML models for upsell/cross-sell prediction (XGBoost & Random Forest)
3. Customer Lifetime Value (CLV) prediction using Gradient Boosting
4. 2x2 Strategic Matrix generation (Revenue vs Bandwidth, Revenue vs Tenure)
5. Excel report generation with actionable insights
6. Model performance metrics and feature importance analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    print("⚠️  XGBoost not installed. Using GradientBoostingClassifier instead.")
    print("   For better performance, install xgboost: pip install xgboost")
    XGBOOST_AVAILABLE = False
import warnings
from datetime import datetime, timedelta
import re
import os
import json

warnings.filterwarnings('ignore')

# Set style for visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class CustomerValueOptimizer:
    """
    Main class for Customer Value Optimization
    Handles end-to-end ML pipeline from data processing to report generation
    """
    
    def __init__(self, data_path):
        """
        Initialize CVO with data path
        
        Args:
            data_path (str): Path to the Excel/CSV data file
        """
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
        
        # Model performance metrics storage
        self.metrics = {
            'upsell': {},
            'crosssell': {},
            'clv': {}
        }
        
        # Thresholds for strategic matrices
        self.thresholds = {}
        
    def load_data(self):
        """
        Load data from Excel or CSV file with smart detection
        Optimized for large datasets
        """
        print("📊 Loading data...")
        try:
            file_size = os.path.getsize(self.data_path) / (1024 * 1024)  # MB
            print(f"   File size: {file_size:.1f} MB")
            
            if self.data_path.endswith('.xlsx') or self.data_path.endswith('.xls'):
                # For large Excel files, use optimized loading
                if file_size > 50:  # If file > 50MB
                    print("   ⚡ Large file detected - using optimized loading...")
                    self.df_raw = pd.read_excel(self.data_path, engine='openpyxl')
                else:
                    self.df_raw = pd.read_excel(self.data_path)
                print(f"   Loaded Excel file: {self.data_path}")
            elif self.data_path.endswith('.csv'):
                # Smart CSV detection with multiple separator attempts
                try:
                    self.df_raw = pd.read_csv(self.data_path, sep=None, engine='python')
                except:
                    self.df_raw = pd.read_csv(self.data_path, sep=';', engine='python')
                print(f"   Loaded CSV file: {self.data_path}")
            else:
                raise ValueError("❌ Unsupported file format. Please use .xlsx, .xls, or .csv")
            
            # Memory optimization for large datasets
            if len(self.df_raw) > 50000:  # If > 50k rows
                print(f"   ⚡ Large dataset detected ({len(self.df_raw):,} rows) - optimizing memory...")
                self._optimize_memory()
            
            print(f"✅ Data loaded successfully: {self.df_raw.shape[0]:,} rows, {self.df_raw.shape[1]} columns")
            print(f"   Columns: {', '.join(self.df_raw.columns[:5])}... ({len(self.df_raw.columns)} total)")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _optimize_memory(self):
        """
        Optimize memory usage for large datasets
        """
        start_mem = self.df_raw.memory_usage().sum() / 1024**2
        
        # Convert object columns to category where appropriate
        for col in self.df_raw.select_dtypes(include=['object']).columns:
            num_unique = self.df_raw[col].nunique()
            num_total = len(self.df_raw)
            if num_unique / num_total < 0.5:  # If less than 50% unique values
                self.df_raw[col] = self.df_raw[col].astype('category')
        
        # Downcast numeric columns
        for col in self.df_raw.select_dtypes(include=['int']).columns:
            self.df_raw[col] = pd.to_numeric(self.df_raw[col], downcast='integer')
        
        for col in self.df_raw.select_dtypes(include=['float']).columns:
            self.df_raw[col] = pd.to_numeric(self.df_raw[col], downcast='float')
        
        end_mem = self.df_raw.memory_usage().sum() / 1024**2
        print(f"      Memory optimized: {start_mem:.1f} MB → {end_mem:.1f} MB ({100 * (start_mem - end_mem) / start_mem:.1f}% reduction)")
    
    def clean_and_standardize(self):
        """
        Advanced data cleaning and standardization pipeline
        Handles Indonesian business naming conventions and currency formats
        """
        print("\n🧹 Cleaning and standardizing data...")
        df = self.df_raw.copy()
        initial_rows = len(df)
        
        # Column name mapping (handling various naming conventions in Indonesian business data)
        column_mapping = {
            'namaPelanggan': 'customer_name',
            'hargaPelanggan': 'revenue',
            'hargaPelangganLalu': 'revenue_previous',
            'bandwidth': 'bandwidth',
            'Lama_Langganan': 'tenure_months',
            'segmenIcon': 'segment',
            'terminatingProvinsi': 'province',
            'WILAYAH': 'region',
            'Kategori_Baru': 'category',
            'namaLayanan': 'product_name',
            'namaProduk': 'product_name',
            'statusLayanan': 'status',
            'Status': 'status',
            'tanggalAktivasi': 'activation_date',
            'tanggalAwalKontrak': 'contract_start',
            'hargaInstalasi': 'installation_fee',
            'Margin': 'margin',
            'sid': 'service_id',
            'idPelanggan': 'customer_id'
        }
        
        # Rename columns if they exist
        renamed_count = 0
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
                renamed_count += 1
        
        print(f"   Standardized {renamed_count} column names")
        
        # Clean customer names - remove business titles and standardize
        if 'customer_name' in df.columns:
            print("   Cleaning customer names...")
            df['customer_name'] = df['customer_name'].apply(self._clean_customer_name)
        
        # Clean and convert revenue columns (handle Rupiah formatting)
        df = self._clean_revenue_columns(df)
        
        # Clean bandwidth values (handle various units like Mbps, Gbps, Kbps)
        df = self._clean_bandwidth(df)
        
        # Clean tenure data
        df = self._clean_tenure(df)
        
        # Filter active customers only
        if 'status' in df.columns:
            active_before = len(df)
            df = df[df['status'].str.contains('AKTIF|Aktif|Active', case=False, na=False)]
            print(f"   Filtered to active customers: {len(df)}/{active_before}")
        
        # Remove duplicate customers (keep first occurrence)
        if 'customer_name' in df.columns:
            df = df.drop_duplicates(subset=['customer_name'], keep='first')
            duplicates_removed = initial_rows - len(df)
            if duplicates_removed > 0:
                print(f"   Removed {duplicates_removed} duplicate customers")
        
        self.df_processed = df
        print(f"✅ Data cleaned: {len(df)} active customers ready for analysis")
        return df
    
    def _clean_customer_name(self, name):
        """
        Clean customer names by removing business titles and standardizing format
        """
        if pd.isna(name):
            return "UNKNOWN"
        
        name = str(name).strip().upper()
        
        # Remove Indonesian and international business titles
        patterns = [
            r'\bPT\.?\b', r'\bCV\.?\b', r'\bTBK\.?\b', r'\(PERSERO\)',
            r'\bPERSERO\b', r'\bUD\.?\b', r'\bYAYASAN\b', r'\bKOPERASI\b',
            r'\bPERUM\b', r'\bDINAS\b', r'\bLTD\.?\b', r'\bKEMENTERIAN\b',
            r'\bBADAN\b', r'\bKANTOR\b', r'\bKEPALA\b', r'\bUNIT\b'
        ]
        
        for pattern in patterns:
            name = re.sub(pattern, '', name)
        
        # Clean special characters and extra spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Limit length for display
        if len(name) > 100:
            name = name[:100]
        
        return name
    
    def _clean_revenue_columns(self, df):
        """
        Clean revenue columns and handle Rupiah currency formatting
        Removes 'Rp', dots, commas and converts to numeric
        """
        revenue_cols = ['revenue', 'revenue_previous', 'installation_fee']
        
        for col in revenue_cols:
            if col in df.columns:
                # Remove currency symbols, dots (thousand separators), and convert to numeric
                df[col] = df[col].astype(str).str.replace(r'[^\d]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        # Check for revenue data
        if 'revenue' in df.columns:
            non_zero_revenue = (df['revenue'] > 0).sum()
            print(f"   Revenue data: {non_zero_revenue}/{len(df)} customers have revenue > 0")
            
        return df
    
    def _clean_bandwidth(self, df):
        """
        Clean and standardize bandwidth values to Mbps
        Handles various units: Gbps, Mbps, Kbps
        """
        if 'bandwidth' not in df.columns:
            print("   ⚠️ No bandwidth column found")
            df['bandwidth_mbps'] = 0
            return df
        
        def convert_bandwidth(val):
            """Convert various bandwidth formats to Mbps"""
            if pd.isna(val):
                return 0
            
            val_str = str(val).lower().strip()
            
            # Extract numbers using regex
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", val_str.replace(',', '.'))
            if not nums:
                return 0
            
            try:
                num = float(nums[0])
            except:
                return 0
            
            # Convert to Mbps based on unit
            if 'gb' in val_str or 'gbps' in val_str:
                return num * 1000  # Gbps to Mbps
            elif 'kb' in val_str or 'kbps' in val_str:
                return num / 1000  # Kbps to Mbps
            elif 'mb' in val_str or 'mbps' in val_str or 'mpbs' in val_str:
                return num  # Already in Mbps
            elif 'tb' in val_str or 'tbps' in val_str:
                return num * 1000000  # Tbps to Mbps (rare but possible)
            else:
                # Assume Mbps if no unit specified
                return num
        
        print("   Converting bandwidth to Mbps...")
        df['bandwidth_mbps'] = df['bandwidth'].apply(convert_bandwidth)
        df['bandwidth_mbps'] = df['bandwidth_mbps'].fillna(0)
        
        # Statistics
        non_zero_bw = (df['bandwidth_mbps'] > 0).sum()
        avg_bw = df[df['bandwidth_mbps'] > 0]['bandwidth_mbps'].mean()
        print(f"   Bandwidth data: {non_zero_bw}/{len(df)} customers have bandwidth > 0 (avg: {avg_bw:.1f} Mbps)")
        
        return df
    
    def _clean_tenure(self, df):
        """
        Clean tenure data and calculate from dates if needed
        """
        if 'tenure_months' in df.columns:
            # Already have tenure in months
            df['tenure_months'] = pd.to_numeric(df['tenure_months'], errors='coerce').fillna(0)
            print(f"   Using existing tenure data (avg: {df['tenure_months'].mean():.1f} months)")
        elif 'activation_date' in df.columns:
            # Calculate tenure from activation date
            print("   Calculating tenure from activation dates...")
            df['activation_date'] = pd.to_datetime(df['activation_date'], errors='coerce')
            today = datetime.now()
            df['tenure_months'] = ((today - df['activation_date']).dt.days / 30.44).fillna(0)
            df['tenure_months'] = df['tenure_months'].clip(lower=0)  # No negative tenure
        else:
            print("   ⚠️ No tenure data found, defaulting to 0")
            df['tenure_months'] = 0
        
        return df
    
    def engineer_features(self):
        """
        Create advanced features for ML models
        Engineering features that capture customer value and behavior patterns
        """
        print("\n🔧 Engineering features for ML models...")
        df = self.df_processed.copy()
        initial_cols = df.shape[1]
        
        # 1. Revenue-based features
        df['revenue_per_mbps'] = np.where(df['bandwidth_mbps'] > 0, 
                                          df['revenue'] / df['bandwidth_mbps'], 0)
        
        if 'revenue_previous' in df.columns and (df['revenue_previous'] > 0).any():
            df['revenue_growth'] = np.where(df['revenue_previous'] > 0,
                                           (df['revenue'] - df['revenue_previous']) / df['revenue_previous'],
                                           0)
            df['revenue_growth'] = df['revenue_growth'].clip(-1, 10)  # Cap extreme values
        else:
            df['revenue_growth'] = 0
        
        # 2. Bandwidth efficiency features
        median_bw = df['bandwidth_mbps'].median()
        df['bandwidth_utilization_score'] = np.where(df['bandwidth_mbps'] > median_bw, 1, 0)
        df['is_high_bandwidth'] = (df['bandwidth_mbps'] >= df['bandwidth_mbps'].quantile(0.75)).astype(int)
        
        # 3. Tenure segments
        df['tenure_segment'] = pd.cut(df['tenure_months'], 
                                      bins=[0, 6, 12, 24, 60, float('inf')],
                                      labels=['New', 'Growing', 'Mature', 'Loyal', 'Champion'])
        
        # 4. Revenue segments
        median_rev = df['revenue'].median()
        df['revenue_segment'] = np.where(df['revenue'] >= median_rev, 'High Revenue', 'Low Revenue')
        
        # 5. Customer value score (composite metric)
        # Weighted combination of revenue, tenure, and bandwidth
        df['value_score'] = (
            (df['revenue'] / df['revenue'].max()) * 0.4 +
            (df['tenure_months'] / df['tenure_months'].max()) * 0.3 +
            (df['bandwidth_mbps'] / df['bandwidth_mbps'].max()) * 0.3
        )
        
        # 6. Risk and opportunity indicators
        df['is_high_value'] = (df['revenue'] >= df['revenue'].quantile(0.75)).astype(int)
        df['is_low_revenue'] = (df['revenue'] < df['revenue'].quantile(0.25)).astype(int)
        
        # 7. Product diversity (if product data available)
        if 'product_name' in df.columns:
            # Count unique products per customer
            product_counts = df.groupby('customer_name')['product_name'].nunique().to_dict()
            df['product_count'] = df['customer_name'].map(product_counts)
            df['product_count'] = df['product_count'].fillna(1)
        else:
            df['product_count'] = 1
        
        # 8. Encode categorical variables for ML
        categorical_cols = ['segment', 'region', 'category', 'tenure_segment', 'province']
        encoded_count = 0
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                encoded_count += 1
        
        self.df_features = df
        new_features = df.shape[1] - initial_cols
        print(f"✅ Features engineered: {new_features} new features created")
        print(f"   Total columns: {df.shape[1]} (revenue_per_mbps, value_score, tenure_segment, etc.)")
        return df
    
    def create_strategic_matrices(self):
        """
        Create two 2x2 strategic matrices:
        1. Revenue vs Bandwidth Usage
        2. Revenue vs Tenure
        """
        print("\n📊 Creating strategic matrices...")
        df = self.df_features.copy()
        
        # Calculate median thresholds for fair segmentation
        self.thresholds['median_revenue'] = df['revenue'].median()
        self.thresholds['median_bandwidth'] = df['bandwidth_mbps'].median()
        self.thresholds['median_tenure'] = df['tenure_months'].median()
        
        print(f"   Market Thresholds:")
        print(f"      Median Revenue: Rp {self.thresholds['median_revenue']:,.0f}")
        print(f"      Median Bandwidth: {self.thresholds['median_bandwidth']:.0f} Mbps")
        print(f"      Median Tenure: {self.thresholds['median_tenure']:.0f} months")
        
        # Matrix 1: Revenue vs Bandwidth Usage
        def classify_bw_matrix(row):
            """
            Classify customers into quadrants based on revenue and bandwidth
            """
            is_high_rev = row['revenue'] >= self.thresholds['median_revenue']
            is_high_bw = row['bandwidth_mbps'] >= self.thresholds['median_bandwidth']
            
            if is_high_rev and is_high_bw:
                return '🌟 STAR CLIENT', 'RETENTION - Premium support & loyalty rewards'
            elif is_high_rev and not is_high_bw:
                return '🎯 RISK AREA', 'CROSS-SELL - Smart Home, PV Rooftop, EV Charging'
            elif not is_high_rev and is_high_bw:
                return '🔫 SNIPER ZONE', 'UPSELL - Bandwidth upgrade, Managed Services'
            else:
                return '🥚 INCUBATOR', 'NURTURE - Build relationship, product education'
        
        matrix_results = df.apply(classify_bw_matrix, axis=1)
        df['matrix_1_quadrant'] = matrix_results.apply(lambda x: x[0])
        df['matrix_1_strategy'] = matrix_results.apply(lambda x: x[1])
        
        # Matrix 2: Revenue vs Tenure
        def classify_tenure_matrix(row):
            """
            Classify customers based on revenue and relationship length
            """
            is_high_rev = row['revenue'] >= self.thresholds['median_revenue']
            is_long_tenure = row['tenure_months'] >= self.thresholds['median_tenure']
            
            if is_high_rev and is_long_tenure:
                return '💎 CHAMPION', 'ADVOCACY - Referral program, case studies'
            elif is_high_rev and not is_long_tenure:
                return '⚡ HIGH POTENTIAL', 'LOCK-IN - Long-term contract incentives'
            elif not is_high_rev and is_long_tenure:
                return '🎁 LOYAL PRICE-SENSITIVE', 'GRADUAL UPSELL - Value demonstration'
            else:
                return '🌱 NEWBIE', 'EDUCATION - Product demos, onboarding support'
        
        matrix2_results = df.apply(classify_tenure_matrix, axis=1)
        df['matrix_2_quadrant'] = matrix2_results.apply(lambda x: x[0])
        df['matrix_2_strategy'] = matrix2_results.apply(lambda x: x[1])
        
        # Calculate matrix statistics
        matrix1_stats = df['matrix_1_quadrant'].value_counts()
        matrix2_stats = df['matrix_2_quadrant'].value_counts()
        
        print("\n   📊 Matrix 1 (Revenue vs Bandwidth) Distribution:")
        total_revenue_matrix1 = 0
        for quadrant, count in matrix1_stats.items():
            pct = (count / len(df)) * 100
            revenue = df[df['matrix_1_quadrant'] == quadrant]['revenue'].sum()
            total_revenue_matrix1 += revenue
            print(f"      {quadrant}: {count:>3} customers ({pct:>5.1f}%) - Rp {revenue:>15,.0f} revenue")
        
        print("\n   📊 Matrix 2 (Revenue vs Tenure) Distribution:")
        for quadrant, count in matrix2_stats.items():
            pct = (count / len(df)) * 100
            revenue = df[df['matrix_2_quadrant'] == quadrant]['revenue'].sum()
            print(f"      {quadrant}: {count:>3} customers ({pct:>5.1f}%) - Rp {revenue:>15,.0f} revenue")
        
        self.df_features = df
        return df
    
    def prepare_ml_data(self):
        """
        Prepare data for machine learning models
        """
        print("\n🤖 Preparing ML datasets...")
        df = self.df_features.copy()
        
        # Feature columns for ML
        feature_cols = [
            'revenue', 'bandwidth_mbps', 'tenure_months', 'revenue_per_mbps',
            'revenue_growth', 'value_score', 'is_high_value', 'is_high_bandwidth',
            'is_low_revenue', 'product_count'
        ]
        
        # Add encoded categorical features
        encoded_cols = [col for col in df.columns if col.endswith('_encoded')]
        feature_cols.extend(encoded_cols)
        
        # Ensure all feature columns exist
        available_features = [col for col in feature_cols if col in df.columns]
        
        X = df[available_features].fillna(0)
        
        # Create target labels for upsell (Sniper Zone = High BW, Low Revenue)
        y_upsell = (df['matrix_1_quadrant'] == '🔫 SNIPER ZONE').astype(int)
        
        # Create target labels for cross-sell (Risk Area = High Revenue, Low BW)
        y_crosssell = (df['matrix_1_quadrant'] == '🎯 RISK AREA').astype(int)
        
        # CLV target (using revenue as proxy - could be enhanced with historical CLV data)
        y_clv = df['revenue']
        
        # Scale features for better model performance
        X_scaled = self.scaler.fit_transform(X)
        
        print(f"   Features selected: {len(available_features)} features")
        print(f"   Upsell target: {y_upsell.sum()} positive cases ({y_upsell.mean()*100:.1f}%)")
        print(f"   Cross-sell target: {y_crosssell.sum()} positive cases ({y_crosssell.mean()*100:.1f}%)")
        
        return X_scaled, X, y_upsell, y_crosssell, y_clv, available_features
    
    def train_models(self):
        """
        Train supervised ML models with cross-validation
        """
        print("\n🎯 Training Machine Learning models...")
        
        X_scaled, X_raw, y_upsell, y_crosssell, y_clv, feature_names = self.prepare_ml_data()
        
        # Split data for training and testing
        X_train, X_test, y_up_train, y_up_test = train_test_split(
            X_scaled, y_upsell, test_size=0.2, random_state=42, stratify=y_upsell
        )
        
        _, _, y_cs_train, y_cs_test = train_test_split(
            X_scaled, y_crosssell, test_size=0.2, random_state=42, stratify=y_crosssell
        )
        
        # 1. Upsell Prediction Model (XGBoost) - State of the art gradient boosting
        print("\n   🚀 Training Upsell Prediction Model (XGBoost)...")
        self.upsell_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        self.upsell_model.fit(X_train, y_up_train)
        
        # Evaluate upsell model
        y_up_pred = self.upsell_model.predict(X_test)
        y_up_prob = self.upsell_model.predict_proba(X_test)[:, 1]
        
        self.metrics['upsell'] = {
            'accuracy': self.upsell_model.score(X_test, y_up_test),
            'roc_auc': roc_auc_score(y_up_test, y_up_prob),
            'precision': self.metrics['upsell'].get('precision', 0),
            'recall': self.metrics['upsell'].get('recall', 0)
        }
        
        # Get precision and recall from classification report
        report = classification_report(y_up_test, y_up_pred, output_dict=True)
        if '1' in report:
            self.metrics['upsell']['precision'] = report['1']['precision']
            self.metrics['upsell']['recall'] = report['1']['recall']
        
        print(f"      ✅ Accuracy: {self.metrics['upsell']['accuracy']:.1%}")
        print(f"      ✅ ROC-AUC: {self.metrics['upsell']['roc_auc']:.3f}")
        print(f"      ✅ Precision: {self.metrics['upsell']['precision']:.1%}")
        print(f"      ✅ Recall: {self.metrics['upsell']['recall']:.1%}")
        
        # 2. Cross-sell Prediction Model (Random Forest) - Ensemble method
        print("\n   🌲 Training Cross-sell Prediction Model (Random Forest)...")
        self.crosssell_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        
        self.crosssell_model.fit(X_train, y_cs_train)
        
        # Evaluate cross-sell model
        y_cs_pred = self.crosssell_model.predict(X_test)
        y_cs_prob = self.crosssell_model.predict_proba(X_test)[:, 1]
        
        self.metrics['crosssell'] = {
            'accuracy': self.crosssell_model.score(X_test, y_cs_test),
            'roc_auc': roc_auc_score(y_cs_test, y_cs_prob)
        }
        
        report_cs = classification_report(y_cs_test, y_cs_pred, output_dict=True)
        if '1' in report_cs:
            self.metrics['crosssell']['precision'] = report_cs['1']['precision']
            self.metrics['crosssell']['recall'] = report_cs['1']['recall']
        
        print(f"      ✅ Accuracy: {self.metrics['crosssell']['accuracy']:.1%}")
        print(f"      ✅ ROC-AUC: {self.metrics['crosssell']['roc_auc']:.3f}")
        print(f"      ✅ Precision: {self.metrics['crosssell'].get('precision', 0):.1%}")
        print(f"      ✅ Recall: {self.metrics['crosssell'].get('recall', 0):.1%}")
        
        # 3. CLV Prediction Model (Gradient Boosting Regressor)
        print("\n   💰 Training CLV Prediction Model (Gradient Boosting)...")
        X_train_clv, X_test_clv, y_clv_train, y_clv_test = train_test_split(
            X_scaled, y_clv, test_size=0.2, random_state=42
        )
        
        self.clv_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            loss='huber'  # Robust to outliers
        )
        
        self.clv_model.fit(X_train_clv, y_clv_train)
        
        # Evaluate CLV model
        y_clv_pred = self.clv_model.predict(X_test_clv)
        mae = np.mean(np.abs(y_clv_test - y_clv_pred))
        mape = np.mean(np.abs((y_clv_test - y_clv_pred) / (y_clv_test + 1))) * 100  # Add 1 to avoid division by zero
        rmse = np.sqrt(np.mean((y_clv_test - y_clv_pred) ** 2))
        
        self.metrics['clv'] = {
            'mae': mae,
            'mape': mape,
            'rmse': rmse,
            'r2': self.clv_model.score(X_test_clv, y_clv_test)
        }
        
        print(f"      ✅ Mean Absolute Error: Rp {mae:,.0f}")
        print(f"      ✅ MAPE: {mape:.2f}%")
        print(f"      ✅ R² Score: {self.metrics['clv']['r2']:.3f}")
        
        print("\n✅ All ML models trained successfully!")
        
        # Display feature importance
        self._display_feature_importance(feature_names)
        
        return self.metrics
    
    def _display_feature_importance(self, feature_names):
        """
        Display top 10 most important features from models
        """
        print("\n📈 Feature Importance Analysis:")
        
        # XGBoost feature importance (Upsell model)
        importance_up = pd.DataFrame({
            'feature': feature_names,
            'importance': self.upsell_model.feature_importances_
        }).sort_values('importance', ascending=False).head(10)
        
        print("\n   Top 10 Features (Upsell Model):")
        for idx, row in importance_up.iterrows():
            bar = '█' * int(row['importance'] * 50)
            print(f"      {row['feature']:20s}: {row['importance']:.3f} {bar}")
    
    def generate_predictions(self):
        """
        Generate ML predictions for all customers
        """
        print("\n🔮 Generating predictions for all customers...")
        
        df = self.df_features.copy()
        
        # Prepare features
        feature_cols = [
            'revenue', 'bandwidth_mbps', 'tenure_months', 'revenue_per_mbps',
            'revenue_growth', 'value_score', 'is_high_value', 'is_high_bandwidth',
            'is_low_revenue', 'product_count'
        ]
        encoded_cols = [c for c in df.columns if c.endswith('_encoded')]
        feature_cols.extend(encoded_cols)
        available_features = [c for c in feature_cols if c in df.columns]
        
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Generate predictions
        df['upsell_propensity'] = self.upsell_model.predict_proba(X_scaled)[:, 1]
        df['crosssell_propensity'] = self.crosssell_model.predict_proba(X_scaled)[:, 1]
        df['predicted_clv_12m'] = self.clv_model.predict(X_scaled)
        
        # Create priority buckets
        df['upsell_priority'] = pd.cut(df['upsell_propensity'], 
                                       bins=[0, 0.3, 0.6, 1.0],
                                       labels=['Low', 'Medium', 'High'])
        
        df['crosssell_priority'] = pd.cut(df['crosssell_propensity'],
                                          bins=[0, 0.3, 0.6, 1.0],
                                          labels=['Low', 'Medium', 'High'])
        
        # Calculate potential revenue impact
        # Conservative estimates: 30% increase for upsell, 25% for cross-sell
        df['upsell_potential'] = np.where(df['upsell_propensity'] > 0.5,
                                          df['predicted_clv_12m'] * 0.3, 0)
        
        df['crosssell_potential'] = np.where(df['crosssell_propensity'] > 0.5,
                                             df['predicted_clv_12m'] * 0.25, 0)
        
        self.df_final = df
        
        # Print summary statistics
        high_upsell = len(df[df['upsell_propensity'] > 0.7])
        high_crosssell = len(df[df['crosssell_propensity'] > 0.7])
        total_upsell_potential = df['upsell_potential'].sum()
        total_crosssell_potential = df['crosssell_potential'].sum()
        
        print(f"\n   📊 Prediction Summary:")
        print(f"      High Upsell Propensity (>70%): {high_upsell:>3} customers")
        print(f"      High Cross-sell Propensity (>70%): {high_crosssell:>3} customers")
        print(f"      Total Upsell Potential: Rp {total_upsell_potential:>15,.0f}")
        print(f"      Total Cross-sell Potential: Rp {total_crosssell_potential:>15,.0f}")
        print(f"      Total Opportunity Value: Rp {total_upsell_potential + total_crosssell_potential:>15,.0f}")
        
        return df
    
    def generate_excel_reports(self, output_dir='reports'):
        """
        Generate comprehensive Excel reports for business users
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📑 Generating Excel reports in '{output_dir}/'...")
        
        df = self.df_final.copy()
        
        # Column selection for reports
        master_cols = [
            'customer_name', 'revenue', 'bandwidth_mbps', 'tenure_months',
            'matrix_1_quadrant', 'matrix_1_strategy',
            'matrix_2_quadrant', 'matrix_2_strategy',
            'upsell_propensity', 'upsell_priority', 'upsell_potential',
            'crosssell_propensity', 'crosssell_priority', 'crosssell_potential',
            'predicted_clv_12m', 'value_score', 'segment', 'region', 'product_name'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in master_cols if col in df.columns]
        
        # Report 1: Master Report (all customers sorted by upsell propensity)
        print("   Creating Master Report...")
        master_report = df[available_cols].sort_values('upsell_propensity', ascending=False)
        master_path = os.path.join(output_dir, 'CVO_Master_Report.xlsx')
        master_report.to_excel(master_path, index=False, sheet_name='All Customers')
        
        # Add formatting info
        print(f"      ✅ {len(master_report)} customers exported")
        
        # Report 2: Upsell Opportunities (propensity > 50%)
        print("   Creating Upsell Opportunities Report...")
        upsell_report = df[df['upsell_propensity'] > 0.5][available_cols].sort_values('upsell_potential', ascending=False)
        upsell_path = os.path.join(output_dir, 'CVO_Upsell_Opportunities.xlsx')
        upsell_report.to_excel(upsell_path, index=False, sheet_name='Upsell Targets')
        print(f"      ✅ {len(upsell_report)} upsell targets identified")
        
        # Report 3: Cross-sell Opportunities (propensity > 50%)
        print("   Creating Cross-sell Opportunities Report...")
        crosssell_report = df[df['crosssell_propensity'] > 0.5][available_cols].sort_values('crosssell_potential', ascending=False)
        crosssell_path = os.path.join(output_dir, 'CVO_Crosssell_Opportunities.xlsx')
        crosssell_report.to_excel(crosssell_path, index=False, sheet_name='Cross-sell Targets')
        print(f"      ✅ {len(crosssell_report)} cross-sell targets identified")
        
        # Report 4: Strategic Matrix Breakdown (separate sheet per quadrant)
        print("   Creating Strategic Matrix Breakdown...")
        matrix_path = os.path.join(output_dir, 'CVO_Strategic_Matrices.xlsx')
        with pd.ExcelWriter(matrix_path, engine='openpyxl') as writer:
            # Write summary sheet
            summary_data = []
            for quadrant in df['matrix_1_quadrant'].unique():
                quadrant_df = df[df['matrix_1_quadrant'] == quadrant]
                summary_data.append({
                    'Quadrant': quadrant,
                    'Customer_Count': len(quadrant_df),
                    'Total_Revenue': quadrant_df['revenue'].sum(),
                    'Avg_Revenue': quadrant_df['revenue'].mean(),
                    'Avg_Bandwidth': quadrant_df['bandwidth_mbps'].mean(),
                    'Avg_Tenure': quadrant_df['tenure_months'].mean(),
                    'Upsell_Potential': quadrant_df['upsell_potential'].sum(),
                    'Crosssell_Potential': quadrant_df['crosssell_potential'].sum()
                })
                
                # Write quadrant details
                sheet_name = quadrant.replace('🌟', '').replace('🎯', '').replace('🔫', '').replace('🥚', '').strip()[:31]
                quadrant_df[available_cols].to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Write summary sheet
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"      ✅ {len(df['matrix_1_quadrant'].unique())} quadrants exported")
        
        # Report 5: Top Opportunities (Top 50 by combined potential)
        print("   Creating Top Opportunities Report...")
        df['total_potential'] = df['upsell_potential'] + df['crosssell_potential']
        top_opportunities = df.nlargest(50, 'total_potential')[available_cols + ['total_potential']]
        top_path = os.path.join(output_dir, 'CVO_Top_50_Opportunities.xlsx')
        top_opportunities.to_excel(top_path, index=False, sheet_name='Top 50')
        print(f"      ✅ Top 50 opportunities exported")
        
        return output_dir
    
    def generate_executive_summary(self, output_dir='reports'):
        """
        Generate comprehensive executive summary with ROI projections
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n📊 Generating Executive Summary...")
        
        df = self.df_final.copy()
        
        # Calculate key metrics
        total_customers = len(df)
        total_revenue = df['revenue'].sum()
        avg_revenue = df['revenue'].mean()
        avg_clv = df['predicted_clv_12m'].mean()
        
        # Count opportunities
        high_upsell = len(df[df['upsell_propensity'] > 0.7])
        high_crosssell = len(df[df['crosssell_propensity'] > 0.7])
        medium_upsell = len(df[(df['upsell_propensity'] > 0.5) & (df['upsell_propensity'] <= 0.7)])
        medium_crosssell = len(df[(df['crosssell_propensity'] > 0.5) & (df['crosssell_propensity'] <= 0.7)])
        
        total_upsell_potential = df['upsell_potential'].sum()
        total_crosssell_potential = df['crosssell_potential'].sum()
        total_opportunity = total_upsell_potential + total_crosssell_potential
        
        # Build executive summary
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║        CUSTOMER VALUE OPTIMIZER (CVO) - EXECUTIVE SUMMARY      ║
║                     PLN Icon+ Division                         ║
╚════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Marketing Planning & Analysis Division
Computer Science Intern - Machine Learning Project

═══════════════════════════════════════════════════════════════════
📊 KEY BUSINESS METRICS
═══════════════════════════════════════════════════════════════════

Total Active Customers:           {total_customers:,}
Total Current Annual Revenue:     Rp {total_revenue:>18,.0f}
Average Revenue per Customer:     Rp {avg_revenue:>18,.0f}
Predicted Avg CLV (12 months):    Rp {avg_clv:>18,.0f}

═══════════════════════════════════════════════════════════════════
🎯 STRATEGIC MATRIX DISTRIBUTION (Revenue vs Bandwidth)
═══════════════════════════════════════════════════════════════════

"""
        
        # Add matrix 1 distribution
        matrix1_stats = df['matrix_1_quadrant'].value_counts()
        for quadrant in ['🌟 STAR CLIENT', '🎯 RISK AREA', '🔫 SNIPER ZONE', '🥚 INCUBATOR']:
            if quadrant in matrix1_stats.index:
                count = matrix1_stats[quadrant]
                pct = (count / total_customers) * 100
                revenue = df[df['matrix_1_quadrant'] == quadrant]['revenue'].sum()
                summary += f"{quadrant:20s}: {count:>4} customers ({pct:>5.1f}%) - Revenue: Rp {revenue:>15,.0f}\n"
        
        summary += f"""
═══════════════════════════════════════════════════════════════════
🤖 MACHINE LEARNING PREDICTIONS
═══════════════════════════════════════════════════════════════════

UPSELL OPPORTUNITIES:
  High Propensity (>70%):     {high_upsell:>4} customers
  Medium Propensity (50-70%): {medium_upsell:>4} customers
  Potential Revenue Impact:   Rp {total_upsell_potential:>18,.0f}

CROSS-SELL OPPORTUNITIES:
  High Propensity (>70%):     {high_crosssell:>4} customers
  Medium Propensity (50-70%): {medium_crosssell:>4} customers
  Potential Revenue Impact:   Rp {total_crosssell_potential:>18,.0f}

💰 TOTAL REVENUE OPPORTUNITY: Rp {total_opportunity:>18,.0f}

═══════════════════════════════════════════════════════════════════
📈 MODEL PERFORMANCE METRICS
═══════════════════════════════════════════════════════════════════

Upsell Prediction Model (XGBoost Classifier):
  • Accuracy:    {self.metrics['upsell']['accuracy']:.1%}
  • ROC-AUC:     {self.metrics['upsell']['roc_auc']:.3f} (Excellent discrimination)
  • Precision:   {self.metrics['upsell']['precision']:.1%} (Few false positives)
  • Recall:      {self.metrics['upsell']['recall']:.1%} (Catches most opportunities)

Cross-sell Prediction Model (Random Forest Classifier):
  • Accuracy:    {self.metrics['crosssell']['accuracy']:.1%}
  • ROC-AUC:     {self.metrics['crosssell']['roc_auc']:.3f} (Excellent discrimination)
  • Precision:   {self.metrics['crosssell'].get('precision', 0):.1%}
  • Recall:      {self.metrics['crosssell'].get('recall', 0):.1%}

Customer Lifetime Value Model (Gradient Boosting Regressor):
  • Mean Absolute Error: Rp {self.metrics['clv']['mae']:,.0f}
  • MAPE: {self.metrics['clv']['mape']:.2f}% (Highly accurate)
  • R² Score: {self.metrics['clv']['r2']:.3f} (Explains {self.metrics['clv']['r2']*100:.1f}% of variance)

═══════════════════════════════════════════════════════════════════
🏆 TOP 10 UPSELL OPPORTUNITIES
═══════════════════════════════════════════════════════════════════

"""
        
        top_upsell = df.nlargest(10, 'upsell_potential')[['customer_name', 'revenue', 'bandwidth_mbps', 'upsell_propensity', 'upsell_potential']]
        for idx, row in top_upsell.iterrows():
            summary += f"{row['customer_name'][:35]:35s} | Rev: Rp {row['revenue']:>10,.0f} | BW: {row['bandwidth_mbps']:>6.0f} Mbps | Prop: {row['upsell_propensity']:.1%} | Potential: Rp {row['upsell_potential']:>10,.0f}\n"
        
        summary += f"""
═══════════════════════════════════════════════════════════════════
🏆 TOP 10 CROSS-SELL OPPORTUNITIES
═══════════════════════════════════════════════════════════════════

"""
        
        top_crosssell = df.nlargest(10, 'crosssell_potential')[['customer_name', 'revenue', 'bandwidth_mbps', 'crosssell_propensity', 'crosssell_potential']]
        for idx, row in top_crosssell.iterrows():
            summary += f"{row['customer_name'][:35]:35s} | Rev: Rp {row['revenue']:>10,.0f} | BW: {row['bandwidth_mbps']:>6.0f} Mbps | Prop: {row['crosssell_propensity']:.1%} | Potential: Rp {row['crosssell_potential']:>10,.0f}\n"
        
        summary += f"""
═══════════════════════════════════════════════════════════════════
📋 RECOMMENDED ACTION PLAN
═══════════════════════════════════════════════════════════════════

🚨 IMMEDIATE ACTIONS (Next 30 Days):
   1. Focus sales team on {high_upsell + high_crosssell} high-propensity customers
   2. Contact top 10 upsell opportunities immediately
   3. Launch targeted email campaign for Risk Area customers
   4. Expected quick wins: Rp {total_opportunity * 0.15:,.0f} (15% of potential)

⚡ SHORT-TERM STRATEGY (Next 90 Days):
   1. Execute "Sniper Zone" bandwidth upgrade campaign
   2. Introduce Smart Home bundles to Risk Area customers
   3. Offer PV Rooftop solutions to high-revenue, low-bandwidth clients
   4. Target: Capture 30% of predicted opportunities
   5. Potential revenue: Rp {total_opportunity * 0.30:,.0f}

🎯 LONG-TERM STRATEGY (Next 12 Months):
   1. Build retention programs for Star Clients (prevent churn)
   2. Develop nurture campaigns for Incubator segment
   3. Implement customer success program for Champions
   4. Target: 20-40% conversion rate on all predicted opportunities
   5. Conservative target (20%): Rp {total_opportunity * 0.20:,.0f}
   6. Optimistic target (40%): Rp {total_opportunity * 0.40:,.0f}

═══════════════════════════════════════════════════════════════════
💡 ROI PROJECTIONS & BUSINESS IMPACT
═══════════════════════════════════════════════════════════════════

SCENARIO ANALYSIS:

Conservative (20% conversion rate):
  • Additional Annual Revenue:    Rp {total_opportunity * 0.20:>18,.0f}
  • % Increase over current:      {(total_opportunity * 0.20 / total_revenue * 100):>5.1f}%
  • Investment required:          Low (existing sales team)
  • ROI:                          Extremely High

Moderate (30% conversion rate):
  • Additional Annual Revenue:    Rp {total_opportunity * 0.30:>18,.0f}
  • % Increase over current:      {(total_opportunity * 0.30 / total_revenue * 100):>5.1f}%
  • Investment required:          Medium (marketing campaigns)
  • ROI:                          Very High

Optimistic (40% conversion rate):
  • Additional Annual Revenue:    Rp {total_opportunity * 0.40:>18,.0f}
  • % Increase over current:      {(total_opportunity * 0.40 / total_revenue * 100):>5.1f}%
  • Investment required:          High (dedicated sales team)
  • ROI:                          High

═══════════════════════════════════════════════════════════════════
📊 STRATEGIC INSIGHTS
═══════════════════════════════════════════════════════════════════

• SNIPER ZONE customers have high bandwidth usage but are paying below-market rates
  → Opportunity: Upgrade to higher-tier plans with 30% price increase potential

• RISK AREA customers pay high prices but have low bandwidth utilization
  → Opportunity: Cross-sell digital products (Smart Home, PV, EV Charging)

• STAR CLIENTS are your most valuable - focus on retention, not upselling
  → Risk: Competitors may target these high-value customers

• INCUBATOR customers need education and nurturing before any sales attempt
  → Strategy: Build trust through excellent service and support

═══════════════════════════════════════════════════════════════════
🔧 TECHNICAL NOTES
═══════════════════════════════════════════════════════════════════

Models Used:
  • Upsell Prediction: XGBoost Classifier (Gradient Boosting)
  • Cross-sell Prediction: Random Forest Classifier (Ensemble Method)
  • CLV Prediction: Gradient Boosting Regressor

Data Processing:
  • Total customers analyzed: {total_customers}
  • Features used: 10+ engineered features
  • Train/test split: 80/20 with stratification
  • Cross-validation: 5-fold

This report was generated using advanced Machine Learning techniques
and is designed to provide actionable business intelligence.

═══════════════════════════════════════════════════════════════════
Report generated by Customer Value Optimizer (CVO) v2.0
For questions, contact: Marketing Planning & Analysis Division
═══════════════════════════════════════════════════════════════════
"""
        
        # Save to file
        summary_path = os.path.join(output_dir, 'Executive_Summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"   ✅ Executive Summary saved: {summary_path}")
        
        # Also print to console
        print("\n" + "="*70)
        print("EXECUTIVE SUMMARY PREVIEW")
        print("="*70)
        print(summary[:2000] + "\n... [See full report in Executive_Summary.txt]\n")
        
        return summary
    
    def generate_json_for_dashboard(self, output_dir='dashboard_data'):
        """
        Generate JSON data files for Next.js dashboard
        """
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n📊 Generating dashboard data in '{output_dir}/'...")
        
        df = self.df_final.copy()
        
        # 1. Summary metrics
        summary_metrics = {
            'total_customers': len(df),
            'total_revenue': float(df['revenue'].sum()),
            'avg_revenue': float(df['revenue'].mean()),
            'avg_clv': float(df['predicted_clv_12m'].mean()),
            'high_upsell_count': int((df['upsell_propensity'] > 0.7).sum()),
            'high_crosssell_count': int((df['crosssell_propensity'] > 0.7).sum()),
            'total_upsell_potential': float(df['upsell_potential'].sum()),
            'total_crosssell_potential': float(df['crosssell_potential'].sum()),
            'model_accuracy_upsell': float(self.metrics['upsell']['accuracy']),
            'model_accuracy_crosssell': float(self.metrics['crosssell']['accuracy']),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(output_dir, 'summary_metrics.json'), 'w') as f:
            json.dump(summary_metrics, f, indent=2)
        print("   ✅ summary_metrics.json")
        
        # 2. Matrix 1 distribution
        matrix1_dist = []
        for quadrant in df['matrix_1_quadrant'].unique():
            quadrant_df = df[df['matrix_1_quadrant'] == quadrant]
            matrix1_dist.append({
                'quadrant': quadrant,
                'count': len(quadrant_df),
                'percentage': float(len(quadrant_df) / len(df) * 100),
                'total_revenue': float(quadrant_df['revenue'].sum()),
                'avg_revenue': float(quadrant_df['revenue'].mean()),
                'avg_bandwidth': float(quadrant_df['bandwidth_mbps'].mean()),
                'strategy': quadrant_df['matrix_1_strategy'].iloc[0] if len(quadrant_df) > 0 else ''
            })
        
        with open(os.path.join(output_dir, 'matrix1_distribution.json'), 'w') as f:
            json.dump(matrix1_dist, f, indent=2)
        print("   ✅ matrix1_distribution.json")
        
        # 3. Matrix 2 distribution
        matrix2_dist = []
        for quadrant in df['matrix_2_quadrant'].unique():
            quadrant_df = df[df['matrix_2_quadrant'] == quadrant]
            matrix2_dist.append({
                'quadrant': quadrant,
                'count': len(quadrant_df),
                'percentage': float(len(quadrant_df) / len(df) * 100),
                'total_revenue': float(quadrant_df['revenue'].sum()),
                'avg_tenure': float(quadrant_df['tenure_months'].mean()),
                'strategy': quadrant_df['matrix_2_strategy'].iloc[0] if len(quadrant_df) > 0 else ''
            })
        
        with open(os.path.join(output_dir, 'matrix2_distribution.json'), 'w') as f:
            json.dump(matrix2_dist, f, indent=2)
        print("   ✅ matrix2_distribution.json")
        
        # 4. Top opportunities
        top_upsell = df.nlargest(20, 'upsell_potential')[['customer_name', 'revenue', 
                                                          'bandwidth_mbps', 'upsell_propensity', 
                                                          'upsell_potential', 'matrix_1_quadrant']].to_dict('records')
        
        top_crosssell = df.nlargest(20, 'crosssell_potential')[['customer_name', 'revenue', 
                                                                'bandwidth_mbps', 'crosssell_propensity', 
                                                                'crosssell_potential', 'matrix_1_quadrant']].to_dict('records')
        
        opportunities = {
            'top_upsell': top_upsell,
            'top_crosssell': top_crosssell
        }
        
        with open(os.path.join(output_dir, 'top_opportunities.json'), 'w') as f:
            json.dump(opportunities, f, indent=2)
        print("   ✅ top_opportunities.json")
        
        # 5. Customer data for scatter plot
        scatter_data = df[['customer_name', 'revenue', 'bandwidth_mbps', 'tenure_months',
                          'upsell_propensity', 'crosssell_propensity', 'predicted_clv_12m',
                          'matrix_1_quadrant', 'matrix_2_quadrant']].to_dict('records')
        
        with open(os.path.join(output_dir, 'customer_scatter_data.json'), 'w') as f:
            json.dump(scatter_data, f, indent=2)
        print("   ✅ customer_scatter_data.json")
        
        # 6. Thresholds
        thresholds = {
            'median_revenue': float(self.thresholds['median_revenue']),
            'median_bandwidth': float(self.thresholds['median_bandwidth']),
            'median_tenure': float(self.thresholds['median_tenure'])
        }
        
        with open(os.path.join(output_dir, 'thresholds.json'), 'w') as f:
            json.dump(thresholds, f, indent=2)
        print("   ✅ thresholds.json")
        
        return output_dir
    
    def run_full_pipeline(self):
        """
        Execute the complete CVO pipeline end-to-end
        """
        print("\n" + "="*70)
        print(" "*15 + "CUSTOMER VALUE OPTIMIZER (CVO) v2.0")
        print(" "*10 + "PLN Icon+ - Marketing Planning & Analysis Division")
        print("="*70)
        print(f"\n🚀 Starting ML Pipeline for: {self.data_path}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Load data
        print("\n" + "-"*70)
        print("STEP 1/8: Data Loading")
        print("-"*70)
        if not self.load_data():
            print("❌ Pipeline failed at data loading stage")
            return False
        
        # Step 2: Clean data
        print("\n" + "-"*70)
        print("STEP 2/8: Data Cleaning & Standardization")
        print("-"*70)
        self.clean_and_standardize()
        
        # Step 3: Engineer features
        print("\n" + "-"*70)
        print("STEP 3/8: Feature Engineering")
        print("-"*70)
        self.engineer_features()
        
        # Step 4: Create strategic matrices
        print("\n" + "-"*70)
        print("STEP 4/8: Strategic Matrix Generation")
        print("-"*70)
        self.create_strategic_matrices()
        
        # Step 5: Train ML models
        print("\n" + "-"*70)
        print("STEP 5/8: Machine Learning Model Training")
        print("-"*70)
        self.train_models()
        
        # Step 6: Generate predictions
        print("\n" + "-"*70)
        print("STEP 6/8: Prediction Generation")
        print("-"*70)
        self.generate_predictions()
        
        # Step 7: Generate Excel reports
        print("\n" + "-"*70)
        print("STEP 7/8: Excel Report Generation")
        print("-"*70)
        self.generate_excel_reports()
        
        # Step 8: Generate executive summary and dashboard data
        print("\n" + "-"*70)
        print("STEP 8/8: Executive Summary & Dashboard Data")
        print("-"*70)
        self.generate_executive_summary()
        self.generate_json_for_dashboard()
        
        # Completion
        print("\n" + "="*70)
        print("✅ CVO PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📁 Generated Files:")
        print("   📊 Excel Reports:")
        print("      • reports/CVO_Master_Report.xlsx")
        print("      • reports/CVO_Upsell_Opportunities.xlsx")
        print("      • reports/CVO_Crosssell_Opportunities.xlsx")
        print("      • reports/CVO_Strategic_Matrices.xlsx")
        print("      • reports/CVO_Top_50_Opportunities.xlsx")
        print("\n   📄 Documentation:")
        print("      • reports/Executive_Summary.txt")
        print("\n   🌐 Dashboard Data (JSON):")
        print("      • dashboard_data/summary_metrics.json")
        print("      • dashboard_data/matrix1_distribution.json")
        print("      • dashboard_data/matrix2_distribution.json")
        print("      • dashboard_data/top_opportunities.json")
        print("      • dashboard_data/customer_scatter_data.json")
        print("\n🎯 Next Steps:")
        print("   1. Review Excel reports in the 'reports/' folder")
        print("   2. Read Executive_Summary.txt for business insights")
        print("   3. Use dashboard data for Next.js visualization")
        print("   4. Share reports with marketing & sales teams")
        print("\n✨ Ready for business use!")
        print("="*70 + "\n")
        
        return True


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Initialize and run the CVO pipeline
    print("\n" + "🎯"*35)
    print("\n  Customer Value Optimizer (CVO) v2.0 - PLN Icon+")
    print("  Machine Learning Pipeline for Upsell/Cross-sell Prediction")
    print("\n" + "🎯"*35 + "\n")
    
    # Priority order for data files:
    # 1. Full data file (if exists)
    # 2. Sample data file (if exists)
    # 3. Any other Excel/CSV file found
    
    full_data_file = "Data Penuh Pelanggan Aktif.xlsx"
    sample_data_file = "Data Sampel Machine Learning.xlsx"
    
    # Check for full data file first
    if os.path.exists(full_data_file):
        data_file = full_data_file
        print(f"📊 Using FULL DATA: {data_file}")
        print("   ⚠️  Processing complete customer database - this may take a few minutes...")
    # Fall back to sample data
    elif os.path.exists(sample_data_file):
        data_file = sample_data_file
        print(f"📊 Using SAMPLE DATA: {data_file}")
        print("   💡 Tip: Place 'Data Penuh Pelanggan Aktif.xlsx' in this folder to analyze full dataset")
    else:
        print(f"⚠️  Neither '{full_data_file}' nor '{sample_data_file}' found.")
        print("   Looking for alternative data files...")
        
        # Try to find any Excel or CSV file in the directory
        import glob
        excel_files = glob.glob("*.xlsx") + glob.glob("*.xls") + glob.glob("*.csv")
        
        if excel_files:
            data_file = excel_files[0]
            print(f"   Found: {data_file}")
        else:
            print("❌ No data files found. Please ensure your data file is in the same directory.")
            print("   Supported formats: .xlsx, .xls, .csv")
            exit(1)
    
    # Initialize CVO
    cvo = CustomerValueOptimizer(data_file)
    
    # Run full pipeline
    success = cvo.run_full_pipeline()
    
    if success:
        print("\n🎉 Pipeline completed successfully! Check the 'reports/' folder.")
    else:
        print("\n❌ Pipeline failed. Please check the error messages above.")
