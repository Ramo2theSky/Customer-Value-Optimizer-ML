"use client";

import { useState, useEffect } from "react";
import {
  Users,
  Search,
  Filter,
  Building2,
  Wifi,
  TrendingUp,
  AlertTriangle,
  Download,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  Calendar,
  DollarSign,
  Shield,
  Zap,
  Loader2,
  AlertCircle,
  Target,
  Star,
  BarChart3,
  Award,
  ArrowRight,
  Layers,
} from "lucide-react";
import Link from "next/link";

// API Configuration
const API_BASE_URL = "http://localhost:8000";

// Types - CVO NBO Master Data Structure (22 fields)
interface Customer {
  // Core identifiers
  id: string;
  customer_name: string;
  industry: string;
  segment: string;
  
  // Revenue and financial
  current_spend: number;
  potential_revenue: number;
  revenue: number;
  
  // Tier information
  current_tier: string;
  recommended_tier: string;
  tier_priority: string;
  
  // Bandwidth
  bandwidth_original: number;
  bandwidth_mbps: number;
  
  // NBO scores and priority
  upsell_score: number;
  priority: "High" | "Medium" | "Low";
  
  // Product information
  current_product: string;
  recommended_product: string;
  
  // CLV and tenure
  clv_predicted: number;
  tenure_months: number;
  
  // AI reasoning
  reasoning: string;
  
  // Legacy fields for compatibility
  bandwidth_segment?: string;
  bandwidth_score?: number;
  strategy_label?: string;
  strategy_color?: string;
  strategy_action?: string;
}

// API Response Type
interface ApiResponse {
  data: Customer[];
  total: number;
}

// Filter options
const industries = [
  "All Industries",
  "BANKING & FINANCIAL",
  "MANUFACTURE",
  "RETAIL DISTRIBUTION",
  "GOVERNMENT",
  "HOSPITALITY",
  "HEALTHCARE",
  "EDUCATION",
  "ENERGY & RESOURCES",
  "PROPERTIES & CONSTRUCTION",
  "TRANSPORTATION & LOGISTICS",
  "OTHERS",
];

const priorities = ["All Priorities", "High", "Medium", "Low"];

// Helper functions
const formatIDR = (value: number) => {
  if (!value || value === 0) return "Rp 0";
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const formatNumber = (value: number) => {
  return new Intl.NumberFormat("id-ID").format(value);
};

const getPriorityColor = (priority: string) => {
  switch (priority?.toLowerCase()) {
    case "high":
      return { bg: "bg-red-100", text: "text-red-800", border: "border-red-200" };
    case "medium":
      return { bg: "bg-yellow-100", text: "text-yellow-800", border: "border-yellow-200" };
    case "low":
      return { bg: "bg-green-100", text: "text-green-800", border: "border-green-200" };
    default:
      return { bg: "bg-gray-100", text: "text-gray-800", border: "border-gray-200" };
  }
};

const getUpsellScoreColor = (score: number) => {
  if (score >= 80) return { bg: "bg-green-500", text: "text-green-700", label: "Excellent" };
  if (score >= 60) return { bg: "bg-blue-500", text: "text-blue-700", label: "Good" };
  if (score >= 40) return { bg: "bg-yellow-500", text: "text-yellow-700", label: "Average" };
  return { bg: "bg-orange-500", text: "text-orange-700", label: "Below Average" };
};

const getTierBadgeColor = (tier: string) => {
  const tierLower = tier?.toLowerCase() || "";
  if (tierLower.includes("enterprise")) return { bg: "bg-purple-100", text: "text-purple-800" };
  if (tierLower.includes("premium")) return { bg: "bg-blue-100", text: "text-blue-800" };
  if (tierLower.includes("standard")) return { bg: "bg-green-100", text: "text-green-800" };
  if (tierLower.includes("basic")) return { bg: "bg-gray-100", text: "text-gray-800" };
  return { bg: "bg-indigo-100", text: "text-indigo-800" };
};

export default function CustomersPage() {
  // State
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("All Industries");
  const [selectedPriority, setSelectedPriority] = useState("All Priorities");
  const [selectedCurrentTier, setSelectedCurrentTier] = useState("All Current Tiers");
  const [selectedRecommendedTier, setSelectedRecommendedTier] = useState("All Recommended Tiers");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const itemsPerPage = 10;

  // Dynamic filter options from data
  const [currentTiers, setCurrentTiers] = useState<string[]>(["All Current Tiers"]);
  const [recommendedTiers, setRecommendedTiers] = useState<string[]>(["All Recommended Tiers"]);

  // Fetch customers from API
  const fetchCustomers = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_BASE_URL}/customers?sort_by=upsell_score&sort_order=desc`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ApiResponse = await response.json();
      setCustomers(result.data);
      setFilteredCustomers(result.data);
      
      // Extract unique tier values for filters
      const uniqueCurrentTiers = Array.from(new Set(result.data.map(c => c.current_tier).filter(Boolean)));
      const uniqueRecommendedTiers = Array.from(new Set(result.data.map(c => c.recommended_tier).filter(Boolean)));
      
      setCurrentTiers(["All Current Tiers", ...uniqueCurrentTiers]);
      setRecommendedTiers(["All Recommended Tiers", ...uniqueRecommendedTiers]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch customers");
    } finally {
      setLoading(false);
    }
  };

  // Fetch data on mount
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Filter logic
  useEffect(() => {
    let filtered = customers;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.customer_name?.toLowerCase().includes(query) ||
          c.industry?.toLowerCase().includes(query) ||
          c.current_product?.toLowerCase().includes(query)
      );
    }

    // Industry filter
    if (selectedIndustry !== "All Industries") {
      filtered = filtered.filter((c) => c.industry === selectedIndustry);
    }

    // Priority filter
    if (selectedPriority !== "All Priorities") {
      filtered = filtered.filter((c) => c.priority?.toLowerCase() === selectedPriority.toLowerCase());
    }

    // Current Tier filter
    if (selectedCurrentTier !== "All Current Tiers") {
      filtered = filtered.filter((c) => c.current_tier === selectedCurrentTier);
    }

    // Recommended Tier filter
    if (selectedRecommendedTier !== "All Recommended Tiers") {
      filtered = filtered.filter((c) => c.recommended_tier === selectedRecommendedTier);
    }

    setFilteredCustomers(filtered);
    setCurrentPage(1);
  }, [searchQuery, selectedIndustry, selectedPriority, selectedCurrentTier, selectedRecommendedTier, customers]);

  // Pagination
  const totalPages = Math.ceil(filteredCustomers.length / itemsPerPage);
  const paginatedCustomers = filteredCustomers.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Stats calculations
  const stats = {
    totalCustomers: filteredCustomers.length,
    highPriorityCount: filteredCustomers.filter(c => c.priority === "High").length,
    avgUpsellScore: filteredCustomers.length > 0 
      ? Math.round(filteredCustomers.reduce((sum, c) => sum + (c.upsell_score || 0), 0) / filteredCustomers.length)
      : 0,
    totalPotentialRevenue: filteredCustomers.reduce((sum, c) => sum + (c.potential_revenue || 0), 0),
  };

  const handleExport = () => {
    // Create CSV content
    const headers = [
      "ID", "Customer Name", "Industry", "Segment", "Current Tier", "Recommended Tier",
      "Priority", "Upsell Score", "Current Spend", "Potential Revenue", "CLV Predicted",
      "Tenure (Months)", "Bandwidth (Mbps)", "Current Product", "Recommended Product"
    ];
    
    const rows = filteredCustomers.map(c => [
      c.id, c.customer_name, c.industry, c.segment, c.current_tier, c.recommended_tier,
      c.priority, c.upsell_score, c.current_spend, c.potential_revenue, c.clv_predicted,
      c.tenure_months, c.bandwidth_mbps, c.current_product, c.recommended_product
    ]);
    
    const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `nbo-customers-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
  };

  // Loading State
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">Loading NBO Customers...</h2>
          <p className="text-sm text-gray-500 mt-2">Fetching data from CVO Master database</p>
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Failed to Load Data</h2>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <button
            onClick={fetchCustomers}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">NBO Customer Directory</h1>
                <p className="text-xs text-gray-500">CVO Master - Next Best Offer Intelligence</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium"
              >
                Back to Dashboard
              </Link>
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        {/* Stats Bar */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div>
                <p className="text-xs text-gray-500">Total NBO Customers</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.totalCustomers)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">High Priority</p>
                <p className="text-2xl font-bold text-red-600">{formatNumber(stats.highPriorityCount)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Avg Upsell Score</p>
                <p className="text-2xl font-bold text-blue-600">{stats.avgUpsellScore}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Potential Revenue</p>
                <p className="text-2xl font-bold text-green-600">{formatIDR(stats.totalPotentialRevenue)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Smart Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Smart Filters</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search customer, industry..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Industry Filter */}
            <div className="relative">
              <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                {industries.map((ind) => (
                  <option key={ind} value={ind}>
                    {ind}
                  </option>
                ))}
              </select>
            </div>

            {/* Priority Filter */}
            <div className="relative">
              <AlertTriangle className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                {priorities.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>

            {/* Current Tier Filter */}
            <div className="relative">
              <Layers className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedCurrentTier}
                onChange={(e) => setSelectedCurrentTier(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                {currentTiers.map((tier) => (
                  <option key={tier} value={tier}>
                    {tier}
                  </option>
                ))}
              </select>
            </div>

            {/* Recommended Tier Filter */}
            <div className="relative">
              <Star className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedRecommendedTier}
                onChange={(e) => setSelectedRecommendedTier(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                {recommendedTiers.map((tier) => (
                  <option key={tier} value={tier}>
                    {tier}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Clear Filters */}
          {(searchQuery || selectedIndustry !== "All Industries" || selectedPriority !== "All Priorities" || 
            selectedCurrentTier !== "All Current Tiers" || selectedRecommendedTier !== "All Recommended Tiers") && (
            <button
              onClick={() => {
                setSearchQuery("");
                setSelectedIndustry("All Industries");
                setSelectedPriority("All Priorities");
                setSelectedCurrentTier("All Current Tiers");
                setSelectedRecommendedTier("All Recommended Tiers");
              }}
              className="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg text-sm font-medium"
            >
              Clear All Filters
            </button>
          )}
        </div>

        {/* Customer Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Customer Name
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Industry
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Current → Recommended
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Upsell Score
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Potential Revenue
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    CLV Predicted
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {paginatedCustomers.map((customer) => {
                  const priorityColors = getPriorityColor(customer.priority);
                  const upsellColors = getUpsellScoreColor(customer.upsell_score);
                  const currentTierColors = getTierBadgeColor(customer.current_tier);
                  const recommendedTierColors = getTierBadgeColor(customer.recommended_tier);

                  return (
                    <tr
                      key={customer.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => {
                        setSelectedCustomer(customer);
                        setIsDetailOpen(true);
                      }}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{customer.customer_name}</p>
                            <p className="text-xs text-gray-500">ID: {customer.id}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {customer.industry}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${currentTierColors.bg} ${currentTierColors.text}`}>
                            {customer.current_tier || "N/A"}
                          </span>
                          <ArrowRight className="w-3 h-3 text-gray-400" />
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${recommendedTierColors.bg} ${recommendedTierColors.text}`}>
                            {customer.recommended_tier || "N/A"}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${upsellColors.bg}`}
                              style={{ width: `${Math.min(customer.upsell_score || 0, 100)}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-900">{customer.upsell_score || 0}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors.bg} ${priorityColors.text}`}>
                          {customer.priority || "N/A"}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-gray-900">{formatIDR(customer.revenue || customer.current_spend || 0)}</p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-green-600">{formatIDR(customer.potential_revenue || 0)}</p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-purple-600">{formatIDR(customer.clv_predicted || 0)}</p>
                      </td>
                      <td className="px-6 py-4">
                        <button className="p-2 hover:bg-gray-100 rounded-lg">
                          <MoreHorizontal className="w-4 h-4 text-gray-400" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Showing {paginatedCustomers.length} of {filteredCustomers.length} customers
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm text-gray-700">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Customer Detail Modal */}
      {isDetailOpen && selectedCustomer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedCustomer.customer_name}</h2>
                  <p className="text-sm text-gray-500 mt-1">ID: {selectedCustomer.id} | Segment: {selectedCustomer.segment}</p>
                </div>
                <button
                  onClick={() => setIsDetailOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Priority & Score Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className={`p-4 rounded-lg border ${getPriorityColor(selectedCustomer.priority).border} ${getPriorityColor(selectedCustomer.priority).bg}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className={`w-5 h-5 ${getPriorityColor(selectedCustomer.priority).text}`} />
                    <span className="font-semibold text-gray-900">Priority</span>
                  </div>
                  <p className="text-2xl font-bold">{selectedCustomer.priority}</p>
                  <p className="text-xs text-gray-600 mt-1">Tier Priority: {selectedCustomer.tier_priority}</p>
                </div>

                <div className="p-4 rounded-lg border border-blue-200 bg-blue-50">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-gray-900">Upsell Score</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-700">{selectedCustomer.upsell_score || 0}</p>
                  <p className="text-xs text-gray-600 mt-1">{getUpsellScoreColor(selectedCustomer.upsell_score || 0).label} Opportunity</p>
                </div>

                <div className="p-4 rounded-lg border border-green-200 bg-green-50">
                  <div className="flex items-center gap-2 mb-2">
                    <Award className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-gray-900">CLV Predicted</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700">{formatIDR(selectedCustomer.clv_predicted || 0)}</p>
                  <p className="text-xs text-gray-600 mt-1">Customer Lifetime Value</p>
                </div>
              </div>

              {/* Tier Comparison */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Layers className="w-5 h-5" />
                  Tier Comparison
                </h3>
                <div className="grid grid-cols-2 gap-6">
                  <div className="bg-white p-4 rounded-lg border">
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Current Tier</p>
                    <p className="text-lg font-semibold text-gray-900 mt-1">{selectedCustomer.current_tier}</p>
                    <div className="mt-3 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Product:</span>
                        <span className="font-medium">{selectedCustomer.current_product}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Bandwidth:</span>
                        <span className="font-medium">{selectedCustomer.bandwidth_original} Mbps</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white p-4 rounded-lg border border-blue-200">
                    <p className="text-xs text-blue-600 uppercase tracking-wide">Recommended Tier</p>
                    <p className="text-lg font-semibold text-blue-900 mt-1">{selectedCustomer.recommended_tier}</p>
                    <div className="mt-3 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Product:</span>
                        <span className="font-medium text-blue-700">{selectedCustomer.recommended_product}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Bandwidth:</span>
                        <span className="font-medium text-blue-700">{selectedCustomer.bandwidth_mbps} Mbps</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Revenue & Financial Info */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">Current Spend</p>
                  <p className="text-lg font-semibold text-gray-900">{formatIDR(selectedCustomer.current_spend || 0)}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">Revenue</p>
                  <p className="text-lg font-semibold text-gray-900">{formatIDR(selectedCustomer.revenue || 0)}</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-xs text-green-600">Potential Revenue</p>
                  <p className="text-lg font-semibold text-green-700">{formatIDR(selectedCustomer.potential_revenue || 0)}</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-xs text-blue-600">Upside</p>
                  <p className="text-lg font-semibold text-blue-700">
                    {formatIDR((selectedCustomer.potential_revenue || 0) - (selectedCustomer.current_spend || 0))}
                  </p>
                </div>
              </div>

              {/* Customer Info Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Industry</p>
                      <p className="text-sm font-medium">{selectedCustomer.industry}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Segment</p>
                      <p className="text-sm font-medium">{selectedCustomer.segment}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Wifi className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Bandwidth</p>
                      <p className="text-sm font-medium">{selectedCustomer.bandwidth_mbps} Mbps</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Tenure</p>
                      <p className="text-sm font-medium">{selectedCustomer.tenure_months} months</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Tier Priority Rank</p>
                      <p className="text-sm font-medium">#{selectedCustomer.tier_priority}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Original Bandwidth</p>
                      <p className="text-sm font-medium">{selectedCustomer.bandwidth_original} Mbps</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Reasoning Section */}
              <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <h3 className="font-semibold text-indigo-900 mb-2 flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  AI Reasoning - Next Best Offer
                </h3>
                <p className="text-sm text-indigo-800 leading-relaxed">{selectedCustomer.reasoning || "No reasoning available"}</p>
              </div>

              {/* Product Recommendation */}
              <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Award className="w-5 h-5 text-blue-600" />
                  NBO Product Recommendation
                </h3>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <p className="text-sm text-gray-600">From: <span className="font-medium text-gray-900">{selectedCustomer.current_product}</span></p>
                    <div className="flex items-center justify-center my-2">
                      <ArrowRight className="w-5 h-5 text-blue-500" />
                    </div>
                    <p className="text-sm text-gray-600">To: <span className="font-medium text-blue-700">{selectedCustomer.recommended_product}</span></p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Potential Revenue Increase</p>
                    <p className="text-xl font-bold text-green-600">
                      +{formatIDR((selectedCustomer.potential_revenue || 0) - (selectedCustomer.current_spend || 0))}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setIsDetailOpen(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={() => alert("Action triggered for " + selectedCustomer.customer_name)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
              >
                Take Action
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
