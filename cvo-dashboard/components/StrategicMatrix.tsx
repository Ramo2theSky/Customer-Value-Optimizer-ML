"use client";

import { useState } from "react";
import { Info, ZoomIn, ZoomOut, Maximize2 } from "lucide-react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";

interface QuadrantData {
  name: string;
  count: number;
  percentage?: string;
  color: string;
}

interface ScatterPoint {
  customer: string;
  revenue: number;
  bandwidth: number;
  x: number;
  y: number;
  category: string;
  tier: string;
  priority: string;
  nbo: string;
  potential: number;
}

interface StrategicMatrixProps {
  title: string;
  xAxisLabel: string;
  yAxisLabel: string;
  quadrants: QuadrantData[];
  totalCustomers: number;
  scatterData?: any[];
  showFullAnalysis?: boolean;
}

const COLORS = {
  "SNIPER": "#10B981",
  "RISIKO": "#EF4444",
  "UPSELL": "#F59E0B",
  "CROSS-SELL": "#3B82F6",
  "RETENTION": "#6B7280",
  "default": "#6B7280"
};

export default function StrategicMatrix({
  title,
  xAxisLabel,
  yAxisLabel,
  quadrants,
  totalCustomers,
  scatterData = [],
  showFullAnalysis = false,
}: StrategicMatrixProps) {
  const [viewMode, setViewMode] = useState<"grid" | "scatter">(scatterData.length > 0 ? "scatter" : "grid");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Prepare scatter data
  const preparedScatterData: ScatterPoint[] = scatterData.map((item) => ({
    customer: item.customer || item.nama_pelanggan || "Unknown",
    revenue: item.revenue || item.pendapatan_rp || 0,
    bandwidth: item.bandwidth || item.bandwidth_mbps || 0,
    x: item.bandwidth || item.bandwidth_mbps || 0,
    y: item.revenue || item.pendapatan_rp || 0,
    category: item.category || item.kategori_strategis || "Unknown",
    tier: item.tier || item.tier_saat_ini || "Unknown",
    priority: item.priority || "Normal",
    nbo: item.nbo || item.next_best_offer || "-",
    potential: item.potential || item.potensi_revenue_rp || 0,
  }));

  // Calculate medians for quadrant lines
  const xValues = preparedScatterData.map(d => d.x).sort((a, b) => a - b);
  const yValues = preparedScatterData.map(d => d.y).sort((a, b) => a - b);
  const xMedian = xValues[Math.floor(xValues.length / 2)] || 50;
  const yMedian = yValues[Math.floor(yValues.length / 2)] || 5000000;

  // Filter data by category if selected
  const filteredData = selectedCategory
    ? preparedScatterData.filter(d => d.category === selectedCategory)
    : preparedScatterData;

  const getPointColor = (category: string) => {
    return COLORS[category as keyof typeof COLORS] || COLORS.default;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-200 max-w-xs">
          <p className="font-bold text-gray-900 mb-2">{data.customer}</p>
          <div className="space-y-1 text-sm">
            <p><span className="text-gray-500">Pendapatan:</span> Rp {data.revenue.toLocaleString()}</p>
            <p><span className="text-gray-500">Bandwidth:</span> {data.bandwidth.toFixed(1)} Mbps</p>
            <p><span className="text-gray-500">Kategori:</span> <span style={{ color: getPointColor(data.category) }}>{data.category}</span></p>
            <p><span className="text-gray-500">Tier:</span> {data.tier}</p>
            <p><span className="text-gray-500">NBO:</span> {data.nbo}</p>
            <p><span className="text-gray-500">Potensi:</span> Rp {data.potential.toLocaleString()}</p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center gap-2">
          {scatterData.length > 0 && (
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode("grid")}
                className={`px-3 py-1 rounded-md text-sm transition-all ${
                  viewMode === "grid"
                    ? "bg-white shadow text-gray-900"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Grid
              </button>
              <button
                onClick={() => setViewMode("scatter")}
                className={`px-3 py-1 rounded-md text-sm transition-all ${
                  viewMode === "scatter"
                    ? "bg-white shadow text-gray-900"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Sebaran
              </button>
            </div>
          )}
          <div className="group relative">
            <Info className="h-5 w-5 text-gray-400 cursor-help" />
            <div className="absolute right-0 top-6 w-64 bg-gray-800 text-white text-xs rounded-lg p-3 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
              Analisis matriks menunjukkan distribusi pelanggan. Klik titik untuk detail. Kuadran dibagi berdasarkan nilai median.
            </div>
          </div>
        </div>
      </div>

      {viewMode === "grid" ? (
        <div className="relative">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-8 -rotate-90 text-sm font-medium text-gray-500 whitespace-nowrap">
            {yAxisLabel}
          </div>

          <div className="grid grid-cols-2 grid-rows-2 gap-2 ml-8">
            {quadrants.map((quadrant, index) => {
              const labels = [
                { x: "High", y: "High" },
                { x: "Low", y: "High" },
                { x: "High", y: "Low" },
                { x: "Low", y: "Low" },
              ][index];
              const percentage = quadrant.percentage || ((quadrant.count / totalCustomers) * 100).toFixed(1);
              
              return (
                <div
                  key={quadrant.name}
                  className="relative p-4 rounded-lg transition-all duration-300 hover:shadow-md cursor-pointer group"
                  style={{ backgroundColor: `${quadrant.color}15` }}
                >
                  <div
                    className="absolute top-2 right-2 w-3 h-3 rounded-full"
                    style={{ backgroundColor: quadrant.color }}
                  />
                  <div className="text-xs text-gray-500 mb-1">
                    {labels.y} {yAxisLabel.split(" ")[0]} / {labels.x} {xAxisLabel.split(" ")[0]}
                  </div>
                  <div className="text-2xl font-bold" style={{ color: quadrant.color }}>
                    {quadrant.count.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">pelanggan ({percentage}%)</div>
                </div>
              );
            })}
          </div>

          <div className="mt-2 text-center text-sm font-medium text-gray-500">
            {xAxisLabel}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-3 py-1 rounded-full text-xs transition-all ${
                selectedCategory === null
                  ? "bg-gray-800 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              Semua ({preparedScatterData.length})
            </button>
            {Object.entries(COLORS).filter(([k]) => k !== "default").map(([category, color]) => {
              const count = preparedScatterData.filter(d => d.category === category).length;
              if (count === 0) return null;
              return (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
                  className={`px-3 py-1 rounded-full text-xs transition-all flex items-center gap-1 ${
                    selectedCategory === category
                      ? "ring-2 ring-offset-1"
                      : ""
                  }`}
                  style={{
                    backgroundColor: selectedCategory === category ? color : `${color}20`,
                    color: selectedCategory === category ? "white" : color,
                    outlineColor: color,
                  }}
                >
                  <div className="w-2 h-2 rounded-full bg-current" />
                  {category} ({count})
                </button>
              );
            })}
          </div>

          {/* Scatter Plot */}
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis
                  type="number"
                  dataKey="x"
                  name="Bandwidth"
                  unit=" Mbps"
                  stroke="#6B7280"
                  fontSize={12}
                  tickFormatter={(value) => `${value}`}
                />
                <YAxis
                  type="number"
                  dataKey="y"
                  name="Pendapatan"
                  stroke="#6B7280"
                  fontSize={12}
                  tickFormatter={(value) => `Rp ${(value / 1000000).toFixed(0)}M`}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
                <ReferenceLine x={xMedian} stroke="#9CA3AF" strokeDasharray="3 3" />
                <ReferenceLine y={yMedian} stroke="#9CA3AF" strokeDasharray="3 3" />
                <Scatter name="Customers" data={filteredData} fill="#8884d8">
                  {filteredData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getPointColor(entry.category)} fillOpacity={0.7} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Quadrant Labels */}
          <div className="grid grid-cols-2 gap-2 text-xs text-center text-gray-500">
            <div className="p-2 bg-green-50 rounded">Pendapatan Tinggi / Bandwidth Rendah (Potensi Upsell)</div>
            <div className="p-2 bg-emerald-50 rounded">Pendapatan Tinggi / Bandwidth Tinggi (Premium)</div>
            <div className="p-2 bg-gray-50 rounded">Pendapatan Rendah / Bandwidth Rendah (Level Pemula)</div>
            <div className="p-2 bg-blue-50 rounded">Pendapatan Rendah / Bandwidth Tinggi (Cross-sell)</div>
          </div>
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Total Pelanggan</span>
          <span className="font-semibold text-gray-900">{totalCustomers.toLocaleString()}</span>
        </div>
        {showFullAnalysis && scatterData.length > 0 && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Wawasan Strategis:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• {preparedScatterData.filter(d => d.y > yMedian && d.x < xMedian).length} pelanggan memiliki pendapatan tinggi tapi bandwidth rendah (kandidat upsell)</li>
              <li>• {preparedScatterData.filter(d => d.y < yMedian && d.x > xMedian).length} pelanggan memiliki bandwidth tinggi tapi pendapatan rendah (kandidat cross-sell)</li>
              <li>• {preparedScatterData.filter(d => d.category === "SNIPER").length} target SNIPER prioritas tinggi teridentifikasi</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
