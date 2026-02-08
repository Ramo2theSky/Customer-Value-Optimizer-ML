"""
CVO FastAPI Backend
===================
High-performance API untuk dashboard dengan:
- Pagination (20-50 rows per page)
- Data sampling untuk charts (max 1000 points)
- Pre-aggregated stats
- Search & filter
- Response caching
- Compression

Run: uvicorn cvo_api:app --reload --port 8000
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from functools import lru_cache
import json
import os
from datetime import datetime

# Initialize FastAPI
app = FastAPI(
    title="CVO Dashboard API",
    description="High-performance API for PLN Icon+ Customer Value Optimizer",
    version="7.0.0"
)

# Enable CORS untuk Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global data storage
DATA_CACHE = None
DF_CACHE = None

def load_data():
    """Load data dari JSON (sekali saat startup) and normalize for frontend compatibility.

    Normalizations applied:
    - Trim `strategy_label` whitespace
    - Provide `segment` from `bandwidth_segment` if missing
    - Provide `current_spend` alias from `revenue` if missing
    - Map `priority` values (Indonesian/variants) to High/Medium/Low
    - Scale `upsell_score` from 0-1 to 0-100 when needed
    - Parse numeric Mbps from `bandwidth_original` strings
    """
    global DATA_CACHE, DF_CACHE

    if DATA_CACHE is not None:
        return DATA_CACHE, DF_CACHE

    json_path = 'cvo-dashboard/public/data/dashboard_data.json'

    if not os.path.exists(json_path):
        raise HTTPException(status_code=500, detail="Data file not found. Run Python pipeline first.")

    with open(json_path, 'r', encoding='utf-8') as f:
        DATA_CACHE = json.load(f)

    # Convert ke DataFrame untuk query cepat and normalize fields expected by frontend
    df = pd.DataFrame(DATA_CACHE)

    # Trim whitespace in strategy_label
    if 'strategy_label' in df.columns:
        df['strategy_label'] = df['strategy_label'].astype(str).str.strip()

    # Provide backwards-compatible 'segment' (frontend expects this)
    if 'segment' not in df.columns:
        if 'bandwidth_segment' in df.columns:
            df['segment'] = df['bandwidth_segment']
        else:
            df['segment'] = None

    # Provide 'current_spend' alias for legacy frontend usage
    if 'current_spend' not in df.columns and 'revenue' in df.columns:
        df['current_spend'] = df['revenue']

    # Normalize priority labels from Indonesian / inconsistent values to English High/Medium/Low
    def _map_priority(x):
        if pd.isna(x):
            return None
        s = str(x).strip().lower()
        if 'tinggi' in s or 'high' in s:
            return 'High'
        if 'sedang' in s or 'medium' in s:
            return 'Medium'
        if 'rendah' in s or 'low' in s:
            return 'Low'
        return x

    if 'priority' in df.columns:
        df['priority'] = df['priority'].apply(_map_priority)

    # Upsell score: scale 0-1 -> 0-100 if needed (frontend uses percent-style values)
    if 'upsell_score' in df.columns:
        try:
            ups_max = df['upsell_score'].dropna().astype(float).abs().max()
            if ups_max <= 1.01:
                df['upsell_score'] = df['upsell_score'].astype(float) * 100.0
            df['upsell_score'] = df['upsell_score'].fillna(0).astype(float).round(2)
        except Exception:
            df['upsell_score'] = df['upsell_score'].fillna(0)

    # Parse numeric Mbps from bandwidth_original (e.g., "100 MBPS" -> 100.0)
    if 'bandwidth_original' in df.columns:
        def _parse_bw(x):
            try:
                s = str(x)
                num = ''.join(ch for ch in s if (ch.isdigit() or ch == '.' or ch == ',' ))
                num = num.replace(',', '.')
                return float(num) if num else None
            except Exception:
                return None
        df['bandwidth_original'] = df['bandwidth_original'].apply(_parse_bw)

    # Normalize tier_priority to a readable string
    if 'tier_priority' in df.columns:
        df['tier_priority'] = df['tier_priority'].astype(str)

    # Finalize caches
    DF_CACHE = df
    DATA_CACHE = df.to_dict(orient='records')

    print(f"[OK] Loaded {len(DATA_CACHE)} customers into memory (normalized)")
    return DATA_CACHE, DF_CACHE

# Pydantic models - Updated for CVO_NBO_Master with 22+ columns
class Customer(BaseModel):
    id: str
    customer_name: str
    revenue: float
    bandwidth_segment: str
    bandwidth_score: int
    tenure: float
    strategy_label: str
    strategy_color: str
    strategy_action: str
    recommended_product: str
    reasoning: str
    industry: str
    # New fields from CVO_NBO_Master
    current_tier: Optional[str] = None
    recommended_tier: Optional[str] = None
    tier_priority: Optional[str] = None
    bandwidth_original: Optional[str] = None
    bandwidth_mbps: Optional[float] = None
    upsell_score: Optional[float] = Field(None, ge=0, le=1)
    priority: Optional[str] = None  # High/Medium/Low
    potential_revenue: Optional[float] = None
    current_product: Optional[str] = None
    clv_predicted: Optional[float] = None
    tenure_months: Optional[float] = None

class StatsResponse(BaseModel):
    total_customers: int
    total_revenue: float
    total_potential_revenue: float
    avg_revenue: float
    avg_upsell_score: float
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    # Dynamic strategy counts - will be populated from actual data
    strategy_counts: Dict[str, int]
    generated_at: str

class PaginatedCustomers(BaseModel):
    data: List[Customer]
    total: int
    page: int
    per_page: int
    total_pages: int

class ChartData(BaseModel):
    sales_matrix: List[Dict[str, Any]]  # Sampled untuk Revenue vs Bandwidth
    trust_matrix: List[Dict[str, Any]]  # Sampled untuk Revenue vs Tenure
    sample_size: int
    total_size: int

class PriorityCounts(BaseModel):
    high: int
    medium: int
    low: int

# Startup event
@app.on_event("startup")
async def startup_event():
    load_data()
    print("[START] API Ready! Endpoints:")
    print("   GET /stats - Dashboard statistics")
    print("   GET /customers - Paginated customer list")
    print("   GET /chart-data - Sampled data untuk charts")
    print("   GET /search - Search customers")

@app.get("/")
async def root():
    return {
        "message": "CVO Dashboard API",
        "version": "7.0.0",
        "docs": "/docs",
        "endpoints": ["/stats", "/customers", "/chart-data", "/search", "/industries", "/strategies", "/priorities"]
    }

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get pre-computed dashboard statistics for CVO_NBO_Master data"""
    _, df = load_data()
    
    # Calculate strategy counts dynamically from actual data
    strategy_counts = df['strategy_label'].value_counts().to_dict()
    strategy_counts = {str(k): int(v) for k, v in strategy_counts.items()}
    
    # Calculate priority counts
    priority_counts = df['priority'].value_counts().to_dict() if 'priority' in df.columns else {}
    
    # Handle potential_revenue - use column if exists, otherwise calculate as 30% of risk revenue
    if 'potential_revenue' in df.columns:
        total_potential_revenue = float(df['potential_revenue'].fillna(0).sum())
    else:
        # Fallback: calculate 30% of revenue for risk customers
        risk_mask = df['strategy_label'].str.contains('RISIKO', case=False, na=False)
        total_potential_revenue = float(df[risk_mask]['revenue'].sum() * 0.3)
    
    # Calculate average upsell score
    if 'upsell_score' in df.columns:
        avg_upsell = float(df['upsell_score'].fillna(0).mean())
    else:
        avg_upsell = 0.0
    
    stats = {
        "total_customers": len(df),
        "total_revenue": float(df['revenue'].sum()),
        "total_potential_revenue": total_potential_revenue,
        # Backwards-compatible alias expected by frontend
        "potential_revenue": total_potential_revenue,
        "avg_revenue": float(df['revenue'].mean()),
        "avg_upsell_score": avg_upsell,
        "high_priority_count": int(priority_counts.get('High', 0)),
        "medium_priority_count": int(priority_counts.get('Medium', 0)),
        "low_priority_count": int(priority_counts.get('Low', 0)),
        "strategy_counts": strategy_counts,
        "generated_at": datetime.now().isoformat()
    }
    
    return stats

@app.get("/strategies")
async def get_strategies():
    """Get list of unique strategy labels with counts (UI-friendly format)"""
    _, df = load_data()
    
    strategy_counts = df['strategy_label'].value_counts().to_dict()
    
    # Color palette for strategies
    STRATEGY_COLORS = [
        "#10B981",  # green
        "#F97316",  # orange
        "#3B82F6",  # blue
        "#9E9E9E",  # gray
        "#8B5CF6",  # purple
        "#06B6D4",  # cyan
        "#F59E0B",  # amber
        "#EF4444",  # red
        "#EC4899",  # pink
        "#14B8A6",  # teal
    ]
    
    # Build strategy objects with label, count, and color
    strategies = []
    for idx, (label, count) in enumerate(strategy_counts.items()):
        strategies.append({
            "label": str(label),
            "count": int(count),
            "color": STRATEGY_COLORS[idx % len(STRATEGY_COLORS)]
        })
    
    return {
        "strategies": strategies,
        "total_unique": len(strategy_counts)
    }

@app.get("/priorities")
async def get_priorities():
    """Get priority distribution"""
    _, df = load_data()
    
    if 'priority' in df.columns:
        priority_counts = df['priority'].value_counts().to_dict()
    else:
        priority_counts = {}
    
    return {
        "priorities": priority_counts,
        "high_priority_revenue": float(df[df['priority'] == 'High']['revenue'].sum()) if 'priority' in df.columns else 0.0
    }

@app.get("/customers", response_model=PaginatedCustomers)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(100, ge=1, le=1000, description="Items per page (max 1000)"),
    strategy: Optional[str] = Query(None, description="Filter by strategy label (e.g., '[TARGET] NON-BW HIGH VALUE')"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    bandwidth: Optional[str] = Query(None, description="Filter by bandwidth segment: Low, Mid, High"),
    priority: Optional[str] = Query(None, description="Filter by priority: High, Medium, Low"),
    sort_by: str = Query("revenue", description="Sort field: revenue, tenure, customer_name, upsell_score, potential_revenue"),
    sort_order: str = Query("desc", description="Sort order: asc, desc")
):
    """Get paginated customer list dengan filtering - supports new CVO_NBO_Master fields"""
    _, df = load_data()
    
    # Apply filters
    filtered_df = df.copy()
    
    if strategy:
        filtered_df = filtered_df[filtered_df['strategy_label'] == strategy]
    
    if industry:
        filtered_df = filtered_df[filtered_df['industry'].str.contains(industry, case=False, na=False)]
    
    if bandwidth:
        filtered_df = filtered_df[filtered_df['bandwidth_segment'].str.lower() == bandwidth.lower()]
    
    if priority and 'priority' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['priority'] == priority]
    
    # Sort
    ascending = sort_order.lower() == "asc"
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
    else:
        filtered_df = filtered_df.sort_values(by="revenue", ascending=ascending)
    
    # Pagination
    total = len(filtered_df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_df = filtered_df.iloc[start_idx:end_idx]
    
    # Convert ke dict
    customers = paginated_df.to_dict('records')
    
    return {
        "data": customers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@app.get("/all-customers")
async def get_all_customers(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    bandwidth: Optional[str] = Query(None, description="Filter by bandwidth segment: Low, Mid, High"),
    priority: Optional[str] = Query(None, description="Filter by priority: High, Medium, Low"),
    sort_by: str = Query("revenue", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order")
):
    """Get ALL customers (5,663 rows) - Gunakan dengan hati-hati, untuk export atau processing"""
    _, df = load_data()
    
    # Apply filters
    if strategy:
        df = df[df['strategy_label'] == strategy]
    
    if industry:
        df = df[df['industry'].str.contains(industry, case=False, na=False)]
    
    if bandwidth:
        df = df[df['bandwidth_segment'].str.lower() == bandwidth.lower()]
    
    if priority and 'priority' in df.columns:
        df = df[df['priority'] == priority]
    
    # Sort
    ascending = sort_order.lower() == "asc"
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)
    else:
        df = df.sort_values(by="revenue", ascending=ascending)
    
    # Convert ke list of dicts (semua data!)
    customers = df.to_dict('records')
    
    return {
        "data": customers,
        "total": len(customers),
        "note": "Warning: This endpoint returns all data. Use /customers for pagination."
    }

@app.get("/chart-data", response_model=ChartData)
async def get_chart_data(
    sample_size: int = Query(2000, ge=500, le=5000, description="Max points untuk chart (sampling, default 2000)"),
    strategy: Optional[str] = Query(None, description="Filter by strategy")
):
    """Get sampled data untuk charts (tidak kirim semua 5,663 points jika lebih besar dari sample_size)"""
    _, df = load_data()
    
    # Filter jika diminta
    if strategy:
        df = df[df['strategy_label'] == strategy]
    
    # Sampling untuk performance
    # Stratified sampling: ambil sample dari setiap strategy
    if len(df) > sample_size:
        strategies = df['strategy_label'].unique()
        samples = []
        
        for strat in strategies:
            strat_df = df[df['strategy_label'] == strat]
            # Proportional sampling
            strat_sample_size = max(20, int(sample_size * len(strat_df) / len(df)))
            samples.append(strat_df.sample(min(strat_sample_size, len(strat_df))))
        
        sampled_df = pd.concat(samples).sample(frac=1).reset_index(drop=True)  # Shuffle
    else:
        sampled_df = df
    
    # Define columns to include (including new fields if they exist)
    sales_cols = ['customer_name', 'industry', 'revenue', 'bandwidth_score', 
                  'bandwidth_segment', 'strategy_label', 'recommended_product']
    trust_cols = ['customer_name', 'industry', 'revenue', 'tenure',
                  'strategy_label', 'recommended_product']
    
    # Add new fields if they exist
    new_fields = ['upsell_score', 'priority', 'potential_revenue', 'current_product', 
                  'current_tier', 'recommended_tier', 'clv_predicted']
    
    for field in new_fields:
        if field in sampled_df.columns:
            sales_cols.append(field)
            trust_cols.append(field)
    
    # Prepare chart data
    sales_matrix = sampled_df[sales_cols].to_dict('records')
    trust_matrix = sampled_df[trust_cols].to_dict('records')
    
    return {
        "sales_matrix": sales_matrix,
        "trust_matrix": trust_matrix,
        "sample_size": len(sampled_df),
        "total_size": len(df)
    }

@app.get("/chart-data-full")
async def get_chart_data_full(
    strategy: Optional[str] = Query(None, description="Filter by strategy")
):
    """
    Get FULL data untuk charts (5,663 points!)
    ⚠️ WARNING: Ini akan kirim SEMUA data. Browser mungkin lambat.
    """
    _, df = load_data()
    
    # Filter jika diminta
    if strategy:
        df = df[df['strategy_label'] == strategy]
    
    # Define columns to include (including new fields if they exist)
    sales_cols = ['customer_name', 'industry', 'revenue', 'bandwidth_score', 
                  'bandwidth_segment', 'strategy_label', 'recommended_product']
    trust_cols = ['customer_name', 'industry', 'revenue', 'tenure',
                  'strategy_label', 'recommended_product']
    
    # Add new fields if they exist
    new_fields = ['upsell_score', 'priority', 'potential_revenue', 'current_product', 
                  'current_tier', 'recommended_tier', 'clv_predicted']
    
    for field in new_fields:
        if field in df.columns:
            sales_cols.append(field)
            trust_cols.append(field)
    
    # Prepare chart data - SEMUA DATA (tanpa sampling!)
    sales_matrix = df[sales_cols].to_dict('records')
    trust_matrix = df[trust_cols].to_dict('records')
    
    return {
        "sales_matrix": sales_matrix,
        "trust_matrix": trust_matrix,
        "total_size": len(df),
        "warning": "Full dataset loaded. Browser may be slow."
    }

@app.get("/search")
async def search_customers(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results")
):
    """Search customers by name, industry, or product"""
    _, df = load_data()
    
    query = q.lower()
    
    # Search di nama, industri, dan produk
    search_columns = ['customer_name', 'industry', 'recommended_product']
    
    # Add current_product to search if it exists
    if 'current_product' in df.columns:
        search_columns.append('current_product')
    
    mask = df[search_columns].apply(
        lambda col: col.str.lower().str.contains(query, na=False)
    ).any(axis=1)
    
    results = df[mask].head(limit).to_dict('records')
    
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }

@app.get("/customer/{customer_id}")
async def get_customer_detail(customer_id: str):
    """Get single customer detail with all new CVO_NBO_Master fields"""
    _, df = load_data()
    
    customer = df[df['id'] == customer_id].to_dict('records')
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer[0]

@app.get("/industries")
async def get_industries():
    """Get list of unique industries with revenue totals"""
    _, df = load_data()
    
    industry_stats = df.groupby('industry').agg({
        'revenue': ['count', 'sum', 'mean']
    }).round(2)
    
    industry_stats.columns = ['count', 'total_revenue', 'avg_revenue']
    industry_stats = industry_stats.sort_values('total_revenue', ascending=False)
    
    industries_data = industry_stats.to_dict('index')
    
    return {
        "industries": list(industries_data.keys()),
        "stats": industries_data,
        "total_unique": len(industries_data)
    }

@app.get("/tiers")
async def get_tiers():
    """Get tier distribution (current and recommended)"""
    _, df = load_data()
    
    result = {}
    
    if 'current_tier' in df.columns:
        result['current_tiers'] = df['current_tier'].value_counts().to_dict()
    
    if 'recommended_tier' in df.columns:
        result['recommended_tiers'] = df['recommended_tier'].value_counts().to_dict()
    
    if 'tier_priority' in df.columns:
        result['tier_priorities'] = df['tier_priority'].value_counts().to_dict()
    
    return result

@app.get("/products")
async def get_products():
    """Get current and recommended product distribution"""
    _, df = load_data()
    
    result = {
        "recommended_products": df['recommended_product'].value_counts().to_dict()
    }
    
    if 'current_product' in df.columns:
        result['current_products'] = df['current_product'].value_counts().to_dict()
    
    return result

# Health check
@app.get("/health")
async def health_check():
    _, df = load_data()
    
    health_info = {
        "status": "healthy",
        "customers_loaded": len(df),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "columns": list(df.columns),
        "column_count": len(df.columns)
    }
    
    # Add strategy count summary
    health_info["strategy_summary"] = df['strategy_label'].value_counts().to_dict()
    
    return health_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
