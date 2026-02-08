# CVO Dashboard - Konfigurasi Data Lengkap

## 📊 Konfigurasi Tersedia

### **1. Pagination (100-1000 rows per page)** ⭐ Direkomendasikan
**Keuntungan:**
- Load cepat (<1 detik)
- Browser tidak freeze
- Bisa scroll/lihat semua data via pagination
- Chart tetap smooth

**Cara pakai:**
```typescript
// Default: 100 rows
const { customers, setPerPage } = useCustomerData();

// Ganti ke 500 rows
setPerPage(500);

// Atau 1000 rows (maksimum)
setPerPage(1000);
```

### **2. Semua Data (57k rows)** ⚠️ Hati-hati
**Gunakan jika:**
- Perlu export semua data ke Excel
- Proses batch/analisis
- Tidak untuk ditampilkan di UI

**Cara pakai:**
```typescript
const { customers, loadAllData } = useCustomerData();

// Klik button "Load All Data"
<button onClick={loadAllData}>Load All (57k)</button>
```

⚠️ **Warning:** Browser bisa freeze/lambat dengan 57k rows!

### **3. Chart Data - Sampling (2000 points)** 📈
Chart tetap menggunakan sampling (tidak bisa 57k points):
- 2000 points sudah cukup untuk visualisasi
- Render cepat (<1 detik)
- Tetap representatif (stratified sampling)

## 🚀 Cara Jalankan

### **Step 1: Install API Dependencies**
```bash
cd D:\ICON+
pip install fastapi uvicorn pandas numpy pydantic
```

### **Step 2: Jalankan Backend**
```bash
# Terminal 1
cd D:\ICON+
python cvo_api.py

# Atau
uvicorn cvo_api:app --reload --port 8000
```

### **Step 3: Jalankan Frontend**
```bash
# Terminal 2
cd D:\ICON+\cvo-dashboard
npm run dev
```

## 📈 Endpoints API

### **Pagination (Direkomendasikan)**
```bash
# 100 rows (default)
GET /customers?page=1&per_page=100

# 500 rows
GET /customers?page=1&per_page=500

# 1000 rows (max)
GET /customers?page=1&per_page=1000
```

### **All Data (57k)**
```bash
GET /all-customers
```
⚠️ Response: ~25 MB JSON

### **Chart Data (Sampling)**
```bash
# 2000 points (default)
GET /chart-data?sample_size=2000

# 5000 points (max)
GET /chart-data?sample_size=5000
```

### **Stats**
```bash
GET /stats
```

### **Search**
```bash
GET /search?q=bank&limit=50
```

## 🎯 Rekomendasi Penggunaan

### **Untuk Daily Use:**
```typescript
const [perPage, setPerPage] = useState(100);
// Lihat 100 customers per page
// Navigate dengan pagination
```

### **Untuk Analisis:**
```typescript
const [perPage, setPerPage] = useState(500);
// Lihat 500 customers sekaligus
// Scroll dalam table
```

### **Untuk Export:**
```typescript
const { loadAllData } = useCustomerData();
// Load semua 57k data
// Export ke Excel
```

## ⚡ Performa

| Mode | Rows | Load Time | Browser | RAM |
|------|------|-----------|---------|-----|
| Default | 100 | <500ms | Smooth | 50MB |
| Extended | 500 | <1s | Good | 150MB |
| Maximum | 1000 | <2s | OK | 300MB |
| All Data | 57,000 | 5-10s | ⚠️ Lag | 2GB+ |

## 🔧 Update yang Dilakukan

### **Backend (`cvo_api.py`):**
- ✅ Pagination: max 1000 rows (dari 100)
- ✅ `/all-customers` endpoint (57k data)
- ✅ Chart sampling: max 5000 points (dari 2000)
- ✅ Compression & CORS enabled

### **Frontend (`hooks/useCustomerData.ts`):**
- ✅ Default 100 rows
- ✅ Bisa set sampai 1000 rows
- ✅ Fungsi `loadAllData()` untuk 57k
- ✅ Chart 2000 points

## 💡 Tips

**Jangan load 57k data kecuali:**
- Export ke Excel
- Batch processing
- Offline analysis

**Gunakan 100-500 rows untuk:**
- Daily monitoring
- Review customers
- Quick analysis

**Chart sampling 2000 points:**
- Sudah cukup untuk visualisasi
- Tidak perlu 57k points di chart
- Stratified sampling (representatif)

## ✅ Status
Semua endpoint siap digunakan! 
Pilih mode yang sesuai kebutuhan.
