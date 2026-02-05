"use client";

import { ChevronRight, Target, TrendingUp, Users } from "lucide-react";

interface TierData {
  tier: string;
  count: number;
  avg_revenue: number;
  total_revenue: number;
  total_potential: number;
  avg_bandwidth: number;
  next_tier: string | null;
  recommendation: string;
}

interface TierRoadmapProps {
  roadmap: TierData[];
}

const TIER_COLORS: Record<string, string> = {
  "DI Only": "#3B82F6",
  "TS Only": "#8B5CF6",
  "SDS Only": "#10B981",
  "GE Only": "#22C55E",
  "DI-TS": "#F59E0B",
  "DI-SDS": "#F97316",
  "DI-GE": "#EF4444",
  "SDS-TS": "#EC4899",
  "GE-SDS": "#14B8A6",
  "GE-TS": "#6366F1",
  "DI-SDS-TS": "#8B5CF6",
  "DI-GE-TS": "#A855F7",
  "DI-GE-SDS": "#9333EA",
  "GE-SDS-TS": "#7C3AED",
  "ALL NOMENKLATUR": "#10B981",
};

const getTierProgress = (tier: string): number => {
  const progress: Record<string, number> = {
    "DI Only": 1,
    "TS Only": 1,
    "SDS Only": 1,
    "GE Only": 1,
    "DI-TS": 2,
    "DI-SDS": 2,
    "DI-GE": 2,
    "SDS-TS": 2,
    "GE-SDS": 2,
    "GE-TS": 2,
    "DI-SDS-TS": 3,
    "DI-GE-TS": 3,
    "DI-GE-SDS": 3,
    "GE-SDS-TS": 3,
    "ALL NOMENKLATUR": 4,
  };
  return progress[tier] || 1;
};

export default function TierRoadmap({ roadmap }: TierRoadmapProps) {
  if (!roadmap || roadmap.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center py-12">
          <Target className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Peta Jalan Tier</h3>
          <p className="text-gray-500">Data tier tidak tersedia</p>
        </div>
      </div>
    );
  }

  const totalCustomers = roadmap.reduce((sum, tier) => sum + tier.count, 0);
  const totalRevenue = roadmap.reduce((sum, tier) => sum + tier.total_revenue, 0);
  const totalPotential = roadmap.reduce((sum, tier) => sum + tier.total_potential, 0);

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-5 h-5 text-blue-100" />
            <span className="text-blue-100 text-sm">Total Pelanggan</span>
          </div>
          <div className="text-3xl font-bold">{totalCustomers.toLocaleString()}</div>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-green-100" />
            <span className="text-green-100 text-sm">Total Pendapatan</span>
          </div>
          <div className="text-3xl font-bold">Rp {(totalRevenue / 1000000000).toFixed(1)}B</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Target className="w-5 h-5 text-purple-100" />
            <span className="text-purple-100 text-sm">Potensi Upsell</span>
          </div>
          <div className="text-3xl font-bold">Rp {(totalPotential / 1000000000).toFixed(1)}B</div>
        </div>
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-orange-100" />
            <span className="text-orange-100 text-sm">Tingkat Tier</span>
          </div>
          <div className="text-3xl font-bold">{roadmap.length}</div>
        </div>
      </div>

      {/* Tier Flow Diagram */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Peta Jalan Perkembangan Tier</h3>
        
        <div className="space-y-6">
          {roadmap.map((tier, index) => {
            const progress = getTierProgress(tier.tier);
            const color = TIER_COLORS[tier.tier] || "#6B7280";
            const isLast = index === roadmap.length - 1;
            
            return (
              <div key={tier.tier} className="relative">
                {/* Connection Line */}
                {!isLast && (
                  <div className="absolute left-6 top-16 w-0.5 h-8 bg-gray-200" />
                )}
                
                <div className="flex items-start gap-4">
                  {/* Tier Indicator */}
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg shrink-0"
                    style={{ backgroundColor: color }}
                  >
                    {progress}
                  </div>
                  
                  {/* Tier Card */}
                  <div className="flex-1 bg-gray-50 rounded-xl p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900 text-lg">{tier.tier}</h4>
                        <p className="text-sm text-gray-500">{tier.recommendation}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold" style={{ color }}>
                          {tier.count.toLocaleString()}
                        </div>
                         <div className="text-xs text-gray-500">
                           {((tier.count / totalCustomers) * 100).toFixed(1)}% dari pelanggan
                         </div>
                      </div>
                    </div>
                    
                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
                       <div>
                         <div className="text-xs text-gray-500 mb-1">Rata-rata Pendapatan</div>
                         <div className="font-semibold text-gray-900">
                           Rp {(tier.avg_revenue / 1000000).toFixed(1)}M
                         </div>
                       </div>
                       <div>
                         <div className="text-xs text-gray-500 mb-1">Total Pendapatan</div>
                         <div className="font-semibold text-gray-900">
                           Rp {(tier.total_revenue / 1000000000).toFixed(1)}B
                         </div>
                       </div>
                       <div>
                         <div className="text-xs text-gray-500 mb-1">Potensi Upsell</div>
                         <div className="font-semibold text-green-600">
                           Rp {(tier.total_potential / 1000000000).toFixed(1)}B
                         </div>
                       </div>
                       <div>
                         <div className="text-xs text-gray-500 mb-1">Rata-rata Bandwidth</div>
                         <div className="font-semibold text-gray-900">
                           {tier.avg_bandwidth.toFixed(1)} Mbps
                         </div>
                       </div>
                    </div>
                    
                     {/* Next Tier */}
                     {tier.next_tier && (
                       <div className="mt-4 flex items-center gap-2 text-sm">
                         <span className="text-gray-500">Target berikutnya:</span>
                         <span className="font-medium" style={{ color: TIER_COLORS[tier.next_tier] }}>
                           {tier.next_tier}
                         </span>
                         <ChevronRight className="w-4 h-4 text-gray-400" />
                       </div>
                     )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Strategy Recommendations */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rekomendasi Strategis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
            <h4 className="font-semibold text-blue-900 mb-2">Pelanggan Single Tier</h4>
            <p className="text-sm text-blue-800 mb-2">
              {roadmap.filter(t => getTierProgress(t.tier) === 1).reduce((sum, t) => sum + t.count, 0).toLocaleString()} pelanggan 
              dengan hanya satu tier produk. Prioritas: Cross-sell layanan tambahan.
            </p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
            <h4 className="font-semibold text-purple-900 mb-2">Pelanggan Dual Tier</h4>
            <p className="text-sm text-purple-800 mb-2">
              {roadmap.filter(t => getTierProgress(t.tier) === 2).reduce((sum, t) => sum + t.count, 0).toLocaleString()} pelanggan 
              dengan dua tier produk. Prioritas: Upsell untuk melengkapi portofolio.
            </p>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg border border-orange-100">
            <h4 className="font-semibold text-orange-900 mb-2">Pelanggan Triple Tier</h4>
            <p className="text-sm text-orange-800 mb-2">
              {roadmap.filter(t => getTierProgress(t.tier) === 3).reduce((sum, t) => sum + t.count, 0).toLocaleString()} pelanggan 
              dengan tiga tier. Prioritas: Layanan premium dan retensi.
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-100">
            <h4 className="font-semibold text-green-900 mb-2">Portofolio Lengkap</h4>
            <p className="text-sm text-green-800 mb-2">
              {roadmap.filter(t => getTierProgress(t.tier) === 4).reduce((sum, t) => sum + t.count, 0).toLocaleString()} pelanggan 
              dengan cakupan tier penuh. Prioritas: Retensi dan upsell premium.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
