"use client";

import { useState } from "react";
import { ChevronUp, ChevronDown, ExternalLink, Target } from "lucide-react";
import { formatCurrency, getPropensityCategory, getPropensityColor } from "@/lib/utils";

interface Opportunity {
  customerId: string;
  customerName: string;
  segment: string;
  currentRevenue: number;
  potentialRevenue: number;
  propensityScore: number;
  bandwidthUtilization: number;
  tenureMonths: number;
  recommendedAction: string;
  estimatedValue: number;
}

interface OpportunitiesTableProps {
  opportunities: Opportunity[];
  maxRows?: number;
}

type SortKey = keyof Opportunity;
type SortDirection = "asc" | "desc";

export default function OpportunitiesTable({
  opportunities,
  maxRows = 10,
}: OpportunitiesTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("propensityScore");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const sortedOpportunities = [...opportunities]
    .sort((a, b) => {
      const aValue = a[sortKey];
      const bValue = b[sortKey];
      
      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortDirection === "asc"
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      return sortDirection === "asc"
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    })
    .slice(0, maxRows);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDirection("desc");
    }
  };

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column) {
      return <div className="w-4 h-4" />;
    }
    return sortDirection === "asc" ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    );
  };

  const TableHeader = ({
    column,
    children,
    className = "",
  }: {
    column: SortKey;
    children: React.ReactNode;
    className?: string;
  }) => (
    <th
      className={`px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-50 transition-colors ${className}`}
      onClick={() => handleSort(column)}
    >
      <div className="flex items-center gap-1">
        {children}
        <SortIcon column={column} />
      </div>
    </th>
  );

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Peluang Upsell Terbaik</h3>
            <p className="text-sm text-gray-500">
              Pelanggan dengan skor propensity tertinggi dan potensi pendapatan
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-pln-blue" />
            <span className="text-sm font-medium text-gray-600">
              {opportunities.length} peluang teridentifikasi
            </span>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <TableHeader column="customerName">Pelanggan</TableHeader>
              <TableHeader column="segment">Segmen</TableHeader>
              <TableHeader column="currentRevenue">Pendapatan Saat Ini</TableHeader>
              <TableHeader column="potentialRevenue">Pendapatan Potensi</TableHeader>
              <TableHeader column="propensityScore">Propensity</TableHeader>
              <TableHeader column="estimatedValue">Nilai Estimasi</TableHeader>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Tindakan
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {sortedOpportunities.map((opp) => (
              <>
                <tr
                  key={opp.customerId}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() =>
                    setExpandedRow(expandedRow === opp.customerId ? null : opp.customerId)
                  }
                >
                  <td className="px-4 py-4">
                    <div>
                      <p className="font-medium text-gray-900">{opp.customerName}</p>
                      <p className="text-xs text-gray-500">{opp.customerId}</p>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {opp.segment}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {formatCurrency(opp.currentRevenue)}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {formatCurrency(opp.potentialRevenue)}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-16 h-2 rounded-full bg-gray-200 overflow-hidden"
                      >
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${opp.propensityScore * 100}%`,
                            backgroundColor: getPropensityColor(opp.propensityScore),
                          }}
                        />
                      </div>
                      <span
                        className="text-sm font-medium"
                        style={{ color: getPropensityColor(opp.propensityScore) }}
                      >
                        {(opp.propensityScore * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm font-medium text-green-600">
                    {formatCurrency(opp.estimatedValue)}
                  </td>
                  <td className="px-4 py-4">
                    <button className="inline-flex items-center gap-1 text-sm text-pln-blue hover:text-pln-blue-light transition-colors">
                      {opp.recommendedAction}
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
                {expandedRow === opp.customerId && (
                  <tr className="bg-gray-50">
                    <td colSpan={7} className="px-4 py-4">
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Pemanfaatan Bandwidth</p>
                          <p className="font-medium text-gray-900">
                            {(opp.bandwidthUtilization * 100).toFixed(1)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Masa Langganan</p>
                          <p className="font-medium text-gray-900">{opp.tenureMonths} bulan</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Kategori</p>
                          <p className="font-medium" style={{ color: getPropensityColor(opp.propensityScore) }}>
                            Prioritas {getPropensityCategory(opp.propensityScore)}
                          </p>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      <div className="p-4 border-t border-gray-100 bg-gray-50">
        <button className="w-full py-2 text-sm font-medium text-pln-blue hover:text-pln-blue-light transition-colors">
          Lihat Semua Peluang
        </button>
      </div>
    </div>
  );
}
