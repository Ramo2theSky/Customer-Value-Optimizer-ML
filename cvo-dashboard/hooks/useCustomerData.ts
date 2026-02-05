// hooks/useCustomerData.ts
// Updated: Support untuk banyak data dengan pagination

import { useState, useEffect, useCallback } from 'react';
import { CustomerData, StrategyCount } from '@/types';

const API_BASE_URL = 'http://localhost:8000';

// Strategy color helper - returns hex color based on strategy label
const getStrategyColor = (label: string): string => {
  // Map common strategy patterns to colors
  if (label.includes('STAR') || label.includes('BINTANG')) {
    return '#10B981'; // green-500
  }
  if (label.includes('RISIKO') || (label.includes('TARGET') && label.includes('NON-BW'))) {
    return '#F97316'; // orange-500
  }
  if (label.includes('SNIPER')) {
    return '#3B82F6'; // blue-500
  }
  if (label.includes('POTENSIAL') || label.includes('POTENSI') || label.includes('SAT')) {
    return '#A855F7'; // purple-500
  }
  if (label.includes('PEMULA') || label.includes('UMKM')) {
    return '#06B6D4'; // cyan-500
  }
  return '#6B7280'; // gray-500
};

interface UseCustomerDataReturn {
  customers: CustomerData[];
  summary: any;
  chartData: any;
  strategies: StrategyCount[];
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    perPage: number;
    totalPages: number;
    total: number;
  };
  setPage: (page: number) => void;
  setPerPage: (perPage: number) => void;
  loadAllData: () => Promise<void>; // Untuk load semua data (57k)
  loadFullChartData: () => Promise<void>; // Untuk load chart dengan 57k points
  useFullData: boolean;
  setUseFullData: (use: boolean) => void;
  refetch: () => void;
  filterStrategy: string;
  setFilterStrategy: (strategy: string) => void;
  filterIndustry: string;
  setFilterIndustry: (industry: string) => void;
  filterBandwidth: string;
  setFilterBandwidth: (bandwidth: string) => void;
  filterPriority: string;
  setFilterPriority: (priority: string) => void;
  filterCurrentTier: string;
  setFilterCurrentTier: (tier: string) => void;
  filterRecommendedTier: string;
  setFilterRecommendedTier: (tier: string) => void;
}

export function useCustomerData(): UseCustomerDataReturn {
  const [customers, setCustomers] = useState<CustomerData[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [chartData, setChartData] = useState<any>(null);
  const [strategies, setStrategies] = useState<StrategyCount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination state - default 100 rows (bisa diubah sampai 1000)
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(100);
  const [pagination, setPagination] = useState({
    page: 1,
    perPage: 100,
    totalPages: 1,
    total: 0
  });
  
  // Flag untuk pakai full data di chart (57k points!)
  const [useFullData, setUseFullData] = useState(false);
  
  // Filters
  const [filterStrategy, setFilterStrategy] = useState<string>("");
  const [filterIndustry, setFilterIndustry] = useState<string>("");
  const [filterBandwidth, setFilterBandwidth] = useState<string>("");
  const [filterPriority, setFilterPriority] = useState<string>("");
  const [filterCurrentTier, setFilterCurrentTier] = useState<string>("");
  const [filterRecommendedTier, setFilterRecommendedTier] = useState<string>("");

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Fetch stats (kecil, cepat)
      const statsRes = await fetch(`${API_BASE_URL}/stats`);
      if (!statsRes.ok) throw new Error('Failed to fetch stats');
      const statsData = await statsRes.json();
      setSummary(statsData);
      
      // Fetch strategies
      const strategiesRes = await fetch(`${API_BASE_URL}/strategies`);
      if (strategiesRes.ok) {
        const strategiesData = await strategiesRes.json();
        // Transform API format {"strategies": ["label1", "label2"], "counts": {"label1": 123, "label2": 456}}
        // to frontend format [{label: "label1", count: 123, color: "#10B981"}, {label: "label2", count: 456, color: "#3B82F6"}]
        const transformedStrategies = (strategiesData.strategies || []).map((label: string) => ({
          label,
          count: strategiesData.counts?.[label] || 0,
          color: getStrategyColor(label)
        }));
        setStrategies(transformedStrategies);
      }
      
      // Build URL dengan semua filters
      let customersUrl = `${API_BASE_URL}/customers?page=${page}&per_page=${perPage}&sort_by=revenue&sort_order=desc`;
      if (filterStrategy) {
        customersUrl += `&strategy=${encodeURIComponent(filterStrategy)}`;
      }
      if (filterIndustry) {
        customersUrl += `&industry=${encodeURIComponent(filterIndustry)}`;
      }
      if (filterBandwidth) {
        customersUrl += `&bandwidth=${encodeURIComponent(filterBandwidth)}`;
      }
      if (filterPriority) {
        customersUrl += `&priority=${encodeURIComponent(filterPriority)}`;
      }
      if (filterCurrentTier) {
        customersUrl += `&current_tier=${encodeURIComponent(filterCurrentTier)}`;
      }
      if (filterRecommendedTier) {
        customersUrl += `&recommended_tier=${encodeURIComponent(filterRecommendedTier)}`;
      }
      
      // Fetch paginated customers - bisa 100-1000 rows
      const customersRes = await fetch(customersUrl);
      if (!customersRes.ok) throw new Error('Failed to fetch customers');
      const customersData = await customersRes.json();
      setCustomers(customersData.data);
      setPagination({
        page: customersData.page,
        perPage: customersData.per_page,
        totalPages: customersData.total_pages,
        total: customersData.total
      });
      
      // Fetch chart data - sampled atau full (57k)
      const chartEndpoint = useFullData 
        ? `${API_BASE_URL}/chart-data-full`  // 57k points!
        : `${API_BASE_URL}/chart-data?sample_size=2000`;  // 2000 points
      
      const chartRes = await fetch(chartEndpoint);
      if (!chartRes.ok) throw new Error('Failed to fetch chart data');
      const chartDataRes = await chartRes.json();
      setChartData(chartDataRes);
      
      setIsLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsLoading(false);
    }
  }, [page, perPage, useFullData, filterStrategy, filterIndustry, filterBandwidth, filterPriority, filterCurrentTier, filterRecommendedTier]);

  // Load semua data (57k) - hati-hati, hanya untuk export atau kebutuhan khusus
  const loadAllData = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE_URL}/all-customers?sort_by=revenue&sort_order=desc`);
      if (!res.ok) throw new Error('Failed to fetch all data');
      const data = await res.json();
      setCustomers(data.data);
      setPagination({
        page: 1,
        perPage: data.total,
        totalPages: 1,
        total: data.total
      });
      setIsLoading(false);
    } catch (err) {
      console.error('Error loading all data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsLoading(false);
    }
  };

  // Load chart dengan full data (57k points!)
  const loadFullChartData = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE_URL}/chart-data-full`);
      if (!res.ok) throw new Error('Failed to fetch full chart data');
      const data = await res.json();
      setChartData(data);
      setUseFullData(true);
      setIsLoading(false);
    } catch (err) {
      console.error('Error loading full chart data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { 
    customers, 
    summary, 
    chartData,
    strategies,
    isLoading, 
    error,
    pagination,
    setPage,
    setPerPage,
    loadAllData, // Fungsi untuk load semua data
    loadFullChartData, // Fungsi untuk load chart 57k points
    useFullData, // Flag apakah pakai full data
    setUseFullData, // Setter untuk flag
    refetch: fetchData,
    filterStrategy,
    setFilterStrategy,
    filterIndustry,
    setFilterIndustry,
    filterBandwidth,
    setFilterBandwidth,
    filterPriority,
    setFilterPriority,
    filterCurrentTier,
    setFilterCurrentTier,
    filterRecommendedTier,
    setFilterRecommendedTier
  };
}

// Hook untuk search
export function useSearchCustomers() {
  const [results, setResults] = useState<CustomerData[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const search = async (query: string, limit: number = 50) => {
    if (query.length < 2) {
      setResults([]);
      return;
    }
    
    setIsSearching(true);
    try {
      const res = await fetch(
        `${API_BASE_URL}/search?q=${encodeURIComponent(query)}&limit=${limit}`
      );
      if (res.ok) {
        const data = await res.json();
        setResults(data.results);
      }
    } catch (err) {
      console.error('Search error:', err);
    }
    setIsSearching(false);
  };

  return { results, isSearching, search };
}
