"use client";

import { Users, TrendingUp, Calendar, Target, Crown, Sparkles, Wallet, GraduationCap } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface QuadrantData {
  id: string;
  name: string;
  subtitle: string;
  count: number;
  avgRevenue: number;
  percentage: number;
  color: string;
  bgColor: string;
  strategy: string;
  action: string;
  icon: React.ReactNode;
}

interface RevenueTenureMatrixProps {
  data?: Array<{
    customer: string;
    revenue: number;
    tenure: number;
    [key: string]: any;
  }>;
  revenueThreshold?: number;
  tenureThreshold?: number;
}

export default function RevenueTenureMatrix({
  data = [],
  revenueThreshold = 5000000,
  tenureThreshold = 24,
}: RevenueTenureMatrixProps) {
  // Calculate quadrants based on data or use default
  const calculateQuadrants = (): QuadrantData[] => {
    if (!data || data.length === 0) {
      return getDefaultQuadrants();
    }

    const sultanLoyal = data.filter(d => d.revenue >= revenueThreshold && d.tenure >= tenureThreshold);
    const orangKayaBaru = data.filter(d => d.revenue >= revenueThreshold && d.tenure < tenureThreshold);
    const sahabatHemat = data.filter(d => d.revenue < revenueThreshold && d.tenure >= tenureThreshold);
    const pemula = data.filter(d => d.revenue < revenueThreshold && d.tenure < tenureThreshold);

    const total = data.length;

    return [
      {
        id: "sultan-loyal",
        name: "SULTAN LOYAL",
        subtitle: "Pelanggan Setia Premium",
        count: sultanLoyal.length,
        avgRevenue: sultanLoyal.length > 0 
          ? sultanLoyal.reduce((sum, d) => sum + d.revenue, 0) / sultanLoyal.length 
          : 0,
        percentage: total > 0 ? (sultanLoyal.length / total) * 100 : 0,
        color: "#10B981",
        bgColor: "#10B98115",
        strategy: "RETENTION & ADVOCACY",
        action: "Loyalty rewards, exclusive access, referral program",
        icon: <Crown className="w-6 h-6" />,
      },
      {
        id: "orang-kaya-baru",
        name: "ORANG KAYA BARU",
        subtitle: "Pelanggan Baru Premium",
        count: orangKayaBaru.length,
        avgRevenue: orangKayaBaru.length > 0 
          ? orangKayaBaru.reduce((sum, d) => sum + d.revenue, 0) / orangKayaBaru.length 
          : 0,
        percentage: total > 0 ? (orangKayaBaru.length / total) * 100 : 0,
        color: "#3B82F6",
        bgColor: "#3B82F615",
        strategy: "GROWTH & ENGAGEMENT",
        action: "Onboarding program, upsell services, relationship building",
        icon: <Sparkles className="w-6 h-6" />,
      },
      {
        id: "sahabat-hemat",
        name: "SAHABAT HEMAT",
        subtitle: "Pelanggan Loyal Hemat",
        count: sahabatHemat.length,
        avgRevenue: sahabatHemat.length > 0 
          ? sahabatHemat.reduce((sum, d) => sum + d.revenue, 0) / sahabatHemat.length 
          : 0,
        percentage: total > 0 ? (sahabatHemat.length / total) * 100 : 0,
        color: "#F59E0B",
        bgColor: "#F59E0B15",
        strategy: "VALUE UPGRADE",
        action: "Gradual tier upgrades, bundle offers, loyalty incentives",
        icon: <Wallet className="w-6 h-6" />,
      },
      {
        id: "pemula",
        name: "PEMULA",
        subtitle: "Pelanggan Baru Dasar",
        count: pemula.length,
        avgRevenue: pemula.length > 0 
          ? pemula.reduce((sum, d) => sum + d.revenue, 0) / pemula.length 
          : 0,
        percentage: total > 0 ? (pemula.length / total) * 100 : 0,
        color: "#6B7280",
        bgColor: "#6B728015",
        strategy: "DEVELOPMENT",
        action: "Education, starter packages, gradual feature introduction",
        icon: <GraduationCap className="w-6 h-6" />,
      },
    ];
  };

  const getDefaultQuadrants = (): QuadrantData[] => [
    {
      id: "sultan-loyal",
      name: "SULTAN LOYAL",
      subtitle: "Pelanggan Setia Premium",
      count: 1423,
      avgRevenue: 8540000,
      percentage: 25.1,
      color: "#10B981",
      bgColor: "#10B98115",
      strategy: "RETENTION & ADVOCACY",
      action: "Loyalty rewards, exclusive access, referral program",
      icon: <Crown className="w-6 h-6" />,
    },
    {
      id: "orang-kaya-baru",
      name: "ORANG KAYA BARU",
      subtitle: "Pelanggan Baru Premium",
      count: 890,
      avgRevenue: 7200000,
      percentage: 15.7,
      color: "#3B82F6",
      bgColor: "#3B82F615",
      strategy: "GROWTH & ENGAGEMENT",
      action: "Onboarding program, upsell services, relationship building",
      icon: <Sparkles className="w-6 h-6" />,
    },
    {
      id: "sahabat-hemat",
      name: "SAHABAT HEMAT",
      subtitle: "Pelanggan Loyal Hemat",
      count: 1250,
      avgRevenue: 3200000,
      percentage: 22.1,
      color: "#F59E0B",
      bgColor: "#F59E0B15",
      strategy: "VALUE UPGRADE",
      action: "Gradual tier upgrades, bundle offers, loyalty incentives",
      icon: <Wallet className="w-6 h-6" />,
    },
    {
      id: "pemula",
      name: "PEMULA",
      subtitle: "Pelanggan Baru Dasar",
      count: 2100,
      avgRevenue: 1800000,
      percentage: 37.1,
      color: "#6B7280",
      bgColor: "#6B728015",
      strategy: "DEVELOPMENT",
      action: "Education, starter packages, gradual feature introduction",
      icon: <GraduationCap className="w-6 h-6" />,
    },
  ];

  const quadrants = calculateQuadrants();
  const totalCustomers = quadrants.reduce((sum, q) => sum + q.count, 0);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Matriks Pendapatan & Masa Langganan</h3>
          <p className="text-sm text-gray-500">
            Segmen pelanggan berdasarkan pendapatan dan loyalitas
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Target className="w-5 h-5 text-pln-blue" />
          <span>{totalCustomers.toLocaleString()} pelanggan</span>
        </div>
      </div>

      {/* Matrix Grid */}
      <div className="relative">
        {/* Y-axis label */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 -rotate-90 text-xs font-medium text-gray-500 whitespace-nowrap">
          PENDAPATAN TINGGI →
        </div>

        <div className="grid grid-cols-2 gap-4 ml-4">
          {quadrants.map((quadrant) => (
            <div
              key={quadrant.id}
              className="relative rounded-xl p-5 transition-all duration-300 hover:shadow-lg group"
              style={{ backgroundColor: quadrant.bgColor }}
            >
              {/* Color indicator */}
              <div 
                className="absolute top-3 right-3 w-4 h-4 rounded-full"
                style={{ backgroundColor: quadrant.color }}
              />

              {/* Icon and Title */}
              <div className="flex items-start gap-3 mb-4">
                <div 
                  className="p-2 rounded-lg"
                  style={{ backgroundColor: `${quadrant.color}30`, color: quadrant.color }}
                >
                  {quadrant.icon}
                </div>
                <div>
                  <h4 className="font-bold text-gray-900" style={{ color: quadrant.color }}>
                    {quadrant.name}
                  </h4>
                  <p className="text-xs text-gray-500">{quadrant.subtitle}</p>
                </div>
              </div>

              {/* Stats */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>Jumlah Pelanggan</span>
                  </div>
                  <span className="font-bold text-gray-900">{quadrant.count.toLocaleString()}</span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>Rata-rata Pendapatan</span>
                  </div>
                  <span className="font-bold text-gray-900">
                    {formatCurrency(quadrant.avgRevenue)}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>Persentase</span>
                  </div>
                  <span className="font-bold" style={{ color: quadrant.color }}>
                    {quadrant.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Strategy & Action */}
              <div className="mt-4 pt-4 border-t border-gray-200/50">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                  Strategi
                </p>
                <p className="text-sm font-medium text-gray-800 mb-2">
                  {quadrant.strategy}
                </p>
                <p className="text-xs text-gray-600 leading-relaxed">
                  {quadrant.action}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* X-axis label */}
        <div className="mt-4 text-center">
          <span className="text-xs font-medium text-gray-500">← MASA LANGGANAN PENDEK</span>
          <span className="mx-4 text-gray-300">|</span>
          <span className="text-xs font-medium text-gray-500">MASA LANGGANAN PANJANG →</span>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        {quadrants.map((q) => (
          <div 
            key={q.id} 
            className="flex items-center gap-2 p-2 rounded-lg bg-gray-50"
          >
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: q.color }}
            />
            <span className="text-xs text-gray-700 font-medium truncate">{q.name}</span>
          </div>
        ))}
      </div>

      {/* Summary insights */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">Wawasan Strategis:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>
            • {quadrants[0].count.toLocaleString()} pelanggan "Sultan Loyal" - Prioritaskan retensi dengan program VIP
          </li>
          <li>
            • {quadrants[1].count.toLocaleString()} pelanggan "Orang Kaya Baru" - Fokus onboarding dan engagement
          </li>
          <li>
            • {quadrants[2].count.toLocaleString()} pelanggan "Sahabat Hemat" - Target upgrade bertahap
          </li>
          <li>
            • {quadrants[3].count.toLocaleString()} pelanggan "Pemula" - Butuh edukasi dan nurturing
          </li>
        </ul>
      </div>
    </div>
  );
}
