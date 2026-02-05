# CARA MENGGUNAKAN SEMUA DATA (57,864 Pelanggan)

## 🎯 3 Cara Mengakses Semua Data

### **CARA 1: Pagination (Direkomendasikan)** ⭐
Gunakan rows per page selector untuk melihat lebih banyak data:

**Langkah:**
1. Di dashboard, lihat bagian **"Priority Action List"**
2. Klik dropdown **"20 rows"** (di kanan atas tabel)
3. Pilih:
   - **100 rows** → Lihat 100 pelanggan
   - **500 rows** → Lihat 500 pelanggan  
   - **1000 rows** → Lihat 1000 pelanggan (maksimum)

**Keuntungan:**
- ⚡ Cepat (1-2 detik load)
- 🔄 Bisa navigasi halaman (Previous/Next)
- 💾 Tidak freeze browser

---

### **CARA 2: Load All Data (57k Sekaligus)** ⚠️
Tekan tombol biru **"Load All (57k)"**

**Langkah:**
1. Di dashboard, klik tombol **"Load All (57k)"** di kanan atas tabel
2. Konfirmasi warning dialog
3. Tunggu 5-10 detik
4. Semua 57,864 pelanggan akan ditampilkan

**Peringatan:**
- ⚠️ Browser mungkin lambat/freeze
- ⚠️ Butuh memori tinggi (2GB+)
- ⚠️ Scroll akan berat
- ✅ Gunakan hanya untuk export atau kebutuhan khusus

**Jika browser freeze:**
- Refresh halaman (F5)
- Ulangi dengan rows lebih sedikit (500-1000)

---

### **CARA 3: Export ke Excel** 📊
Export semua data tanpa menampilkan di browser

**Langkah:**
1. Klik tombol **"Export"** di header (sebelah kanan)
2. File Excel akan di-download
3. Buka di Excel/Google Sheets
4. Analisis semua 57k data offline

---

## 🔧 Teknis (untuk Developer)

### **Update Hook:**
```typescript
const { 
  customers,        // Data yang ditampilkan (20-1000-57000)
  summary,          // Stats
  chartData,        // Data untuk chart (sampling 2000)
  pagination,       // Info page
  setPerPage,       // Ganti jumlah rows (20, 50, 100, 500, 1000)
  loadAllData,      // Fungsi load 57k
  refetch           // Refresh data
} = useCustomerData();
```

### **API Endpoints:**

**Pagination (Default):**
```
GET /customers?page=1&per_page=100
```

**All Data (57k):**
```
GET /all-customers
```

**Chart Data (Sampling):**
```
GET /chart-data?sample_size=2000
```

### **Frontend Code:**

```typescript
// Ganti rows per page
setPerPage(500);  // 20, 50, 100, 500, 1000
refetch();

// Load semua data
const handleLoadAll = async () => {
  await loadAllData(); // 57k rows
};
```

---

## 📊 Perbandingan Mode

| Mode | Rows | Load Time | Browser | RAM | Use Case |
|------|------|-----------|---------|-----|----------|
| **Default** | 100 | <1s | ⚡ Smooth | 50MB | Daily monitoring |
| **Extended** | 500 | 1-2s | ✅ Good | 150MB | Analysis |
| **Maximum** | 1000 | 2-3s | ⚠️ OK | 300MB | Deep review |
| **All Data** | 57,000 | 5-10s | 🐌 Lag | 2GB+ | Export only |

---

## 🚀 Cara Jalankan

### **Step 1: Jalankan Backend**
```bash
cd D:\ICON+
python cvo_api.py
```

### **Step 2: Jalankan Frontend**
```bash
cd D:\ICON+\cvo-dashboard
npm run dev
```

### **Step 3: Buka Browser**
http://localhost:3000

---

## 💡 Tips Penggunaan

**Untuk kerja sehari-hari:**
- Gunakan **100-500 rows**
- Navigate dengan pagination
- Filter by strategy (Star/Risk/Sniper)

**Untuk presentasi/reporting:**
- Export ke Excel
- Gunakan chart (sampling sudah cukup)
- Tidak perlu load 57k di browser

**Untuk analisis mendalam:**
- Load **1000 rows** maksimum
- Scroll manual dalam tabel
- Filter spesifik

**Jangan pernah:**
- ❌ Load 57k untuk daily use
- ❌ Scroll cepat dengan 57k rows
- ❌ Buka multiple tab dengan 57k data

---

## ⚡ Troubleshooting

**Browser freeze/lag:**
→ Refresh (F5) dan gunakan rows lebih sedikit

**Out of memory:**
→ Tutup tab lain, gunakan 100-500 rows saja

**Load lama:**
→ Cek koneksi, atau gunakan pagination

**Data tidak muncul:**
→ Cek backend running (localhost:8000)

---

## ✅ Status
Semua fitur siap digunakan! Pilih mode yang sesuai kebutuhan Anda.
