import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number, decimals: number = 0): string {
  if (num === undefined || num === null || isNaN(num)) {
    return "-";
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(decimals) + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(decimals) + "K";
  } else {
    return num.toFixed(decimals);
  }
}

export function formatCurrency(num: number): string {
  if (num === undefined || num === null || isNaN(num)) {
    return "Rp -";
  }
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
}

export function formatPercent(num: number, decimals: number = 1): string {
  if (num === undefined || num === null || isNaN(num)) {
    return "-%";
  }
  return num.toFixed(decimals) + "%";
}

export function getPropensityCategory(score: number): string {
  if (score >= 0.75) return "High";
  if (score >= 0.5) return "Medium";
  return "Low";
}

export function getPropensityColor(score: number): string {
  if (score >= 0.75) return "#10B981";
  if (score >= 0.5) return "#F59E0B";
  return "#EF4444";
}
