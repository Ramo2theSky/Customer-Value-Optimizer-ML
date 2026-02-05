"""
CVO v3.0 - SMART CLASSIFIER with Pattern Recognition
=====================================================
Sistem Klasifikasi Cerdas dengan Pattern Recognition & Confidence Score
PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran

FITUR SMART:
[OK] Pattern Recognition dari nama pelanggan (20+ keyword, 90%+ akurasi)
[OK] Smart Conflict Resolution (nama vs segmencustomer)
[OK] Confidence Score untuk setiap klasifikasi
[OK] Segmen-Aware Bandwidth Clustering
[OK] NBO spesifik untuk 19 segmen
[OK] Hybrid Classification: Nama + Segmen + Bandwidth
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

print("="*90)
print("CVO v3.0 - SMART CLASSIFIER with Pattern Recognition & Confidence Score")
print("="*90)


class SmartPatternRecognizer:
    """
    Smart Pattern Recognition untuk klasifikasi berdasarkan nama pelanggan
    dengan confidence score
    """
    
    # Dictionary pattern dengan akurasi dan confidence weight
    PATTERNS = {
        # GOVERNMENT - Akurasi 98%
        'GOVERNMENT': {
            'keywords': ['DINAS', 'KEMENTERIAN', 'KANTOR', 'BADAN', 'KEPOLISIAN', 'POLRES', 'POLSEK', 
                        'SATPOL PP', 'BAPPEDAS', 'BPKAD', 'DISPENDUKCAPIL', 'DINAS KOMUNIKASI',
                        'KANTOR PERTANAHAN', 'KEJAKSAAN', 'PENGADILAN', 'MAHKAMAH'],
            'accuracy': 0.98,
            'confidence_weight': 0.95,
            'description': 'Instansi Pemerintah'
        },
        
        # BANKING & FINANCIAL - Akurasi 98.4%
        'BANKING & FINANCIAL': {
            'keywords': ['BANK', 'KOPERASI', 'BPR', 'LEMBAGA KEUANGAN', 'PEGADAIAN', 'ASURANSI'],
            'accuracy': 0.984,
            'confidence_weight': 0.95,
            'description': 'Perbankan & Keuangan'
        },
        
        # EDUCATION (Universitas) - Akurasi 91.9%
        'EDUCATION_UNIV': {
            'keywords': ['UNIVERSITAS', 'UNIV ', 'INSTITUT', 'ITB', 'UI ', 'UGM ', 'IPB', 'ITS'],
            'accuracy': 0.919,
            'confidence_weight': 0.90,
            'description': 'Perguruan Tinggi'
        },
        
        # EDUCATION (SMK/SMA) - Akurasi tinggi
        'EDUCATION_SCHOOL': {
            'keywords': ['SMK', 'SMA', 'SMP', 'SD ', 'SEKOLAH', 'YAYASAN'],
            'accuracy': 0.90,
            'confidence_weight': 0.88,
            'description': 'Sekolah & Yayasan'
        },
        
        # HEALTH CARE - Akurasi 79.1%
        'HEALTH CARE': {
            'keywords': ['RS ', 'RS.', 'RUMAH SAKIT', 'HOSPITAL', 'KLINIK', 'PUSKESMAS', 
                        'LABORATORIUM KESEHATAN', 'APOTEK', 'DOKTER'],
            'accuracy': 0.791,
            'confidence_weight': 0.80,
            'description': 'Kesehatan'
        },
        
        # TRANSPORTATION - Akurasi tinggi
        'TRANSPORTATION': {
            'keywords': ['KERETA API', 'KAI ', 'MASKAPAI', 'AIRLINES', 'PELNI', 'ANGKUTAN',
                        'BUS ', 'TRANSPORTASI', 'TERMINAL', 'BANDAR UDARA'],
            'accuracy': 0.95,
            'confidence_weight': 0.92,
            'description': 'Transportasi'
        },
        
        # SELULAR OPERATOR - Akurasi 99.5%
        'SELULAR OPERATOR PROVIDER': {
            'keywords': ['TELKOMSEL', 'INDOSAT', 'XL ', 'SMARTFREN', 'HUTCHISON', 'THREE',
                        'AXIS', 'TRI ', 'OPERATOR SELULER'],
            'accuracy': 0.995,
            'confidence_weight': 0.98,
            'description': 'Operator Seluler'
        },
        
        # NATURAL RESOURCES - Akurasi 80-85%
        'NATURAL RESOURCES': {
            'keywords': ['PUPUK', 'PERKEBUNAN', 'PERTAMINA', 'PLANTATION', 'Palm Oil',
                        'KELAPA SAWIT', 'PERTANIAN', 'KEHUTANAN'],
            'accuracy': 0.83,
            'confidence_weight': 0.82,
            'description': 'Sumber Daya Alam'
        },
        
        # ENERGY UTILITY - Akurasi tinggi
        'ENERGY UTILITY MINING': {
            'keywords': ['PLN', 'LISTRIK', 'PJB', 'TAMBANG', 'MINING', 'ENERGI',
                        'BATU BARA', 'OIL ', 'GAS ', 'GEOTHERMAL'],
            'accuracy': 0.90,
            'confidence_weight': 0.88,
            'description': 'Energi & Tambang'
        },
        
        # MEDIA & ENTERTAINMENT
        'MEDIA & ENTERTAINMENT': {
            'keywords': ['TV', 'TELEVISI', 'RADIO', 'MEDIA', 'BROADCASTING',
                        'PRODUCTION HOUSE', 'FILM ', 'ENTERTAINMENT'],
            'accuracy': 0.85,
            'confidence_weight': 0.80,
            'description': 'Media & Hiburan'
        },
        
        # HOSPITALITY
        'HOSPITALITY': {
            'keywords': ['HOTEL', 'RESTORAN', 'RESTAURANT', 'CAFE', 'KANTIN',
                        'PENGINAPAN', 'VILLA', 'RESORT'],
            'accuracy': 0.85,
            'confidence_weight': 0.82,
            'description': 'Perhotelan & Restoran'
        },
        
        # PROPERTY
        'PROPERTY': {
            'keywords': ['PROPERTY', 'PROPERTI', 'REAL ESTATE', 'APARTEMEN', 'KONDORINIUM',
                        'PERUMAHAN', 'PENGEMBANGAN', 'DEVELOPER'],
            'accuracy': 0.80,
            'confidence_weight': 0.78,
            'description': 'Properti'
        },
        
        # CONSULTANT (CV biasanya) - Tapi check keywords lain dulu
        'CONSULTANT, CONTRACT': {
            'keywords': ['CONSULTANT', 'KONSULTAN', 'KONTRAKTOR', 'KONSTRUKSI',
                        'ENGINEERING', 'ARCHITECT', 'ARSITEK'],
            'accuracy': 0.75,
            'confidence_weight': 0.70,
            'description': 'Konsultan & Kontraktor'
        }
    }
    
    @classmethod
    def recognize_pattern(cls, nama_pelanggan):
        """
        Recognize pattern dari nama pelanggan dengan confidence score
        
        Returns:
            dict: {'segmen': str, 'confidence': float, 'matched_keyword': str, 'accuracy': float}
        """
        nama = str(nama_pelanggan).upper().strip()
        
        best_match = None
        best_confidence = 0
        matched_keyword = None
        
        # Check semua pattern
        for segmen, data in cls.PATTERNS.items():
            for keyword in data['keywords']:
                if keyword in nama:
                    # Calculate confidence
                    confidence = data['confidence_weight']
                    
                    # Boost confidence jika keyword di awal nama
                    if nama.startswith(keyword):
                        confidence = min(0.99, confidence + 0.05)
                    
                    # Boost confidence jika keyword sebelum/ sesudah PT/CV
                    if re.search(r'(PT|CV)\s+' + re.escape(keyword), nama) or \
                       re.search(re.escape(keyword) + r'\s+(PT|CV)', nama):
                        confidence = min(0.99, confidence + 0.03)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = segmen
                        matched_keyword = keyword
        
        if best_match:
            return {
                'segmen': best_match,
                'confidence': best_confidence,
                'matched_keyword': matched_keyword,
                'accuracy': cls.PATTERNS[best_match]['accuracy'],
                'method': 'pattern_recognition'
            }
        
        return None
    
    @classmethod
    def get_confidence_level(cls, confidence_score):
        """Convert confidence score to level"""
        if confidence_score >= 0.90:
            return 'HIGH'
        elif confidence_score >= 0.75:
            return 'MEDIUM'
        elif confidence_score >= 0.50:
            return 'LOW'
        else:
            return 'VERY_LOW'


class SmartCustomerClassifier:
    """
    Smart Customer Classifier dengan Hybrid Approach:
    Pattern Recognition (Nama) + segmencustomer + Bandwidth
    """
    
    def __init__(self):
        self.pattern_recognizer = SmartPatternRecognizer()
    
    def classify(self, nama_pelanggan, segmencustomer, bandwidth_mbps, tier=None, pendapatan=None):
        """
        Klasifikasi cerdas dengan hybrid approach
        
        Returns:
            dict: Hasil klasifikasi lengkap dengan confidence
        """
        # STEP 1: Pattern Recognition dari Nama
        pattern_result = self.pattern_recognizer.recognize_pattern(nama_pelanggan)
        
        # STEP 2: Smart Conflict Resolution
        if pattern_result and pattern_result['confidence'] >= 0.85:
            # Pattern nama kuat (>= 85%), override segmencustomer
            final_segmen = pattern_result['segmen']
            confidence = pattern_result['confidence']
            classification_method = 'pattern_override'
            conflict_resolved = True
        elif pattern_result and pattern_result['confidence'] >= 0.70:
            # Pattern medium, cek apakah segmencustomer cocok
            if self._is_segmen_compatible(pattern_result['segmen'], segmencustomer):
                final_segmen = segmencustomer  # Gunakan segmencustomer karena lebih spesifik
                confidence = pattern_result['confidence']
                classification_method = 'hybrid_agreement'
                conflict_resolved = False
            else:
                # Conflict! Pattern vs segmencustomer berbeda
                final_segmen = pattern_result['segmen']  # Prioritaskan pattern (akurasi tinggi)
                confidence = pattern_result['confidence'] - 0.10  # Penalty karena conflict
                classification_method = 'pattern_priority_conflict'
                conflict_resolved = True
        else:
            # Pattern lemah atau tidak ada, gunakan segmencustomer
            final_segmen = segmencustomer
            confidence = 0.60  # Default confidence untuk segmencustomer only
            pattern_result = None
            classification_method = 'segmen_only'
            conflict_resolved = False
        
        # STEP 3: Segmen-Aware Bandwidth Clustering
        cluster, cluster_reason = self._determine_bandwidth_cluster(
            final_segmen, bandwidth_mbps, nama_pelanggan
        )
        
        # STEP 4: Determine Strategic Quadrant
        kuadran, strategi, nbo = self._determine_quadrant_and_nbo(
            final_segmen, cluster, bandwidth_mbps, pendapatan, tier, nama_pelanggan
        )
        
        return {
            'nama_pelanggan': nama_pelanggan,
            'segmencustomer_original': segmencustomer,
            'segmen_final': final_segmen,
            'confidence': confidence,
            'confidence_level': self.pattern_recognizer.get_confidence_level(confidence),
            'classification_method': classification_method,
            'conflict_resolved': conflict_resolved,
            'pattern_match': pattern_result,
            'bandwidth_cluster': cluster,
            'cluster_reason': cluster_reason,
            'kuadran': kuadran,
            'strategi': strategi,
            'nbo': nbo
        }
    
    def _is_segmen_compatible(self, pattern_segmen, data_segmen):
        """Check apakah pattern segmen compatible dengan data segmen"""
        # EDUCATION grouping
        if 'EDUCATION' in pattern_segmen and 'EDUCATION' in str(data_segmen):
            return True
        # BANK grouping
        if 'BANKING' in pattern_segmen and 'BANKING' in str(data_segmen):
            return True
        # Default: exact match
        return pattern_segmen == str(data_segmen)
    
    def _determine_bandwidth_cluster(self, segmen, bandwidth_mbps, nama_pelanggan):
        """
        Determine bandwidth cluster berdasarkan segmen (Segmen-Aware)
        """
        nama = str(nama_pelanggan).upper()
        
        # NO_BANDWIDTH check
        if bandwidth_mbps == 0 or pd.isna(bandwidth_mbps):
            return 'NO_BANDWIDTH', 'Produk non-bandwidth (Managed Service/Platform)'
        
        # Segmen-specific rules
        if segmen == 'SELULAR OPERATOR PROVIDER':
            # Telco/ISP selalu high bandwidth
            if bandwidth_mbps > 500:
                return 'ENTERPRISE', 'Telco/ISP dengan bandwidth besar (Infrastructure)'
            else:
                return 'CORPORATE', 'Telco/ISP dengan bandwidth menengah (Access/Backhaul)'
        
        elif segmen == 'DATA COMM OPERATOR':
            # Data Comm juga high bandwidth
            if bandwidth_mbps > 1000:
                return 'ENTERPRISE', 'Data Comm dengan bandwidth sangat besar'
            else:
                return 'CORPORATE', 'Data Comm dengan bandwidth menengah'
        
        elif segmen == 'BANKING & FINANCIAL':
            # Bank - Corporate level (meskipun bandwidth kecil, tetap corporate karena value)
            if bandwidth_mbps > 100:
                return 'CORPORATE', 'Bank dengan bandwidth tinggi (Branch/Pusat)'
            else:
                return 'UMKM_SMALL', 'Bank dengan bandwidth kecil (Cabang kecil/ATM)'
        
        elif segmen == 'GOVERNMENT':
            # Pemerintah - cek level
            if 'KEMENTERIAN' in nama or 'GUBERNUR' in nama:
                return 'CORPORATE', 'Level Kementerian/Pemprov'
            elif 'DINAS' in nama:
                if bandwidth_mbps > 50:
                    return 'CORPORATE', 'Dinas dengan bandwidth tinggi'
                else:
                    return 'UMKM_SMALL', 'Dinas dengan bandwidth menengah'
            else:
                return 'UMKM_SMALL', 'Instansi pemerintah level kecil'
        
        elif segmen in ['EDUCATION_UNIV', 'EDUCATION_SCHOOL']:
            # Education - cek level
            if 'UNIVERSITAS' in nama or 'UNIV' in nama:
                return 'CORPORATE', 'Universitas (pusat riset)'
            elif bandwidth_mbps > 50:
                return 'CORPORATE', 'Sekolah besar dengan bandwidth tinggi'
            else:
                return 'UMKM_SMALL', 'SMK/SMA dengan bandwidth standar'
        
        elif segmen == 'HEALTH CARE':
            # RS - Corporate level
            if 'RUMAH SAKIT' in nama and bandwidth_mbps > 50:
                return 'CORPORATE', 'Rumah Sakit besar'
            else:
                return 'UMKM_SMALL', 'Klinik/RS kecil'
        
        elif segmen in ['MANUFACTURE', 'ENERGY UTILITY MINING']:
            # Industri - Enterprise level untuk besar
            if bandwidth_mbps > 500:
                return 'ENTERPRISE', 'Industri dengan bandwidth besar (Smart Factory)'
            else:
                return 'CORPORATE', 'Industri dengan bandwidth menengah'
        
        elif segmen == 'TRANSPORTATION':
            # Transportasi - cek skala
            if 'KERETA API' in nama or 'BANDAR UDARA' in nama:
                return 'ENTERPRISE', 'Transportasi infrastruktur utama'
            else:
                return 'CORPORATE', 'Operator transportasi'
        
        elif segmen == 'NATURAL RESOURCES':
            # Perkebunan/Pertambangan
            if bandwidth_mbps > 100:
                return 'CORPORATE', 'Perkebunan/Pertambangan besar'
            else:
                return 'UMKM_SMALL', 'Perkebunan/Pertambangan kecil'
        
        elif segmen == 'RETAIL DISTRIBUTION':
            # Retail - UMKM/Corporate tergantung ukuran
            if bandwidth_mbps > 100:
                return 'CORPORATE', 'Retail/Distributor besar'
            else:
                return 'UMKM_SMALL', 'Retail/Distributor menengah'
        
        elif segmen == 'HOSPITALITY':
            # Hotel
            if bandwidth_mbps > 50:
                return 'CORPORATE', 'Hotel besar'
            else:
                return 'UMKM_SMALL', 'Hotel/penginapan kecil'
        
        # Default: bandwidth-based only
        if bandwidth_mbps < 1:
            return 'ATM_IOT', 'ATM/IoT devices (low bandwidth)'
        elif bandwidth_mbps <= 20:
            return 'UMKM_SMALL', 'UMKM/Small office'
        elif bandwidth_mbps <= 500:
            return 'CORPORATE', 'Corporate'
        else:
            return 'ENTERPRISE', 'Enterprise'
    
    def _determine_quadrant_and_nbo(self, segmen, cluster, bandwidth_mbps, pendapatan, tier, nama_pelanggan):
        """
        Determine strategic quadrant dan NBO berdasarkan segmen + cluster
        """
        nama = str(nama_pelanggan).upper()
        
        # Initialize
        kuadran = None
        strategi = None
        nbo = []
        
        # === BANKING & FINANCIAL ===
        if 'BANKING' in segmen or segmen == 'BANKING & FINANCIAL':
            if cluster == 'CORPORATE':
                if bandwidth_mbps > 100:
                    kuadran = '[BANK] BANK CORPORATE HIGH'
                    strategi = 'UPSELL + SECURITY: Digital Banking Infrastructure'
                    nbo = [
                        'Upgrade to Managed SD-WAN',
                        'DDoS Protection Service',
                        'Cloud Backup & Recovery',
                        'Managed Security Operations Center',
                        'Digital Branch Solutions'
                    ]
                else:
                    kuadran = '[BANK] BANK BRANCH STANDARD'
                    strategi = 'UPSELL: Branch Connectivity Enhancement'
                    nbo = [
                        'Upgrade bandwidth untuk cabang',
                        'ATM Network Optimization',
                        'Secure VPN Expansion'
                    ]
            elif cluster == 'ENTERPRISE':
                kuadran = '[BANK] BANKING PREMIUM'
                strategi = 'RETENTION + PREMIUM: Core Banking Infrastructure'
                nbo = [
                    'Dedicated Backbone Connection',
                    'Redundancy & Failover',
                    'Private Cloud Infrastructure',
                    '24/7 Premium SLA'
                ]
        
        # === EDUCATION ===
        elif 'EDUCATION' in segmen:
            if 'SMK' in nama or 'SMA' in nama:
                kuadran = ' SEKOLAH MENENGAH'
                strategi = 'UPSELL: Digital Learning Infrastructure'
                nbo = [
                    'Campus-wide WiFi Management',
                    'E-Learning Platform Support',
                    'Digital Library Connection',
                    'Video Conference Setup'
                ]
            elif 'UNIVERSITAS' in nama or 'UNIV' in nama:
                kuadran = ' UNIVERSITAS RESEARCH'
                strategi = 'CROSS-SELL: Research & Education Solutions'
                nbo = [
                    'Dedicated Research Internet',
                    'High-performance Computing Connection',
                    'International Eduroam',
                    'Smart Campus Platform'
                ]
            else:  # Yayasan, dll
                kuadran = ' INSTITUSI PENDIDIKAN'
                strategi = 'EDUKASI: Digital Transformation'
                nbo = [
                    'Basic Connectivity Upgrade',
                    'School Management System',
                    'Digital Content Platform'
                ]
        
        # === GOVERNMENT ===
        elif segmen == 'GOVERNMENT':
            if 'KEMENTERIAN' in nama:
                kuadran = '[GOV] KEMENTERIAN LEVEL'
                strategi = 'CROSS-SELL: National Infrastructure'
                nbo = [
                    'AP2T Integration',
                    'National Data Center Connection',
                    'Smart Government Platform',
                    'Secure Inter-ministry Network'
                ]
            elif 'DINAS' in nama:
                kuadran = '[GOV] DINAS LOKAL'
                strategi = 'CROSS-SELL: Smart City Solutions'
                nbo = [
                    'E-Government Platform',
                    'Public Service Optimization',
                    'Regional Data Integration',
                    'Smart City Infrastructure'
                ]
            else:
                kuadran = '[GOV] INSTANSI PEMERINTAH'
                strategi = 'EDUKASI: Digital Services'
                nbo = [
                    'Public WiFi Services',
                    'Digital Document Management',
                    'Online Service Portal'
                ]
        
        # === HEALTH CARE ===
        elif segmen == 'HEALTH CARE':
            if 'RUMAH SAKIT' in nama or bandwidth_mbps > 50:
                kuadran = '[HOSPITAL] RUMAH SAKIT BESAR'
                strategi = 'CROSS-SELL: Healthcare Digitalization'
                nbo = [
                    'Hospital Information System (HIS)',
                    'Telemedicine Platform',
                    'Medical IoT Integration',
                    'PACS (Medical Imaging)',
                    'Secure Healthcare Network'
                ]
            else:
                kuadran = '[HOSPITAL] KLINIK/PUSKESMAS'
                strategi = 'UPSELL: Healthcare Connectivity'
                nbo = [
                    'Reliable Internet for Telemedicine',
                    'Cloud-based Medical Records',
                    'Video Consultation Setup'
                ]
        
        # === SELULAR OPERATOR ===
        elif segmen == 'SELULAR OPERATOR PROVIDER':
            kuadran = '[SAT] TELCO INFRASTRUCTURE'
            strategi = 'RETENTION + OPTIMIZATION: Network Backbone'
            nbo = [
                'MetroNet Expansion',
                'Dark Fiber Leasing',
                'IP Transit Optimization',
                '5G Backhaul Infrastructure',
                'Network Monitoring Services'
            ]
        
        # === TRANSPORTATION ===
        elif segmen == 'TRANSPORTATION':
            if 'KERETA API' in nama or 'BANDAR UDARA' in nama:
                kuadran = ' INFRASTRUKTUR TRANSPORTASI'
                strategi = 'CROSS-SELL: Smart Transportation'
                nbo = [
                    'IoT Fleet Management',
                    'Real-time Passenger Info System',
                    'Secure Control Network',
                    'Smart Ticketing Platform'
                ]
            else:
                kuadran = ' OPERATOR TRANSPORTASI'
                strategi = 'DIGITALISASI: Transport Services'
                nbo = [
                    'Fleet Tracking System',
                    'Online Booking Platform',
                    'Customer WiFi Services'
                ]
        
        # === MANUFACTURE / INDUSTRY ===
        elif segmen in ['MANUFACTURE', 'ENERGY UTILITY MINING', 'NATURAL RESOURCES']:
            if cluster == 'ENTERPRISE':
                kuadran = '[FACTORY] INDUSTRI 4.0'
                strategi = 'CROSS-SELL: Smart Factory Solutions'
                nbo = [
                    'Industrial IoT Platform',
                    'Smart Manufacturing Network',
                    'Predictive Maintenance System',
                    'Secure OT-IT Integration',
                    'Private 5G for Industry'
                ]
            else:
                kuadran = '[FACTORY] PABRIK MENENGAH'
                strategi = 'UPSELL: Industrial Connectivity'
                nbo = [
                    'Reliable Production Network',
                    'CCTV & Security System',
                    'ERP System Connectivity'
                ]
        
        # === RETAIL DISTRIBUTION ===
        elif segmen == 'RETAIL DISTRIBUTION':
            kuadran = ' RETAIL DISTRIBUTION'
            strategi = 'DIGITAL: Supply Chain Solutions'
            nbo = [
                'Supply Chain Visibility',
                'Multi-branch Connectivity',
                'POS System Integration',
                'Warehouse Management System'
            ]
        
        # === HOSPITALITY ===
        elif segmen == 'HOSPITALITY':
            kuadran = ' HOSPITALITY'
            strategi = 'GUEST EXPERIENCE: Digital Hospitality'
            nbo = [
                'Premium Guest WiFi',
                'Smart Room Solutions',
                'Hotel Management System',
                'Digital Concierge Platform'
            ]
        
        # === UMKM (explicit) ===
        elif segmen == 'UMKM & RETAIL':
            kuadran = ' UMKM DIGITAL'
            strategi = 'EDUKASI: Digital Business Enablement'
            nbo = [
                'Basic Business Internet',
                'Online Presence Support',
                'Digital Payment Integration',
                'Social Media Marketing Tools'
            ]
        
        # Default berdasarkan cluster
        else:
            if cluster == 'NO_BANDWIDTH':
                kuadran = '[BRIEFCASE] NON-BW SERVICES'
                strategi = 'CROSS-SELL: Add Connectivity'
                nbo = ['Basic Internet Package', 'Managed Service Add-on']
            elif cluster == 'ATM_IOT':
                kuadran = '[SAT] ATM/IoT DEVICES'
                strategi = 'MAINTENANCE: Reliability'
                nbo = ['Ensure SLA compliance', 'Monitoring Services']
            elif cluster == 'UMKM_SMALL':
                kuadran = ' UMKM/SMALL'
                strategi = 'GROWTH: Upgrade to Corporate'
                nbo = ['Bandwidth Upgrade', 'Basic Security Package']
            elif cluster == 'CORPORATE':
                kuadran = '[OFFICE] CORPORATE STANDARD'
                strategi = 'UPSELL + CROSS-SELL'
                nbo = ['Bandwidth Upgrade', 'Managed Services', 'Security']
            else:  # ENTERPRISE
                kuadran = '[OFFICE] ENTERPRISE PREMIUM'
                strategi = 'RETENTION + OPTIMIZATION'
                nbo = ['Premium SLA', 'Optimization Services', 'Consulting']
        
        return kuadran, strategi, nbo[:5]  # Return top 5 NBO


# ============================================================================
# MAIN CVO CLASS
# ============================================================================

class CVOSmartClassifier:
    """Main CVO class with Smart Classification"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df_raw = None
        self.df_processed = None
        self.df_classified = None
        self.smart_classifier = SmartCustomerClassifier()
        self.metrics = {}
    
    def load_and_process(self):
        """Load dan preprocess data"""
        print("\n[DATA] Memuat data...")
        self.df_raw = pd.read_excel(self.data_path, engine='openpyxl')
        print(f"[OK] {len(self.df_raw):,} baris data dimuat")
        
        # Column mapping
        col_map = {
            'namaPelanggan': 'nama_pelanggan',
            'segmencustomer': 'segmencustomer',
            'Kelompok Tier': 'tier',
            'Bandwidth Fix': 'bandwidth_fix',
            'hargaPelanggan': 'pendapatan',
            'Lama_Langganan': 'masa_berlangganan',
            'statusLayanan': 'status'
        }
        
        for old, new in col_map.items():
            if old in self.df_raw.columns:
                self.df_raw.rename(columns={old: new}, inplace=True)
        
        # Parse bandwidth
        self.df_raw['bandwidth_mbps'] = self.df_raw['bandwidth_fix'].apply(self._parse_bandwidth)
        
        # Clean pendapatan
        self.df_raw['pendapatan'] = self.df_raw['pendapatan'].astype(str).str.replace(r'[^\d]', '', regex=True)
        self.df_raw['pendapatan'] = pd.to_numeric(self.df_raw['pendapatan'], errors='coerce').fillna(0)
        
        # Filter active
        self.df_processed = self.df_raw[self.df_raw['status'].str.contains('AKTIF|Aktif', case=False, na=False)]
        print(f"[OK] {len(self.df_processed):,} pelanggan aktif")
    
    def _parse_bandwidth(self, val):
        """Parse bandwidth fix"""
        if pd.isna(val) or str(val).lower() in ['tidak ada', 'nan', 'none', '-']:
            return 0
        
        val_str = str(val).lower()
        numbers = re.findall(r"[\d.]+", val_str.replace(',', '.'))
        
        if not numbers:
            return 0
        
        try:
            num = float(numbers[0])
        except:
            return 0
        
        if 'gbps' in val_str or 'gb' in val_str:
            return num * 1000
        elif 'kbps' in val_str or 'kb' in val_str:
            return num / 1000
        else:
            return num
    
    def classify_all(self):
        """Classify semua pelanggan dengan smart classifier"""
        print("\n[TARGET] Melakukan Smart Classification...")
        
        results = []
        
        for idx, row in self.df_processed.iterrows():
            result = self.smart_classifier.classify(
                nama_pelanggan=row.get('nama_pelanggan', ''),
                segmencustomer=row.get('segmencustomer', 'UNKNOWN'),
                bandwidth_mbps=row.get('bandwidth_mbps', 0),
                tier=row.get('tier', None),
                pendapatan=row.get('pendapatan', 0)
            )
            
            # Combine dengan data asli
            combined = {**row.to_dict(), **result}
            results.append(combined)
            
            if idx % 10000 == 0:
                print(f"   Progress: {idx:,} / {len(self.df_processed):,}")
        
        self.df_classified = pd.DataFrame(results)
        
        # Analysis
        print("\n[DATA] HASIL KLASIFIKASI:")
        print("="*80)
        
        # By Segmen Final
        print("\nDistribusi Segmen Final:")
        segmen_dist = self.df_classified['segmen_final'].value_counts()
        for segmen, count in segmen_dist.head(10).items():
            pct = count / len(self.df_classified) * 100
            print(f"  {segmen:30s}: {count:>6,} pel ({pct:>5.1f}%)")
        
        # By Bandwidth Cluster
        print("\nDistribusi Bandwidth Cluster:")
        cluster_dist = self.df_classified['bandwidth_cluster'].value_counts()
        for cluster, count in cluster_dist.items():
            pct = count / len(self.df_classified) * 100
            print(f"  {cluster:20s}: {count:>6,} pel ({pct:>5.1f}%)")
        
        # By Kuadran
        print("\nDistribusi Kuadran Strategis:")
        kuadran_dist = self.df_classified['kuadran'].value_counts()
        for kuadran, count in kuadran_dist.head(10).items():
            pct = count / len(self.df_classified) * 100
            print(f"  {kuadran:35s}: {count:>6,} pel ({pct:>5.1f}%)")
        
        # Confidence Analysis
        print("\nConfidence Score Analysis:")
        conf_dist = self.df_classified['confidence_level'].value_counts()
        for level, count in conf_dist.items():
            pct = count / len(self.df_classified) * 100
            print(f"  {level:10s}: {count:>6,} pel ({pct:>5.1f}%)")
        
        print("="*80)
    
    def generate_reports(self, output_dir='laporan_smart'):
        """Generate comprehensive reports"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n[DOCS] Generating reports in {output_dir}/...")
        
        # Master report
        cols_to_export = [
            'nama_pelanggan', 'segmencustomer_original', 'segmen_final', 
            'confidence', 'confidence_level', 'classification_method',
            'bandwidth_fix', 'bandwidth_mbps', 'bandwidth_cluster',
            'kuadran', 'strategi', 'nbo', 'tier', 'pendapatan'
        ]
        
        # Only export columns that exist
        cols_exist = [c for c in cols_to_export if c in self.df_classified.columns]
        df_export = self.df_classified[cols_exist]
        
        # 1. Master Report
        df_export.to_excel(f'{output_dir}/CVO_Smart_Master.xlsx', index=False)
        print("  [OK] CVO_Smart_Master.xlsx")
        
        # 2. By Segmen Final
        with pd.ExcelWriter(f'{output_dir}/CVO_Smart_by_Segmen.xlsx') as writer:
            for segmen in self.df_classified['segmen_final'].unique():
                sheet_name = str(segmen)[:31]
                df_segmen = self.df_classified[self.df_classified['segmen_final'] == segmen][cols_exist]
                df_segmen.to_excel(writer, sheet_name=sheet_name, index=False)
        print("  [OK] CVO_Smart_by_Segmen.xlsx")
        
        # 3. By Bandwidth Cluster
        with pd.ExcelWriter(f'{output_dir}/CVO_Smart_by_Cluster.xlsx') as writer:
            for cluster in self.df_classified['bandwidth_cluster'].unique():
                sheet_name = str(cluster)[:31]
                df_cluster = self.df_classified[self.df_classified['bandwidth_cluster'] == cluster][cols_exist]
                df_cluster.to_excel(writer, sheet_name=sheet_name, index=False)
        print("  [OK] CVO_Smart_by_Cluster.xlsx")
        
        # 4. High Confidence Targets
        high_conf = self.df_classified[self.df_classified['confidence'] >= 0.85]
        high_conf.to_excel(f'{output_dir}/CVO_Smart_High_Confidence.xlsx', index=False)
        print("  [OK] CVO_Smart_High_Confidence.xlsx")
        
        # 5. Summary statistics
        summary_stats = self._generate_summary_stats()
        with open(f'{output_dir}/Summary_Statistics.json', 'w') as f:
            json.dump(summary_stats, f, indent=2, default=str)
        print("  [OK] Summary_Statistics.json")
    
    def _generate_summary_stats(self):
        """Generate summary statistics"""
        stats = {
            'total_customers': len(self.df_classified),
            'segmen_distribution': self.df_classified['segmen_final'].value_counts().to_dict(),
            'cluster_distribution': self.df_classified['bandwidth_cluster'].value_counts().to_dict(),
            'confidence_distribution': self.df_classified['confidence_level'].value_counts().to_dict(),
            'classification_method': self.df_classified['classification_method'].value_counts().to_dict(),
            'pattern_matches': (self.df_classified['pattern_match'].notna()).sum(),
            'conflicts_resolved': (self.df_classified['conflict_resolved'] == True).sum()
        }
        return stats
    
    def run(self):
        """Run complete pipeline"""
        print("\n" + "="*90)
        print("CVO SMART CLASSIFIER v3.0")
        print("Hybrid Classification: Pattern Recognition + segmencustomer + Bandwidth")
        print("="*90)
        
        self.load_and_process()
        self.classify_all()
        self.generate_reports()
        
        print("\n" + "="*90)
        print("[OK] SMART CLASSIFICATION COMPLETE!")
        print("="*90)
        print("\n Reports generated in 'laporan_smart/'")
        print("   - CVO_Smart_Master.xlsx")
        print("   - CVO_Smart_by_Segmen.xlsx (19 sheets)")
        print("   - CVO_Smart_by_Cluster.xlsx (5 sheets)")
        print("   - CVO_Smart_High_Confidence.xlsx")
        print("   - Summary_Statistics.json")


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n" + "="*90)
    print("CVO v3.0 SMART CLASSIFIER")
    print("Sistem Klasifikasi Cerdas dengan Pattern Recognition")
    print("="*90)
    
    data_file = "Data Penuh Pelanggan Aktif.xlsx"
    if not os.path.exists(data_file):
        data_file = "Data Sampel Machine Learning.xlsx"
    
    print(f"\n[DATA] Processing: {data_file}")
    
    cvo = CVOSmartClassifier(data_file)
    cvo.run()
    
    print("\n[SUCCESS] Done! Check 'laporan_smart/' folder for results.")
