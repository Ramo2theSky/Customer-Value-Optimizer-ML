// components/ClientTable.tsx
// Tabel yang terhubung dengan data JSON dari Python

"use client";

import { CustomerData } from "@/types";
import { ChevronRight, ArrowRight } from "lucide-react";

interface ClientTableProps {
  customers: CustomerData[];
  onSelectCustomer: (customer: CustomerData) => void;
}

// Format currency IDR
const formatIDR = (value: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

// Priority badge colors
const PRIORITY_BADGES: Record<string, { bg: string; text: string; border: string }> = {
  High: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
  Medium: { bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200" },
  Low: { bg: "bg-green-50", text: "text-green-700", border: "border-green-200" },
};

// Strategy color helper - returns dynamic color based on strategy label
const getStrategyColor = (label: string): { bg: string; text: string } => {
  // Map common strategy patterns to colors
  if (label.includes('STAR') || label.includes('BINTANG')) {
    return { bg: "bg-green-100", text: "text-green-700" };
  }
  if (label.includes('RISIKO') || label.includes('TARGET') && label.includes('NON-BW')) {
    return { bg: "bg-orange-100", text: "text-orange-700" };
  }
  if (label.includes('SNIPER')) {
    return { bg: "bg-blue-100", text: "text-blue-700" };
  }
  if (label.includes('POTENSIAL') || label.includes('POTENSI') || label.includes('SAT')) {
    return { bg: "bg-purple-100", text: "text-purple-700" };
  }
  if (label.includes('PEMULA') || label.includes('UMKM')) {
    return { bg: "bg-cyan-100", text: "text-cyan-700" };
  }
  return { bg: "bg-gray-100", text: "text-gray-700" };
};

// Progress bar for upsell score
const UpsellScoreBar = ({ score }: { score: number }) => {
  let colorClass = "bg-green-500";
  if (score < 40) colorClass = "bg-red-500";
  else if (score < 70) colorClass = "bg-yellow-500";
  
  return (
    <div className="w-full">
      <div className="flex items-center gap-2">
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full ${colorClass} transition-all duration-300`}
            style={{ width: `${score}%` }}
          />
        </div>
        <span className="text-xs font-medium text-gray-600 w-8">{score}</span>
      </div>
    </div>
  );
};

export default function ClientTable({ customers, onSelectCustomer }: ClientTableProps) {
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
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
              Customer Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
              Industry
            </th>
            <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase">
              Revenue
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase">
              Tier Transition
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase w-32">
              Upsell Score
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase">
              Priority
            </th>
            <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase">
              Potential Revenue
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase">
              Strategy
            </th>
            <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase">
              Action
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {customers.map((customer) => {
            const strategyBadge = getStrategyColor(customer.strategy_label);
            const priorityBadge = PRIORITY_BADGES[customer.priority] || PRIORITY_BADGES.Low;

            return (
              <tr
                key={customer.id}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => onSelectCustomer(customer)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {customer.customer_name}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-600">{customer.industry}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="text-sm font-medium text-gray-900">
                    {formatIDR(customer.revenue)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <div className="flex items-center justify-center gap-1 text-sm">
                    <span className="text-gray-600">{customer.current_tier || "-"}</span>
                    <ArrowRight className="w-3 h-3 text-gray-400" />
                    <span className="font-medium text-blue-600">{customer.recommended_tier || "-"}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <UpsellScoreBar score={customer.upsell_score || 0} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span
                    className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium border ${priorityBadge.bg} ${priorityBadge.text} ${priorityBadge.border}`}
                  >
                    {customer.priority || "Low"}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className="text-sm font-medium text-green-600">
                    {formatIDR(customer.potential_revenue || 0)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span
                    className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${strategyBadge.bg} ${strategyBadge.text}`}
                    title={customer.strategy_action}
                  >
                    {customer.strategy_label}
                  </span>
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
