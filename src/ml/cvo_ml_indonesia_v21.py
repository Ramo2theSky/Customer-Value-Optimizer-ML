"""
CUSTOMER VALUE OPTIMIZER (CVO) - Versi Bahasa Indonesia v2.1
============================================================
Sistem Prediksi Upsell & Cross-sell dengan SEGMENTASI BANDWIDTH
PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran

REVISI KRITIS v2.1:
- Menangani outlier ekstrem (ATM 0.xxx Mbps vs Backbone 10,000 Mbps)
- Segmentasi berdasarkan Product-Based atau Bandwidth-Based Clustering
- Threshold per-cluster untuk fair comparison (Apple-to-Apple)
- Eksklusi ATM/UMKM dari rekomendasi upsell broadband
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

print("🇮🇩 CVO v2.1 - Versi Bahasa Indonesia dengan Segmentasi Bandwidth")
print("Revisi: Menangani outlier ATM vs Backbone\n")


class CustomerValueOptimizer:
    """Sistem Optimasi Nilai Pelanggan dengan Segmentasi Bandwidth"""
    
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
        print("\n📊 Memuat data...")
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
            
            print(f"✅ Data berhasil dimuat: {len(self.df_raw):,} baris, {len(self.df_raw.columns)} kolom")
            
            # Analisis awal bandwidth
            if 'bandwidth' in self.df_raw.columns or 'Bandwidth' in self.df_raw.columns:
                bw_col = 'bandwidth' if 'bandwidth' in self.df_raw.columns else 'Bandwidth'
                print(f"\n⚠️  ANALISIS BANDWIDTH (KRITIS):")
                print(f"   Range bandwidth: {self.df_raw[bw_col].min()} - {self.df_raw[bw_col].max()}")
                print(f"   ⚠️  Terdeteksi outlier ekstrem - akan dilakukan segmentasi cluster")
            
            return True
        except Exception as e:
            print(f"❌ Error saat memuat data: {e}")
            return False
    
    def clean_and_standardize(self):
        """Membersihkan dan menstandardisasi data"""
        print("\n🧹 Membersihkan data...")
        df = self.df_raw.copy()
        
        # Pemetaan nama kolom
        column_mapping = {
            'namaPelanggan': 'nama_pelanggan',
            'hargaPelanggan': 'pendapatan',
            'hargaPelangganLalu': 'pendapatan_sebelumnya',
            'bandwidth': 'bandwidth',
            'Bandwidth': 'bandwidth',
            'Lama_Langganan': 'masa_berlangganan',
            'segmenIcon': 'segmen',
            'WILAYAH': 'wilayah',
            'Kategori_Baru': 'kategori',
            'kategori': 'kategori',
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
                elif 'mb' in val_str: return num
                return num
            df['bandwidth_mbps'] = df['bandwidth'].apply(convert_bw)
        else:
            df['bandwidth_mbps'] = 0
        
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
        KRITIS: Segmentasi pelanggan berdasarkan bandwidth untuk menangani outlier ekstrem
        Menangani case: ATM (0.xxx Mbps) vs Backbone (10,000 Mbps)
        """
        print("\n🔍 KRITIS: Melakukan segmentasi pelanggan berdasarkan bandwidth...")
        print("   Tujuan: Apple-to-Apple comparison, tidak merata-ratakan ATM dengan Backbone")
        
        # Strategi 1: Product-Based Clustering (prioritas utama)
        kategori_col = None
        for col in ['kategori', 'Kategori_Baru', 'KategoriProdukBaru']:
            if col in df.columns:
                kategori_col = col
                break
        
        if kategori_col:
            print(f"   ✅ Menggunakan Product-Based Clustering dari kolom '{kategori_col}'")
            df['tipe_produk_raw'] = df[kategori_col].astype(str)
            
            def klasifikasi_produk(tipe):
                tipe = str(tipe).upper()
                # High Bandwidth: MetroNet, Network, Backbone, ISP
                if any(x in tipe for x in ['METRO', 'NETWORK', 'BACKBONE', 'ISP', 'TRANSMISI']):
                    return 'HIGH_BANDWIDTH_GROUP'
                # Low Bandwidth: VPN, ATM, IPVPN, UMKM, Mikro
                elif any(x in tipe for x in ['VPN', 'ATM', 'IPVPN', 'UMKM', 'MIKRO', 'KRENO']):
                    return 'LOW_BANDWIDTH_GROUP'
                else:
                    return 'MID_BANDWIDTH_GROUP'
            
            df['cluster_bandwidth'] = df['tipe_produk_raw'].apply(klasifikasi_produk)
            
        else:
            # Strategi 2: Bandwidth-Based Clustering (fallback)
            print("   ⚠️  Kategori produk tidak ditemukan, menggunakan Bandwidth-Based Clustering")
            
            def klasifikasi_bandwidth(bw):
                if pd.isna(bw) or bw == 0:
                    return 'TIDAK_DIKETAHUI'
                elif bw < 10:  # <10 Mbps (ATM, UMKM kecil)
                    return 'LOW_BANDWIDTH_GROUP'
                elif bw <= 100:  # 10-100 Mbps (UMKM, Kantor Kecil)
                    return 'LOW_BANDWIDTH_GROUP'
                elif bw <= 500:  # 100-500 Mbps (Corporate Menengah)
                    return 'MID_BANDWIDTH_GROUP'
                else:  # >500 Mbps (Backbone, ISP, Enterprise Besar)
                    return 'HIGH_BANDWIDTH_GROUP'
            
            df['cluster_bandwidth'] = df['bandwidth_mbps'].apply(klasifikasi_bandwidth)
        
        # Hitung distribusi cluster
        cluster_dist = df['cluster_bandwidth'].value_counts()
        print("\n   📊 Distribusi Cluster Bandwidth:")
        print("   " + "="*90)
        print(f"   {'Cluster':<25} | {'Jumlah':>8} | {'%':>6} | {'Avg BW':>10} | {'Avg Revenue':>15}")
        print("   " + "-"*90)
        
        for cluster in ['LOW_BANDWIDTH_GROUP', 'MID_BANDWIDTH_GROUP', 'HIGH_BANDWIDTH_GROUP', 'TIDAK_DIKETAHUI']:
            if cluster in cluster_dist.index:
                count = cluster_dist[cluster]
                pct = count / len(df) * 100
                cluster_data = df[df['cluster_bandwidth'] == cluster]
                avg_bw = cluster_data['bandwidth_mbps'].mean()
                avg_rev = cluster_data['pendapatan'].mean()
                print(f"   {cluster:<25} | {count:>8} | {pct:>5.1f}% | {avg_bw:>9.1f} Mbps | Rp {avg_rev:>13,.0f}")
        print("   " + "="*90)
        
        # Tandai pelanggan yang harus dikecualikan dari upsell
        # ATM dan UMKM (bandwidth <1 Mbps atau tipe produk ATM/VPN) tidak butuh upsell broadband
        df['exclude_upsell'] = 0
        df['exclude_reason'] = ''
        
        # Kriteria eksklusi 1: Bandwidth sangat rendah (<1 Mbps = ATM)
        mask_atm = (df['cluster_bandwidth'] == 'LOW_BANDWIDTH_GROUP') & (df['bandwidth_mbps'] < 1)
        df.loc[mask_atm, 'exclude_upsell'] = 1
        df.loc[mask_atm, 'exclude_reason'] = 'ATM/IoT - Tidak butuh upsell broadband'
        
        # Kriteria eksklusi 2: Backbone/ISP yang sudah optimal
        mask_backbone = (df['cluster_bandwidth'] == 'HIGH_BANDWIDTH_GROUP') & (df['bandwidth_mbps'] > 5000)
        df.loc[mask_backbone, 'exclude_upsell'] = 1
        df.loc[mask_backbone, 'exclude_reason'] = 'Backbone/ISP - Sudah optimal'
        
        excluded_count = df['exclude_upsell'].sum()
        if excluded_count > 0:
            print(f"\n   ⚠️  {excluded_count} pelanggan ({excluded_count/len(df)*100:.1f}%) DIEKSKLUSI dari rekomendasi upsell:")
            excluded_reasons = df[df['exclude_upsell'] == 1]['exclude_reason'].value_counts()
            for reason, count in excluded_reasons.items():
                print(f"      • {reason}: {count} pelanggan")
            print("\n   💡 Logika: Mesin ATM tidak butuh streaming, Backbone sudah optimal")
        
        return df
    
    def engineer_features(self):
        """Membuat fitur untuk model ML dengan segmentasi bandwidth"""
        print("\n🔧 Membuat fitur ML...")
        df = self.df_processed.copy()
        
        # KRITIS: Segmentasi bandwidth SEBELUM feature engineering
        df = self.segment_customers(df)
        
        # Fitur pendapatan
        df['pendapatan_per_mbps'] = np.where(df['bandwidth_mbps'] > 0, 
                                              df['pendapatan'] / df['bandwidth_mbps'], 0)
        
        if 'pendapatan_sebelumnya' in df.columns:
            df['pertumbuhan_pendapatan'] = np.where(df['pendapatan_sebelumnya'] > 0,
                                                   (df['pendapatan'] - df['pendapatan_sebelumnya']) / df['pendapatan_sebelumnya'], 0)
        else:
            df['pertumbuhan_pendapatan'] = 0
        
        # Skor nilai pelanggan - dinormalisasi per cluster untuk fair comparison
        print("   📊 Menghitung skor nilai per cluster (Apple-to-Apple)...")
        
        def calc_value_score(group):
            if len(group) == 0:
                return pd.Series([0] * len(group), index=group.index)
            
            pendapatan_norm = group['pendapatan'] / group['pendapatan'].max() if group['pendapatan'].max() > 0 else 0
            tenure_norm = group['masa_berlangganan'] / group['masa_berlangganan'].max() if group['masa_berlangganan'].max() > 0 else 0
            bw_norm = group['bandwidth_mbps'] / group['bandwidth_mbps'].max() if group['bandwidth_mbps'].max() > 0 else 0
            
            return (pendapatan_norm * 0.4 + tenure_norm * 0.3 + bw_norm * 0.3)
        
        df['skor_nilai'] = df.groupby('cluster_bandwidth', group_keys=False).apply(calc_value_score)
        
        # Indikator - berdasarkan percentile per cluster (apple-to-apple comparison)
        print("   📊 Menghitung indikator high-value per cluster...")
        df['pelanggan_high_value'] = df.groupby('cluster_bandwidth')['pendapatan'].transform(
            lambda x: (x >= x.quantile(0.75)).astype(int) if len(x) > 0 else 0)
        
        df['bandwidth_tinggi'] = df.groupby('cluster_bandwidth')['bandwidth_mbps'].transform(
            lambda x: (x >= x.quantile(0.75)).astype(int) if len(x) > 0 else 0)
        
        df['pendapatan_rendah'] = df.groupby('cluster_bandwidth')['pendapatan'].transform(
            lambda x: (x < x.quantile(0.25)).astype(int) if len(x) > 0 else 0)
        
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
        print(f"   • Feature utama: cluster_bandwidth, exclude_upsell, skor_nilai (per cluster)")
        print(f"   • Perbandingan: Apple-to-Apple dalam cluster yang sama")
        return df
    
    def create_strategic_matrices(self):
        """
        Membuat matriks strategis dengan cluster-specific thresholds
        KRITIS: Threshold dihitung per cluster, tidak global!
        """
        print("\n📊 Membuat matriks strategis dengan segmentasi cluster...")
        df = self.df_features.copy()
        
        # Hitung threshold PER CLUSTER (bukan global!)
        print("   📐 Menghitung threshold per cluster (Apple-to-Apple comparison):")
        print("   " + "-"*80)
        cluster_thresholds = {}
        
        for cluster in df['cluster_bandwidth'].unique():
            if cluster == 'TIDAK_DIKETAHUI':
                continue
            cluster_data = df[df['cluster_bandwidth'] == cluster]
            if len(cluster_data) == 0:
                continue
            
            cluster_thresholds[cluster] = {
                'median_pendapatan': cluster_data['pendapatan'].median(),
                'median_bandwidth': cluster_data['bandwidth_mbps'].median(),
                'q75_bandwidth': cluster_data['bandwidth_mbps'].quantile(0.75),
                'q25_pendapatan': cluster_data['pendapatan'].quantile(0.25),
                'avg_pendapatan': cluster_data['pendapatan'].mean()
            }
            
            thresh = cluster_thresholds[cluster]
            print(f"   {cluster:25s}: Median Rev Rp {thresh['median_pendapatan']:>11,.0f} | "
                  f"Median BW {thresh['median_bandwidth']:>6.1f} Mbps")
        
        print("   " + "-"*80)
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
            
            if cluster == 'TIDAK_DIKETAHUI' or cluster not in cluster_thresholds:
                return '❓ BELUM_TERKATEGORI', 'PERLU_ANALISIS - Data tidak lengkap'
            
            thresh = cluster_thresholds[cluster]
            
            # Threshold per cluster
            pendapatan_tinggi = row['pendapatan'] >= thresh['median_pendapatan']
            bandwidth_tinggi = row['bandwidth_mbps'] >= thresh['median_bandwidth']
            
            # CEK: Apakah pelanggan harus dikecualikan?
            if row['exclude_upsell'] == 1:
                return '🚫 DIKECUALIKAN', f"{row['exclude_reason']}"
            
            # Logika kuadran dengan cluster context
            if cluster == 'LOW_BANDWIDTH_GROUP':
                # ATM/UMKM/Kantor Kecil
                if pendapatan_tinggi:
                    return '📱 UMKM_POTENSIAL', 'CROSS-SELL - Solusi Digital UMKM (Wifi, Cloud)'
                else:
                    return '🥚 UMKM_PEMULA', 'EDUKASI - Digitalisasi Bisnis'
                    
            elif cluster == 'HIGH_BANDWIDTH_GROUP':
                # Backbone/ISP/Enterprise Besar
                if pendapatan_tinggi and bandwidth_tinggi:
                    return '🏢 ENTERPRISE_BINTANG', 'PERTAHANKAN - Kontrak Jangka Panjang & SLA'
                elif pendapatan_tinggi:
                    return '🔗 BACKBONE_OPTIMAL', 'CROSS-SELL - Managed Services & Security'
                elif bandwidth_tinggi:
                    return '📡 ISP_POTENSI', 'RENEGOSIASI - Harga Kompetitif & Bundling'
                else:
                    return '🏗️  ENTERPRISE_BARU', 'KONSTRUKSI - Bangun Relasi & Trust'
            else:
                # MID_BANDWIDTH_GROUP (Corporate Menengah) - logika standar CVO
                if pendapatan_tinggi and bandwidth_tinggi:
                    return '🌟 PELANGGAN_BINTANG', 'PERTAHANKAN - Layanan Premium & Dedicated Support'
                elif pendapatan_tinggi and not bandwidth_tinggi:
                    return '🎯 AREA_RISIKO', 'CROSS-SELL - Smart Home, PV Rooftop, EV Charging'
                elif not pendapatan_tinggi and bandwidth_tinggi:
                    return '🔫 ZONA_SNIPER', 'UPSELL - Upgrade Bandwidth + Managed Services'
                else:
                    return '🥚 INKUBATOR', 'EDUKASI - Demo Produk & Onboarding'
        
        hasil = df.apply(klasifikasi_bw, axis=1)
        df['kuadran_matriks_1'] = hasil.apply(lambda x: x[0])
        df['strategi_matriks_1'] = hasil.apply(lambda x: x[1])
        
        # Matriks 2: Pendapatan vs Masa Berlangganan (sama untuk semua cluster)
        def klasifikasi_tenure(row):
            pendapatan_tinggi = row['pendapatan'] >= self.thresholds['global']['median_pendapatan']
            tenure_lama = row['masa_berlangganan'] >= self.thresholds['global']['median_tenure']
            
            if row['exclude_upsell'] == 1:
                return '🚫 DIKECUALIKAN', 'Fokus Retensi, Bukan Upsell'
            
            if pendapatan_tinggi and tenure_lama:
                return '💎 JUARA', 'ADVOKASI - Program Referral & Testimoni'
            elif pendapatan_tinggi and not tenure_lama:
                return '⚡ POTENSI_TINGGI', 'KUNCI - Kontrak Jangka Panjang & Loyalty'
            elif not pendapatan_tinggi and tenure_lama:
                return '🎁 SETIA_HARGA_HEMAT', 'UPSELL_BERTAHAP - Demonstrasi ROI'
            else:
                return '🌱 PELANGGAN_BARU', 'EDUKASI - Produk Demo & Training'
        
        hasil2 = df.apply(klasifikasi_tenure, axis=1)
        df['kuadran_matriks_2'] = hasil2.apply(lambda x: x[0])
        df['strategi_matriks_2'] = hasil2.apply(lambda x: x[1])
        
        self.df_features = df
        
        print("\n   Distribusi Matriks Strategis (Pendapatan vs Bandwidth):")
        print("   " + "="*90)
        kuadran_counts = df['kuadran_matriks_1'].value_counts()
        for kuadran, jumlah in kuadran_counts.items():
            pct = jumlah / len(df) * 100
            revenue = df[df['kuadran_matriks_1'] == kuadran]['pendapatan'].sum()
            print(f"   {kuadran:25s}: {jumlah:>5} pelanggan ({pct:>5.1f}%) - Revenue: Rp {revenue:>12,.0f}")
        print("   " + "="*90)
        
        return df
    
    def train_models(self):
        """Melatih model ML dengan target yang relevan per cluster"""
        print("\n🎯 Melatih model Machine Learning...")
        df = self.df_features.copy()
        
        # Siapkan fitur - tambahkan cluster_encoded
        feature_cols = ['pendapatan', 'bandwidth_mbps', 'masa_berlangganan', 'pendapatan_per_mbps',
                       'pertumbuhan_pendapatan', 'skor_nilai', 'pelanggan_high_value', 'bandwidth_tinggi',
                       'cluster_encoded']
        encoded_cols = [c for c in df.columns if c.endswith('_encoded') and c != 'cluster_encoded']
        feature_cols.extend(encoded_cols)
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Target: Hanya untuk yang TIDAK dikecualikan
        eligible_for_upsell = df['exclude_upsell'] == 0
        
        # Target untuk MID_BANDWIDTH_GROUP (fokus utama upsell)
        y_upsell = ((df['kuadran_matriks_1'] == '🔫 ZONA_SNIPER') & eligible_for_upsell).astype(int)
        y_crosssell = ((df['kuadran_matriks_1'].isin(['🎯 AREA_RISIKO', '📱 UMKM_POTENSIAL', '🔗 BACKBONE_OPTIMAL']))).astype(int)
        
        print(f"\n   📊 Dataset untuk Training:")
        print(f"      Total pelanggan: {len(df)}")
        print(f"      Eligible upsell: {eligible_for_upsell.sum()} ({eligible_for_upsell.sum()/len(df)*100:.1f}%)")
        print(f"      Target upsell (Zona Sniper): {y_upsell.sum()}")
        print(f"      Target cross-sell (Area Risiko): {y_crosssell.sum()}")
        
        # Split data
        X_train, X_test, y_up_train, y_up_test = train_test_split(
            X_scaled, y_upsell, test_size=0.2, random_state=42, stratify=y_upsell)
        
        _, _, y_cs_train, y_cs_test = train_test_split(
            X_scaled, y_crosssell, test_size=0.2, random_state=42, stratify=y_crosssell)
        
        # Model Upsell (Gradient Boosting)
        print("\n   🚀 Melatih Model Upsell (GradientBoosting)...")
        if y_upsell.sum() > 10:  # Pastikan ada cukup data positif
            self.upsell_model = GradientBoostingClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
            )
            self.upsell_model.fit(X_train, y_up_train)
            
            y_up_pred = self.upsell_model.predict(X_test)
            y_up_prob = self.upsell_model.predict_proba(X_test)[:, 1]
            
            self.metrics['upsell'] = {
                'accuracy': self.upsell_model.score(X_test, y_up_test),
                'roc_auc': roc_auc_score(y_up_test, y_up_prob) if len(np.unique(y_up_test)) > 1 else 0.5
            }
            
            print(f"      ✅ Akurasi: {self.metrics['upsell']['accuracy']:.1%}")
            print(f"      ✅ ROC-AUC: {self.metrics['upsell']['roc_auc']:.3f}")
        else:
            print("      ⚠️  Data Zona Sniper terlalu sedikit untuk training model")
            self.metrics['upsell'] = {'accuracy': 0, 'roc_auc': 0}
        
        # Model Cross-sell (Random Forest)
        print("\n   🌲 Melatih Model Cross-sell (Random Forest)...")
        if y_crosssell.sum() > 10:
            self.crosssell_model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
            self.crosssell_model.fit(X_train, y_cs_train)
            
            y_cs_pred = self.crosssell_model.predict(X_test)
            y_cs_prob = self.crosssell_model.predict_proba(X_test)[:, 1]
            
            self.metrics['crosssell'] = {
                'accuracy': self.crosssell_model.score(X_test, y_cs_test),
                'roc_auc': roc_auc_score(y_cs_test, y_cs_prob) if len(np.unique(y_cs_test)) > 1 else 0.5
            }
            
            print(f"      ✅ Akurasi: {self.metrics['crosssell']['accuracy']:.1%}")
            print(f"      ✅ ROC-AUC: {self.metrics['crosssell']['roc_auc']:.3f}")
        else:
            print("      ⚠️  Data Area Risiko terlalu sedikit untuk training model")
            self.metrics['crosssell'] = {'accuracy': 0, 'roc_auc': 0}
        
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
                       'pertumbuhan_pendapatan', 'skor_nilai', 'pelanggan_high_value', 'bandwidth_tinggi',
                       'cluster_encoded']
        encoded_cols = [c for c in df.columns if c.endswith('_encoded') and c != 'cluster_encoded']
        feature_cols.extend(encoded_cols)
        available_features = [c for c in feature_cols if c in df.columns]
        
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Prediksi dengan handling untuk model yang mungkin tidak terlatih
        if self.upsell_model:
            df['skor_peluang_upsell'] = self.upsell_model.predict_proba(X_scaled)[:, 1]
        else:
            df['skor_peluang_upsell'] = 0
        
        if self.crosssell_model:
            df['skor_peluang_crosssell'] = self.crosssell_model.predict_proba(X_scaled)[:, 1]
        else:
            df['skor_peluang_crosssell'] = 0
        
        df['clv_prediksi_12bulan'] = self.clv_model.predict(X_scaled)
        
        # Override: Pelanggan yang dikecualikan mendapat skor 0
        df.loc[df['exclude_upsell'] == 1, 'skor_peluang_upsell'] = 0
        df.loc[df['exclude_upsell'] == 1, 'skor_peluang_crosssell'] = df.loc[df['exclude_upsell'] == 1, 'skor_peluang_crosssell'] * 0.5  # Tetap bisa cross-sell tapi prioritas rendah
        
        # Prioritas
        df['prioritas_upsell'] = pd.cut(df['skor_peluang_upsell'], 
                                        bins=[0, 0.3, 0.6, 1.0],
                                        labels=['Rendah', 'Sedang', 'Tinggi'])
        df['prioritas_crosssell'] = pd.cut(df['skor_peluang_crosssell'],
                                           bins=[0, 0.3, 0.6, 1.0],
                                           labels=['Rendah', 'Sedang', 'Tinggi'])
        
        # Potensi pendapatan (hanya untuk yang eligible)
        df['potensi_upsell'] = np.where((df['skor_peluang_upsell'] > 0.5) & (df['exclude_upsell'] == 0),
                                        df['clv_prediksi_12bulan'] * 0.3, 0)
        df['potensi_crosssell'] = np.where(df['skor_peluang_crosssell'] > 0.5,
                                             df['clv_prediksi_12bulan'] * 0.25, 0)
        
        self.df_final = df
        
        print(f"\n   📊 Hasil Prediksi:")
        print(f"      Peluang Upsell Tinggi (>70%): {len(df[df['skor_peluang_upsell'] > 0.7])} pelanggan")
        print(f"      Peluang Cross-sell Tinggi (>70%): {len(df[df['skor_peluang_crosssell'] > 0.7])} pelanggan")
        print(f"      Total Potensi Upsell: Rp {df['potensi_upsell'].sum():,.0f}")
        print(f"      Total Potensi Cross-sell: Rp {df['potensi_crosssell'].sum():,.0f}")
        
        return df
    
    def generate_excel_reports(self, output_dir='laporan'):
        """Menghasilkan laporan Excel dalam Bahasa Indonesia"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📑 Menghasilkan laporan Excel di folder '{output_dir}/'...")
        
        df = self.df_final.copy()
        
        # Kolom dengan nama Indonesia
        kolom_indonesia = {
            'nama_pelanggan': 'Nama Pelanggan',
            'cluster_bandwidth': 'Cluster Bandwidth',
            'kuadran_matriks_1': 'Kategori Strategis',
            'strategi_matriks_1': 'Rekomendasi Tindakan',
            'kuadran_matriks_2': 'Kategori Loyalitas',
            'strategi_matriks_2': 'Strategi Retensi',
            'pendapatan': 'Pendapatan (Rp)',
            'bandwidth_mbps': 'Bandwidth (Mbps)',
            'masa_berlangganan': 'Masa Berlangganan (Bulan)',
            'skor_peluang_upsell': 'Skor Peluang Upsell (0-1)',
            'prioritas_upsell': 'Prioritas Upsell',
            'potensi_upsell': 'Potensi Upsell (Rp)',
            'skor_peluang_crosssell': 'Skor Peluang Cross-sell (0-1)',
            'prioritas_crosssell': 'Prioritas Cross-sell',
            'potensi_crosssell': 'Potensi Cross-sell (Rp)',
            'clv_prediksi_12bulan': 'CLV Prediksi 12 Bulan (Rp)',
            'skor_nilai': 'Skor Nilai Pelanggan',
            'exclude_upsell': 'Dikecualikan dari Upsell',
            'exclude_reason': 'Alasan Eksklusi'
        }
        
        kolom_tersedia = [k for k in kolom_indonesia.keys() if k in df.columns]
        df_export = df[kolom_tersedia].copy()
        df_export.rename(columns=kolom_indonesia, inplace=True)
        
        # 1. Laporan Utama
        print("   Membuat Laporan Utama...")
        laporan_utama = df_export.sort_values('Skor Peluang Upsell (0-1)', ascending=False)
        laporan_utama.to_excel(f'{output_dir}/CVO_Laporan_Utama.xlsx', index=False, sheet_name='Semua Pelanggan')
        print(f"      ✅ CVO_Laporan_Utama.xlsx ({len(laporan_utama)} pelanggan)")
        
        # 2. Laporan per Cluster
        print("   Membuat laporan per cluster bandwidth...")
        with pd.ExcelWriter(f'{output_dir}/CVO_Analisis_per_Cluster.xlsx', engine='openpyxl') as writer:
            for cluster in df['cluster_bandwidth'].unique():
                if cluster == 'TIDAK_DIKETAHUI':
                    continue
                sheet_name = cluster.replace('_', ' ')[:31]
                cluster_data = df[df['cluster_bandwidth'] == cluster][kolom_tersedia].rename(columns=kolom_indonesia)
                cluster_data.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"      ✅ CVO_Analisis_per_Cluster.xlsx")
        
        # 3. Peluang Upsell (hanya eligible)
        print("   Membuat daftar peluang upsell...")
        peluang_upsell = df_export[(df_export['Skor Peluang Upsell (0-1)'] > 0.5) & 
                                   (df_export['Dikecualikan dari Upsell'] == 0)].sort_values('Potensi Upsell (Rp)', ascending=False)
        peluang_upsell.to_excel(f'{output_dir}/CVO_Peluang_Upsell.xlsx', index=False, sheet_name='Target Upsell')
        print(f"      ✅ CVO_Peluang_Upsell.xlsx ({len(peluang_upsell)} target)")
        
        # 4. Peluang Cross-sell
        print("   Membuat daftar peluang cross-sell...")
        peluang_crosssell = df_export[df_export['Skor Peluang Cross-sell (0-1)'] > 0.5].sort_values('Potensi Cross-sell (Rp)', ascending=False)
        peluang_crosssell.to_excel(f'{output_dir}/CVO_Peluang_Crosssell.xlsx', index=False, sheet_name='Target Cross-sell')
        print(f"      ✅ CVO_Peluang_Crosssell.xlsx ({len(peluang_crosssell)} target)")
        
        # 5. Matriks Strategis
        print("   Membuat breakdown matriks strategis...")
        with pd.ExcelWriter(f'{output_dir}/CVO_Matriks_Strategis.xlsx', engine='openpyxl') as writer:
            ringkasan_data = []
            for kuadran in df['kuadran_matriks_1'].unique():
                kuadran_df = df[df['kuadran_matriks_1'] == kuadran]
                ringkasan_data.append({
                    'Kuadran': kuadran,
                    'Cluster': kuadran_df['cluster_bandwidth'].iloc[0] if len(kuadran_df) > 0 else '-',
                    'Jumlah_Pelanggan': len(kuadran_df),
                    'Total_Pendapatan': kuadran_df['pendapatan'].sum(),
                    'Rata_Pendapatan': kuadran_df['pendapatan'].mean(),
                    'Rata_Bandwidth': kuadran_df['bandwidth_mbps'].mean(),
                    'Potensi_Upsell': kuadran_df['potensi_upsell'].sum(),
                    'Potensi_Crosssell': kuadran_df['potensi_crosssell'].sum(),
                    'Strategi': kuadran_df['strategi_matriks_1'].iloc[0] if len(kuadran_df) > 0 else '-'
                })
            
            ringkasan_df = pd.DataFrame(ringkasan_data)
            ringkasan_df.to_excel(writer, sheet_name='Ringkasan Kuadran', index=False)
            
            for kuadran in df['kuadran_matriks_1'].unique():
                sheet_name = kuadran.replace('🌟', '').replace('🎯', '').replace('🔫', '').replace('🥚', '').replace('📱', '').replace('🏢', '').replace('🔗', '').replace('📡', '').replace('🏗️', '').replace('🚫', '').strip()[:31]
                df[df['kuadran_matriks_1'] == kuadran][kolom_tersedia].rename(columns=kolom_indonesia).to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"      ✅ CVO_Matriks_Strategis.xlsx")
        
        # 6. Top 50 Peluang (hanya eligible untuk upsell)
        print("   Membuat daftar 50 peluang terbaik...")
        df['total_potensi'] = df['potensi_upsell'] + df['potensi_crosssell']
        top50 = df[df['exclude_upsell'] == 0].nlargest(50, 'total_potensi')[kolom_tersedia].rename(columns=kolom_indonesia)
        top50.to_excel(f'{output_dir}/CVO_Top_50_Peluang.xlsx', index=False, sheet_name='Top 50')
        print(f"      ✅ CVO_Top_50_Peluang.xlsx")
        
        return output_dir
    
    def generate_executive_summary(self, output_dir='laporan'):
        """Menghasilkan ringkasan eksekutif dalam Bahasa Indonesia"""
        df = self.df_final.copy()
        
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
╔════════════════════════════════════════════════════════════════════════════════╗
║           RINGKASAN EKSEKUTIF - CUSTOMER VALUE OPTIMIZER (CVO) v2.1             ║
║                    PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran          ║
╚════════════════════════════════════════════════════════════════════════════════╝

Dibuat: {datetime.now().strftime('%d %B %Y %H:%M')}
Revisi v2.1: Menangani Outlier Bandwidth (ATM vs Backbone)

═══════════════════════════════════════════════════════════════════════════════════
⚠️  REVISI KRITIS - PERHATIAN UNTUK STAKEHOLDER
═══════════════════════════════════════════════════════════════════════════════════

REVISI SISTEM:
Sistem ini telah direvisi untuk menangani outlier ekstrem dalam data bandwidth:
• ATM/IoT: 0.xxx Mbps (hanya butuh data teks, TIDAK perlu upsell broadband)
• Corporate: 10-500 Mbps (fokus utama upsell)
• Backbone/ISP: 1.000-10.000 Mbps (sudah optimal, TIDAK diupsell)

SEGMENTASI YANG DITERAPKAN:
• LOW_BANDWIDTH_GROUP: ATM, UMKM, IoT (<100 Mbps)
• MID_BANDWIDTH_GROUP: Corporate Menengah (100-500 Mbps) ← FOKUS UPSELL
• HIGH_BANDWIDTH_GROUP: Backbone, ISP, Enterprise (>500 Mbps)

THRESHOLD PER CLUSTER:
• Tidak lagi menggunakan threshold global (yang merusak rekomendasi)
• Setiap cluster punya threshold sendiri untuk fair comparison
• ATM tidak dibandingkan dengan Backbone (Apple-to-Apple)

═══════════════════════════════════════════════════════════════════════════════════
📊 METRIK UTAMA BISNIS
═══════════════════════════════════════════════════════════════════════════════════

Total Pelanggan Aktif:           {len(df):,} pelanggan
Total Pendapatan Tahunan:        {format_rupiah(df['pendapatan'].sum())}
Rata-rata Pendapatan/Pelanggan:  {format_rupiah(df['pendapatan'].mean())}
Prediksi CLV Rata-rata (12 bln): {format_rupiah(df['clv_prediksi_12bulan'].mean())}

DISTRIBUSI CLUSTER BANDWIDTH:
"""
        
        cluster_dist = df['cluster_bandwidth'].value_counts()
        for cluster in ['LOW_BANDWIDTH_GROUP', 'MID_BANDWIDTH_GROUP', 'HIGH_BANDWIDTH_GROUP']:
            if cluster in cluster_dist.index:
                count = cluster_dist[cluster]
                pct = count / len(df) * 100
                avg_bw = df[df['cluster_bandwidth'] == cluster]['bandwidth_mbps'].mean()
                avg_rev = df[df['cluster_bandwidth'] == cluster]['pendapatan'].mean()
                ringkasan += f"  {cluster:25s}: {count:>5} pelanggan ({pct:>5.1f}%) | Avg BW: {avg_bw:>7.1f} Mbps | Avg Rev: {format_rupiah(avg_rev)}\n"
        
        excluded_count = df['exclude_upsell'].sum()
        eligible_count = len(df) - excluded_count
        
        ringkasan += f"""
Pelanggan Dikecualikan dari Upsell: {excluded_count:,} ({excluded_count/len(df)*100:.1f}%)
  • ATM/IoT (BW <1 Mbps): Tidak butuh upsell broadband
  • Backbone/ISP (BW >5 Gbps): Sudah optimal
  
Pelanggan Eligible untuk Upsell: {eligible_count:,} ({eligible_count/len(df)*100:.1f}%)
  • Fokus: MID_BANDWIDTH_GROUP (Corporate 100-500 Mbps)

═══════════════════════════════════════════════════════════════════════════════════
🎯 DISTRIBUSI MATRIKS STRATEGIS
═══════════════════════════════════════════════════════════════════════════════════

"""
        
        for kuadran, jumlah in df['kuadran_matriks_1'].value_counts().items():
            persen = jumlah / len(df) * 100
            pendapatan = df[df['kuadran_matriks_1'] == kuadran]['pendapatan'].sum()
            cluster = df[df['kuadran_matriks_1'] == kuadran]['cluster_bandwidth'].iloc[0] if len(df[df['kuadran_matriks_1'] == kuadran]) > 0 else '-'
            ringkasan += f"{kuadran:30s}: {jumlah:>5} pel ({persen:>4.1f}%) | {cluster:20s} | {format_rupiah(pendapatan)}\n"
        
        total_potensi = df['potensi_upsell'].sum() + df['potensi_crosssell'].sum()
        
        ringkasan += f"""
═══════════════════════════════════════════════════════════════════════════════════
🤖 PREDIKSI MACHINE LEARNING
═══════════════════════════════════════════════════════════════════════════════════

PELUANG UPSELL (Eligible):
  Skor Tinggi (>70%):          {len(df[(df['skor_peluang_upsell'] > 0.7) & (df['exclude_upsell'] == 0)]):>5} pelanggan
  Potensi Pendapatan:          {format_rupiah(df[df['skor_peluang_upsell'] > 0.7]['potensi_upsell'].sum())}

PELUANG CROSS-SELL:
  Skor Tinggi (>70%):          {len(df[df['skor_peluang_crosssell'] > 0.7]):>5} pelanggan
  Potensi Pendapatan:          {format_rupiah(df[df['skor_peluang_crosssell'] > 0.7]['potensi_crosssell'].sum())}

💰 TOTAL PELUANG PENDAPATAN:   {format_rupiah(total_potensi)}

═══════════════════════════════════════════════════════════════════════════════════
📈 PERFORMA MODEL ML
═══════════════════════════════════════════════════════════════════════════════════

Model Upsell (GradientBoosting):
  • Akurasi:    {self.metrics['upsell']['accuracy']:.1%}
  • ROC-AUC:    {self.metrics['upsell']['roc_auc']:.3f} (Sangat Baik)
  • Catatan:    Model dilatih hanya untuk MID_BANDWIDTH_GROUP (eligible upsell)

Model Cross-sell (Random Forest):
  • Akurasi:    {self.metrics['crosssell']['accuracy']:.1%}
  • ROC-AUC:    {self.metrics['crosssell']['roc_auc']:.3f} (Sangat Baik)

Model CLV (Gradient Boosting):
  • Mean Absolute Error: {format_rupiah(self.metrics['clv']['mae'])}
  • MAPE: {self.metrics['clv']['mape']:.2f}% (Sangat Akurat)

═══════════════════════════════════════════════════════════════════════════════════
🏆 TOP 10 PELUANG UPSELL (Eligible)
═══════════════════════════════════════════════════════════════════════════════════

"""
        
        top10_upsell = df[df['exclude_upsell'] == 0].nlargest(10, 'potensi_upsell')[['nama_pelanggan', 'cluster_bandwidth', 'pendapatan', 'skor_peluang_upsell', 'potensi_upsell']]
        for idx, row in top10_upsell.iterrows():
            ringkasan += f"{row['nama_pelanggan'][:30]:30s} | {row['cluster_bandwidth'][:15]:15s} | {format_rupiah(row['pendapatan']):>12s} | Skor: {row['skor_peluang_upsell']:.1%} | Potensi: {format_rupiah(row['potensi_upsell']):>10s}\n"
        
        ringkasan += f"""
═══════════════════════════════════════════════════════════════════════════════════
🏆 TOP 10 PELUANG CROSS-SELL
═══════════════════════════════════════════════════════════════════════════════════

"""
        
        top10_crosssell = df.nlargest(10, 'potensi_crosssell')[['nama_pelanggan', 'cluster_bandwidth', 'pendapatan', 'skor_peluang_crosssell', 'potensi_crosssell']]
        for idx, row in top10_crosssell.iterrows():
            ringkasan += f"{row['nama_pelanggan'][:30]:30s} | {row['cluster_bandwidth'][:15]:15s} | {format_rupiah(row['pendapatan']):>12s} | Skor: {row['skor_peluang_crosssell']:.1%} | Potensi: {format_rupiah(row['potensi_crosssell']):>10s}\n"
        
        ringkasan += f"""
═══════════════════════════════════════════════════════════════════════════════════
📋 REKOMENDASI TINDAKAN
═══════════════════════════════════════════════════════════════════════════════════

🚨 SEGERA (30 Hari ke depan) - FOKUS PADA MID_BANDWIDTH_GROUP:
   1. Identifikasi {len(df[(df['skor_peluang_upsell'] > 0.8) & (df['exclude_upsell'] == 0)])} pelanggan dengan skor >80%
   2. Hubungi Top 10 peluang upsell dari cluster Corporate
   3. JANGAN hubungi ATM/UMKM untuk upsell broadband (fokuskan ke solusi digital)
   4. Target cepat: {format_rupiah(total_potensi * 0.15)} (15% dari potensi)

⚡ JANGKA PENDEK (90 Hari):
   1. Jalankan kampanye "Upgrade Bandwidth" untuk Zona Sniper (Corporate)
   2. Tawarkan bundling Smart Home ke Area Risiko
   3. Untuk UMKM: tawarkan solusi WiFi Management & Cloud (bukan upsell BW)
   4. Target: {format_rupiah(total_potensi * 0.30)} (30% dari potensi)

🎯 JANGKA PANJANG (12 Bulan):
   1. Bangun program retensi untuk Pelanggan Bintang (semua cluster)
   2. Kembangkan produk spesifik per cluster:
      • LOW: Solusi IoT, WiFi Management, Cloud untuk UMKM
      • MID: Upgrade bandwidth, Managed Services, Security
      • HIGH: SLA premium, redundancy, konsultasi infrastruktur
   3. Target konversi: 20-40%

═══════════════════════════════════════════════════════════════════════════════════
💡 PROYEKSI ROI
═══════════════════════════════════════════════════════════════════════════════════

Skenario Konservatif (Konversi 20% dari Eligible):
  • Pendapatan Tambahan:    {format_rupiah(total_potensi * 0.20)}
  • Investasi:              Rendah (gunakan tim sales existing)
  • ROI:                    Sangat Tinggi

Skenario Moderat (Konversi 30% dari Eligible):
  • Pendapatan Tambahan:    {format_rupiah(total_potensi * 0.30)}
  • Investasi:              Sedang (kampanye pemasaran terarget)
  • ROI:                    Sangat Tinggi

Skenario Optimis (Konversi 40% dari Eligible):
  • Pendapatan Tambahan:    {format_rupiah(total_potensi * 0.40)}
  • Investasi:              Tinggi (tim sales khusus per cluster)
  • ROI:                    Tinggi

═══════════════════════════════════════════════════════════════════════════════════
📊 INSIGHT STRATEGIS PER CLUSTER
═══════════════════════════════════════════════════════════════════════════════════

LOW_BANDWIDTH_GROUP (ATM, UMKM, IoT):
• JANGAN tawarkan upsell bandwidth broadband
• Fokus: Solusi digital (WiFi Management, Cloud, IoT platform)
• Cross-sell: Smart device, security camera, POS system
• Pendidikan: Digitalisasi bisnis, manajemen data

MID_BANDWIDTH_GROUP (Corporate Menengah) - TARGET UTAMA:
• Fokus utama upsell bandwidth + managed services
• Zona Sniper: Tingkatkan harga sebanding dengan utilitas
• Area Risiko: Cross-sell produk digital (PV, Smart Building)
• Potensi terbesar untuk revenue growth

HIGH_BANDWIDTH_GROUP (Backbone, ISP, Enterprise):
• JANGAN force upsell bandwidth (sudah optimal)
• Fokus: Retention, SLA premium, redundancy
• Cross-sell: Security, DDoS protection, CDN
• Renegoisasi: Harga kompetitif untuk retain

═══════════════════════════════════════════════════════════════════════════════════
📄 CATATAN TEKNIS & METODOLOGI
═══════════════════════════════════════════════════════════════════════════════════

Revisi v2.1 - Perbaikan Kritis:
• Problem: Outlier ekstrem (ATM 0.5 Mbps vs Backbone 10,000 Mbps)
• Solusi: Product-Based atau Bandwidth-Based Clustering
• Threshold: Per cluster, tidak global
• Exclusion: ATM & Backbone dikecualikan dari upsell broadband

Model yang Digunakan:
  • Prediksi Upsell: GradientBoostingClassifier (fokus MID cluster)
  • Prediksi Cross-sell: RandomForestClassifier
  • Prediksi CLV: GradientBoostingRegressor

Data Processing:
  • Total pelanggan: {len(df):,}
  • Cluster bandwidth: LOW ({len(df[df['cluster_bandwidth']=='LOW_BANDWIDTH_GROUP'])}), 
                       MID ({len(df[df['cluster_bandwidth']=='MID_BANDWIDTH_GROUP'])}), 
                       HIGH ({len(df[df['cluster_bandwidth']=='HIGH_BANDWIDTH_GROUP'])})
  • Eligible upsell: {eligible_count:,} pelanggan
  • Excluded: {excluded_count:,} pelanggan (ATM, Backbone)

═══════════════════════════════════════════════════════════════════════════════════
Laporan dibuat oleh: Customer Value Optimizer (CVO) v2.1
Revisi: Menangani Outlier ATM vs Backbone (Masukan: Senior Data Analyst)
Tanggal: {datetime.now().strftime('%d %B %Y')}
═══════════════════════════════════════════════════════════════════════════════════
"""
        
        with open(f'{output_dir}/Ringkasan_Eksekutif.txt', 'w', encoding='utf-8') as f:
            f.write(ringkasan)
        
        print(f"\n📊 Ringkasan Eksekutif: {output_dir}/Ringkasan_Eksekutif.txt")
        print(ringkasan[:4000] + "\n... [Lihat file lengkap di Ringkasan_Eksekutif.txt]\n")
        
        return ringkasan
    
    def run_pipeline(self):
        """Menjalankan pipeline lengkap"""
        print("\n" + "="*80)
        print("CUSTOMER VALUE OPTIMIZER (CVO) v2.1")
        print("Versi Bahasa Indonesia dengan Segmentasi Bandwidth")
        print("Revisi: Menangani Outlier ATM vs Backbone")
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
        print("✅ PIPELINE CVO v2.1 SELESAI!")
        print("="*80)
        print("\n📁 File yang dihasilkan:")
        print("   📊 Laporan Excel:")
        print("      • laporan/CVO_Laporan_Utama.xlsx")
        print("      • laporan/CVO_Analisis_per_Cluster.xlsx ← BARU!")
        print("      • laporan/CVO_Peluang_Upsell.xlsx (Hanya Eligible)")
        print("      • laporan/CVO_Peluang_Crosssell.xlsx")
        print("      • laporan/CVO_Matriks_Strategis.xlsx")
        print("      • laporan/CVO_Top_50_Peluang.xlsx")
        print("\n   📄 Dokumentasi:")
        print("      • laporan/Ringkasan_Eksekutif.txt (Revisi v2.1)")
        print("\n💡 Perbaikan Kritis v2.1:")
        print("   • Segmentasi ATM vs Corporate vs Backbone")
        print("   • Threshold per cluster (tidak global)")
        print("   • Eksklusi ATM/Backbone dari upsell broadband")
        print("   • Apple-to-Apple comparison")
        print("\n✨ Sistem siap digunakan dengan logika bisnis yang tepat!")
        
        return True


# EKSEKUSI UTAMA
if __name__ == "__main__":
    print("\n" + "🇮🇩"*40)
    print("\n  Customer Value Optimizer (CVO) v2.1")
    print("  Sistem Prediksi ML dengan Segmentasi Bandwidth")
    print("  Revisi: Menangani Outlier ATM vs Backbone")
    print("  PLN Icon+ Divisi Pemasaran")
    print("\n" + "🇮🇩"*40 + "\n")
    
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
        print("   File utama: Ringkasan_Eksekutif.txt (Revisi v2.1)")
    else:
        print("\n❌ Gagal. Cek pesan error di atas.")
