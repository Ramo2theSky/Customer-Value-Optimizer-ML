"use client";

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
interface MatrixChartProps {
  data: any[]; // Data dari API (sudah processed)
  title: string;
  isFullData?: boolean;
}

// Warna untuk 4 kuadran Sales Matrix
const SALES_COLORS: Record<string, string> = {
  Star: "#4CAF50",      // Hijau
  Risk: "#FF5722",      // Merah/Oranye
  Sniper: "#2196F3",    // Biru
  Incubator: "#9E9E9E", // Abu-abu
};

export default function MatrixChart({ data, title, isFullData = false }: MatrixChartProps) {
  // Data sudah dari API dalam format yang benar
  const scatterData = data.map((item) => {
    const quadrant = item.strategy_label || "Incubator";
    return {
      x: item.bandwidth_score || 1,
      y: (item.revenue || 0) / 1000000, // Convert ke jutaan
      customer_name: item.customer_name,
      industry: item.industry,
      bandwidth_segment: item.bandwidth_segment,
      quadrant: quadrant,
      recommended_product: item.recommended_product,
      fill: SALES_COLORS[quadrant] || "#9E9E9E",
    };
  });

  // Threshold lines
  const bandwidthThreshold = 2; // Mid (antara Low dan Mid/High)
  const revenueThreshold = 2; // Rp 2 juta

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg shadow-xl border border-gray-200 max-w-xs">
          <p className="font-bold text-gray-900 mb-1">{data.customer_name}</p>
          <p className="text-xs text-gray-500 mb-2">{data.industry}</p>
          <div className="space-y-1 text-sm">
            <p>
              <span className="text-gray-500">Bandwidth: </span>
              <span className="font-medium">{data.bandwidth_segment}</span>
            </p>
            <p>
              <span className="text-gray-500">Revenue: </span>
              <span className="font-medium">Rp {data.y.toFixed(1)} M</span>
            </p>
            <p className="text-xs font-semibold mt-1" style={{ color: data.fill }}>
              {data.quadrant}
            </p>
            <p className="text-xs text-blue-600 mt-2 pt-2 border-t border-gray-100">
              {data.recommended_product}
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 overflow-hidden max-w-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-500">Strategic positioning based on revenue and bandwidth</p>
        </div>
      </div>

      <div className="h-80 w-full overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              type="number"
              dataKey="x"
              name="Bandwidth"
              domain={[0.5, 3.5]}
              ticks={[1, 2, 3]}
              stroke="#6B7280"
              fontSize={12}
              tickFormatter={(value) => {
                const labels: Record<number, string> = {
                  1: "Low",
                  2: "Mid",
                  3: "High",
                };
                return labels[value] || value;
              }}
              label={{ 
                value: "Bandwidth Usage", 
                position: "bottom", 
                offset: 20, 
                fontSize: 12,
                fill: "#6B7280"
              }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Revenue"
              stroke="#6B7280"
              fontSize={12}
              tickFormatter={(value) => `Rp ${value.toFixed(0)}M`}
              label={{ 
                value: "Revenue (Million Rp)", 
                angle: -90, 
                position: "insideLeft",
                fontSize: 12,
                fill: "#6B7280"
              }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
            
            {/* Quadrant lines */}
            <ReferenceLine x={bandwidthThreshold} stroke="#9CA3AF" strokeDasharray="5 5" />
            <ReferenceLine y={revenueThreshold} stroke="#9CA3AF" strokeDasharray="5 5" />
            
            <Scatter name="Customers" data={scatterData}>
              {scatterData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.fill} 
                  fillOpacity={0.7}
                  stroke={entry.fill}
                  strokeWidth={1}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Legend dengan deskripsi */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        {Object.entries(SALES_COLORS).map(([label, color]) => (
          <div key={label} className="flex items-start gap-2">
            <div
              className="w-3 h-3 rounded-full mt-1"
              style={{ backgroundColor: color }}
            />
            <div className="text-xs">
              <span className="font-semibold text-gray-700">{label}</span>
              <p className="text-gray-500 mt-0.5">
                {label === "Star" && "High Rev + High BW → Retention"}
                {label === "Risk" && "High Rev + Low BW → Cross-sell"}
                {label === "Sniper" && "Low Rev + High BW → Upsell"}
                {label === "Incubator" && "Low Rev + Low BW → Automation"}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Stats Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-4 gap-2 text-center">
          {Object.entries(SALES_COLORS).map(([label, color]) => {
            const count = scatterData.filter(d => d.quadrant === label).length;
            return (
              <div key={label}>
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-lg font-bold" style={{ color }}>
                  {count.toLocaleString()}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
