"""
Script to run the notebook code directly
This avoids the asyncio issues with nbconvert on Windows
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("Running Notebook: Icon_Plus_Prediksi_Flow_Produk_2_")
print("=" * 50)

# Cell 0: Import libraries
print("\n[Cell 0] Importing libraries...")
try:
    import pandas as pd
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score
    import numpy as np
    print("[OK] All libraries imported successfully")
except ImportError as e:
    print(f"✗ Error importing libraries: {e}")
    sys.exit(1)

# Cell 1: Load data
print("\n[Cell 1] Loading data...")
try:
    file_path = 'SPE-OPT-31122025.xlsx'
    print("1. Sedang membaca file (ini mungkin memakan waktu untuk 200k baris)...")
    df = pd.read_excel(file_path)
    print(f"   Sukses! Total data: {len(df)} baris.")
except FileNotFoundError:
    print(f"   Error: File 'SPE-OPT-31122025.xlsx' tidak ditemukan!")
    print(f"   Pastikan file Excel ada di folder yang sama dengan script ini.")
    print(f"   Lokasi script: {os.path.abspath(__file__)}")
    sys.exit(1)
except Exception as e:
    print(f"   Error: {e}")
    sys.exit(1)

# Cell 2: Feature engineering
print("\n[Cell 2] Feature engineering...")
print("2. Membersihkan & Menambah Fitur Canggih...")

col_id = 'idPerusahaan'
col_prod = 'namaProduk'
col_date = 'tanggalAwalKontrak'
col_segmen = 'segmenCustomer'
col_sbu = 'sbuOwner'
col_price = 'hargaPelanggan'
col_bw = 'bandwidthBaru'

cols_to_use = [col_id, col_prod, col_date, col_segmen, col_sbu, col_price, col_bw]
df_ml = df[cols_to_use].copy()

df_ml[col_date] = pd.to_datetime(df_ml[col_date], errors='coerce')

def clean_currency(x):
    try:
        return float(str(x).replace(',', '.').replace('nan', '0'))
    except:
        return 0
df_ml[col_price] = df_ml[col_price].apply(clean_currency)
df_ml[col_bw] = pd.to_numeric(df_ml[col_bw], errors='coerce').fillna(0)

df_ml.dropna(subset=[col_prod, col_date], inplace=True)
df_ml.sort_values(by=[col_id, col_date], inplace=True)

grouped = df_ml.groupby(col_id)

df_ml['Prev_Product'] = grouped[col_prod].shift(1).fillna('New Customer')
df_ml['Prev_Date'] = grouped[col_date].shift(1)
df_ml['Days_Since_Last'] = (df_ml[col_date] - df_ml['Prev_Date']).dt.days.fillna(-1)
df_ml['Order_Seq'] = grouped.cumcount() + 1
df_ml['Next_Product'] = grouped[col_prod].shift(-1)

train_data_raw = df_ml.dropna(subset=['Next_Product']).copy()
latest_status = df_ml.groupby(col_id).tail(1).copy()

target_counts = train_data_raw['Next_Product'].value_counts()
valid_targets = target_counts[target_counts >= 2].index
train_data = train_data_raw[train_data_raw['Next_Product'].isin(valid_targets)].copy()

print(f"   Data Ready! Added features: Price, Bandwidth, Days_Since_Last, Prev_Product")

# Cell 3: Encoding
print("\n[Cell 3] Encoding data...")
print("3. Encoding Data & Persiapan Fitur...")

le_prod = LabelEncoder()
le_prev_prod = LabelEncoder()
le_segmen = LabelEncoder()
le_sbu = LabelEncoder()
le_target = LabelEncoder()

all_products = pd.concat([
    df_ml[col_prod],
    df_ml['Prev_Product'],
    df_ml['Next_Product'].dropna()
]).unique().astype(str)

le_prod.fit(all_products)
le_prev_prod.fit(all_products)
le_target.fit(all_products)

le_segmen.fit(df_ml[col_segmen].astype(str))
le_sbu.fit(df_ml[col_sbu].astype(str))

train_data['prod_code'] = le_prod.transform(train_data[col_prod].astype(str))
train_data['prev_prod_code'] = le_prev_prod.transform(train_data['Prev_Product'].astype(str))
train_data['segmen_code'] = le_segmen.transform(train_data[col_segmen].astype(str))
train_data['sbu_code'] = le_sbu.transform(train_data[col_sbu].astype(str))
train_data['target_code'] = le_target.transform(train_data['Next_Product'].astype(str))

print("   Encoding Selesai!")
print("   Fitur Siap: Produk, History Produk, Harga, Durasi, Segmen, dll.")

# Cell 4: Training
print("\n[Cell 4] Training XGBoost...")
print("4. Training XGBoost...")

features = [
    'prod_code',
    'prev_prod_code',
    'segmen_code',
    'sbu_code',
    'Days_Since_Last',
    col_price,
    col_bw,
    'Order_Seq'
]

X = train_data[features]

le_target_final = LabelEncoder()
y = le_target_final.fit_transform(train_data['Next_Product'].astype(str))

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = xgb.XGBClassifier(
    objective='multi:softmax',
    eval_metric='mlogloss',
    use_label_encoder=False,
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)

print("   Training model... (ini mungkin memakan waktu)")
model.fit(X_train, y_train)
print("   Model training selesai!")

# Cell 5: Evaluation and Prediction
print("\n[Cell 5] Evaluating and generating predictions...")

preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"   Akurasi Model: {acc*100:.2f}%")

print("\n5. Menghasilkan Prediksi Akhir...")

X_latest = latest_status.copy()

X_latest['prod_code'] = le_prod.transform(X_latest[col_prod].astype(str))
X_latest['prev_prod_code'] = le_prev_prod.transform(X_latest['Prev_Product'].astype(str))
X_latest['segmen_code'] = le_segmen.transform(X_latest[col_segmen].astype(str))
X_latest['sbu_code'] = le_sbu.transform(X_latest[col_sbu].astype(str))

X_final_pred = X_latest[features]

pred_codes = model.predict(X_final_pred)
pred_names = le_target_final.inverse_transform(pred_codes)

hasil_akhir = latest_status[[col_id, col_prod, col_segmen, col_sbu, col_date]].copy()
hasil_akhir.rename(columns={col_prod: 'Produk_Saat_Ini', col_date: 'Tanggal_Terakhir'}, inplace=True)
hasil_akhir['Rekomendasi_Produk_Berikutnya'] = pred_names
hasil_akhir['Beda_ato_ngga'] = np.where(hasil_akhir['Produk_Saat_Ini'] == hasil_akhir['Rekomendasi_Produk_Berikutnya'], 'Sama', 'Beda')

output_filename = 'Hasil_Prediksi_Flow_Fixed.xlsx'
hasil_akhir.to_excel(output_filename, index=False)
print(f"   Selesai! File tersimpan di: {output_filename}")

print("\n" + "=" * 50)
print("Notebook execution completed successfully!")
print("=" * 50)
