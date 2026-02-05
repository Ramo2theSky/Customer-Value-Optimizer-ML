"use client";

import { useState, useEffect } from "react";
import {
  BarChart3,
  TrendingUp,
  Users,
  Target,
  Award,
  Calendar,
  Download,
  ChevronLeft,
  DollarSign,
  Zap,
  Building2,
  PieChart,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  RefreshCcw,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts";

const API_BASE_URL = "http://localhost:8000";

const COLORS = ["#3B82F6", "#22C55E", "#F97316", "#A855F7", "#6B7280", "#EF4444", "#10B981"];

interface StatsData {
  total_customers: number;
  total_revenue: number;
  avg_revenue: number;
  risk_clients: number;
  sniper_targets: number;
  star_clients: number;
  incubator_clients: number;
  potential_revenue: number;
}

interface IndustriesData {
  industries: string[];
  counts: Record<string, number>;
}

interface Customer {
  id: string;
  name: string;
  industry: string;
  quadrant: string;
  revenue: number;
}

interface CustomersData {
  customers: Customer[];
  total: number;
  page: number;
  per_page: number;
}

interface StrategyEffectiveness {
  strategy: string;
  target: number;
  converted: number;
  rate: number;
}

const formatIDR = (value: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export default function ReportsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState("This Month");
  const [stats, setStats] = useState<StatsData | null>(null);
  const [industries, setIndustries] = useState<IndustriesData | null>(null);
  const [customers, setCustomers] = useState<CustomersData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [statsRes, industriesRes, customersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/stats`),
        fetch(`${API_BASE_URL}/industries`),
        fetch(`${API_BASE_URL}/customers?page=1&per_page=1000`),
      ]);

      if (!statsRes.ok) throw new Error(`Stats API error: ${statsRes.status}`);
      if (!industriesRes.ok) throw new Error(`Industries API error: ${industriesRes.status}`);
      if (!customersRes.ok) throw new Error(`Customers API error: ${customersRes.status}`);

      const statsData = await statsRes.json();
      const industriesData = await industriesRes.json();
      const customersData = await customersRes.json();

      setStats(statsData);
      setIndustries(industriesData);
      setCustomers(customersData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Calculate metrics from real data
  const totalRevenue = stats?.total_revenue || 0;
  const avgRevenue = stats?.avg_revenue || 0;
  const totalCustomers = stats?.total_customers || 0;
  const potentialRevenue = stats?.potential_revenue || 0;
  const achievementRate = potentialRevenue > 0 ? ((totalRevenue / potentialRevenue) * 100).toFixed(1) : "0.0";

  // Calculate strategy effectiveness from customers data
  const calculateStrategyEffectiveness = (): StrategyEffectiveness[] => {
    if (!customers?.customers) return [];

    const counts = {
      Star: 0,
      Risk: 0,
      Sniper: 0,
      Incubator: 0,
    };

    customers.customers.forEach((customer) => {
      const quadrant = customer.quadrant?.toLowerCase() || "";
      if (quadrant.includes("star")) counts.Star++;
      else if (quadrant.includes("risk")) counts.Risk++;
      else if (quadrant.includes("sniper")) counts.Sniper++;
      else if (quadrant.includes("incubator")) counts.Incubator++;
    });

    return [
      { strategy: "Star (Retention)", target: stats?.star_clients || 0, converted: counts.Star, rate: stats?.star_clients ? (counts.Star / stats.star_clients) * 100 : 0 },
      { strategy: "Risk (Cross-sell)", target: stats?.risk_clients || 0, converted: counts.Risk, rate: stats?.risk_clients ? (counts.Risk / stats.risk_clients) * 100 : 0 },
      { strategy: "Sniper (Upsell)", target: stats?.sniper_targets || 0, converted: counts.Sniper, rate: stats?.sniper_targets ? (counts.Sniper / stats.sniper_targets) * 100 : 0 },
      { strategy: "Incubator (Auto)", target: stats?.incubator_clients || 0, converted: counts.Incubator, rate: stats?.incubator_clients ? (counts.Incubator / stats.incubator_clients) * 100 : 0 },
    ];
  };

  // Prepare industry data for pie chart
  const prepareIndustryData = () => {
    if (!industries?.industries || !industries?.counts) return [];
    
    return industries.industries.map((industry) => ({
      name: industry,
      value: industries.counts[industry] || 0,
    }));
  };

  const strategyEffectiveness = calculateStrategyEffectiveness();
  const industryData = prepareIndustryData();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
          <p className="text-gray-600 font-medium">Loading report data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 max-w-md text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900">Failed to Load Data</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
          >
            <RefreshCcw className="w-4 h-4" />
            Retry
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
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Management Reports</h1>
                <p className="text-xs text-gray-500">Executive Dashboard & Performance Metrics</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white"
              >
                <option>This Month</option>
                <option>Last Month</option>
                <option>This Quarter</option>
                <option>This Year</option>
              </select>
              <Link
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                Back to Dashboard
              </Link>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium">
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Potential Revenue</p>
                <p className="text-2xl font-bold text-blue-600">{formatIDR(potentialRevenue)}</p>
                <p className="text-xs text-green-600 mt-1">Based on current pipeline</p>
              </div>
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">{formatIDR(totalRevenue)}</p>
                <p className="text-xs text-green-600 mt-1">Across {totalCustomers} customers</p>
              </div>
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Achievement Rate</p>
                <p className="text-2xl font-bold text-purple-600">{achievementRate}%</p>
                <p className="text-xs text-gray-500 mt-1">Avg: {formatIDR(avgRevenue)}</p>
              </div>
              <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Strategies</p>
                <p className="text-2xl font-bold text-orange-600">4</p>
                <p className="text-xs text-gray-500 mt-1">Star, Risk, Sniper, Incubator</p>
              </div>
              <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Stats */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Revenue Overview</h2>
                <p className="text-sm text-gray-500">Key revenue metrics from API data</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Total Revenue</p>
                  <p className="text-xl font-bold text-blue-700">{formatIDR(totalRevenue)}</p>
                </div>
                <div className="w-10 h-10 bg-blue-200 rounded-full flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-blue-700" />
                </div>
              </div>
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Average Revenue</p>
                  <p className="text-xl font-bold text-green-700">{formatIDR(avgRevenue)}</p>
                </div>
                <div className="w-10 h-10 bg-green-200 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-green-700" />
                </div>
              </div>
              <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Potential Revenue</p>
                  <p className="text-xl font-bold text-purple-700">{formatIDR(potentialRevenue)}</p>
                </div>
                <div className="w-10 h-10 bg-purple-200 rounded-full flex items-center justify-center">
                  <Target className="w-5 h-5 text-purple-700" />
                </div>
              </div>
            </div>
          </div>

          {/* Opportunity by Industry */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Opportunity by Industry</h2>
                <p className="text-sm text-gray-500">Customer distribution by industry</p>
              </div>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <RePieChart>
                  <Pie
                    data={industryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {industryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RePieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Strategy Effectiveness */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <PieChart className="w-6 h-6 text-purple-600" />
            <div>
              <h2 className="text-lg font-bold text-gray-900">Strategy Effectiveness</h2>
              <p className="text-sm text-gray-500">Conversion rates by quadrant strategy from real customer data</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {strategyEffectiveness.map((strategy, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{strategy.strategy}</span>
                  <span className="text-sm font-bold text-purple-600">{strategy.rate.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${Math.min(strategy.rate, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Target: {strategy.target.toLocaleString()}</span>
                  <span>Active: {strategy.converted.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Customer Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Customers</p>
                <p className="text-2xl font-bold text-gray-900">{totalCustomers.toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-gray-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Star Clients</p>
                <p className="text-2xl font-bold text-yellow-600">{stats?.star_clients || 0}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-50 rounded-lg flex items-center justify-center">
                <Award className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Risk Clients</p>
                <p className="text-2xl font-bold text-red-600">{stats?.risk_clients || 0}</p>
              </div>
              <div className="w-12 h-12 bg-red-50 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Sniper Targets</p>
                <p className="text-2xl font-bold text-blue-600">{stats?.sniper_targets || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Industry Breakdown */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <Building2 className="w-6 h-6 text-blue-600" />
              <div>
                <h2 className="text-lg font-bold text-gray-900">Industry Breakdown</h2>
                <p className="text-sm text-gray-500">Customer count by industry</p>
              </div>
            </div>

            <div className="space-y-4">
              {industryData.map((industry, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span className="font-medium text-gray-900">{industry.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-gray-900">{industry.value}</span>
                    <span className="text-sm text-gray-500">customers</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Strategy Distribution */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <Activity className="w-6 h-6 text-green-600" />
              <div>
                <h2 className="text-lg font-bold text-gray-900">Strategy Distribution</h2>
                <p className="text-sm text-gray-500">Customer distribution by strategy quadrant</p>
              </div>
            </div>

            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { name: "Star", value: stats?.star_clients || 0, fill: "#EAB308" },
                    { name: "Risk", value: stats?.risk_clients || 0, fill: "#EF4444" },
                    { name: "Sniper", value: stats?.sniper_targets || 0, fill: "#3B82F6" },
                    { name: "Incubator", value: stats?.incubator_clients || 0, fill: "#22C55E" },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="name" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", borderRadius: "8px", border: "1px solid #E5E7EB" }}
                  />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
