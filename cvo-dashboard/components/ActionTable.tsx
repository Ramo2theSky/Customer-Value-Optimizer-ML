"use client";

import { ChevronRight, TrendingUp, AlertTriangle, Shield, Zap } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface Customer {
  id: string;
  nama: string;
  segmen: string;
  monthly_revenue: number;
  sales_strategy: string;
  recommendation_primary: string;
  recommendation_reasoning: string;
  confidence_score: number;
}

interface ActionTableProps {
  customers: Customer[];
  onSelectCustomer: (customer: Customer) => void;
}

const STRATEGY_BADGES: Record<string, { color: string; icon: any; label: string }> = {
  UPSELL: { color: "bg-blue-100 text-blue-700", icon: TrendingUp, label: "UPSELL" },
  CROSS_SELL: { color: "bg-orange-100 text-orange-700", icon: Zap, label: "CROSS-SELL" },
  RETENTION: { color: "bg-green-100 text-green-700", icon: Shield, label: "RETENTION" },
  AUTOMATION: { color: "bg-gray-100 text-gray-700", icon: AlertTriangle, label: "AUTOMATION" },
};

export default function ActionTable({ customers, onSelectCustomer }: ActionTableProps) {
  if (customers.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No customers match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Customer Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Industry
            </th>
            <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Revenue
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Strategy
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Recommended Product
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Confidence
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Action
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {customers.map((customer) => {
            const badge = STRATEGY_BADGES[customer.sales_strategy] || STRATEGY_BADGES.AUTOMATION;
            const Icon = badge.icon;

            return (
              <tr
                key={customer.id}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => onSelectCustomer(customer)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm font-medium text-gray-900">
                      {customer.nama}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-600">{customer.segmen}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="text-sm font-medium text-gray-900">
                    {formatCurrency(customer.monthly_revenue)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${badge.color}`}
                  >
                    <Icon className="w-3 h-3" />
                    {badge.label}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-xs truncate">
                    {customer.recommendation_primary}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 line-clamp-1">
                    {customer.recommendation_reasoning}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <div className="flex items-center justify-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${customer.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">
                      {Math.round(customer.confidence_score * 100)}%
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
