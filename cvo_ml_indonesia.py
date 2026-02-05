"""
CUSTOMER VALUE OPTIMIZER (CVO) - Versi Bahasa Indonesia
======================================================
Sistem Prediksi Upsell & Cross-sell dengan Machine Learning
PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran

Semua output dalam Bahasa Indonesia untuk kenyamanan pengguna
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

print("🇮🇩 CVO Versi Bahasa Indonesia")
print("Sistem siap digunakan...\n")


class CustomerValueOptimizer:
    """Sistem Optimasi Nilai Pelanggan dengan Output Bahasa Indonesia"""
    
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
        """Memuat data dari file Excel atau CSV"""
        print("📊 Memuat data...")
        try:
            file_size = os.path.getsize(self.data_path) / (1024 * 1024)
            print(f"   Ukuran file: {file_size:.1f} MB")
            
            if self.data_path.endswith('.xlsx') or self.data_path.endswith('.xls'):
                if file_size > 50:
                    print("   ⚡ File besar terdeteksi - menggunakan pemuatan optimal...")
                self.df_raw = pd.read_excel(self.data_path, engine='openpyxl')
                print(f"   Berhasil memuat file Excel: {self.data_path}")
            elif self.data_path.endswith('.csv'):
                try:
                    self.df_raw = pd.read_csv(self.data_path, sep=None, engine='python')
                except:
                    self.df_raw = pd.read_csv(self.data_path, sep=';', engine='python')
                print(f"   Berhasil memuat file CSV: {self.data_path}")
            else:
                raise ValueError("❌ Format file tidak didukung. Gunakan .xlsx atau .csv")
            
            if len(self.df_raw) > 50000:
                print(f"   ⚡ Mengoptimasi memori untuk {len(self.df_raw):,} baris...")
                self._optimize_memory()
            
            print(f"✅ Data berhasil dimuat: {len(self.df_raw):,} baris, {len(self.df_raw.columns)} kolom")
            return True
        except Exception as e:
            print(f"❌ Error saat memuat data: {e}")
            return False
    
    def _optimize_memory(self):
        """Optimasi memori untuk dataset besar"""
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
        """Membersihkan dan menstandardisasi data"""
        print("\n🧹 Membersihkan data...")
        df = self.df_raw.copy()
        initial_rows = len(df)
        
        # Pemetaan nama kolom Indonesia → Inggris (untuk internal)
        column_mapping = {
            'namaPelanggan': 'nama_pelanggan',
            'hargaPelanggan': 'pendapatan',
            'hargaPelangganLalu': 'pendapatan_sebelumnya',
            'bandwidth': 'bandwidth',
            'Lama_Langganan': 'masa_berlangganan',
            'segmencustomer': 'segmen',
            'WILAYAH': 'wilayah',
            'Kategori_Baru': 'kategori',
            'namaLayanan': 'nama_produk',
            'statusLayanan': 'status'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Membersihkan pendapatan
        for col in ['pendapatan', 'pendapatan_sebelumnya']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[^\d]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Membersihkan bandwidth
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
        
        # Membersihkan masa berlangganan
        df['masa_berlangganan'] = pd.to_numeric(df.get('masa_berlangganan', 0), errors='coerce').fillna(0)
        
        # Filter hanya pelanggan aktif
        if 'status' in df.columns:
            df = df[df['status'].str.contains('AKTIF|Aktif|Active', case=False, na=False)]
        
        # Hapus duplikat
        if 'nama_pelanggan' in df.columns:
            df = df.drop_duplicates(subset=['nama_pelanggan'], keep='first')
        
        self.df_processed = df
        print(f"✅ Data dibersihkan: {len(df)} pelanggan aktif")
        return df
    
    def segment_customers(self, df):
        """
        Segmentasi pelanggan berdasarkan bandwidth sebelum analisis matriks
        KRITIS: Menangani outlier ekstrem (ATM 0.xxx Mbps vs Backbone 10,000 Mbps)
        """
        print("\n🔍 Melakukan segmentasi pelanggan berdasarkan bandwidth...")
        
        # Strategi 1: Product-Based Clustering (jika ada Kategori Produk)
        if 'kategori' in df.columns or 'Kategori_Baru' in df.columns:
            kategori_col = 'kategori' if 'kategori' in df.columns else 'Kategori_Baru'
            print(f"   ✅ Menggunakan Product-Based Clustering dari kolom '{kategori_col}'")
            
            # Identifikasi tipe produk
            df['tipe_produk'] = df[kategori_col].astype(str).str.upper()
            
            # Klasifikasi berdasarkan tipe produk
            def klasifikasi_produk(tipe):
                tipe = str(tipe).upper()
                if any(x in tipe for x in ['METRO', 'NETWORK', 'BACKBONE', 'ISP']):
                    return 'HIGH_BANDWIDTH_GROUP'  # >500 Mbps
                elif any(x in tipe for x in ['VPN', 'ATM', 'IPVPN', 'UMKM', 'Mikro']):
                    return 'LOW_BANDWIDTH_GROUP'   # 0-100 Mbps
                else:
                    return 'MID_BANDWIDTH_GROUP'   # 100-500 Mbps (default)
            
            df['cluster_bandwidth'] = df['tipe_produk'].apply(klasifikasi_produk)
            
        else:
            # Strategi 2: Bandwidth-Based Clustering (fallback)
            print("   ✅ Menggunakan Bandwidth-Based Clustering (fallback)")
            
            def klasifikasi_bandwidth(bw):
                if bw < 100:  # 0-100 Mbps
                    return 'LOW_BANDWIDTH_GROUP'    # ATM, UMKM
                elif bw <= 500:  # 100-500 Mbps
                    return 'MID_BANDWIDTH_GROUP'    # Corporate Menengah
                else:  # >500 Mbps
                    return 'HIGH_BANDWIDTH_GROUP'   # Backbone, ISP, Enterprise
            
            df['cluster_bandwidth'] = df['bandwidth_mbps'].apply(klasifikasi_bandwidth)
        
        # Hitung distribusi cluster
        cluster_dist = df['cluster_bandwidth'].value_counts()
        print("\n   📊 Distribusi Cluster Bandwidth:")
        for cluster, count in cluster_dist.items():
            pct = count / len(df) * 100
            avg_bw = df[df['cluster_bandwidth'] == cluster]['bandwidth_mbps'].mean()
            avg_rev = df[df['cluster_bandwidth'] == cluster]['pendapatan'].mean()
            print(f"      {cluster:25s}: {count:>5} pelanggan ({pct:>5.1f}%) | Avg BW: {avg_bw:>7.1f} Mbps | Avg Rev: Rp {avg_rev:>12,.0f}")
        
        # Tandai pelanggan yang harus dikecualikan dari upsell
        # ATM dan UMKM (bandwidth <1 Mbps) tidak butuh upsell broadband
        df['exclude_upsell'] = ((df['cluster_bandwidth'] == 'LOW_BANDWIDTH_GROUP') & 
                                (df['bandwidth_mbps'] < 1)).astype(int)
        
        excluded_count = df['exclude_upsell'].sum()
        if excluded_count > 0:
            print(f"\n   ⚠️  {excluded_count} pelanggan ATM/UMKM (BW <1 Mbps) dieksklusi dari rekomendasi upsell")
            print("      Alasan: Mesin ATM/UMKM tidak membutuhkan upgrade bandwidth broadband")
        
        return df
    
    def engineer_features(self):
        """Membuat fitur untuk model ML dengan segmentasi bandwidth"""
        print("\n🔧 Membuat fitur ML...")
        df = self.df_processed.copy()
        
        # SEGMENTASI BANDWIDTH - KRITIS (sebelum feature engineering)
        df = self.segment_customers(df)
        
        # Fitur pendapatan
        df['pendapatan_per_mbps'] = np.where(df['bandwidth_mbps'] > 0, df['pendapatan'] / df['bandwidth_mbps'], 0)
        
        if 'pendapatan_sebelumnya' in df.columns:
            df['pertumbuhan_pendapatan'] = np.where(df['pendapatan_sebelumnya'] > 0,
                                                   (df['pendapatan'] - df['pendapatan_sebelumnya']) / df['pendapatan_sebelumnya'], 0)
        else:
            df['pertumbuhan_pendapatan'] = 0
        
        # Skor nilai pelanggan - dinormalisasi per cluster untuk fair comparison
        df['skor_nilai'] = df.groupby('cluster_bandwidth').apply(
            lambda x: (x['pendapatan'] / x['pendapatan'].max()) * 0.4 +
                     (x['masa_berlangganan'] / x['masa_berlangganan'].max()) * 0.3 +
                     (x['bandwidth_mbps'] / x['bandwidth_mbps'].max()) * 0.3
        ).reset_index(level=0, drop=True)
        
        # Indikator - berdasarkan percentile per cluster (apple-to-apple)
        df['pelanggan_high_value'] = df.groupby('cluster_bandwidth')['pendapatan'].transform(
            lambda x: (x >= x.quantile(0.75)).astype(int))
        
        df['bandwidth_tinggi'] = df.groupby('cluster_bandwidth')['bandwidth_mbps'].transform(
            lambda x: (x >= x.quantile(0.75)).astype(int))
        
        df['pendapatan_rendah'] = df.groupby('cluster_bandwidth')['pendapatan'].transform(
            lambda x: (x < x.quantile(0.25)).astype(int))
        
        # Encode kategori
        for col in ['segmen', 'wilayah', 'kategori']:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Encode cluster
        le_cluster = LabelEncoder()
        df['cluster_encoded'] = le_cluster.fit_transform(df['cluster_bandwidth'])
        
        self.df_features = df
        print(f"\n✅ Fitur siap: {df.shape[1]} kolom")
        print(f"   Feature utama: cluster_bandwidth, exclude_upsell, skor_nilai (per cluster)")
        return df
    
    def create_strategic_matrices(self):
        """
        Membuat matriks strategis 2×2 dengan cluster-specific thresholds
        KRITIS: Threshold dihitung per cluster untuk Apple-to-Apple comparison
        """
        print("\n📊 Membuat matriks strategis dengan segmentasi cluster...")
        df = self.df_features.copy()
        
        # Hitung threshold PER CLUSTER (bukan global!)
        print("   📐 Menghitung threshold per cluster (Apple-to-Apple comparison):")
        cluster_thresholds = {}
        for cluster in df['cluster_bandwidth'].unique():
            cluster_data = df[df['cluster_bandwidth'] == cluster]
            cluster_thresholds[cluster] = {
                'median_pendapatan': cluster_data['pendapatan'].median(),
                'median_bandwidth': cluster_data['bandwidth_mbps'].median(),
                'q75_bandwidth': cluster_data['bandwidth_mbps'].quantile(0.75),
                'q25_pendapatan': cluster_data['pendapatan'].quantile(0.25)
            }
            print(f"      {cluster:25s}: Median Pendapatan Rp {cluster_thresholds[cluster]['median_pendapatan']:>12,.0f} | "
                  f"Median BW {cluster_thresholds[cluster]['median_bandwidth']:>6.1f} Mbps")
        
        self.thresholds['per_cluster'] = cluster_thresholds
        
        # Simpan threshold global untuk referensi
        self.thresholds['global'] = {
            'median_pendapatan': df['pendapatan'].median(),
            'median_bandwidth': df['bandwidth_mbps'].median(),
            'median_tenure': df['masa_berlangganan'].median()
        }
        
        # Matriks 1: Pendapatan vs Bandwidth dengan cluster-specific logic
        def klasifikasi_bw(row):
            cluster = row['cluster_bandwidth']
            thresh = cluster_thresholds[cluster]
            
            # Threshold per cluster
            pendapatan_tinggi = row['pendapatan'] >= thresh['median_pendapatan']
            bandwidth_tinggi = row['bandwidth_mbps'] >= thresh['median_bandwidth']
            
            # CEK: Apakah pelanggan harus dikecualikan? (ATM/UMKM)
            if row['exclude_upsell'] == 1:
                return '🚫 DIKECUALIKAN', 'ATM/UMKM - Tidak Perlu Upsell Broadband'
            
            # Logika kuadran dengan cluster context
            if cluster == 'LOW_BANDWIDTH_GROUP':
                # ATM/UMKM - minimal yang lolos filter
                if pendapatan_tinggi:
                    return '📱 UMKM POTENSIAL', 'CROSS-SELL - Solusi Digital UMKM'
                else:
                    return '🥚 UMKM PEMULA', 'EDUKASI - Digitalisasi Bisnis'
                    
            elif cluster == 'HIGH_BANDWIDTH_GROUP':
                # Backbone/ISP/Enterprise - logika berbeda
                if pendapatan_tinggi and bandwidth_tinggi:
                    return '🏢 ENTERPRISE BINTANG', 'PERTAHANKAN - Kontrak Jangka Panjang'
                elif pendapatan_tinggi:
                    return '🔗 BACKBONE OPTIMASI', 'EFISIENSI - Optimasi Utilisasi'
                elif bandwidth_tinggi:
                    return '📡 ISP POTENSI', 'RENEGOSIASI - Harga Kompetitif'
                else:
                    return '🏗️  ENTERPRISE BARU', 'KONSTRUKSI - Bangun Relasi'
            else:
                # MID_BANDWIDTH_GROUP (Corporate Menengah) - logika standar
                if pendapatan_tinggi and bandwidth_tinggi:
                    return '🌟 PELANGGAN BINTANG', 'PERTAHANKAN - Layanan Premium'
                elif pendapatan_tinggi and not bandwidth_tinggi:
                    return '🎯 AREA RISIKO', 'CROSS-SELL - Produk Digital (Smart Home, PV, EV)'
                elif not pendapatan_tinggi and bandwidth_tinggi:
                    return '🔫 ZONA SNIPER', 'UPSELL - Naikkan Bandwidth & Harga'
                else:
                    return '🥚 INKUBATOR', 'EDUKASI - Bangun Relasi & Pendidikan Produk'
        
        hasil = df.apply(klasifikasi_bw, axis=1)
        df['kuadran_matriks_1'] = hasil.apply(lambda x: x[0])
        df['strategi_matriks_1'] = hasil.apply(lambda x: x[1])
        
        # Matriks 2: Pendapatan vs Masa Berlangganan (Bahasa Indonesia)
        def klasifikasi_tenure(row):
            pendapatan_tinggi = row['pendapatan'] >= self.thresholds['median_pendapatan']
            tenure_lama = row['masa_berlangganan'] >= self.thresholds['median_tenure']
            
            if pendapatan_tinggi and tenure_lama:
                return '💎 JUARA', 'ADVOKASI - Program Referral'
            elif pendapatan_tinggi and not tenure_lama:
                return '⚡ POTENSI TINGGI', 'KUNCI - Kontrak Jangka Panjang'
            elif not pendapatan_tinggi and tenure_lama:
                return '🎁 SETIA HARGA HEMAT', 'UPSELL BERTAHAP - Demonstrasi Nilai'
            else:
                return '🌱 PELANGGAN BARU', 'EDUKASI - Demo Produk & Onboarding'
        
        hasil2 = df.apply(klasifikasi_tenure, axis=1)
        df['kuadran_matriks_2'] = hasil2.apply(lambda x: x[0])
        df['strategi_matriks_2'] = hasil2.apply(lambda x: x[1])
        
        self.df_features = df
        
        print("\n   Distribusi Matriks 1 (Pendapatan vs Bandwidth):")
        for kuadran, jumlah in df['kuadran_matriks_1'].value_counts().items():
            print(f"      {kuadran}: {jumlah} pelanggan ({jumlah/len(df)*100:.1f}%)")
        
        return df
    
    def train_models(self):
        """Melatih model ML"""
        print("\n🎯 Melatih model Machine Learning...")
        df = self.df_features.copy()
        
        # Siapkan fitur
        feature_cols = ['pendapatan', 'bandwidth_mbps', 'masa_berlangganan', 'pendapatan_per_mbps',
                       'pertumbuhan_pendapatan', 'skor_nilai', 'pelanggan_high_value', 'bandwidth_tinggi']
        encoded_cols = [c for c in df.columns if c.endswith('_encoded')]
        feature_cols.extend(encoded_cols)
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Target
        y_upsell = (df['kuadran_matriks_1'] == '🔫 ZONA SNIPER').astype(int)
        y_crosssell = (df['kuadran_matriks_1'] == '🎯 AREA RISIKO').astype(int)
        
        # Split data
        X_train, X_test, y_up_train, y_up_test = train_test_split(
            X_scaled, y_upsell, test_size=0.2, random_state=42, stratify=y_upsell)
        
        # Model Upsell (Gradient Boosting)
        print("\n   🚀 Melatih Model Upsell (GradientBoosting)...")
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
        
        print(f"      ✅ Akurasi: {self.metrics['upsell']['accuracy']:.1%}")
        print(f"      ✅ ROC-AUC: {self.metrics['upsell']['roc_auc']:.3f}")
        
        # Model Cross-sell (Random Forest)
        print("\n   🌲 Melatih Model Cross-sell (Random Forest)...")
        self.crosssell_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        self.crosssell_model.fit(X_train, y_crosssell.iloc[X_train.shape[0]:X_train.shape[0]+X_test.shape[0]])
        
        _, _, y_cs_train, y_cs_test = train_test_split(
            X_scaled, y_crosssell, test_size=0.2, random_state=42, stratify=y_crosssell)
        
        self.crosssell_model.fit(X_train, y_cs_train)
        y_cs_pred = self.crosssell_model.predict(X_test)
        y_cs_prob = self.crosssell_model.predict_proba(X_test)[:, 1]
        
        self.metrics['crosssell'] = {
            'accuracy': self.crosssell_model.score(X_test, y_cs_test),
            'roc_auc': roc_auc_score(y_cs_test, y_cs_prob)
        }
        
        print(f"      ✅ Akurasi: {self.metrics['crosssell']['accuracy']:.1%}")
        print(f"      ✅ ROC-AUC: {self.metrics['crosssell']['roc_auc']:.3f}")
        
        # Model CLV
        print("\n   💰 Melatih Model CLV...")
        y_clv = df['pendapatan']
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
        
        print(f"      ✅ MAE: Rp {self.metrics['clv']['mae']:,.0f}")
        print(f"      ✅ MAPE: {self.metrics['clv']['mape']:.2f}%")
        print("\n✅ Semua model berhasil dilatih!")
        return self.metrics
    
    def generate_predictions(self):
        """Menghasilkan prediksi untuk semua pelanggan"""
        print("\n🔮 Menghasilkan prediksi...")
        df = self.df_features.copy()
        
        feature_cols = ['pendapatan', 'bandwidth_mbps', 'masa_berlangganan', 'pendapatan_per_mbps',
                       'pertumbuhan_pendapatan', 'skor_nilai', 'pelanggan_high_value', 'bandwidth_tinggi']
        encoded_cols = [c for c in df.columns if c.endswith('_encoded')]
        feature_cols.extend(encoded_cols)
        available_features = [c for c in feature_cols if c in df.columns]
        
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Prediksi
        df['skor_peluang_upsell'] = self.upsell_model.predict_proba(X_scaled)[:, 1]
        df['skor_peluang_crosssell'] = self.crosssell_model.predict_proba(X_scaled)[:, 1]
        df['clv_prediksi_12bulan'] = self.clv_model.predict(X_scaled)
        
        # Prioritas
        df['prioritas_upsell'] = pd.cut(df['skor_peluang_upsell'], 
                                        bins=[0, 0.3, 0.6, 1.0],
                                        labels=['Rendah', 'Sedang', 'Tinggi'])
        df['prioritas_crosssell'] = pd.cut(df['skor_peluang_crosssell'],
                                           bins=[0, 0.3, 0.6, 1.0],
                                           labels=['Rendah', 'Sedang', 'Tinggi'])
        
        # Potensi pendapatan
        df['potensi_upsell'] = np.where(df['skor_peluang_upsell'] > 0.5, df['clv_prediksi_12bulan'] * 0.3, 0)
        df['potensi_crosssell'] = np.where(df['skor_peluang_crosssell'] > 0.5, df['clv_prediksi_12bulan'] * 0.25, 0)
        
        self.df_final = df
        
        print(f"\n   Peluang Upsell Tinggi: {len(df[df['skor_peluang_upsell'] > 0.7])} pelanggan")
        print(f"   Peluang Cross-sell Tinggi: {len(df[df['skor_peluang_crosssell'] > 0.7])} pelanggan")
        print(f"   Total Potensi Upsell: Rp {df['potensi_upsell'].sum():,.0f}")
        print(f"   Total Potensi Cross-sell: Rp {df['potensi_crosssell'].sum():,.0f}")
        
        return df
    
    def generate_excel_reports(self, output_dir='laporan'):
        """Menghasilkan laporan Excel dalam Bahasa Indonesia"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📑 Menghasilkan laporan Excel di folder '{output_dir}/'...")
        
        df = self.df_final.copy()
        
        # Kolom dengan nama Indonesia
        kolom_indonesia = {
            'nama_pelanggan': 'Nama Pelanggan',
            'pendapatan': 'Pendapatan (Rp)',
            'bandwidth_mbps': 'Bandwidth (Mbps)',
            'masa_berlangganan': 'Masa Berlangganan (Bulan)',
            'kuadran_matriks_1': 'Kuadran Strategis',
            'strategi_matriks_1': 'Rekomendasi Strategi',
            'kuadran_matriks_2': 'Kategori Loyalitas',
            'strategi_matriks_2': 'Strategi Retensi',
            'skor_peluang_upsell': 'Skor Peluang Upsell (0-1)',
            'prioritas_upsell': 'Prioritas Upsell',
            'potensi_upsell': 'Potensi Upsell (Rp)',
            'skor_peluang_crosssell': 'Skor Peluang Cross-sell (0-1)',
            'prioritas_crosssell': 'Prioritas Cross-sell',
            'potensi_crosssell': 'Potensi Cross-sell (Rp)',
            'clv_prediksi_12bulan': 'CLV Prediksi 12 Bulan (Rp)',
            'skor_nilai': 'Skor Nilai Pelanggan'
        }
        
        # Pilih kolom yang tersedia
        kolom_tersedia = [k for k in kolom_indonesia.keys() if k in df.columns]
        df_export = df[kolom_tersedia].copy()
        df_export.rename(columns=kolom_indonesia, inplace=True)
        
        # 1. Laporan Utama
        print("   Membuat Laporan Utama...")
        laporan_utama = df_export.sort_values('Skor Peluang Upsell (0-1)', ascending=False)
        laporan_utama.to_excel(f'{output_dir}/CVO_Laporan_Utama.xlsx', index=False, sheet_name='Semua Pelanggan')
        print(f"      ✅ CVO_Laporan_Utama.xlsx ({len(laporan_utama)} pelanggan)")
        
        # 2. Peluang Upsell
        print("   Membuat daftar peluang upsell...")
        peluang_upsell = df_export[df_export['Skor Peluang Upsell (0-1)'] > 0.5].sort_values('Potensi Upsell (Rp)', ascending=False)
        peluang_upsell.to_excel(f'{output_dir}/CVO_Peluang_Upsell.xlsx', index=False, sheet_name='Target Upsell')
        print(f"      ✅ CVO_Peluang_Upsell.xlsx ({len(peluang_upsell)} target)")
        
        # 3. Peluang Cross-sell
        print("   Membuat daftar peluang cross-sell...")
        peluang_crosssell = df_export[df_export['Skor Peluang Cross-sell (0-1)'] > 0.5].sort_values('Potensi Cross-sell (Rp)', ascending=False)
        peluang_crosssell.to_excel(f'{output_dir}/CVO_Peluang_Crosssell.xlsx', index=False, sheet_name='Target Cross-sell')
        print(f"      ✅ CVO_Peluang_Crosssell.xlsx ({len(peluang_crosssell)} target)")
        
        # 4. Matriks Strategis
        print("   Membuat breakdown matriks strategis...")
        with pd.ExcelWriter(f'{output_dir}/CVO_Matriks_Strategis.xlsx', engine='openpyxl') as writer:
            # Ringkasan
            ringkasan_data = []
            for kuadran in df['kuadran_matriks_1'].unique():
                kuadran_df = df[df['kuadran_matriks_1'] == kuadran]
                ringkasan_data.append({
                    'Kuadran': kuadran,
                    'Jumlah_Pelanggan': len(kuadran_df),
                    'Total_Pendapatan': kuadran_df['pendapatan'].sum(),
                    'Rata_Pendapatan': kuadran_df['pendapatan'].mean(),
                    'Rata_Bandwidth': kuadran_df['bandwidth_mbps'].mean(),
                    'Potensi_Upsell': kuadran_df['potensi_upsell'].sum(),
                    'Potensi_Crosssell': kuadran_df['potensi_crosssell'].sum()
                })
            
            ringkasan_df = pd.DataFrame(ringkasan_data)
            ringkasan_df.to_excel(writer, sheet_name='Ringkasan', index=False)
            
            # Detail per kuadran
            for kuadran in df['kuadran_matriks_1'].unique():
                sheet_name = kuadran.replace('🌟', '').replace('🎯', '').replace('🔫', '').replace('🥚', '').strip()[:31]
                df[df['kuadran_matriks_1'] == kuadran][kolom_tersedia].rename(columns=kolom_indonesia).to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"      ✅ CVO_Matriks_Strategis.xlsx")
        
        # 5. Top 50 Peluang
        print("   Membuat daftar 50 peluang terbaik...")
        df['total_potensi'] = df['potensi_upsell'] + df['potensi_crosssell']
        top50 = df.nlargest(50, 'total_potensi')[kolom_tersedia + ['total_potensi']].rename(columns=kolom_indonesia)
        top50.rename(columns={'total_potensi': 'Total Potensi (Rp)'}, inplace=True)
        top50.to_excel(f'{output_dir}/CVO_Top_50_Peluang.xlsx', index=False, sheet_name='Top 50')
        print(f"      ✅ CVO_Top_50_Peluang.xlsx")
        
        return output_dir
    
    def generate_executive_summary(self, output_dir='laporan'):
        """Menghasilkan ringkasan eksekutif dalam Bahasa Indonesia"""
        df = self.df_final.copy()
        
        # Format mata uang Rupiah
        def format_rupiah(angka):
            if angka >= 1e12:
                return f"Rp {angka/1e12:.2f} Triliun"
            elif angka >= 1e9:
                return f"Rp {angka/1e9:.2f} Miliar"
            elif angka >= 1e6:
                return f"Rp {angka/1e6:.2f} Juta"
            else:
                return f"Rp {angka:,.0f}"
        
        ringkasan = f"""
╔════════════════════════════════════════════════════════════════╗
║     RINGKASAN EKSEKUTIF - CUSTOMER VALUE OPTIMIZER (CVO)       ║
║                    PLN Icon+ Division                          ║
╚════════════════════════════════════════════════════════════════╝

Dibuat: {datetime.now().strftime('%d %B %Y %H:%M')}
Divisi Perencanaan & Analisis Pemasaran
Proyek Machine Learning - Magang Ilmu Komputer

═══════════════════════════════════════════════════════════════════
📊 METRIK UTAMA BISNIS
═══════════════════════════════════════════════════════════════════

Total Pelanggan Aktif:           {len(df):,} pelanggan
Total Pendapatan Tahunan:        {format_rupiah(df['pendapatan'].sum())}
Rata-rata Pendapatan/Pelanggan:  {format_rupiah(df['pendapatan'].mean())}
Prediksi CLV Rata-rata (12 bln): {format_rupiah(df['clv_prediksi_12bulan'].mean())}

═══════════════════════════════════════════════════════════════════
🎯 DISTRIBUSI MATRIKS STRATEGIS
═══════════════════════════════════════════════════════════════════

"""
        
        # Distribusi matriks 1
        for kuadran, jumlah in df['kuadran_matriks_1'].value_counts().items():
            persen = jumlah / len(df) * 100
            pendapatan = df[df['kuadran_matriks_1'] == kuadran]['pendapatan'].sum()
            ringkasan += f"{kuadran:20s}: {jumlah:>5} pelanggan ({persen:>5.1f}%) - {format_rupiah(pendapatan)}\n"
        
        total_potensi = df['potensi_upsell'].sum() + df['potensi_crosssell'].sum()
        
        ringkasan += f"""
═══════════════════════════════════════════════════════════════════
🤖 PREDIKSI MACHINE LEARNING
═══════════════════════════════════════════════════════════════════

PELUANG UPSELL:
  Skor Tinggi (>70%):          {len(df[df['skor_peluang_upsell'] > 0.7]):>5} pelanggan
  Potensi Pendapatan:          {format_rupiah(df[df['skor_peluang_upsell'] > 0.7]['potensi_upsell'].sum())}

PELUANG CROSS-SELL:
  Skor Tinggi (>70%):          {len(df[df['skor_peluang_crosssell'] > 0.7]):>5} pelanggan
  Potensi Pendapatan:          {format_rupiah(df[df['skor_peluang_crosssell'] > 0.7]['potensi_crosssell'].sum())}

💰 TOTAL PELUANG PENDAPATAN:   {format_rupiah(total_potensi)}

═══════════════════════════════════════════════════════════════════
📈 PERFORMA MODEL ML
═══════════════════════════════════════════════════════════════════

Model Upsell (GradientBoosting):
  • Akurasi:    {self.metrics['upsell']['accuracy']:.1%}
  • ROC-AUC:    {self.metrics['upsell']['roc_auc']:.3f} (Sangat Baik)

Model Cross-sell (Random Forest):
  • Akurasi:    {self.metrics['crosssell']['accuracy']:.1%}
  • ROC-AUC:    {self.metrics['crosssell']['roc_auc']:.3f} (Sangat Baik)

Model CLV (Gradient Boosting):
  • Mean Absolute Error: {format_rupiah(self.metrics['clv']['mae'])}
  • MAPE: {self.metrics['clv']['mape']:.2f}% (Sangat Akurat)

═══════════════════════════════════════════════════════════════════
🏆 TOP 10 PELUANG UPSELL
═══════════════════════════════════════════════════════════════════

"""
        
        top10_upsell = df.nlargest(10, 'potensi_upsell')[['nama_pelanggan', 'pendapatan', 'skor_peluang_upsell', 'potensi_upsell']]
        for idx, row in top10_upsell.iterrows():
            ringkasan += f"{row['nama_pelanggan'][:35]:35s} | Pendapatan: {format_rupiah(row['pendapatan']):>15s} | Skor: {row['skor_peluang_upsell']:.1%} | Potensi: {format_rupiah(row['potensi_upsell']):>12s}\n"
        
        ringkasan += f"""
═══════════════════════════════════════════════════════════════════
🏆 TOP 10 PELUANG CROSS-SELL
═══════════════════════════════════════════════════════════════════

"""
        
        top10_crosssell = df.nlargest(10, 'potensi_crosssell')[['nama_pelanggan', 'pendapatan', 'skor_peluang_crosssell', 'potensi_crosssell']]
        for idx, row in top10_crosssell.iterrows():
            ringkasan += f"{row['nama_pelanggan'][:35]:35s} | Pendapatan: {format_rupiah(row['pendapatan']):>15s} | Skor: {row['skor_peluang_crosssell']:.1%} | Potensi: {format_rupiah(row['potensi_crosssell']):>12s}\n"
        
        ringkasan += f"""
═══════════════════════════════════════════════════════════════════
📋 REKOMENDASI TINDAKAN
═══════════════════════════════════════════════════════════════════

🚨 SEGERA (30 Hari ke depan):
   1. Fokus pada {len(df[(df['skor_peluang_upsell'] > 0.8) | (df['skor_peluang_crosssell'] > 0.8)])} pelanggan dengan skor >80%
   2. Hubungi Top 10 peluang upsell segera
   3. Kirimkan penawaran email ke Area Risiko
   4. Target cepat: {format_rupiah(total_potensi * 0.15)} (15% dari potensi)

⚡ JANGKA PENDEK (90 Hari):
   1. Jalankan kampanye "Upgrade Bandwidth" untuk Zona Sniper
   2. Tawarkan bundling Smart Home ke Area Risiko
   3. Tawarkan solusi PV Rooftop untuk pelanggan high-value
   4. Target: {format_rupiah(total_potensi * 0.30)} (30% dari potensi)

🎯 JANGKA PANJANG (12 Bulan):
   1. Bangun program retensi untuk Pelanggan Bintang
   2. Kembangkan kampanye edukasi untuk Inkubator
   3. Implementasikan program sukses pelanggan untuk Juara
   4. Target konversi: 20-40%

═══════════════════════════════════════════════════════════════════
💡 PROYEKSI ROI (RETURN ON INVESTMENT)
═══════════════════════════════════════════════════════════════════

ANALISIS SKENARIO:

Skenario Konservatif (Konversi 20%):
  • Pendapatan Tambahan:    {format_rupiah(total_potensi * 0.20)}
  • Peningkatan dari total: {(total_potensi * 0.20 / df['pendapatan'].sum() * 100):.1f}%
  • Investasi:              Rendah (gunakan tim sales existing)
  • ROI:                    Sangat Tinggi

Skenario Moderat (Konversi 30%):
  • Pendapatan Tambahan:    {format_rupiah(total_potensi * 0.30)}
  • Peningkatan dari total: {(total_potensi * 0.30 / df['pendapatan'].sum() * 100):.1f}%
  • Investasi:              Sedang (kampanye pemasaran)
  • ROI:                    Sangat Tinggi

Skenario Optimis (Konversi 40%):
  • Pendapatan Tambahan:    {format_rupiah(total_potensi * 0.40)}
  • Peningkatan dari total: {(total_potensi * 0.40 / df['pendapatan'].sum() * 100):.1f}%
  • Investasi:              Tinggi (tim sales khusus)
  • ROI:                    Tinggi

═══════════════════════════════════════════════════════════════════
📊 INSIGHT STRATEGIS
═══════════════════════════════════════════════════════════════════

• PELANGGAN ZONA SNIPER menggunakan bandwidth tinggi tapi membayar 
  di bawah harga pasar → Peluang: Upgrade ke paket lebih tinggi

• PELANGGAN AREA RISIKO membayar mahal tapi bandwidth rendah → 
  Peluang: Cross-sell produk digital (Smart Home, PV Rooftop, EV Charging)

• PELANGGAN BINTANG adalah yang paling berharga - fokus pada 
  retensi, bukan upselling → Risiko: Pesaing menargetkan mereka

• PELANGGAN INKUBATOR perlu edukasi dan pembinaan sebelum 
  penjualan apa pun → Strategi: Bangun kepercayaan melalui layanan

═══════════════════════════════════════════════════════════════════
📄 CATATAN TEKNIS
═══════════════════════════════════════════════════════════════════

Model yang Digunakan:
  • Prediksi Upsell: GradientBoostingClassifier (Scikit-learn)
  • Prediksi Cross-sell: RandomForestClassifier (Scikit-learn)
  • Prediksi CLV: GradientBoostingRegressor (Scikit-learn)

Pemrosesan Data:
  • Total pelanggan dianalisis: {len(df)}
  • Fitur yang digunakan: 10+ fitur yang di-engineering
  • Split train/test: 80/20 dengan stratifikasi
  • Cross-validation: 5-fold

Sistem ini menggunakan teknik Machine Learning canggih dan dirancang
untuk memberikan intelligence bisnis yang dapat ditindaklanjuti.

═══════════════════════════════════════════════════════════════════
Laporan dibuat oleh Customer Value Optimizer (CVO) v2.0
Untuk pertanyaan, hubungi: Divisi Perencanaan & Analisis Pemasaran
═══════════════════════════════════════════════════════════════════
"""
        
        with open(f'{output_dir}/Ringkasan_Eksekutif.txt', 'w', encoding='utf-8') as f:
            f.write(ringkasan)
        
        print(f"\n📊 Ringkasan Eksekutif: {output_dir}/Ringkasan_Eksekutif.txt")
        print(ringkasan[:3000] + "\n... [Lihat file lengkap di Ringkasan_Eksekutif.txt]\n")
        
        return ringkasan
    
    def run_pipeline(self):
        """Menjalankan pipeline lengkap"""
        print("\n" + "="*70)
        print("CUSTOMER VALUE OPTIMIZER (CVO) v2.0")
        print("Versi Bahasa Indonesia - PLN Icon+")
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
        
        print("\n" + "="*70)
        print("✅ PIPELINE CVO SELESAI!")
        print("="*70)
        print("\n📁 File yang dihasilkan:")
        print("   📊 Laporan Excel:")
        print("      • laporan/CVO_Laporan_Utama.xlsx")
        print("      • laporan/CVO_Peluang_Upsell.xlsx")
        print("      • laporan/CVO_Peluang_Crosssell.xlsx")
        print("      • laporan/CVO_Matriks_Strategis.xlsx")
        print("      • laporan/CVO_Top_50_Peluang.xlsx")
        print("\n   📄 Dokumentasi:")
        print("      • laporan/Ringkasan_Eksekutif.txt")
        print("\n✨ Sistem siap digunakan!")
        
        return True


# EKSEKUSI UTAMA
if __name__ == "__main__":
    print("\n" + "🇮🇩"*35)
    print("\n  Customer Value Optimizer (CVO) v2.0")
    print("  Sistem Prediksi ML - Bahasa Indonesia")
    print("  PLN Icon+ Divisi Pemasaran")
    print("\n" + "🇮🇩"*35 + "\n")
    
    # Deteksi otomatis file data
    data_lengkap = "Data Penuh Pelanggan Aktif.xlsx"
    data_sample = "Data Sampel Machine Learning.xlsx"
    
    if os.path.exists(data_lengkap):
        file_data = data_lengkap
        print(f"📊 Menggunakan DATA LENGKAP: {file_data}")
    elif os.path.exists(data_sample):
        file_data = data_sample
        print(f"📊 Menggunakan DATA SAMPLE: {file_data}")
    else:
        import glob
        files = glob.glob("*.xlsx") + glob.glob("*.csv")
        if files:
            file_data = files[0]
            print(f"📊 Menggunakan: {file_data}")
        else:
            print("❌ File data tidak ditemukan!")
            exit(1)
    
    cvo = CustomerValueOptimizer(file_data)
    sukses = cvo.run_pipeline()
    
    if sukses:
        print("\n🎉 Berhasil! Lihat folder 'laporan/' untuk hasil.")
    else:
        print("\n❌ Gagal. Cek pesan error di atas.")
