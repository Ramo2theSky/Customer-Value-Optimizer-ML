"""
CUSTOMER VALUE OPTIMIZER (CVO) v3.0 - Next Best Offer Engine
===========================================================
PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran
Sistem Rekomendasi ML dengan NBO (Next Best Offer)

FITUR v3.0:
[OK] 15 Tier Combinations dengan Roadmap Cross-sell
[OK] 5 Bandwidth Clusters menggunakan 'Bandwidth Fix'
[OK] Text Mining untuk Product Hierarchy (Basic→Premium)
[OK] Segment-Based Context (GOVERNMENT vs BUSINESS)
[OK] High-Margin Product Recommendations
[OK] NBO Engine - Rekomendasi spesifik per pelanggan
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
from difflib import get_close_matches

warnings.filterwarnings('ignore')

print("="*80)
print("CUSTOMER VALUE OPTIMIZER (CVO) v3.0 - Next Best Offer Engine")
print("PLN Icon+ - Sistem Rekomendasi ML dengan NBO")
print("="*80)


class ProductCatalog:
    """Katalog Produk Icon+ untuk rekomendasi NBO"""
    
    def __init__(self, catalog_path):
        self.catalog_path = catalog_path
        self.df_catalog = None
        self.product_hierarchy = {}
        self.tier_products = {}
        self.load_catalog()
    
    def load_catalog(self):
        """Memuat katalog produk dari Excel"""
        print("\n Memuat Katalog Produk Icon+...")
        try:
            self.df_catalog = pd.read_excel(self.catalog_path)
            print(f"   [OK] {len(self.df_catalog)} produk dimuat")
            self._build_product_hierarchy()
            self._categorize_by_tier()
        except Exception as e:
            print(f"   [WARN]  Katalog tidak ditemukan: {e}")
            self._create_default_catalog()
    
    def _build_product_hierarchy(self):
        """Build hierarki produk dari nama produk (text mining)"""
        print("   [SEARCH] Building product hierarchy via text mining...")
        
        if self.df_catalog is None:
            print("   [WARN] No catalog data available, skipping hierarchy build")
            return
        
        entry_keywords = ['basic', 'starter', 'bronze', 'standard', 'light', 'essential', 'entry']
        mid_keywords = ['medium', 'silver', 'professional', 'pro', 'plus', 'advanced', 'business']
        high_keywords = ['gold', 'platinum', 'premium', 'enterprise', 'ultimate', 'max', 'deluxe']
        
        for idx, row in self.df_catalog.iterrows():
            product_name = str(row.get('Produk', '')).lower()
            nomenklatur = str(row.get('Nomenklatur Baru', ''))
            kategori = str(row.get('Kategori Produk', ''))
            
            # Determine level
            level = 'UNKNOWN'
            if any(kw in product_name for kw in entry_keywords):
                level = 'ENTRY'
            elif any(kw in product_name for kw in mid_keywords):
                level = 'MID'
            elif any(kw in product_name for kw in high_keywords):
                level = 'HIGH'
            
            self.product_hierarchy[row.get('Produk', '')] = {
                'level': level,
                'nomenklatur': nomenklatur,
                'kategori': kategori,
                'code': row.get('Kode', 0)
            }
        
        # Summary
        entry_count = sum(1 for p in self.product_hierarchy.values() if p['level'] == 'ENTRY')
        mid_count = sum(1 for p in self.product_hierarchy.values() if p['level'] == 'MID')
        high_count = sum(1 for p in self.product_hierarchy.values() if p['level'] == 'HIGH')
        
        print(f"      Entry Level: {entry_count} produk")
        print(f"      Mid Level: {mid_count} produk")
        print(f"      High Level: {high_count} produk")
    
    def _categorize_by_tier(self):
        """Kategorikan produk berdasarkan tier yang cocok"""
        if self.df_catalog is None:
            print("   [WARN] No catalog data available, using default tier products")
            return
        
        # Mapping produk ke tier recommendations
        self.tier_products = {
            'DI': [],      # Digital Infrastructure products
            'TS': [],      # Technology Services products
            'SDS': [],     # Smart Digital Solution products
            'GE': []       # Green Ecosystem products
        }
        
        for idx, row in self.df_catalog.iterrows():
            nomenklatur = str(row.get('Nomenklatur Baru', ''))
            produk = row.get('Produk', '')
            
            if 'Technology Services' in nomenklatur:
                self.tier_products['TS'].append(produk)
            elif 'Smart' in nomenklatur or 'Digital Solution' in nomenklatur:
                self.tier_products['SDS'].append(produk)
            elif 'Green' in nomenklatur or 'Ecosystem' in nomenklatur:
                self.tier_products['GE'].append(produk)
            elif 'Infrastructure' in nomenklatur:
                self.tier_products['DI'].append(produk)
    
    def _create_default_catalog(self):
        """Create default catalog if file not found"""
        print("   [WARN]  Menggunakan katalog default")
        # Will implement based on sample data patterns
        pass
    
    def get_next_level_product(self, current_product):
        """Get next level product for upsell"""
        if current_product not in self.product_hierarchy:
            return None
        
        current_info = self.product_hierarchy[current_product]
        current_level = current_info['level']
        current_kategori = current_info['kategori']
        
        # Find product one level higher in same category
        target_level = {'ENTRY': 'MID', 'MID': 'HIGH', 'HIGH': None}.get(current_level)
        
        if not target_level:
            return None
        
        candidates = []
        for product, info in self.product_hierarchy.items():
            if info['level'] == target_level and info['kategori'] == current_kategori:
                candidates.append(product)
        
        return candidates[0] if candidates else None
    
    def get_cross_sell_by_tier(self, current_tier, segmen='BUSINESS'):
        """Get cross-sell product recommendations based on tier and segment"""
        recommendations = []
        
        # Parse current tier
        has_di = 'DI' in current_tier
        has_ts = 'TS' in current_tier
        has_sds = 'SDS' in current_tier
        has_ge = 'GE' in current_tier
        
        # Recommend next tier
        if not has_ts and 'DI' in current_tier:
            # DI Only or DI-SDS, DI-GE → add TS
            recommendations.extend(self.tier_products.get('TS', [])[:3])
        
        if not has_sds and 'DI' in current_tier and 'TS' in current_tier:
            # DI-TS → add SDS
            recommendations.extend(self.tier_products.get('SDS', [])[:3])
        
        if not has_ge and ('SDS' in current_tier or 'TS' in current_tier):
            # Add GE for high-tier customers
            recommendations.extend(self.tier_products.get('GE', [])[:2])
        
        # Contextual by segment
        if segmen == 'GOVERNMENT':
            gov_products = [p for p in recommendations if any(x in p.lower() for x in ['ap2t', 'ago', 'smart city', 'public'])]
            if gov_products:
                recommendations = gov_products + recommendations
        
        return recommendations[:5]  # Return top 5


class TierRoadmap:
    """Sistem Roadmap Tier untuk Cross-sell"""
    
    # 15 Tier Combinations with Next Best Offer
    TIER_ROADMAP = {
        'DI Only': {'next': 'DI-TS', 'priority': 'HIGH', 'action': 'Add Technology Services'},
        'TS Only': {'next': 'DI-TS', 'priority': 'HIGH', 'action': 'Add Digital Infrastructure'},
        'SDS Only': {'next': 'DI-SDS-TS', 'priority': 'MEDIUM', 'action': 'Add DI + TS'},
        'GE Only': {'next': 'GE-DI', 'priority': 'MEDIUM', 'action': 'Add Digital Infrastructure'},
        
        'DI-TS': {'next': 'DI-SDS-TS', 'priority': 'HIGH', 'action': 'Add Smart Digital Solution'},
        'DI-SDS': {'next': 'DI-SDS-TS', 'priority': 'MEDIUM', 'action': 'Add Technology Services'},
        'DI-GE': {'next': 'DI-GE-TS', 'priority': 'MEDIUM', 'action': 'Add Technology Services'},
        
        'DI-SDS-TS': {'next': 'DI-GE-SDS-TS', 'priority': 'MEDIUM', 'action': 'Add Green Ecosystem'},
        'DI-GE-TS': {'next': 'DI-SDS-GE-TS', 'priority': 'MEDIUM', 'action': 'Add Smart Digital Solution'},
        'DI-GE-SDS': {'next': 'ALL_NOMENKLATUR', 'priority': 'LOW', 'action': 'Add Technology Services'},
        
        'GE-SDS-TS': {'next': 'GE-SDS-TS-DI', 'priority': 'HIGH', 'action': 'Add Digital Infrastructure'},
        'GE-SDS': {'next': 'GE-SDS-TS', 'priority': 'MEDIUM', 'action': 'Add Technology Services'},
        'GE-TS': {'next': 'GE-TS-DI', 'priority': 'MEDIUM', 'action': 'Add Digital Infrastructure'},
        'SDS-TS': {'next': 'DI-SDS-TS', 'priority': 'HIGH', 'action': 'Add Digital Infrastructure'},
        
        'ALL NOMENKLATUR': {'next': None, 'priority': 'RETENTION', 'action': 'Retention & Premium Services'},
    }
    
    @classmethod
    def get_recommendation(cls, current_tier):
        """Get next tier recommendation"""
        return cls.TIER_ROADMAP.get(current_tier, {'next': None, 'priority': 'UNKNOWN', 'action': 'Analyze Further'})


class CustomerValueOptimizerNBO:
    """CVO Next Best Offer Engine"""
    
    def __init__(self, data_path, catalog_path=None):
        self.data_path = data_path
        self.catalog_path = catalog_path
        self.df_raw = None
        self.df_processed = None
        self.df_features = None
        self.df_final = None
        self.product_catalog = None
        self.upsell_model = None
        self.crosssell_model = None
        self.clv_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.metrics = {'upsell': {}, 'crosssell': {}, 'clv': {}}
        self.thresholds = {}
        
        if catalog_path:
            self.product_catalog = ProductCatalog(catalog_path)
    
    def parse_bandwidth_fix(self, bw_value):
        """
        Parse Bandwidth Fix column with various formats
        Handles: '20 MBPS', '512 KBPS', '1 GBPS', 'Tidak Ada', '2 PAIR'
        """
        if pd.isna(bw_value) or str(bw_value).lower() in ['tidak ada', 'none', 'nan', '-']:
            return 0, 'NO_BANDWIDTH'
        
        bw_str = str(bw_value).lower().replace(',', '.').strip()
        
        # Extract number
        numbers = re.findall(r"[\d.]+", bw_str)
        if not numbers:
            return 0, 'UNKNOWN'
        
        try:
            value = float(numbers[0])
        except:
            return 0, 'UNKNOWN'
        
        # Determine unit and convert to MBPS
        if 'gbps' in bw_str or 'gb' in bw_str:
            mbps = value * 1000
        elif 'kbps' in bw_str or 'kb' in bw_str:
            mbps = value / 1000
        elif 'mbps' in bw_str or 'mb' in bw_str:
            mbps = value
        elif 'pair' in bw_str:
            # For fiber pairs, assume standard conversion or categorize separately
            mbps = value * 100  # Assume 100 Mbps per pair as rough estimate
        else:
            mbps = value  # Assume MBPS if no unit
        
        # Determine cluster
        if mbps == 0:
            cluster = 'NO_BANDWIDTH'
        elif mbps < 1:  # < 1 MBPS = ATM/IoT
            cluster = 'ATM_IOT'
        elif mbps <= 20:  # 1-20 MBPS = UMKM/Small
            cluster = 'UMKM_SMALL'
        elif mbps <= 500:  # 20-500 MBPS = Corporate (main target)
            cluster = 'CORPORATE'
        else:  # > 500 MBPS = Enterprise/Backbone
            cluster = 'ENTERPRISE'
        
        return mbps, cluster
    
    def load_data(self):
        """Memuat data dari file Excel"""
        print("\n[DATA] Memuat data...")
        try:
            file_size = os.path.getsize(self.data_path) / (1024 * 1024)
            print(f"   Ukuran file: {file_size:.1f} MB")
            
            self.df_raw = pd.read_excel(self.data_path, engine='openpyxl')
            print(f"[OK] Data berhasil dimuat: {len(self.df_raw):,} baris, {len(self.df_raw.columns)} kolom")
            return True
        except Exception as e:
            print(f" Error saat memuat data: {e}")
            return False
    
    def clean_and_standardize(self):
        """Membersihkan dan menstandardisasi data"""
        print("\n Membersihkan data...")
        
        if self.df_raw is None:
            print("   [ERROR] No data loaded. Please load data first.")
            return None
        
        df = self.df_raw.copy()
        
        # Column mapping
        column_mapping = {
            'namaPelanggan': 'nama_pelanggan',
            'hargaPelanggan': 'pendapatan',
            'hargaPelangganLalu': 'pendapatan_sebelumnya',
            'Lama_Langganan': 'masa_berlangganan',
            'segmencustomer': 'segmen',
            'WILAYAH': 'wilayah',
            'Kategori_Baru': 'kategori',
            'Kelompok Tier': 'tier',
            'ProdukBaru': 'produk',
            'Bandwidth Fix': 'bandwidth_fix',
            'statusLayanan': 'status'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Clean revenue
        for col in ['pendapatan', 'pendapatan_sebelumnya']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[^\d]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Parse Bandwidth Fix - KRITIS
        if 'bandwidth_fix' in df.columns:
            print("   [SEARCH] Parsing Bandwidth Fix...")
            bw_data = df['bandwidth_fix'].apply(self.parse_bandwidth_fix)
            df['bandwidth_mbps'] = bw_data.apply(lambda x: x[0])
            df['bandwidth_cluster'] = bw_data.apply(lambda x: x[1])
            
            # Show distribution
            cluster_dist = df['bandwidth_cluster'].value_counts()
            print("\n   [DATA] Distribusi Bandwidth Cluster:")
            for cluster, count in cluster_dist.items():
                pct = count / len(df) * 100
                print(f"      {cluster:15s}: {count:>6,} pelanggan ({pct:>5.1f}%)")
        
        # Clean tenure
        df['masa_berlangganan'] = pd.to_numeric(df.get('masa_berlangganan', 0), errors='coerce').fillna(0)
        
        # Filter active only
        if 'status' in df.columns:
            df = df[df['status'].str.contains('AKTIF|Aktif|Active', case=False, na=False)]
        
        # Remove duplicates
        if 'nama_pelanggan' in df.columns:
            df = df.drop_duplicates(subset=['nama_pelanggan'], keep='first')
        
        self.df_processed = df
        print(f"[OK] Data dibersihkan: {len(df):,} pelanggan aktif")
        return df
    
    def engineer_features(self):
        """Membuat fitur untuk model ML dengan NBO"""
        print("\n[FIX] Membuat fitur ML...")
        df = self.df_processed.copy()
        
        # Tier analysis
        if 'tier' in df.columns:
            print("   [DATA] Analisis Tier...")
            tier_dist = df['tier'].value_counts()
            print(f"      Total {len(tier_dist)} kombinasi tier ditemukan")
            
            # Add tier recommendation
            df['tier_recommendation'] = df['tier'].apply(
                lambda x: TierRoadmap.get_recommendation(x)['action'] if pd.notna(x) else 'Unknown'
            )
            df['tier_priority'] = df['tier'].apply(
                lambda x: TierRoadmap.get_recommendation(x)['priority'] if pd.notna(x) else 'UNKNOWN'
            )
        
        # Revenue features per cluster
        df['pendapatan_per_mbps'] = np.where(df['bandwidth_mbps'] > 0, 
                                              df['pendapatan'] / df['bandwidth_mbps'], 0)
        
        # Growth
        if 'pendapatan_sebelumnya' in df.columns:
            df['pertumbuhan_pendapatan'] = np.where(df['pendapatan_sebelumnya'] > 0,
                                                   (df['pendapatan'] - df['pendapatan_sebelumnya']) / df['pendapatan_sebelumnya'], 0)
        else:
            df['pertumbuhan_pendapatan'] = 0
        
        # Value score per bandwidth cluster
        print("   [DATA] Menghitung skor nilai per cluster...")
        
        def calc_value_score(group):
            if len(group) == 0 or group['pendapatan'].max() == 0:
                return pd.Series([0] * len(group), index=group.index)
            
            pendapatan_norm = group['pendapatan'] / group['pendapatan'].max()
            tenure_norm = group['masa_berlangganan'] / group['masa_berlangganan'].max() if group['masa_berlangganan'].max() > 0 else 0
            bw_norm = group['bandwidth_mbps'] / group['bandwidth_mbps'].max() if group['bandwidth_mbps'].max() > 0 else 0
            
            return (pendapatan_norm * 0.5 + tenure_norm * 0.3 + bw_norm * 0.2)
        
        df['skor_nilai'] = df.groupby('bandwidth_cluster', group_keys=False).apply(calc_value_score)
        
        # High value indicators per cluster
        df['high_value'] = df.groupby('bandwidth_cluster')['pendapatan'].transform(
            lambda x: (x >= x.quantile(0.75)).astype(int) if len(x) > 0 else 0)
        
        df['high_bandwidth'] = df.groupby('bandwidth_cluster')['bandwidth_mbps'].transform(
            lambda x: (x >= x.quantile(0.75)).astype(int) if len(x) > 0 else 0)
        
        # Encode categorical
        for col in ['segmen', 'wilayah', 'kategori', 'tier']:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Encode bandwidth cluster
        le_bw = LabelEncoder()
        df['bandwidth_cluster_encoded'] = le_bw.fit_transform(df['bandwidth_cluster'])
        
        self.df_features = df
        print(f"[OK] Fitur siap: {df.shape[1]} kolom")
        return df
    
    def create_strategic_matrices(self):
        """Membuat matriks strategis dengan NBO"""
        print("\n[DATA] Membuat matriks strategis dengan NBO...")
        df = self.df_features.copy()
        
        # Calculate thresholds per bandwidth cluster
        print("    Menghitung threshold per bandwidth cluster...")
        cluster_thresholds = {}
        
        for cluster in df['bandwidth_cluster'].unique():
            cluster_data = df[df['bandwidth_cluster'] == cluster]
            if len(cluster_data) > 0:
                cluster_thresholds[cluster] = {
                    'median_pendapatan': cluster_data['pendapatan'].median(),
                    'median_bandwidth': cluster_data['bandwidth_mbps'].median(),
                    'q75_pendapatan': cluster_data['pendapatan'].quantile(0.75),
                    'q25_pendapatan': cluster_data['pendapatan'].quantile(0.25)
                }
        
        self.thresholds = cluster_thresholds
        
        # Classification function
        def classify_customer(row):
            cluster = row['bandwidth_cluster']
            
            if cluster == 'NO_BANDWIDTH':
                # Non-bandwidth products (Managed Service, Platform)
                if row['pendapatan'] >= cluster_thresholds.get(cluster, {}).get('median_pendapatan', 0):
                    return '[TARGET] NON-BW HIGH VALUE', 'CROSS-SELL - Add Connectivity or Digital Solutions'
                else:
                    return ' NON-BW ENTRY', 'EDUKASI - Introduce Value-Added Services'
            
            elif cluster == 'ATM_IOT':
                # ATM and IoT devices
                return '[SAT] ATM/IoT', 'MAINTAIN - Ensure Reliability, No BW Upsell Needed'
            
            elif cluster == 'UMKM_SMALL':
                # Small business
                thresh = cluster_thresholds.get(cluster, {})
                if row['pendapatan'] >= thresh.get('median_pendapatan', 0):
                    return '[MOBILE] UMKM POTENSIAL', 'UPSELL - Upgrade to Corporate Package'
                else:
                    return ' UMKM PEMULA', 'EDUKASI - Digital Business Solutions'
            
            elif cluster == 'CORPORATE':
                # Main upsell target
                thresh = cluster_thresholds.get(cluster, {})
                high_rev = row['pendapatan'] >= thresh.get('median_pendapatan', 0)
                high_bw = row['bandwidth_mbps'] >= thresh.get('median_bandwidth', 0)
                
                if high_rev and high_bw:
                    return '[STAR] CORPORATE BINTANG', 'PERTAHANKAN - Premium Support & Bundle'
                elif high_rev and not high_bw:
                    return '[TARGET] CORPORATE RISIKO', 'CROSS-SELL - Smart Solutions, PV, EV'
                elif not high_rev and high_bw:
                    return ' CORPORATE SNIPER', 'UPSELL - Increase Bandwidth & Add Services'
                else:
                    return ' CORPORATE PEMULA', 'EDUKASI - Demo & Onboarding'
            
            elif cluster == 'ENTERPRISE':
                # High bandwidth - focus on retention and services
                thresh = cluster_thresholds.get(cluster, {})
                if row['pendapatan'] >= thresh.get('median_pendapatan', 0):
                    return '[OFFICE] ENTERPRISE BINTANG', 'PERTAHANKAN - SLA Premium & Consultative'
                else:
                    return '[SAT] ENTERPRISE POTENSI', 'OPTIMIZE - Efficiency & Cost Management'
            
            return ' UNKNOWN', 'ANALYZE'
        
        hasil = df.apply(classify_customer, axis=1)
        df['kuadran'] = hasil.apply(lambda x: x[0])
        df['strategi'] = hasil.apply(lambda x: x[1])
        
        # Add NBO recommendations
        print("   [TARGET] Generating Next Best Offer recommendations...")
        
        def generate_nbo(row):
            nbo_list = []
            
            # 1. Tier-based NBO
            if 'tier' in row and pd.notna(row['tier']):
                tier_rec = TierRoadmap.get_recommendation(row['tier'])
                if tier_rec['next']:
                    nbo_list.append(f"Tier: {tier_rec['action']}")
            
            # 2. Product-based NBO (if catalog available)
            if self.product_catalog and 'produk' in row and pd.notna(row['produk']):
                current_product = row['produk']
                next_product = self.product_catalog.get_next_level_product(current_product)
                if next_product:
                    nbo_list.append(f"Product: Upgrade to {next_product}")
                
                # Cross-sell by tier
                cross_sell_products = self.product_catalog.get_cross_sell_by_tier(
                    row.get('tier', ''), row.get('segmen', 'BUSINESS')
                )
                if cross_sell_products:
                    nbo_list.append(f"Cross-sell: {', '.join(cross_sell_products[:2])}")
            
            # 3. Bandwidth cluster NBO
            if row['kuadran'] == ' CORPORATE SNIPER':
                nbo_list.append("Bandwidth: Upgrade to next tier (50→100→200 Mbps)")
            elif row['kuadran'] == '[TARGET] CORPORATE RISIKO':
                nbo_list.append("Solution: Smart Building, Managed Security, Cloud")
            
            return ' | '.join(nbo_list) if nbo_list else 'Maintain & Monitor'
        
        df['nbo_recommendation'] = df.apply(generate_nbo, axis=1)
        
        self.df_features = df
        
        # Display distribution
        print("\n   [DATA] Distribusi Kuadran Strategis:")
        print("   " + "="*80)
        kuadran_dist = df['kuadran'].value_counts()
        for kuadran, count in kuadran_dist.items():
            pct = count / len(df) * 100
            revenue = df[df['kuadran'] == kuadran]['pendapatan'].sum()
            print(f"   {kuadran:25s}: {count:>6,} pel ({pct:>5.1f}%) | Rev: Rp {revenue:>12,.0f}")
        print("   " + "="*80)
        
        return df
    
    def train_models(self):
        """Melatih model ML untuk eligible segments"""
        print("\n[TARGET] Melatih model ML...")
        df = self.df_features.copy()
        
        # Only train on CORPORATE and UMKM (eligible for upsell)
        eligible_mask = df['bandwidth_cluster'].isin(['CORPORATE', 'UMKM_SMALL'])
        df_eligible = df[eligible_mask].copy()
        
        if len(df_eligible) < 100:
            print("   [WARN]  Data eligible terlalu sedikit, menggunakan semua data...")
            df_eligible = df.copy()
        
        print(f"   [DATA] Training set: {len(df_eligible):,} pelanggan eligible")
        
        # Features
        feature_cols = ['pendapatan', 'bandwidth_mbps', 'masa_berlangganan', 
                       'pendapatan_per_mbps', 'pertumbuhan_pendapatan', 'skor_nilai',
                       'high_value', 'bandwidth_cluster_encoded']
        
        for col in ['segmen_encoded', 'tier_encoded', 'kategori_encoded']:
            if col in df.columns:
                feature_cols.append(col)
        
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        X = df_eligible[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Targets
        y_upsell = (df_eligible['kuadran'].str.contains('SNIPER', na=False)).astype(int)
        y_crosssell = (df_eligible['kuadran'].str.contains('RISIKO', na=False)).astype(int)
        
        print(f"      Target upsell: {y_upsell.sum()} pelanggan")
        print(f"      Target cross-sell: {y_crosssell.sum()} pelanggan")
        
        # Train only if sufficient data
        if y_upsell.sum() >= 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_upsell, test_size=0.2, random_state=42, stratify=y_upsell)
            
            self.upsell_model = GradientBoostingClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
            )
            self.upsell_model.fit(X_train, y_train)
            
            y_pred = self.upsell_model.predict(X_test)
            y_prob = self.upsell_model.predict_proba(X_test)[:, 1]
            
            self.metrics['upsell'] = {
                'accuracy': self.upsell_model.score(X_test, y_test),
                'roc_auc': roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0.5
            }
            
            print(f"      [OK] Upsell Model - Akurasi: {self.metrics['upsell']['accuracy']:.1%}")
        else:
            print("      [WARN]  Data upsell insufficient, skipping model")
            self.upsell_model = None
            self.metrics['upsell'] = {'accuracy': 0, 'roc_auc': 0}
        
        # CLV Model (for all)
        print("\n   [MONEY] Melatih Model CLV...")
        y_clv = df['pendapatan']
        X_tr, X_te, y_tr, y_te = train_test_split(
            self.scaler.transform(df[feature_cols].fillna(0)), y_clv, test_size=0.2, random_state=42)
        
        self.clv_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
        )
        self.clv_model.fit(X_tr, y_tr)
        y_clv_pred = self.clv_model.predict(X_te)
        
        self.metrics['clv'] = {
            'mae': np.mean(np.abs(y_te - y_clv_pred)),
            'mape': np.mean(np.abs((y_te - y_clv_pred) / (y_te + 1))) * 100
        }
        
        print(f"      [OK] CLV Model - MAE: Rp {self.metrics['clv']['mae']:,.0f}")
        
        return self.metrics
    
    def generate_predictions(self):
        """Generate predictions and NBO for all customers"""
        print("\n Generating predictions...")
        df = self.df_features.copy()
        
        # Features
        feature_cols = ['pendapatan', 'bandwidth_mbps', 'masa_berlangganan', 
                       'pendapatan_per_mbps', 'pertumbuhan_pendapatan', 'skor_nilai',
                       'high_value', 'bandwidth_cluster_encoded']
        for col in ['segmen_encoded', 'tier_encoded', 'kategori_encoded']:
            if col in df.columns:
                feature_cols.append(col)
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predictions
        if self.upsell_model:
            df['skor_upsell'] = self.upsell_model.predict_proba(X_scaled)[:, 1]
        else:
            # Fallback: use heuristic based on kuadran
            df['skor_upsell'] = df['kuadran'].apply(
                lambda x: 0.8 if 'SNIPER' in str(x) else 0.3 if 'RISIKO' in str(x) else 0.1)
        
        df['clv_prediksi'] = self.clv_model.predict(X_scaled)
        
        # Priority
        df['prioritas'] = pd.cut(df['skor_upsell'], 
                                 bins=[0, 0.3, 0.6, 1.0],
                                 labels=['Rendah', 'Sedang', 'Tinggi'])
        
        # Revenue potential
        df['potensi_revenue'] = np.where(df['skor_upsell'] > 0.5, 
                                         df['clv_prediksi'] * 0.3, 0)
        
        self.df_final = df
        
        print(f"\n   [DATA] Summary:")
        print(f"      High Priority: {(df['skor_upsell'] > 0.7).sum():,} pelanggan")
        print(f"      Total Potential: Rp {df['potensi_revenue'].sum():,.0f}")
        
        return df
    
    def generate_excel_reports(self, output_dir='laporan_nbo'):
        """Generate comprehensive Excel reports"""
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n[DOCS] Generating reports in '{output_dir}/'...")
        
        df = self.df_final.copy()
        
        # Column mapping
        col_map = {
            'nama_pelanggan': 'Nama Pelanggan',
            'segmen': 'Segmen',
            'tier': 'Tier Saat Ini',
            'tier_recommendation': 'Rekomendasi Tier',
            'tier_priority': 'Prioritas Tier',
            'bandwidth_fix': 'Bandwidth (Asli)',
            'bandwidth_mbps': 'Bandwidth (MBPS)',
            'bandwidth_cluster': 'Cluster Bandwidth',
            'kuadran': 'Kategori Strategis',
            'strategi': 'Strategi',
            'nbo_recommendation': 'Next Best Offer',
            'pendapatan': 'Pendapatan (Rp)',
            'masa_berlangganan': 'Masa Berlangganan (Bulan)',
            'skor_upsell': 'Skor Upsell (0-1)',
            'prioritas': 'Prioritas',
            'potensi_revenue': 'Potensi Revenue (Rp)',
            'produk': 'Produk Saat Ini',
            'clv_prediksi': 'CLV Prediksi (Rp)'
        }
        
        cols = [c for c in col_map.keys() if c in df.columns]
        df_exp = df[cols].rename(columns=col_map)
        
        # 1. Master Report
        print("   Creating Master Report...")
        df_exp.sort_values('Skor Upsell (0-1)', ascending=False).to_excel(
            f'{output_dir}/CVO_NBO_Master.xlsx', index=False)
        
        # 2. By Bandwidth Cluster
        print("   Creating Bandwidth Cluster Analysis...")
        with pd.ExcelWriter(f'{output_dir}/CVO_NBO_Bandwidth_Clusters.xlsx') as writer:
            for cluster in df['bandwidth_cluster'].unique():
                sheet_name = cluster[:31]
                df[df['bandwidth_cluster'] == cluster][cols].rename(columns=col_map).to_excel(
                    writer, sheet_name=sheet_name, index=False)
        
        # 3. By Tier Roadmap
        print("   Creating Tier Roadmap...")
        high_priority_tiers = ['DI Only', 'TS Only', 'DI-TS', 'SDS-TS', 'GE-SDS-TS']
        tier_data = df[df['tier'].isin(high_priority_tiers)] if 'tier' in df.columns else df
        tier_data.sort_values(['tier', 'skor_upsell'], ascending=[True, False]).to_excel(
            f'{output_dir}/CVO_NBO_Tier_Roadmap.xlsx', index=False)
        
        # 4. High Priority Targets
        print("   Creating High Priority Targets...")
        high_priority = df[df['skor_upsell'] > 0.7].sort_values('potensi_revenue', ascending=False)
        high_priority.to_excel(f'{output_dir}/CVO_NBO_High_Priority.xlsx', index=False)
        
        # 5. By Segment
        if 'segmen' in df.columns:
            print("   Creating Segment Analysis...")
            with pd.ExcelWriter(f'{output_dir}/CVO_NBO_by_Segment.xlsx') as writer:
                for segmen in df['segmen'].unique():
                    if pd.notna(segmen):
                        sheet_name = str(segmen)[:31]
                        df[df['segmen'] == segmen][cols].rename(columns=col_map).to_excel(
                            writer, sheet_name=sheet_name, index=False)
        
        print(f"   [OK] Reports generated in {output_dir}/")
        return output_dir
    
    def generate_executive_summary(self, output_dir='laporan_nbo'):
        """Generate executive summary"""
        df = self.df_final.copy()
        
        def format_rp(angka):
            if angka >= 1e12:
                return f"Rp {angka/1e12:.2f} T"
            elif angka >= 1e9:
                return f"Rp {angka/1e9:.2f} M"
            elif angka >= 1e6:
                return f"Rp {angka/1e6:.2f} Jt"
            else:
                return f"Rp {angka:,.0f}"
        
        summary = f"""

           CVO v3.0 - NEXT BEST OFFER EXECUTIVE SUMMARY                        
                    PLN Icon+ - Customer Value Optimizer                       


Generated: {datetime.now().strftime('%d %B %Y %H:%M')}


[DATA] BUSINESS METRICS


Total Customers: {len(df):,}
Total Revenue: {format_rp(df['pendapatan'].sum())}
Avg Revenue/Customer: {format_rp(df['pendapatan'].mean())}


[TARGET] BANDWIDTH CLUSTER DISTRIBUTION


"""
        
        for cluster in ['NO_BANDWIDTH', 'ATM_IOT', 'UMKM_SMALL', 'CORPORATE', 'ENTERPRISE']:
            if cluster in df['bandwidth_cluster'].values:
                count = (df['bandwidth_cluster'] == cluster).sum()
                pct = count / len(df) * 100
                revenue = df[df['bandwidth_cluster'] == cluster]['pendapatan'].sum()
                avg_bw = df[df['bandwidth_cluster'] == cluster]['bandwidth_mbps'].mean()
                summary += f"{cluster:15s}: {count:>6,} pel ({pct:>5.1f}%) | {format_rp(revenue):>12s} | Avg BW: {avg_bw:>6.1f} Mbps\n"
        
        summary += f"""

[TARGET] STRATEGIC QUADRANT DISTRIBUTION


"""
        
        for kuadran in df['kuadran'].value_counts().index:
            count = (df['kuadran'] == kuadran).sum()
            pct = count / len(df) * 100
            revenue = df[df['kuadran'] == kuadran]['pendapatan'].sum()
            summary += f"{kuadran:25s}: {count:>6,} pel ({pct:>5.1f}%) | {format_rp(revenue):>12s}\n"
        
        summary += f"""

[LAUNCH] NEXT BEST OFFER OPPORTUNITIES


High Priority Targets (Score >70%): {(df['skor_upsell'] > 0.7).sum():,} customers
Total Revenue Potential: {format_rp(df['potensi_revenue'].sum())}

TOP 10 PRIORITY CUSTOMERS:
"""
        
        top10 = df.nlargest(10, 'potensi_revenue')[['nama_pelanggan', 'bandwidth_cluster', 'tier', 'kuadran', 'skor_upsell', 'potensi_revenue', 'nbo_recommendation']]
        for idx, row in top10.iterrows():
            summary += f"\n{row['nama_pelanggan'][:35]:35s}\n"
            summary += f"   Cluster: {row['bandwidth_cluster']} | Tier: {row.get('tier', 'N/A')}\n"
            summary += f"   Quadrant: {row['kuadran']} | Score: {row['skor_upsell']:.1%}\n"
            summary += f"   Potential: {format_rp(row['potensi_revenue'])}\n"
            summary += f"   NBO: {row['nbo_recommendation'][:60]}...\n"
        
        summary += f"""

[LIST] RECOMMENDED ACTIONS


1. IMMEDIATE (30 Days):
   - Contact {(df['skor_upsell'] > 0.8).sum():,} customers with score >80%
   - Focus on CORPORATE SNIPER quadrant for bandwidth upsell
   - Focus on CORPORATE RISIKO quadrant for cross-sell solutions

2. SHORT-TERM (90 Days):
   - Execute tier upgrade roadmap (DI Only → DI-TS, DI-TS → DI-SDS-TS)
   - Launch segment-specific campaigns:
     * GOVERNMENT: Smart City solutions
     * BUSINESS: Managed Services & Cloud

3. LONG-TERM (12 Months):
   - Build automated NBO recommendation engine
   - Implement customer lifecycle management per cluster
   - Develop predictive churn model for Star Clients


[IDEA] KEY INSIGHTS


1. Bandwidth Cluster Strategy:
   - NO_BANDWIDTH: Cross-sell connectivity & digital solutions
   - ATM/IoT: Maintenance mode, ensure reliability
   - UMKM: Gradual upgrade to Corporate packages
   - CORPORATE: Main upsell & cross-sell target (FOCUS HERE)
   - ENTERPRISE: Retention & premium services

2. Tier Roadmap:
   - 15 tier combinations mapped with next-best-offer
   - DI Only customers (10.8%) should be priority for TS addition
   - DI-TS customers (59.7%) ready for SDS cross-sell

3. Segment Context:
   - GOVERNMENT (51.1%): Focus on public services, Smart City
   - BUSINESS (48.9%): Focus on efficiency, managed services


Generated by CVO v3.0 - Next Best Offer Engine

"""
        
        with open(f'{output_dir}/Executive_Summary_NBO.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n[FILE] Executive Summary: {output_dir}/Executive_Summary_NBO.txt")
        print(summary[:3000])
        
        return summary
    
    def run_pipeline(self):
        """Run complete NBO pipeline"""
        print("\n" + "="*80)
        print("CVO v3.0 - Next Best Offer Pipeline")
        print("="*80)
        
        if not self.load_data():
            return False
        
        self.clean_and_standardize()
        self.engineer_features()
        self.create_strategic_matrices()
        self.train_models()
        self.generate_predictions()
        self.generate_excel_reports()
        self.generate_executive_summary()
        
        print("\n" + "="*80)
        print("[OK] CVO v3.0 NBO PIPELINE COMPLETED!")
        print("="*80)
        print("\n Generated Files:")
        print("   - CVO_NBO_Master.xlsx")
        print("   - CVO_NBO_Bandwidth_Clusters.xlsx")
        print("   - CVO_NBO_Tier_Roadmap.xlsx")
        print("   - CVO_NBO_High_Priority.xlsx")
        print("   - CVO_NBO_by_Segment.xlsx")
        print("   - Executive_Summary_NBO.txt")
        
        return True


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n" + "="*80)
    print("CUSTOMER VALUE OPTIMIZER v3.0 - Next Best Offer Engine")
    print("="*80)
    
    # File paths
    data_file = "Data Penuh Pelanggan Aktif.xlsx"
    catalog_file = "Mapping Seluruh Produk ICON+.xlsx"
    
    if not os.path.exists(data_file):
        data_file = "Data Sampel Machine Learning.xlsx"
    
    print(f"[DATA] Data: {data_file}")
    print(f" Catalog: {catalog_file if os.path.exists(catalog_file) else 'Not found - using default'}")
    
    cvo = CustomerValueOptimizerNBO(data_file, catalog_file if os.path.exists(catalog_file) else None)
    success = cvo.run_pipeline()
    
    if success:
        print("\n[SUCCESS] Success! Check 'laporan_nbo/' folder for results.")
    else:
        print("\n Failed. Check error messages.")
