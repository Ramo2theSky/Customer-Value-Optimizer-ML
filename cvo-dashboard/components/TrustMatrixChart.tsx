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

interface TrustMatrixChartProps {
  data: any[];
  title: string;
  isFullData?: boolean;
}

// The Trust Matrix (LTV vs Tenure) - 4 Quadrants
const TRUST_COLORS: Record<string, string> = {
  "Sultan Loyal": "#2E7D32",      // High LTV + High Tenure → Big Ticket Cross-sell
  "New Potential": "#1565C0",     // High LTV + Low Tenure → Onboarding
  "Price Sensitive": "#F57C00",   // Low LTV + High Tenure → At Risk
  "New & Low": "#757575",         // Low LTV + Low Tenure → Incubator
};

// Strategy actions for each quadrant
const STRATEGY_ACTIONS: Record<string, string> = {
  "Sultan Loyal": "BIG TICKET CROSS-SELL (PV Rooftop, Smart Office)",
  "New Potential": "ONBOARDING",
  "Price Sensitive": "RETENTION/NUDGING",
  "New & Low": "AUTOMATION",
};

export default function TrustMatrixChart({ data, title, isFullData = false }: TrustMatrixChartProps) {
  // Calculate LTV and assign to quadrants
  const scatterData = data.map((item) => {
    const revenue = item.revenue || 0;
    const tenure = item.tenure || 0;
    
    // LTV = Monthly Revenue × 12 months × Tenure years (simplified)
    const ltv = revenue * 12 * Math.max(tenure, 0.5); // minimum 0.5 year to avoid 0
    
    // Thresholds for quadrants
    const ltvThreshold = 500000000; // Rp 500 juta LTV
    const tenureThreshold = 10; // 10 years
    
    // Assign quadrant based on LTV and Tenure
    let quadrant: string;
    if (ltv >= ltvThreshold && tenure >= tenureThreshold) {
      quadrant = "Sultan Loyal";
    } else if (ltv >= ltvThreshold && tenure < tenureThreshold) {
      quadrant = "New Potential";
    } else if (ltv < ltvThreshold && tenure >= tenureThreshold) {
      quadrant = "Price Sensitive";
    } else {
      quadrant = "New & Low";
    }
    
    return {
      x: tenure,
      y: ltv / 1000000, // Convert to millions for display
      customer_name: item.customer_name,
      industry: item.industry,
      monthly_revenue: revenue / 1000000,
      quadrant: quadrant,
      strategy_action: STRATEGY_ACTIONS[quadrant],
      recommended_product: item.recommended_product,
      fill: TRUST_COLORS[quadrant],
    };
  });

  // Threshold lines
  const tenureThreshold = 10; // 10 tahun
  const ltvThreshold = 500; // Rp 500 juta (dalam jutaan)

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
              <span className="text-gray-500">Tenure: </span>
              <span className="font-medium">{data.x} years</span>
            </p>
            <p>
              <span className="text-gray-500">Monthly Revenue: </span>
              <span className="font-medium">Rp {data.monthly_revenue.toFixed(1)} M</span>
            </p>
            <p>
              <span className="text-gray-500">LTV: </span>
              <span className="font-semibold text-blue-600">Rp {data.y.toFixed(0)} M</span>
            </p>
            <p className="text-xs font-semibold mt-2" style={{ color: data.fill }}>
              {data.quadrant}
            </p>
            <p className="text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded mt-1">
              Action: {data.strategy_action}
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
          <p className="text-sm text-gray-500">Lifetime Value (LTV) vs Customer Tenure</p>
        </div>
      </div>

      <div className="h-80 w-full overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 50 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              type="number"
              dataKey="x"
              name="Tenure"
              domain={[0, 'auto']}
              stroke="#6B7280"
              fontSize={12}
              tickFormatter={(value) => `${value}y`}
              label={{ 
                value: 'Customer Tenure (Years)', 
                position: 'bottom', 
                offset: 25, 
                fontSize: 12,
                fill: "#6B7280"
              }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="LTV"
              stroke="#6B7280"
              fontSize={12}
              tickFormatter={(value) => `Rp ${value.toFixed(0)}M`}
              label={{ 
                value: 'Lifetime Value (Million Rp)', 
                angle: -90, 
                position: 'insideLeft',
                fontSize: 12,
                fill: "#6B7280"
              }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
            
            {/* Quadrant lines */}
            <ReferenceLine x={tenureThreshold} stroke="#9CA3AF" strokeDasharray="5 5" />
            <ReferenceLine y={ltvThreshold} stroke="#9CA3AF" strokeDasharray="5 5" />
            
            <Scatter name="Customers" data={scatterData}>
              {scatterData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} fillOpacity={0.7} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Legend dengan deskripsi strategi */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        {Object.entries(TRUST_COLORS).map(([label, color]) => {
          const count = scatterData.filter(d => d.quadrant === label).length;
          return (
            <div key={label} className="flex items-start gap-2">
              <div
                className="w-3 h-3 rounded-full mt-1 flex-shrink-0"
                style={{ backgroundColor: color }}
              />
              <div className="text-xs min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-700">{label}</span>
                  <span className="text-gray-400">({count.toLocaleString()})</span>
                </div>
                <p className="text-gray-500 mt-0.5 truncate">
                  {STRATEGY_ACTIONS[label]}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Threshold explanation */}
      <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
        <p>Threshold: LTV ≥ Rp 500M | Tenure ≥ 10 years</p>
      </div>
    </div>
  );
}
