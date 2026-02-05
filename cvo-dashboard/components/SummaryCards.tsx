"use client";

import { Users, TrendingUp, Target, DollarSign, Activity, Shield } from "lucide-react";
import { formatNumber, formatCurrency } from "@/lib/utils";

interface SummaryMetric {
  label: string;
  value: number;
  format: "number" | "currency" | "percent";
  change?: number;
  icon: React.ReactNode;
  color: string;
}

interface SummaryCardsProps {
  metrics: {
    totalCustomers?: number;
    total_customers?: number;
    totalRevenue?: number;
    total_revenue?: number;
    upsellOpportunities?: number;
    potentialRevenue?: number;
    activeServices?: number;
    churnRiskCount?: number;
    avgRevenuePerUser?: number;
    modelAccuracy?: number;
    opportunitiesCount?: number;
    avgRevenue?: number;
    avg_revenue?: number;
    avgBandwidth?: number;
    avg_bandwidth?: number;
    avgTenure?: number;
    avg_tenure?: number;
  };
}

export default function SummaryCards({ metrics }: SummaryCardsProps) {
  const cards: SummaryMetric[] = [
    {
      label: "Total Pelanggan",
      value: metrics.totalCustomers || metrics.total_customers || 0,
      format: "number",
      change: 3.2,
      icon: <Users className="h-6 w-6" />,
      color: "#0047AB",
    },
    {
      label: "Total Pendapatan",
      value: metrics.totalRevenue || metrics.total_revenue || 0,
      format: "currency",
      change: 8.5,
      icon: <DollarSign className="h-6 w-6" />,
      color: "#FFD700",
    },
    {
      label: "Peluang Upsell",
      value: metrics.upsellOpportunities || metrics.opportunitiesCount || 0,
      format: "number",
      change: 12.3,
      icon: <Target className="h-6 w-6" />,
      color: "#10B981",
    },
    {
      label: "Rata-rata Pendapatan",
      value: metrics.avgRevenuePerUser || metrics.avgRevenue || metrics.avg_revenue || 0,
      format: "currency",
      change: 5.2,
      icon: <TrendingUp className="h-6 w-6" />,
      color: "#8B5CF6",
    },
    {
      label: "Rata-rata Bandwidth",
      value: metrics.avgBandwidth || metrics.avg_bandwidth || 0,
      format: "number",
      change: 4.1,
      icon: <Activity className="h-6 w-6" />,
      color: "#F59E0B",
    },
    {
      label: "Akurasi Model",
      value: metrics.modelAccuracy || 85.7,
      format: "percent",
      change: 1.8,
      icon: <Shield className="h-6 w-6" />,
      color: "#06B6D4",
    },
  ];

  const formatValue = (metric: SummaryMetric): string => {
    if (metric.format === "currency") {
      return formatCurrency(metric.value);
    } else if (metric.format === "percent") {
      return metric.value.toFixed(1) + "%";
    } else {
      return formatNumber(metric.value);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
      {cards.map((card, index) => (
        <div
          key={card.label}
          className="bg-white rounded-xl shadow-lg p-6 border-l-4 transition-all duration-300 hover:shadow-xl hover:scale-105"
          style={{ 
            borderLeftColor: card.color,
            animationDelay: `${index * 0.1}s`
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <div
              className="p-3 rounded-lg"
              style={{ backgroundColor: `${card.color}20` }}
            >
              <div style={{ color: card.color }}>{card.icon}</div>
            </div>
            {card.change && (
              <span className="text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                +{card.change}%
              </span>
            )}
          </div>
          <p className="text-gray-600 text-sm mb-1">{card.label}</p>
          <p className="text-2xl font-bold text-gray-900">{formatValue(card)}</p>
        </div>
      ))}
    </div>
  );
}
