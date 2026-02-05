"use client";

import { useState } from "react";
import {
  Megaphone,
  Target,
  Zap,
  Shield,
  Users,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Play,
  Pause,
  Plus,
  Calendar,
  DollarSign,
  Building2,
  MoreHorizontal,
  Download,
  ChevronLeft,
} from "lucide-react";
import Link from "next/link";

// Campaign types
interface Campaign {
  id: string;
  name: string;
  description: string;
  strategy: string;
  targetIndustry: string;
  targetCount: number;
  contactedCount: number;
  convertedCount: number;
  potentialRevenue: number;
  realizedRevenue: number;
  status: "ongoing" | "completed" | "draft" | "paused";
  startDate: string;
  endDate: string;
  createdBy: string;
  icon: any;
  color: string;
  progress: number;
}

// Dummy campaigns based on ML analysis
const dummyCampaigns: Campaign[] = [
  {
    id: "CAMP-001",
    name: "Q1 Banking Security Push",
    description: "Kampanye cross-selling CCTV/Security ke 50 klien Banking yang masih pakai Tier Basic (DI Only). Target: Upgrade ke Managed Security + CCTV Analytics.",
    strategy: "Risk → Cross-sell",
    targetIndustry: "BANKING & FINANCIAL",
    targetCount: 50,
    contactedCount: 35,
    convertedCount: 8,
    potentialRevenue: 500000000,
    realizedRevenue: 80000000,
    status: "ongoing",
    startDate: "2026-01-01",
    endDate: "2026-03-31",
    createdBy: "Sales Manager - Budi",
    icon: Shield,
    color: "blue",
    progress: 70,
  },
  {
    id: "CAMP-002",
    name: "Sniper Upgrade Wave",
    description: "Kampanye upselling bandwidth ke klien 'Sniper Zone' (High Usage, Low Revenue). Penawaran diskon 20% untuk upgrade ke tier Mid/High.",
    strategy: "Sniper → Upsell",
    targetIndustry: "ALL",
    targetCount: 120,
    contactedCount: 85,
    convertedCount: 22,
    potentialRevenue: 1200000000,
    realizedRevenue: 220000000,
    status: "ongoing",
    startDate: "2026-01-15",
    endDate: "2026-02-28",
    createdBy: "Sales Manager - Siti",
    icon: Zap,
    color: "orange",
    progress: 71,
  },
  {
    id: "CAMP-003",
    name: "Green Energy Branding",
    description: "Penawaran PV Rooftop ke klien 'Star Clients' dari sektor Manufacturing. Target perusahaan dengan revenue > Rp 5M/bulan.",
    strategy: "Star → Retention",
    targetIndustry: "MANUFACTURE",
    targetCount: 25,
    contactedCount: 12,
    convertedCount: 3,
    potentialRevenue: 2500000000,
    realizedRevenue: 300000000,
    status: "ongoing",
    startDate: "2026-01-10",
    endDate: "2026-04-30",
    createdBy: "Sales Manager - Ahmad",
    icon: TrendingUp,
    color: "green",
    progress: 48,
  },
  {
    id: "CAMP-004",
    name: "Manufacturing IoT Initiative",
    description: "Target klien Manufacture dengan tenure > 5 tahun. Penawaran Smart Factory IoT untuk efisiensi produksi.",
    strategy: "Star → Cross-sell",
    targetIndustry: "MANUFACTURE",
    targetCount: 40,
    contactedCount: 0,
    convertedCount: 0,
    potentialRevenue: 800000000,
    realizedRevenue: 0,
    status: "draft",
    startDate: "2026-02-01",
    endDate: "2026-05-31",
    createdBy: "Sales Manager - Dedi",
    icon: Target,
    color: "purple",
    progress: 0,
  },
  {
    id: "CAMP-005",
    name: "Hospitality Recovery Program",
    description: "Program khusus untuk sektor Hospitality yang terdampak pandemi. Penawaran bundling DI + WiFi dengan harga special.",
    strategy: "Incubator → Automation",
    targetIndustry: "HOSPITALITY",
    targetCount: 60,
    contactedCount: 45,
    convertedCount: 15,
    potentialRevenue: 450000000,
    realizedRevenue: 112500000,
    status: "paused",
    startDate: "2025-11-01",
    endDate: "2025-12-31",
    createdBy: "Sales Manager - Eka",
    icon: Building2,
    color: "gray",
    progress: 75,
  },
  {
    id: "CAMP-006",
    name: "Retail Distribution Expansion",
    description: "Target klien Retail dengan cabang > 10 outlet. Penawaran Managed WiFi Enterprise untuk semua cabang.",
    strategy: "Sniper → Upsell",
    targetIndustry: "RETAIL DISTRIBUTION",
    targetCount: 30,
    contactedCount: 30,
    convertedCount: 12,
    potentialRevenue: 600000000,
    realizedRevenue: 240000000,
    status: "completed",
    startDate: "2025-09-01",
    endDate: "2025-12-31",
    createdBy: "Sales Manager - Gunawan",
    icon: Users,
    color: "teal",
    progress: 100,
  },
];

const formatIDR = (value: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "ongoing":
      return { text: "Ongoing", class: "bg-green-100 text-green-800", icon: Play };
    case "completed":
      return { text: "Completed", class: "bg-blue-100 text-blue-800", icon: CheckCircle };
    case "draft":
      return { text: "Draft", class: "bg-gray-100 text-gray-800", icon: AlertCircle };
    case "paused":
      return { text: "Paused", class: "bg-yellow-100 text-yellow-800", icon: Pause };
    default:
      return { text: status, class: "bg-gray-100 text-gray-800", icon: Clock };
  }
};

export default function CampaignsPage() {
  const [campaigns] = useState<Campaign[]>(dummyCampaigns);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);

  const totalPotential = campaigns.reduce((sum, c) => sum + c.potentialRevenue, 0);
  const totalRealized = campaigns.reduce((sum, c) => sum + c.realizedRevenue, 0);
  const activeCampaigns = campaigns.filter((c) => c.status === "ongoing").length;
  const avgConversion = Math.round(
    campaigns.reduce((sum, c) => sum + (c.convertedCount / Math.max(c.contactedCount, 1)) * 100, 0) / campaigns.length
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                <Megaphone className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Strategic Campaigns</h1>
                <p className="text-xs text-gray-500">Program Kerja dari Hasil ML Analysis</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                Back to Dashboard
              </Link>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium">
                <Plus className="w-4 h-4" />
                New Campaign
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Campaigns</p>
                <p className="text-3xl font-bold text-gray-900">{activeCampaigns}</p>
              </div>
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <Play className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Potential Revenue</p>
                <p className="text-3xl font-bold text-blue-600">{formatIDR(totalPotential)}</p>
              </div>
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Realized Revenue</p>
                <p className="text-3xl font-bold text-green-600">{formatIDR(totalRealized)}</p>
              </div>
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${(totalRealized / totalPotential) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {((totalRealized / totalPotential) * 100).toFixed(1)}% achievement
              </p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Conversion</p>
                <p className="text-3xl font-bold text-purple-600">{avgConversion}%</p>
              </div>
              <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Campaign Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => {
            const StatusBadge = getStatusBadge(campaign.status);
            const Icon = campaign.icon;

            return (
              <div
                key={campaign.id}
                className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden cursor-pointer"
                onClick={() => setSelectedCampaign(campaign)}
              >
                {/* Card Header */}
                <div className={`h-2 bg-${campaign.color}-500`} style={{ backgroundColor: getColorHex(campaign.color) }} />
                
                <div className="p-6">
                  {/* Icon & Title */}
                  <div className="flex items-start gap-4 mb-4">
                    <div
                      className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: `${getColorHex(campaign.color)}20` }}
                    >
                      <Icon className="w-6 h-6" style={{ color: getColorHex(campaign.color) }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${StatusBadge.class}`}>
                          {StatusBadge.text}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-900 truncate">{campaign.name}</h3>
                      <p className="text-sm text-gray-500">{campaign.id}</p>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{campaign.description}</p>

                  {/* Strategy Tag */}
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                      {campaign.strategy}
                    </span>
                    <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                      {campaign.targetIndustry}
                    </span>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">Target</p>
                      <p className="text-lg font-bold text-gray-900">{campaign.targetCount} PT</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">Contacted</p>
                      <p className="text-lg font-bold text-blue-600">{campaign.contactedCount} PT</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">Converted</p>
                      <p className="text-lg font-bold text-green-600">{campaign.convertedCount} PT</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">Conversion</p>
                      <p className="text-lg font-bold text-purple-600">
                        {Math.round((campaign.convertedCount / Math.max(campaign.contactedCount, 1)) * 100)}%
                      </p>
                    </div>
                  </div>

                  {/* Revenue */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-500">Revenue Progress</span>
                      <span className="text-sm font-medium text-gray-900">
                        {formatIDR(campaign.realizedRevenue)} / {formatIDR(campaign.potentialRevenue)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all"
                        style={{
                          width: `${campaign.progress}%`,
                          backgroundColor: getColorHex(campaign.color),
                        }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{campaign.progress}% progress</p>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-xs text-gray-500">{campaign.startDate} - {campaign.endDate}</span>
                    </div>
                    <button className="p-2 hover:bg-gray-100 rounded-lg">
                      <MoreHorizontal className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* Campaign Detail Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div
                    className="w-14 h-14 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${getColorHex(selectedCampaign.color)}20` }}
                  >
                    <selectedCampaign.icon
                      className="w-7 h-7"
                      style={{ color: getColorHex(selectedCampaign.color) }}
                    />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      {(() => {
                        const Status = getStatusBadge(selectedCampaign.status);
                        return (
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${Status.class}`}>
                            {Status.text}
                          </span>
                        );
                      })()}
                      <span className="text-sm text-gray-500">{selectedCampaign.id}</span>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedCampaign.name}</h2>
                    <p className="text-sm text-gray-500">Created by {selectedCampaign.createdBy}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedCampaign(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Description */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-600">{selectedCampaign.description}</p>
              </div>

              {/* Strategy & Target */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Strategy</p>
                  <p className="font-semibold text-gray-900">{selectedCampaign.strategy}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Target Industry</p>
                  <p className="font-semibold text-gray-900">{selectedCampaign.targetIndustry}</p>
                </div>
              </div>

              {/* Progress Stats */}
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{selectedCampaign.targetCount}</p>
                  <p className="text-xs text-gray-600">Target PT</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-2xl font-bold text-yellow-600">{selectedCampaign.contactedCount}</p>
                  <p className="text-xs text-gray-600">Contacted</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{selectedCampaign.convertedCount}</p>
                  <p className="text-xs text-gray-600">Converted</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">
                    {Math.round((selectedCampaign.convertedCount / Math.max(selectedCampaign.contactedCount, 1)) * 100)}%
                  </p>
                  <p className="text-xs text-gray-600">Conversion</p>
                </div>
              </div>

              {/* Revenue */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">Revenue Performance</h3>
                  <span className="text-sm text-gray-500">
                    {formatIDR(selectedCampaign.realizedRevenue)} / {formatIDR(selectedCampaign.potentialRevenue)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                  <div
                    className="h-3 rounded-full transition-all"
                    style={{
                      width: `${selectedCampaign.progress}%`,
                      backgroundColor: getColorHex(selectedCampaign.color),
                    }}
                  />
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">{selectedCampaign.progress}% achieved</span>
                  <span className="text-green-600 font-medium">
                    Remaining: {formatIDR(selectedCampaign.potentialRevenue - selectedCampaign.realizedRevenue)}
                  </span>
                </div>
              </div>

              {/* Timeline */}
              <div className="flex items-center gap-4">
                <div className="flex-1 p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Start Date</p>
                  <p className="font-semibold text-gray-900">{selectedCampaign.startDate}</p>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400" />
                <div className="flex-1 p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">End Date</p>
                  <p className="font-semibold text-gray-900">{selectedCampaign.endDate}</p>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setSelectedCampaign(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                <Download className="w-4 h-4" />
                Export Report
              </button>
              <button
                className="px-4 py-2 rounded-lg text-white font-medium"
                style={{ backgroundColor: getColorHex(selectedCampaign.color) }}
              >
                Manage Campaign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to get color hex
function getColorHex(color: string): string {
  const colors: Record<string, string> = {
    blue: "#3B82F6",
    orange: "#F97316",
    green: "#22C55E",
    purple: "#A855F7",
    gray: "#6B7280",
    teal: "#14B8A6",
    red: "#EF4444",
    yellow: "#EAB308",
  };
  return colors[color] || "#6B7280";
}
