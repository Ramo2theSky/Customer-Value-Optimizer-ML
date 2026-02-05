"use client";

import { useState } from "react";
import { Package, ArrowRight, TrendingUp, Users, Star, ChevronRight, Sparkles, Target, ShoppingCart } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface CrossSellRecommendation {
  id: string;
  customerName: string;
  currentProducts: string[];
  recommendedProduct: string;
  category: string;
  confidenceScore: number;
  potentialRevenue: number;
  reason: string;
}

interface CrossSellPanelProps {
  recommendations?: CrossSellRecommendation[];
  maxItems?: number;
}

const defaultRecommendations: CrossSellRecommendation[] = [
  {
    id: "1",
    customerName: "PT Maju Jaya Indonesia",
    currentProducts: ["ICONNET 100", "Email Hosting"],
    recommendedProduct: "Cloud Backup",
    category: "Cloud Services",
    confidenceScore: 0.92,
    potentialRevenue: 2500000,
    reason: "Pelanggan dengan layanan internet stabil membutuhkan backup data untuk melindungi operasional bisnis",
  },
  {
    id: "2",
    customerName: "CV Teknologi Nusantara",
    currentProducts: ["ICONNET 200"],
    recommendedProduct: "CCTV Cloud",
    category: "Security",
    confidenceScore: 0.88,
    potentialRevenue: 1800000,
    reason: "Bisnis retail memerlukan monitoring keamanan 24/7 dengan akses cloud",
  },
  {
    id: "3",
    customerName: "PT Digital Solusi Prima",
    currentProducts: ["ICONNET 500", "Web Hosting"],
    recommendedProduct: "DDoS Protection",
    category: "Security",
    confidenceScore: 0.85,
    potentialRevenue: 3500000,
    reason: "Pelanggan enterprise dengan presence online tinggi butuh perlindungan dari serangan DDoS",
  },
  {
    id: "4",
    customerName: "PT Karya Mandiri Sejahtera",
    currentProducts: ["ICONNET 300"],
    recommendedProduct: "Managed IT Services",
    category: "Managed Services",
    confidenceScore: 0.82,
    potentialRevenue: 5000000,
    reason: "Perusahaan dengan tim IT terbatas akan mendapat manfaat dari layanan managed IT",
  },
  {
    id: "5",
    customerName: "PT Sinar Mas Digital",
    currentProducts: ["Dedicated Internet 100", "SIP Trunk"],
    recommendedProduct: "UCaaS",
    category: "Communication",
    confidenceScore: 0.90,
    potentialRevenue: 4200000,
    reason: "Upgrade komunikasi terpadu untuk meningkatkan kolaborasi tim yang sudah menggunakan SIP",
  },
  {
    id: "6",
    customerName: "CV Sukses Abadi",
    currentProducts: ["ICONNET 100"],
    recommendedProduct: "Google Workspace",
    category: "Productivity",
    confidenceScore: 0.78,
    potentialRevenue: 1200000,
    reason: "Pelanggan UMKM membutuhkan tools kolaborasi untuk produktivitas tim",
  },
  {
    id: "7",
    customerName: "PT Energi Listrik Nasional",
    currentProducts: ["MPLS VPN", "Data Center"],
    recommendedProduct: "SD-WAN",
    category: "Networking",
    confidenceScore: 0.87,
    potentialRevenue: 7500000,
    reason: "Enterprise dengan multi-site akan mendapat fleksibilitas dan efisiensi dengan SD-WAN",
  },
  {
    id: "8",
    customerName: "PT Media Telekomunikasi",
    currentProducts: ["ICONNET 1000", "Cloud Connect"],
    recommendedProduct: "Multi-Cloud Connect",
    category: "Cloud",
    confidenceScore: 0.84,
    potentialRevenue: 6000000,
    reason: "Pelanggan cloud existing siap untuk arsitektur multi-cloud yang lebih kompleks",
  },
];

export default function CrossSellPanel({
  recommendations = defaultRecommendations,
  maxItems = 5,
}: CrossSellPanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const categories = Array.from(
    new Set(recommendations.map((r) => r.category))
  );

  const filteredRecommendations = activeCategory
    ? recommendations.filter((r) => r.category === activeCategory)
    : recommendations;

  const displayRecommendations = filteredRecommendations.slice(0, maxItems);

  const totalPotentialRevenue = displayRecommendations.reduce(
    (sum, r) => sum + r.potentialRevenue,
    0
  );

  const avgConfidence = displayRecommendations.length > 0
    ? displayRecommendations.reduce((sum, r) => sum + r.confidenceScore, 0) /
      displayRecommendations.length
    : 0;

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return "text-green-600 bg-green-50";
    if (score >= 0.8) return "text-blue-600 bg-blue-50";
    if (score >= 0.7) return "text-yellow-600 bg-yellow-50";
    return "text-gray-600 bg-gray-50";
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case "cloud services":
      case "cloud":
        return <Sparkles className="w-4 h-4" />;
      case "security":
        return <Target className="w-4 h-4" />;
      case "managed services":
        return <Users className="w-4 h-4" />;
      case "communication":
        return <TrendingUp className="w-4 h-4" />;
      case "productivity":
        return <Star className="w-4 h-4" />;
      case "networking":
        return <ArrowRight className="w-4 h-4" />;
      default:
        return <Package className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <ShoppingCart className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Rekomendasi Cross-Sell
            </h3>
          </div>
          <p className="text-sm text-gray-500">
              Peluang penawaran produk tambahan berdasarkan analisis AI
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-purple-600">
            {displayRecommendations.length}
          </p>
          <p className="text-xs text-gray-500">rekomendasi</p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-3 bg-purple-50 rounded-lg">
          <p className="text-xs text-gray-600 mb-1">Potensi Pendapatan</p>
          <p className="text-lg font-bold text-purple-700">
            {formatCurrency(totalPotentialRevenue)}
          </p>
        </div>
        <div className="p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-gray-600 mb-1">Kepercayaan AI</p>
          <p className="text-lg font-bold text-blue-700">
            {(avgConfidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-5">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            activeCategory === null
              ? "bg-purple-100 text-purple-700"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Semua
        </button>
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1 ${
              activeCategory === category
                ? "bg-purple-100 text-purple-700"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {getCategoryIcon(category)}
            {category}
          </button>
        ))}
      </div>

      {/* Recommendations List */}
      <div className="space-y-3">
        {displayRecommendations.map((rec) => (
          <div
            key={rec.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 hover:shadow-md transition-all cursor-pointer"
            onClick={() =>
              setExpandedId(expandedId === rec.id ? null : rec.id)
            }
          >
            {/* Main Row */}
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {rec.customerName}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(
                      rec.confidenceScore
                    )}`}
                  >
                    {(rec.confidenceScore * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-gray-500 mb-2">
                  Produk: {rec.currentProducts.join(", ")}
                </p>
              </div>
              <div className="flex items-center gap-1 text-purple-600">
                <ChevronRight
                  className={`w-5 h-5 transition-transform ${
                    expandedId === rec.id ? "rotate-90" : ""
                  }`}
                />
              </div>
            </div>

            {/* Recommended Product */}
            <div className="flex items-center gap-3 p-2 bg-purple-50 rounded-lg mt-2">
              <div className="p-1.5 bg-purple-100 rounded-md">
                <Package className="w-4 h-4 text-purple-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-purple-900">
                  {rec.recommendedProduct}
                </p>
                <p className="text-xs text-purple-700">
                  Potensi: {formatCurrency(rec.potentialRevenue)}
                </p>
              </div>
            </div>

            {/* Expanded Details */}
            {expandedId === rec.id && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <div className="space-y-3">
                  <div>
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                      Alasan Rekomendasi
                    </p>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {rec.reason}
                    </p>
                  </div>
                  <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">Kategori:</span>
                      <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium text-gray-700">
                        {rec.category}
                      </span>
                    </div>
                    <button className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
                      <ShoppingCart className="w-3 h-3" />
                      Buat Penawaran
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      {filteredRecommendations.length > maxItems && (
        <button className="w-full mt-4 py-2 text-sm font-medium text-purple-600 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
          Lihat {filteredRecommendations.length - maxItems} Rekomendasi Lainnya
        </button>
      )}

      {/* Insight */}
      <div className="mt-5 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
        <div className="flex items-start gap-2">
          <Sparkles className="w-4 h-4 text-purple-600 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-purple-900">
              Insight AI
            </p>
            <p className="text-xs text-purple-800 mt-1">
              Pelanggan dengan bandwidth tinggi lebih cenderung membeli layanan
              cloud dan security. Fokus pada segmen Corporate dan Enterprise
              untuk hasil terbaik.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
