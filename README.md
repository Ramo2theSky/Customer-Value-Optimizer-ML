# CVO (Customer Value Optimizer) - NBO Engine v4.2

## 🎯 Project Overview

Sistem **AI-Powered Sales Intelligence** untuk PLN Icon+ yang menganalisis **5,663 pelanggan** menggunakan Machine Learning untuk memberikan rekomendasi produk yang presisi melalui framework **Next Best Offer (NBO)**.

### Business Impact
- 💰 **Total Revenue Managed**: Rp 120.8 Miliar/bulan
- 📊 **High-Value Accounts**: 1,285 priority targets
- 🎯 **4 Strategic Quadrants**: ML-powered customer segmentation
- 📈 **Potential Upside**: Rp 280+ Miliar additional revenue opportunity

---

## 📁 Project Structure (Organized)

```
D:/ICON+/
│
├── 📂 data/                          # All data files
│   ├── 📂 raw/                       # Raw input data
│   │   ├── 20260204 List Pelanggan Aktif PLN Icon Plus.xlsx
│   │   ├── Data Penuh Pelanggan Aktif.xlsx
│   │   └── Data Sampel*.xlsx
│   ├── 📂 processed/                 # Cleaned & processed data
│   │   └── Data Penuh Pelanggan Aktif Clean.xlsx
│   ├── 📂 validation/                # Validation lists
│   │   └── 20260204 List Pelanggan Aktif.xlsx
│   ├── 📂 catalog/                   # Product catalogs
│   │   ├── Mapping Seluruh Produk ICON+.xlsx
│   │   └── Product_Segment_Mapping_Full.xlsx
│   └── 📂 archive/                   # Archived/old data
│
├── 📂 src/                           # Source code
│   ├── 📂 pipeline/                  # Data processing pipelines
│   │   ├── cvo_nbo_advanced_v4_2.py
│   │   └── cvo_nbo_master_pipeline.py
│   ├── 📂 ml/                        # Machine Learning engines
│   │   ├── cvo_ml_engine.py
│   │   ├── cvo_nbo_v30.py
│   │   └── cvo_smart_classifier_v30.py
│   ├── 📂 api/                       # API & backend
│   │   └── cvo_api.py
│   ├── 📂 utils/                     # Helper utilities
│   │   └── [helper scripts]
│   └── 📂 archive/                   # Old/deprecated versions
│
├── 📂 notebooks/                     # Jupyter notebooks
│   ├── cvo_nbo_analysis_v4_2.ipynb
│   ├── 3 Project ML Icon+.ipynb
│   └── 📂 archive/
│
├── 📂 docs/                          # Documentation
│   ├── API_SETUP_GUIDE.md
│   ├── CARA_GUNAKAN_SEMUA_DATA.md
│   ├── PANDUAN_PENGGUNAAN.md
│   └── use-cases/                    # Use case documentation
│
├── 📂 output/                        # Generated outputs
│   ├── CVO_NBO_Master_2026_Advanced.xlsx
│   ├── dashboard_data.json
│   ├── 📂 visualizations/
│   │   ├── cvo_dual_matrix.png
│   │   └── cvo_dual_matrix_full.png
│   ├── 📂 dashboard_data/
│   └── 📂 reports/
│       ├── CVO_NBO_Master.xlsx
│       └── [other reports]
│
├── 📂 cvo-dashboard/                 # Next.js Frontend Application
│   ├── app/
│   ├── components/
│   ├── hooks/
│   └── public/data/
│
├── 📂 archive/                       # Temp & obsolete files
│
├── 📄 requirements.txt               # Python dependencies
└── 📄 README.md                      # This file
```

---

## 🚀 Quick Start

### 1. Setup Backend (FastAPI)

```bash
# Navigate to API directory
cd src/api

# Install dependencies
pip install -r ../../requirements.txt

# Start API server
python cvo_api.py
# API will run at http://localhost:8000
```

### 2. Setup Frontend (Next.js)

```bash
# Navigate to dashboard
cd cvo-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
# Dashboard will run at http://localhost:3000
```

### 3. Generate NBO (Optional)

```bash
# Run NBO pipeline
cd src/pipeline
python cvo_nbo_advanced_v4_2.py

# Output will be saved to output/ folder
```

---

## 📊 Data Flow

```
Input Data (data/raw/)
    ↓
Data Cleaning & Validation
    ↓
ML Processing (src/ml/)
    ↓
NBO Generation (src/pipeline/)
    ↓
API Serving (src/api/)
    ↓
Dashboard Display (cvo-dashboard/)
```

---

## 🎯 Key Features

### 1. 8-Factor NBO Scoring
- **Tier Compatibility** (15%)
- **Category Match** (15%)
- **Bandwidth Suitability** (15%)
- **Industry Fit** (15%)
- **Product Co-occurrence** (10%)
- **Regional Availability** (5%)
- **ARPU Affordability** (15%) - *Data-driven thresholds*
- **Tenure Strategy** (10%) - *Churn risk detection*

### 2. Smart Data Cleaning
- Handles "5 IP" (IP-Only customers)
- Handles "Berkontrak 2026" (Churn risk)
- Handles ARPU = 0 (Bundled products)
- Realistic thresholds based on data distribution

### 3. 4-Quadrant Strategy
- **Star**: High Revenue + High Bandwidth → RETAIN
- **Risk**: High Revenue + Low Bandwidth → CROSS-SELL
- **Sniper**: Low Revenue + High Bandwidth → UPSELL
- **Incubator**: Low Revenue + Low Bandwidth → AUTOMATE

---

## 📈 Output Format

### Excel Output (`output/CVO_NBO_Master_2026_Advanced.xlsx`)

**26 Columns:**
1. ID
2. Nama Pelanggan
3. Revenue
4. ARPU_Category (Entry/Mid/High/Enterprise)
5. Tenure_Tahun
6. Tenure_Strategy (Renewal Risk/Growth/Loyalty)
7. Bandwidth
8. Bandwidth_Type (Connectivity/IP-Only/Non-Connectivity)
9. Industry
10. Current_Tier
11. Current_Products
12. Product_Count
13. Strategy (Star/Risk/Sniper/Incubator)
14. Action
15. Priority (High/Medium/Low)
16. SBU
17. Status
18-26. NBO_1/2/3: Product, Score, Reasoning

---

## 🔧 Configuration

### ARPU Thresholds (Realistic)
```python
Entry: < Rp 1,000,000
Mid: Rp 1,000,000 - 3,500,000
High: Rp 3,500,000 - 15,000,000
Enterprise: > Rp 15,000,000
```

### Environment Variables
```bash
# Backend
API_BASE_URL=http://localhost:8000
DATA_FILE=data/processed/CVO_NBO_Master_2026_Advanced.xlsx

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📚 Documentation

- **[Setup Guide](docs/API_SETUP_GUIDE.md)** - API configuration
- **[User Guide](docs/PANDUAN_PENGGUNAAN.md)** - How to use
- **[Data Guide](docs/CARA_GUNAKAN_SEMUA_DATA.md)** - Data management
- **[Bahasa Indonesia](docs/VERSI_BAHASA_INDONESIA.md)** - Versi Indonesia

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- FastAPI (Async web framework)
- Pandas (Data processing)
- Scikit-learn (ML algorithms)

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts (Visualizations)

**Data:**
- Excel (Input/Output)
- JSON (API format)

---

## 📊 Business Metrics (Current Run)

```
Total Companies: 5,663
Total Revenue: Rp 120,758,064,079
Average Revenue: Rp 21,324,045

Strategy Distribution:
- Star: 2,689 (47%)
- Sniper: 2,149 (38%)
- Incubator: 559 (10%)
- Risk: 266 (5%)

Priority Distribution:
- Medium: 4,128 (73%)
- High: 1,285 (23%)
- Low: 250 (4%)

Top Industry: GOVERNMENT (1,629 companies)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- PLN Icon+ - Divisi Perencanaan & Analisis Pemasaran
- Data Science Team
- Business Development Team

---

**Last Updated:** February 2026  
**Version:** 4.2  
**Status:** Production Ready ✅
