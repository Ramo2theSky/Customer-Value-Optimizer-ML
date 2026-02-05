"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface PropensityData {
  range: string;
  count: number;
  percentage: number;
}

interface PropensityChartProps {
  data: PropensityData[];
}

export default function PropensityChart({ data }: PropensityChartProps) {
  const getBarColor = (index: number): string => {
    const colors = [
      "#EF4444",
      "#F87171",
      "#FB923C",
      "#FBBF24",
      "#FCD34D",
      "#A3E635",
      "#4ADE80",
      "#22C55E",
      "#16A34A",
      "#15803D",
    ];
    return colors[index] || "#0047AB";
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900">Rentang Skor: {item.range}</p>
          <p className="text-sm text-gray-600">Jumlah: {item.count.toLocaleString()}</p>
          <p className="text-sm text-gray-600">Persentase: {item.percentage}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Distribusi Skor Propensity</h3>
        <p className="text-sm text-gray-500">Distribusi pelanggan berdasarkan skor propensity upsell</p>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              dataKey="range"
              tick={{ fill: "#6B7280", fontSize: 12 }}
              axisLine={{ stroke: "#E5E7EB" }}
            />
            <YAxis
              tick={{ fill: "#6B7280", fontSize: 12 }}
              axisLine={{ stroke: "#E5E7EB" }}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(index)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-red-500" />
          <span className="text-gray-600">Rendah (0.0-0.4)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-yellow-500" />
          <span className="text-gray-600">Sedang (0.4-0.7)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-green-500" />
          <span className="text-gray-600">Tinggi (0.7-1.0)</span>
        </div>
      </div>
    </div>
  );
}
