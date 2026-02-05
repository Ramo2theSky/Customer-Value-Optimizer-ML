"use client";

import { X, TrendingUp, Shield, Zap, Clock, DollarSign, Activity } from "lucide-react";
import { formatCurrency, formatNumber } from "@/lib/utils";

interface Customer {
  id: string;
  nama: string;
  segmen: string;
  monthly_revenue: number;
  bandwidth_mbps: number;
  bandwidth_cluster: string;
  tenure_years: number;
  tenure_cluster: string;
  ltv: number;
  sales_quadrant: string;
  sales_strategy: string;
  sales_action: string;
  trust_quadrant: string;
  trust_strategy: string;
  recommendation_primary: string;
  recommendation_secondary: string;
  recommendation_reasoning: string;
  confidence_score: number;
}

interface CustomerDetailProps {
  customer: Customer;
  onClose: () => void;
}

const STRATEGY_CONFIG: Record<string, { color: string; bgColor: string; icon: any; title: string }> = {
  UPSELL: {
    color: "text-blue-700",
    bgColor: "bg-blue-50",
    icon: TrendingUp,
    title: "Upsell Opportunity",
  },
  CROSS_SELL: {
    color: "text-orange-700",
    bgColor: "bg-orange-50",
    icon: Zap,
    title: "Cross-sell Opportunity",
  },
  RETENTION: {
    color: "text-green-700",
    bgColor: "bg-green-50",
    icon: Shield,
    title: "Retention Priority",
  },
  AUTOMATION: {
    color: "text-gray-700",
    bgColor: "bg-gray-50",
    icon: Activity,
    title: "Automation Candidate",
  },
};

export default function CustomerDetail({ customer, onClose }: CustomerDetailProps) {
  const config = STRATEGY_CONFIG[customer.sales_strategy] || STRATEGY_CONFIG.AUTOMATION;
  const Icon = config.icon;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Backdrop */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={onClose}
                  className="text-white hover:text-gray-200 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
                <div>
                  <h2 className="text-xl font-bold text-white">{customer.nama}</h2>
                  <p className="text-blue-100 text-sm">
                    {customer.segmen} • {customer.bandwidth_cluster} Bandwidth
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-white bg-opacity-20 rounded-full text-white text-sm">
                  <Icon className="w-4 h-4" />
                  {customer.sales_strategy.replace("_", "-")}
                </span>
              </div>
            </div>
          </div>

          <div className="p-6">
            {/* AI Recommendation Card */}
            <div className={`${config.bgColor} rounded-xl p-6 mb-6 border-2 border-opacity-20`}>
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 ${config.bgColor} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${config.color}`} />
                </div>
                <div className="flex-1">
                  <h3 className={`text-lg font-bold ${config.color} mb-2`}>
                    AI Recommendation: {config.title}
                  </h3>
                  <p className="text-xl font-semibold text-gray-900 mb-3">
                    "We recommend offering: {customer.recommendation_primary}"
                  </p>
                  {customer.recommendation_secondary && (
                    <p className="text-sm text-gray-600 mb-3">
                      Secondary: {customer.recommendation_secondary}
                    </p>
                  )}
                  <div className="bg-white bg-opacity-60 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">
                      The Reasoning (Why?)
                    </h4>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {customer.recommendation_reasoning}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-500 mb-1">
                  <DollarSign className="w-4 h-4" />
                  <span className="text-xs">Monthly Revenue</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {formatCurrency(customer.monthly_revenue)}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-500 mb-1">
                  <Activity className="w-4 h-4" />
                  <span className="text-xs">Bandwidth</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {formatNumber(customer.bandwidth_mbps)} Mbps
                </p>
                <p className="text-xs text-gray-500">{customer.bandwidth_cluster}</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-500 mb-1">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs">Tenure</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {customer.tenure_years} years
                </p>
                <p className="text-xs text-gray-500">{customer.tenure_cluster}</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-500 mb-1">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs">Lifetime Value</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {formatCurrency(customer.ltv)}
                </p>
              </div>
            </div>

            {/* Matrix Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Sales Matrix Position */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">
                  Sales Matrix Position
                </h4>
                <div className="flex items-center gap-3 mb-3">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{
                      backgroundColor:
                        customer.sales_quadrant === "STAR_CLIENTS"
                          ? "#4CAF50"
                          : customer.sales_quadrant === "RISK_AREA"
                          ? "#FF5722"
                          : customer.sales_quadrant === "SNIPER_ZONE"
                          ? "#2196F3"
                          : "#9E9E9E",
                    }}
                  />
                  <span className="font-medium text-gray-900">
                    {customer.sales_quadrant.replace("_", " ")}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  Strategy: {customer.sales_strategy.replace("_", "-")}
                </p>
                <p className="text-xs text-gray-500">{customer.sales_action}</p>
              </div>

              {/* Trust Matrix Position */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">
                  Trust Matrix Position
                </h4>
                <div className="flex items-center gap-3 mb-3">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{
                      backgroundColor:
                        customer.trust_quadrant === "SULTAN_LOYAL"
                          ? "#2E7D32"
                          : customer.trust_quadrant === "NEW_POTENTIAL"
                          ? "#1565C0"
                          : customer.trust_quadrant === "LOYAL_BUT_LOW"
                          ? "#F57C00"
                          : "#757575",
                    }}
                  />
                  <span className="font-medium text-gray-900">
                    {customer.trust_quadrant.replace("_", " ")}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  Strategy: {customer.trust_strategy.replace("_", "-")}
                </p>
                <p className="text-xs text-gray-500">
                  {customer.tenure_cluster} customer with {customer.tenure_years} years tenure
                </p>
              </div>
            </div>

            {/* Confidence Score */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">AI Confidence Score</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Math.round(customer.confidence_score * 100)}%
                  </p>
                </div>
                <div className="flex-1 max-w-md mx-4">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-blue-700 h-3 rounded-full"
                      style={{ width: `${customer.confidence_score * 100}%` }}
                    />
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
