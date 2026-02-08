// types/index.ts
// Type definitions matching Python output

export interface CustomerData {
  id: string;
  customer_name: string;
  revenue: number;
  bandwidth_segment: 'Low' | 'Mid' | 'High';
  bandwidth_score: number; // 1, 2, 3 untuk chart
  tenure: number;
  strategy_label: string; // Dynamic strategy labels
  strategy_color: string;
  strategy_action: string;
  recommended_product: string;
  reasoning: string;
  industry: string;
  // NBO (Next Best Offer) fields
  current_tier: string;
  recommended_tier: string;
  upsell_score: number; // 0-100
  priority: 'High' | 'Medium' | 'Low';
  potential_revenue: number;
}

export interface DashboardSummary {
  total_customers: number;
  total_revenue: number;
  avg_revenue: number;
  potential_revenue: number;
  avg_upsell_score: number;
  high_priority_count: number;
  medium_priority_count: number;
  low_priority_count: number;
  strategies: StrategyCount[];
  generated_at: string;
}

export interface StrategyCount {
  label: string;
  count: number;
  color: string;
}

export interface StrategyConfig {
  label: string;
  color: string;
  action: string;
  description: string;
}
