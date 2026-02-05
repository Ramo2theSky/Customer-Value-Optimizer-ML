"use client";

import { useState } from "react";
import {
  Zap,
  Download,
  Search,
  Users,
  TrendingUp,
  Target,
  DollarSign,
  AlertTriangle,
  BarChart3,
  Activity,
} from "lucide-react";
import * as XLSX from "xlsx";
import Link from "next/link";
import { useCustomerData } from "@/hooks/useCustomerData";
import { CustomerData } from "@/types";
import MatrixChart from "@/components/MatrixChart";
import TrustMatrixChart from "@/components/TrustMatrixChart";
import ClientTable from "@/components/ClientTable";
import SkeletonLoader from "@/components/SkeletonLoader";

// API Base URL
const API_BASE_URL = "http://localhost:8000";

// Format currency IDR yang proper (tidak hardcode 0)
const formatIDR = (value: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export default function Dashboard() {
  // Ambil data dari API backend
  const { 
    customers, 
    summary, 
    chartData,
    strategies,
    isLoading, 
    error,
    pagination,
    setPerPage,
    loadAllData,
    loadFullChartData,
    useFullData,
    setUseFullData,
    refetch,
    filterStrategy,
    setFilterStrategy,
    filterIndustry,
    setFilterIndustry,
    filterBandwidth,
    setFilterBandwidth,
    filterPriority,
    setFilterPriority,
    filterCurrentTier,
    setFilterCurrentTier,
    filterRecommendedTier,
    setFilterRecommendedTier
  } = useCustomerData();
  
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerData | null>(null);
  const [isLoadingAll, setIsLoadingAll] = useState(false);
  const [isLoadingFullChart, setIsLoadingFullChart] = useState(false);

  // Loading state dengan skeleton (tidak layar putih!)
  if (isLoading) {
    return <SkeletonLoader />;
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Error loading data: {error}</p>
          <p className="text-gray-500 mt-2">Please run Python pipeline first</p>
        </div>
      </div>
    );
  }

  // Filter customers berdasarkan search (strategy sudah di-filter di API)
  const filteredCustomers = searchQuery
    ? customers.filter((c) => {
        const query = searchQuery.toLowerCase();
        return (
          c.customer_name?.toLowerCase().includes(query) ||
          c.industry?.toLowerCase().includes(query)
        );
      })
    : customers;

  // HITUNG STATS DINAMIS DARI SUMMARY API (tidak dari data terfilter!)
  const stats = {
    totalRevenue: summary?.total_revenue || 0,
    totalCustomers: summary?.total_customers || 0,
    avgRevenue: summary?.avg_revenue || 0,
    // NBO Stats
    potentialRevenue: summary?.potential_revenue || 0,
    avgUpsellScore: summary?.avg_upsell_score || 0,
    highPriorityCount: summary?.high_priority_count || 0,
    mediumPriorityCount: summary?.medium_priority_count || 0,
    lowPriorityCount: summary?.low_priority_count || 0,
  };

  // Get top 4 strategies by count for display
  const topStrategies = strategies.slice(0, 4);



  // Export SEMUA data master (57k customers) - Master Analysis Format
  const handleExport = async () => {
    try {
      // Fetch all data dari API
      const res = await fetch(`${API_BASE_URL}/all-customers?sort_by=revenue&sort_order=desc`);
      if (!res.ok) throw new Error('Failed to fetch data for export');
      const allData = await res.json();
      
      const wb = XLSX.utils.book_new();
      const data = allData.data.map((c: any) => ({
        ID: c.id,
        Customer_Name: c.customer_name,
        Industry: c.industry,
        "Revenue (Monthly)": c.revenue,
        Bandwidth_Segment: c.bandwidth_segment,
        Bandwidth_Score: c.bandwidth_score,
        Tenure_Years: c.tenure,
        Current_Tier: c.current_tier,
        Recommended_Tier: c.recommended_tier,
        Upsell_Score: c.upsell_score,
        Priority: c.priority,
        Potential_Revenue: c.potential_revenue,
        Strategy_Label: c.strategy_label,
        Strategy_Action: c.strategy_action,
        Recommended_Product: c.recommended_product,
        Reasoning: c.reasoning,
        Strategy_Color: c.strategy_color,
      }));
      const ws = XLSX.utils.json_to_sheet(data);
      
      // Set column widths for better readability
      ws['!cols'] = [
        { wch: 10 },  // ID
        { wch: 30 },  // Customer_Name
        { wch: 20 },  // Industry
        { wch: 18 },  // Revenue (Monthly)
        { wch: 18 },  // Bandwidth_Segment
        { wch: 15 },  // Bandwidth_Score
        { wch: 13 },  // Tenure_Years
        { wch: 15 },  // Current_Tier
        { wch: 18 },  // Recommended_Tier
        { wch: 12 },  // Upsell_Score
        { wch: 10 },  // Priority
        { wch: 18 },  // Potential_Revenue
        { wch: 25 },  // Strategy_Label
        { wch: 25 },  // Strategy_Action
        { wch: 25 },  // Recommended_Product
        { wch: 50 },  // Reasoning
        { wch: 15 },  // Strategy_Color
      ];
      
      XLSX.utils.book_append_sheet(wb, ws, "Master Analysis");
      XLSX.writeFile(wb, `CVO_Master_Analysis_${new Date().toISOString().split("T")[0]}_${allData.total.toLocaleString()}_customers.xlsx`);
    } catch (err) {
      console.error('Export error:', err);
      alert('Failed to export data. Please try again.');
    }
  };

  // Fungsi untuk load semua data (57k)
  const handleLoadAllData = async () => {
    if (confirm("Anda akan memuat SEMUA data (57,000+ pelanggan).\n\nINI BISA MENYEBABKAN:\n- Browser lambat/freeze\n- Memori tinggi\n- Waktu load 5-10 detik\n\nLanjutkan?")) {
      setIsLoadingAll(true);
      await loadAllData();
      setIsLoadingAll(false);
    }
  };

  // Fungsi untuk ganti jumlah rows per page
  const handleChangeRowsPerPage = (rows: number) => {
    setPerPage(rows);
    refetch();
  };

  // Fungsi untuk load chart dengan 57k points
  const handleLoadFullChart = async () => {
    if (confirm("Anda akan memuat SEMUA data untuk chart (57,000+ points).\n\nINI BISA MENYEBABKAN:\n- Browser lambat/freeze\n- Chart render 3-5 detik\n- Memori tinggi (500MB+)\n\nLanjutkan?")) {
      setIsLoadingFullChart(true);
      await loadFullChartData();
      setIsLoadingFullChart(false);
    }
  };

  // Toggle untuk switch antara sampled/full chart
  const toggleFullChart = async () => {
    if (!useFullData) {
      // Switch ke full data
      await handleLoadFullChart();
    } else {
      // Switch ke sampled data
      setUseFullData(false);
      refetch();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 overflow-x-hidden">
      {/* Top Navigation Bar */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">PLN Icon+</h1>
                <p className="text-xs text-gray-500">Customer Value Optimizer</p>
              </div>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search customer by name or industry..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex overflow-x-hidden min-w-0">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          <nav className="p-4 space-y-2">
            <Link
              href="/"
              className="flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-700 rounded-lg"
            >
              <BarChart3 className="w-5 h-5" />
              <span className="font-medium">Dashboard</span>
            </Link>
            <Link
              href="/customers"
              className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg"
            >
              <Users className="w-5 h-5" />
              <span>Customers</span>
              <span className="ml-auto bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">
                {stats.totalCustomers.toLocaleString()}
              </span>
            </Link>
            <Link
              href="/campaigns"
              className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg"
            >
              <Target className="w-5 h-5" />
              <span>Campaigns</span>
            </Link>
            <Link
              href="/reports"
              className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg"
            >
              <Activity className="w-5 h-5" />
              <span>Reports</span>
            </Link>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 min-w-0 overflow-x-hidden">
          {/* Stats Cards - Dynamic Strategy Categories from API */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {topStrategies.length > 0 ? topStrategies.map((strategy, index) => {
              const icons = [DollarSign, AlertTriangle, Target, Users];
              const Icon = icons[index % icons.length];
              const isActive = filterStrategy === strategy.label;
              
              return (
                <div 
                  key={strategy.label}
                  onClick={() => setFilterStrategy(strategy.label)}
                  className={`bg-white rounded-xl shadow-sm p-6 border-l-4 cursor-pointer transition-all hover:shadow-md ${isActive ? 'ring-2 ring-offset-2' : ''}`}
                  style={{ 
                    borderLeftColor: strategy.color || '#6B7280',
                    outlineColor: isActive ? strategy.color || '#6B7280' : undefined 
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 mb-1 truncate max-w-[180px]" title={strategy.label}>
                        {strategy.label}
                      </p>
                      <h3 className="text-2xl font-bold text-gray-900">
                        {strategy.count.toLocaleString()}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {((strategy.count / stats.totalCustomers) * 100).toFixed(1)}% of customers
                      </p>
                    </div>
                    <div 
                      className="w-12 h-12 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${strategy.color}20` || '#F3F4F6' }}
                    >
                      <Icon className="w-6 h-6" style={{ color: strategy.color || '#6B7280' }} />
                    </div>
                  </div>
                </div>
              );
            }) : (
              // Fallback loading state
              <>
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-gray-300">
                    <div className="animate-pulse flex items-center justify-between">
                      <div className="space-y-2">
                        <div className="h-4 w-24 bg-gray-200 rounded"></div>
                        <div className="h-8 w-16 bg-gray-200 rounded"></div>
                      </div>
                      <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>

          {/* Summary Bar - NBO (Next Best Offer) Metrics */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl shadow-sm p-4 mb-8 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-8 flex-wrap">
                <div>
                  <p className="text-xs text-blue-200">Total Customers</p>
                  <p className="text-xl font-bold">{stats.totalCustomers.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-blue-200">Total Revenue</p>
                  <p className="text-xl font-bold">{formatIDR(stats.totalRevenue)}</p>
                </div>
                <div>
                  <p className="text-xs text-blue-200">Avg Revenue</p>
                  <p className="text-xl font-bold">{formatIDR(stats.avgRevenue)}</p>
                </div>
                <div>
                  <p className="text-xs text-blue-200">Potential Revenue (NBO)</p>
                  <p className="text-xl font-bold text-yellow-300">{formatIDR(stats.potentialRevenue)}</p>
                </div>
                <div>
                  <p className="text-xs text-blue-200">Avg Upsell Score</p>
                  <p className="text-xl font-bold">{stats.avgUpsellScore.toFixed(0)}/100</p>
                </div>
                <div>
                  <p className="text-xs text-blue-200">High Priority</p>
                  <p className="text-xl font-bold text-red-300">{stats.highPriorityCount.toLocaleString()}</p>
                </div>
              </div>
              {(filterStrategy || filterPriority || filterCurrentTier || filterRecommendedTier) && (
                <button
                  onClick={() => {
                    setFilterStrategy("");
                    setFilterPriority("");
                    setFilterCurrentTier("");
                    setFilterRecommendedTier("");
                  }}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </div>

          {/* Matrix Charts - DUAL MATRIX */}
          <div className="mb-8">
            {/* Toggle untuk Full Chart Data */}
            <div className="bg-white rounded-xl shadow-sm p-4 mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900">NBO (Next Best Offer) Matrix Visualization</h3>
                <p className="text-sm text-gray-500">
                  {useFullData 
                    ? `⚠️ Full data loaded: ${chartData?.total_size?.toLocaleString() || 0} points (Browser may be slow)` 
                    : `✓ Sampled data: ${chartData?.sample_size || 2000} points (Fast)`}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Customer segmentation for upsell & cross-sell opportunities
                </p>
              </div>
              <button
                onClick={toggleFullChart}
                disabled={isLoadingFullChart}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isLoadingFullChart
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : useFullData
                      ? "bg-orange-500 text-white hover:bg-orange-600"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
              >
                {isLoadingFullChart 
                  ? "Loading 57k Points..." 
                  : useFullData 
                    ? "Switch to Sampled (Fast)" 
                    : "Load Full Data (57k)"
                }
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-hidden">
              {/* Matrix 1: Revenue vs Bandwidth */}
              <div className="min-w-0">
                <MatrixChart
                  data={chartData?.sales_matrix || []}
                  title="Sales Matrix: Revenue vs Bandwidth"
                  isFullData={useFullData}
                />
              </div>
              
              {/* Matrix 2: Revenue vs Tenure */}
              <div className="min-w-0">
                <TrustMatrixChart
                  data={chartData?.trust_matrix || []}
                  title="Trust Matrix: Revenue vs Tenure"
                  isFullData={useFullData}
                />
              </div>
            </div>
          </div>

          {/* Action Table */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Priority Action List</h3>
                <p className="text-sm text-gray-500">
                  {(() => {
                    const filters = [];
                    if (filterStrategy) filters.push(filterStrategy);
                    if (filterPriority) filters.push(`${filterPriority} Priority`);
                    if (filterCurrentTier) filters.push(`Current: ${filterCurrentTier}`);
                    if (filterRecommendedTier) filters.push(`Rec: ${filterRecommendedTier}`);
                    if (filterIndustry) filters.push(filterIndustry);
                    if (filterBandwidth) filters.push(`${filterBandwidth} BW`);
                    
                    if (filters.length > 0) {
                      return `${pagination.total.toLocaleString()} clients found (${filters.join(' + ')}) | Showing ${customers.length.toLocaleString()} rows`;
                    }
                    return `${pagination.total.toLocaleString()} total pelanggan | Menampilkan ${customers.length.toLocaleString()} rows`;
                  })()}
                  {pagination.total > customers.length && ` (Page ${pagination.page}/${pagination.totalPages})`}
                </p>
              </div>
              <div className="flex gap-3 items-center">
                {/* Rows per page selector */}
                <select
                  value={pagination.perPage}
                  onChange={(e) => handleChangeRowsPerPage(Number(e.target.value))}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  disabled={isLoadingAll}
                >
                  <option value={20}>20 rows</option>
                  <option value={50}>50 rows</option>
                  <option value={100}>100 rows</option>
                  <option value={500}>500 rows</option>
                  <option value={1000}>1000 rows</option>
                </select>

                {/* Industry filter */}
                <div className="flex items-center gap-2">
                  <select
                    value={filterIndustry}
                    onChange={(e) => setFilterIndustry(e.target.value)}
                    className={`px-3 py-2 border rounded-lg text-sm min-w-[140px] ${
                      filterIndustry 
                        ? "border-purple-500 bg-purple-50 text-purple-700 font-medium" 
                        : "border-gray-300"
                    }`}
                  >
                    <option value="">All Industries</option>
                    <option value="BANKING & FINANCIAL">Banking & Financial</option>
                    <option value="MANUFACTURE">Manufacture</option>
                    <option value="RETAIL DISTRIBUTION">Retail Distribution</option>
                    <option value="GOVERNMENT">Government</option>
                    <option value="HOSPITALITY">Hospitality</option>
                    <option value="HEALTHCARE">Healthcare</option>
                    <option value="EDUCATION">Education</option>
                    <option value="ENERGY & RESOURCES">Energy & Resources</option>
                    <option value="PROPERTIES & CONSTRUCTION">Properties & Construction</option>
                    <option value="TRANSPORTATION & LOGISTICS">Transportation & Logistics</option>
                    <option value="OTHERS">Others</option>
                  </select>
                  {filterIndustry && (
                    <button
                      onClick={() => setFilterIndustry("")}
                      className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
                      title="Clear filter"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Bandwidth filter */}
                <div className="flex items-center gap-2">
                  <select
                    value={filterBandwidth}
                    onChange={(e) => setFilterBandwidth(e.target.value)}
                    className={`px-3 py-2 border rounded-lg text-sm ${
                      filterBandwidth 
                        ? "border-green-500 bg-green-50 text-green-700 font-medium" 
                        : "border-gray-300"
                    }`}
                  >
                    <option value="">All Bandwidth</option>
                    <option value="Low">Low</option>
                    <option value="Mid">Mid</option>
                    <option value="High">High</option>
                  </select>
                  {filterBandwidth && (
                    <button
                      onClick={() => setFilterBandwidth("")}
                      className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
                      title="Clear filter"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Priority filter */}
                <div className="flex items-center gap-2">
                  <select
                    value={filterPriority}
                    onChange={(e) => setFilterPriority(e.target.value)}
                    className={`px-3 py-2 border rounded-lg text-sm ${
                      filterPriority 
                        ? "border-red-500 bg-red-50 text-red-700 font-medium" 
                        : "border-gray-300"
                    }`}
                  >
                    <option value="">All Priorities</option>
                    <option value="High">High Priority</option>
                    <option value="Medium">Medium Priority</option>
                    <option value="Low">Low Priority</option>
                  </select>
                  {filterPriority && (
                    <button
                      onClick={() => setFilterPriority("")}
                      className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
                      title="Clear filter"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Current Tier filter */}
                <div className="flex items-center gap-2">
                  <select
                    value={filterCurrentTier}
                    onChange={(e) => setFilterCurrentTier(e.target.value)}
                    className={`px-3 py-2 border rounded-lg text-sm min-w-[130px] ${
                      filterCurrentTier 
                        ? "border-indigo-500 bg-indigo-50 text-indigo-700 font-medium" 
                        : "border-gray-300"
                    }`}
                  >
                    <option value="">All Current Tiers</option>
                    <option value="UMKM">UMKM</option>
                    <option value="CORPORATE">Corporate</option>
                    <option value="ENTERPRISE">Enterprise</option>
                    <option value="OFFICE">Office</option>
                    <option value="NON-BW">Non-BW</option>
                  </select>
                  {filterCurrentTier && (
                    <button
                      onClick={() => setFilterCurrentTier("")}
                      className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
                      title="Clear filter"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Recommended Tier filter */}
                <div className="flex items-center gap-2">
                  <select
                    value={filterRecommendedTier}
                    onChange={(e) => setFilterRecommendedTier(e.target.value)}
                    className={`px-3 py-2 border rounded-lg text-sm min-w-[160px] ${
                      filterRecommendedTier 
                        ? "border-teal-500 bg-teal-50 text-teal-700 font-medium" 
                        : "border-gray-300"
                    }`}
                  >
                    <option value="">All Recommended Tiers</option>
                    <option value="UMKM">UMKM</option>
                    <option value="CORPORATE">Corporate</option>
                    <option value="ENTERPRISE">Enterprise</option>
                    <option value="OFFICE">Office</option>
                    <option value="NON-BW">Non-BW</option>
                  </select>
                  {filterRecommendedTier && (
                    <button
                      onClick={() => setFilterRecommendedTier("")}
                      className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
                      title="Clear filter"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Strategy filter - Dynamic from API */}
                <div className="flex items-center gap-2">
                  <select
                    value={filterStrategy}
                    onChange={(e) => setFilterStrategy(e.target.value)}
                    className={`px-3 py-2 border rounded-lg text-sm min-w-[180px] ${
                      filterStrategy 
                        ? "border-blue-500 bg-blue-50 text-blue-700 font-medium" 
                        : "border-gray-300"
                    }`}
                  >
                    <option value="">All Strategies</option>
                    {strategies.map((strategy) => (
                      <option key={strategy.label} value={strategy.label}>
                        {strategy.label}
                      </option>
                    ))}
                  </select>
                  {filterStrategy && (
                    <button
                      onClick={() => setFilterStrategy("")}
                      className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
                      title="Clear filter"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Load All Data Button */}
                <button
                  onClick={handleLoadAllData}
                  disabled={isLoadingAll || customers.length === pagination.total}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isLoadingAll || customers.length === pagination.total
                      ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  }`}
                >
                  {isLoadingAll 
                    ? "Loading..." 
                    : customers.length === pagination.total 
                      ? "All Data Loaded" 
                      : "Load All (57k)"
                  }
                </button>

                {/* Clear All Filters Button */}
                {(filterStrategy || filterIndustry || filterBandwidth || filterPriority || filterCurrentTier || filterRecommendedTier) && (
                  <button
                    onClick={() => {
                      setFilterStrategy("");
                      setFilterIndustry("");
                      setFilterBandwidth("");
                      setFilterPriority("");
                      setFilterCurrentTier("");
                      setFilterRecommendedTier("");
                    }}
                    className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    Clear All Filters
                  </button>
                )}
              </div>
            </div>

            {/* Warning message jika load semua data */}
            {customers.length > 1000 && (
              <div className="px-6 py-3 bg-yellow-50 border-b border-yellow-200">
                <p className="text-sm text-yellow-800">
                  ⚠️ {customers.length.toLocaleString()} rows loaded. Browser mungkin lambat. 
                  Gunakan filter atau kurangi rows untuk performa lebih baik.
                </p>
              </div>
            )}

            <ClientTable
              customers={filteredCustomers}
              onSelectCustomer={setSelectedCustomer}
            />

            {/* Pagination Controls */}
            {pagination.totalPages > 1 && customers.length < pagination.total && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Page {pagination.page} of {pagination.totalPages}
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPerPage(pagination.perPage)}
                    disabled={pagination.page === 1}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPerPage(pagination.perPage)}
                    disabled={pagination.page === pagination.totalPages}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
