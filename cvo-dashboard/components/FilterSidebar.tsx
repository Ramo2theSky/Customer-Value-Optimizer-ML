"use client";

import { useState, useMemo } from "react";
import { Search, Filter, X, ChevronDown, RotateCcw } from "lucide-react";

interface FilterOption {
  value: string;
  label: string;
}

interface FilterState {
  segmenCustomer: string;
  wilayah: string;
  kategoriBaru: string;
  tier: string;
  produkBaru: string;
}

interface FilterSidebarProps {
  onFilterChange?: (filters: FilterState) => void;
  onReset?: () => void;
  className?: string;
}

// Filter options data
const SEGMEN_CUSTOMER_OPTIONS: FilterOption[] = [
  { value: "", label: "Semua Segmen" },
  { value: "BUMN", label: "BUMN" },
  { value: "CORPORATE", label: "Corporate" },
  { value: "DINAS", label: "Dinas" },
  { value: "EDUKASI", label: "Edukasi" },
  { value: "F&B", label: "F&B" },
  { value: "FINANCE", label: "Finance" },
  { value: "HEALTH", label: "Health" },
  { value: "HOTEL", label: "Hotel" },
  { value: "ISP", label: "ISP" },
  { value: "MANUFACTURE", label: "Manufacture" },
  { value: "RETAIL", label: "Retail" },
  { value: "SERVICE", label: "Service" },
  { value: "TELCO", label: "Telco" },
  { value: "TOUR & TRAVEL", label: "Tour & Travel" },
  { value: "TRADING", label: "Trading" },
  { value: "TRANSPORTATION", label: "Transportation" },
  { value: "PROPERTY", label: "Property" },
  { value: "ENERGY", label: "Energy" },
  { value: "MEDIA", label: "Media" },
];

const WILAYAH_OPTIONS: FilterOption[] = [
  { value: "", label: "Semua Wilayah" },
  { value: "JAKARTA", label: "Jakarta" },
  { value: "BANDUNG", label: "Bandung" },
  { value: "SURABAYA", label: "Surabaya" },
  { value: "BALI", label: "Bali" },
];

const KATEGORI_BARU_OPTIONS: FilterOption[] = [
  { value: "", label: "Semua Kategori" },
  { value: "SNIPER", label: "SNIPER - High Value Target" },
  { value: "UPSELL", label: "UPSELL - Revenue Growth" },
  { value: "CROSS-SELL", label: "CROSS-SELL - Service Expansion" },
  { value: "RETENTION", label: "RETENTION - Keep & Nurture" },
];

const TIER_OPTIONS: FilterOption[] = [
  { value: "", label: "Semua Tier" },
  { value: "TIER 1", label: "Tier 1 - Enterprise" },
  { value: "TIER 2", label: "Tier 2 - Corporate" },
  { value: "TIER 3", label: "Tier 3 - Mid Business" },
  { value: "TIER 4", label: "Tier 4 - Small Business" },
  { value: "TIER 5", label: "Tier 5 - Micro Business" },
  { value: "TIER 6", label: "Tier 6 - Starter" },
  { value: "TIER 7", label: "Tier 7 - Basic" },
  { value: "TIER 8", label: "Tier 8 - Standard" },
  { value: "TIER 9", label: "Tier 9 - Professional" },
  { value: "TIER 10", label: "Tier 10 - Premium" },
  { value: "TIER 11", label: "Tier 11 - Elite" },
  { value: "TIER 12", label: "Tier 12 - Ultimate" },
  { value: "TIER 13", label: "Tier 13 - Supreme" },
  { value: "TIER 14", label: "Tier 14 - Exclusive" },
];

const PRODUK_BARU_OPTIONS: FilterOption[] = [
  { value: "", label: "Semua Produk" },
  { value: "ICONNET 100", label: "ICONNET 100 Mbps" },
  { value: "ICONNET 200", label: "ICONNET 200 Mbps" },
  { value: "ICONNET 300", label: "ICONNET 300 Mbps" },
  { value: "ICONNET 500", label: "ICONNET 500 Mbps" },
  { value: "ICONNET 1000", label: "ICONNET 1 Gbps" },
  { value: "DEDICATED 10", label: "Dedicated Internet 10 Mbps" },
  { value: "DEDICATED 20", label: "Dedicated Internet 20 Mbps" },
  { value: "DEDICATED 50", label: "Dedicated Internet 50 Mbps" },
  { value: "DEDICATED 100", label: "Dedicated Internet 100 Mbps" },
  { value: "DEDICATED 200", label: "Dedicated Internet 200 Mbps" },
  { value: "IP TRANSIT", label: "IP Transit" },
  { value: "MPLS", label: "MPLS VPN" },
  { value: "SD-WAN", label: "SD-WAN" },
  { value: "CLOUD CONNECT", label: "Cloud Connect" },
  { value: "DATA CENTER", label: "Data Center" },
  { value: "CCTV CLOUD", label: "CCTV Cloud" },
  { value: "WIFI MANAGED", label: "WiFi Managed Service" },
  { value: "SIP TRUNK", label: "SIP Trunk" },
  { value: "UCAAS", label: "UCaaS" },
  { value: "MANAGED SECURITY", label: "Managed Security" },
  { value: "DDOS PROTECTION", label: "DDoS Protection" },
  { value: "WEB HOSTING", label: "Web Hosting" },
  { value: "DOMAIN", label: "Domain Registration" },
  { value: "EMAIL HOSTING", label: "Email Hosting" },
  { value: "CLOUD BACKUP", label: "Cloud Backup" },
  { value: "OFFICE 365", label: "Microsoft 365" },
  { value: "GOOGLE WORKSPACE", label: "Google Workspace" },
  { value: "VPS", label: "Virtual Private Server" },
  { value: "BARE METAL", label: "Bare Metal Server" },
  { value: "COLOCATION", label: "Colocation" },
  { value: "LOAD BALANCER", label: "Load Balancer" },
  { value: "CDN", label: "Content Delivery Network" },
  { value: "MANAGED FIREWALL", label: "Managed Firewall" },
  { value: "NAC", label: "Network Access Control" },
  { value: "PENETRATION TESTING", label: "Penetration Testing" },
  { value: "SECURITY AUDIT", label: "Security Audit" },
  { value: "IOT CONNECTIVITY", label: "IoT Connectivity" },
  { value: "IOT PLATFORM", label: "IoT Platform" },
  { value: "API MANAGEMENT", label: "API Management" },
  { value: "DIGITAL SIGNAGE", label: "Digital Signage" },
  { value: "VIDEO CONFERENCE", label: "Video Conference" },
  { value: "PBX", label: "PBX System" },
  { value: "CALL CENTER", label: "Call Center Solution" },
  { value: "BULK SMS", label: "Bulk SMS Gateway" },
  { value: "WHATSAPP API", label: "WhatsApp Business API" },
  { value: "SMS GATEWAY", label: "SMS Gateway" },
  { value: "IVR", label: "Interactive Voice Response" },
  { value: "FLEET MANAGEMENT", label: "Fleet Management" },
  { value: "GPS TRACKING", label: "GPS Tracking" },
  { value: "SMART BUILDING", label: "Smart Building Solution" },
  { value: "SMART CITY", label: "Smart City Solution" },
  { value: "5G CONNECT", label: "5G Connectivity" },
  { value: "LEASED LINE", label: "Leased Line" },
  { value: "METRO ETHERNET", label: "Metro Ethernet" },
  { value: "VPN REMOTE", label: "VPN Remote Access" },
  { value: "DARK FIBER", label: "Dark Fiber" },
  { value: "WAVELENGTH", label: "Wavelength Service" },
  { value: "DCI", label: "Data Center Interconnect" },
  { value: "CLOUD EXCHANGE", label: "Cloud Exchange" },
  { value: "MULTI-CLOUD", label: "Multi-Cloud Connect" },
  { value: "HYBRID CLOUD", label: "Hybrid Cloud" },
  { value: "PRIVATE CLOUD", label: "Private Cloud" },
  { value: "PUBLIC CLOUD", label: "Public Cloud" },
  { value: "DR SITE", label: "Disaster Recovery Site" },
  { value: "BACKUP AS SERVICE", label: "Backup as a Service" },
  { value: "DISASTER RECOVERY", label: "Disaster Recovery" },
  { value: "BUSINESS CONTINUITY", label: "Business Continuity" },
  { value: "MANAGED IT", label: "Managed IT Services" },
  { value: "NOC", label: "Network Operations Center" },
  { value: "SOC", label: "Security Operations Center" },
  { value: "HELPDESK", label: "Helpdesk Services" },
  { value: "FIELD SERVICE", label: "Field Service Support" },
  { value: "REMOTE SUPPORT", label: "Remote IT Support" },
  { value: "ON-SITE SUPPORT", label: "On-Site Support" },
  { value: "MAINTENANCE", label: "Maintenance Services" },
  { value: "CONSULTING", label: "IT Consulting" },
  { value: "SYSTEM INTEGRATION", label: "System Integration" },
  { value: "MIGRATION", label: "Migration Services" },
  { value: "DEPLOYMENT", label: "Deployment Services" },
  { value: "TRAINING", label: "Training & Certification" },
  { value: "CERTIFICATION", label: "Product Certification" },
  { value: "WARRANTY", label: "Extended Warranty" },
  { value: "INSURANCE", label: "Equipment Insurance" },
  { value: "FINANCING", label: "Equipment Financing" },
  { value: "LEASING", label: "Equipment Leasing" },
  { value: "RENTAL", label: "Short-term Rental" },
  { value: "PAYMENT PLAN", label: "Flexible Payment Plan" },
  { value: "BUNDLE PROMO", label: "Bundle Promo" },
  { value: "LOYALTY REWARD", label: "Loyalty Reward Program" },
  { value: "REFERRAL", label: "Referral Program" },
  { value: "CASHBACK", label: "Cashback Program" },
  { value: "DISCOUNT", label: "Volume Discount" },
  { value: "PRICE LOCK", label: "Price Lock Guarantee" },
  { value: "FREE TRIAL", label: "Free Trial Period" },
  { value: "MONEY BACK", label: "Money Back Guarantee" },
  { value: "UPGRADE CREDIT", label: "Upgrade Credit" },
  { value: "INSTALLMENT", label: "Installment Plan" },
  { value: "ANNUAL SUBSCRIPTION", label: "Annual Subscription" },
  { value: "MONTHLY SUBSCRIPTION", label: "Monthly Subscription" },
  { value: "PAY AS YOU GO", label: "Pay-as-you-go" },
  { value: "COMMITTED USE", label: "Committed Use Discount" },
  { value: "SUSTAINED USE", label: "Sustained Use Discount" },
  { value: "PREEMPTIBLE", label: "Preemptible Pricing" },
  { value: "SPOT INSTANCE", label: "Spot Instance" },
  { value: "RESERVED CAPACITY", label: "Reserved Capacity" },
  { value: "ON-DEMAND", label: "On-Demand Pricing" },
  { value: "DEDICATED HOSTING", label: "Dedicated Hosting" },
  { value: "SHARED HOSTING", label: "Shared Hosting" },
  { value: "WORDPRESS HOSTING", label: "WordPress Hosting" },
  { value: "E-COMMERCE HOSTING", label: "E-Commerce Hosting" },
  { value: "VIDEO STREAMING", label: "Video Streaming" },
  { value: "LIVE STREAMING", label: "Live Streaming Platform" },
  { value: "OTT PLATFORM", label: "OTT Platform" },
  { value: "GAMING SERVER", label: "Gaming Server" },
  { value: "VOICE CHAT", label: "Voice Chat Service" },
  { value: "IN-GAME COMMERCE", label: "In-Game Commerce" },
  { value: "ESPORTS", label: "Esports Platform" },
  { value: "GAME STREAMING", label: "Game Streaming" },
  { value: "METAVERSE", label: "Metaverse Solutions" },
  { value: "VR AR", label: "VR/AR Services" },
  { value: "AI ML PLATFORM", label: "AI/ML Platform" },
  { value: "BIG DATA", label: "Big Data Analytics" },
  { value: "DATA LAKE", label: "Data Lake" },
  { value: "DATA WAREHOUSE", label: "Data Warehouse" },
  { value: "ETL SERVICE", label: "ETL Service" },
  { value: "BI TOOLS", label: "Business Intelligence Tools" },
  { value: "DASHBOARD", label: "Dashboard & Reporting" },
  { value: "PREDICTIVE ANALYTICS", label: "Predictive Analytics" },
  { value: "CUSTOMER ANALYTICS", label: "Customer Analytics" },
  { value: "MARKETING AUTOMATION", label: "Marketing Automation" },
  { value: "CRM INTEGRATION", label: "CRM Integration" },
  { value: "ERP INTEGRATION", label: "ERP Integration" },
  { value: "HRMS", label: "HR Management System" },
  { value: "PAYROLL", label: "Payroll System" },
  { value: "ACCOUNTING", label: "Cloud Accounting" },
  { value: "INVENTORY", label: "Inventory Management" },
  { value: "PROCUREMENT", label: "E-Procurement" },
  { value: "SUPPLY CHAIN", label: "Supply Chain Management" },
  { value: "LOGISTICS", label: "Logistics Platform" },
  { value: "WAREHOUSE MGMT", label: "Warehouse Management" },
  { value: "TRANSPORT MGMT", label: "Transport Management" },
  { value: "ROUTE OPTIMIZATION", label: "Route Optimization" },
  { value: "DELIVERY TRACKING", label: "Delivery Tracking" },
  { value: "PROOF OF DELIVERY", label: "Proof of Delivery" },
  { value: "SIGNATURE CAPTURE", label: "Digital Signature Capture" },
  { value: "MOBILE APP", label: "Mobile App Development" },
  { value: "WEB DEVELOPMENT", label: "Web Development" },
  { value: "E-COMMERCE", label: "E-Commerce Platform" },
  { value: "MARKETPLACE", label: "Marketplace Platform" },
  { value: "PAYMENT GATEWAY", label: "Payment Gateway" },
  { value: "BILLING SYSTEM", label: "Billing System" },
  { value: "INVOICING", label: "Automated Invoicing" },
  { value: "SUBSCRIPTION MGMT", label: "Subscription Management" },
  { value: "REVENUE RECOGNITION", label: "Revenue Recognition" },
  { value: "TAX COMPLIANCE", label: "Tax Compliance" },
  { value: "REGULATORY", label: "Regulatory Compliance" },
  { value: "AUDIT TRAIL", label: "Audit Trail" },
  { value: "ACCESS CONTROL", label: "Access Control System" },
  { value: "BIOMETRICS", label: "Biometric Authentication" },
  { value: "SSO", label: "Single Sign-On" },
  { value: "MFA", label: "Multi-Factor Authentication" },
  { value: "PASSWORD MGMT", label: "Password Management" },
  { value: "SECRETS MGMT", label: "Secrets Management" },
  { value: "KEY MANAGEMENT", label: "Key Management Service" },
  { value: "CERTIFICATE MGMT", label: "Certificate Management" },
  { value: "PKI", label: "Public Key Infrastructure" },
  { value: "ENCRYPTION", label: "Encryption Service" },
  { value: "TOKENIZATION", label: "Tokenization" },
  { value: "DATA MASKING", label: "Data Masking" },
  { value: "ANONYMIZATION", label: "Data Anonymization" },
  { value: "PRIVACY COMPLIANCE", label: "Privacy Compliance" },
  { value: "GDPR", label: "GDPR Compliance" },
  { value: "PDPA", label: "PDPA Compliance" },
  { value: "ISO 27001", label: "ISO 27001 Certification" },
  { value: "SOC 2", label: "SOC 2 Compliance" },
  { value: "PCI DSS", label: "PCI DSS Compliance" },
  { value: "HIPAA", label: "HIPAA Compliance" },
  { value: "ITIL", label: "ITIL Framework" },
  { value: "COBIT", label: "COBIT Framework" },
  { value: "NIST", label: "NIST Framework" },
  { value: "CIS", label: "CIS Controls" },
  { value: "OWASP", label: "OWASP Top 10" },
  { value: "ZERO TRUST", label: "Zero Trust Architecture" },
  { value: "SASE", label: "SASE Solution" },
  { value: "CASB", label: "CASB" },
  { value: "SWG", label: "Secure Web Gateway" },
  { value: "ZTNA", label: "Zero Trust Network Access" },
  { value: "BROWSER ISOLATION", label: "Browser Isolation" },
  { value: "EMAIL SECURITY", label: "Email Security" },
  { value: "THREAT INTELLIGENCE", label: "Threat Intelligence" },
  { value: "SIEM", label: "SIEM" },
  { value: "SOAR", label: "SOAR" },
  { value: "EDR", label: "EDR" },
  { value: "XDR", label: "XDR" },
  { value: "MDR", label: "MDR" },
  { value: "NDR", label: "NDR" },
];

export default function FilterSidebar({
  onFilterChange,
  onReset,
  className = "",
}: FilterSidebarProps) {
  const [filters, setFilters] = useState<FilterState>({
    segmenCustomer: "",
    wilayah: "",
    kategoriBaru: "",
    tier: "",
    produkBaru: "",
  });

  const [searchProduct, setSearchProduct] = useState("");
  const [isProductDropdownOpen, setIsProductDropdownOpen] = useState(false);

  const filteredProducts = useMemo(() => {
    if (!searchProduct) return PRODUK_BARU_OPTIONS.slice(0, 10);
    return PRODUK_BARU_OPTIONS.filter(
      (p) =>
        p.label.toLowerCase().includes(searchProduct.toLowerCase()) ||
        p.value.toLowerCase().includes(searchProduct.toLowerCase())
    ).slice(0, 20);
  }, [searchProduct]);

  const activeFilterCount = Object.values(filters).filter((v) => v !== "").length;

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleReset = () => {
    const resetFilters = {
      segmenCustomer: "",
      wilayah: "",
      kategoriBaru: "",
      tier: "",
      produkBaru: "",
    };
    setFilters(resetFilters);
    setSearchProduct("");
    onReset?.();
    onFilterChange?.(resetFilters);
  };

  const FilterSelect = ({
    label,
    value,
    onChange,
    options,
  }: {
    label: string;
    value: string;
    onChange: (value: string) => void;
    options: FilterOption[];
  }) => (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
    </div>
  );

  return (
    <div className={`bg-white rounded-xl shadow-lg p-5 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Filter Data</h3>
        </div>
        {activeFilterCount > 0 && (
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
            {activeFilterCount} aktif
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="space-y-4">
        {/* Segmen Customer */}
        <FilterSelect
          label="Segmen Customer"
          value={filters.segmenCustomer}
          onChange={(v) => handleFilterChange("segmenCustomer", v)}
          options={SEGMEN_CUSTOMER_OPTIONS}
        />

        {/* Wilayah */}
        <FilterSelect
          label="Wilayah"
          value={filters.wilayah}
          onChange={(v) => handleFilterChange("wilayah", v)}
          options={WILAYAH_OPTIONS}
        />

        {/* Kategori Baru */}
        <FilterSelect
          label="Kategori Baru"
          value={filters.kategoriBaru}
          onChange={(v) => handleFilterChange("kategoriBaru", v)}
          options={KATEGORI_BARU_OPTIONS}
        />

        {/* Tier */}
        <FilterSelect
          label="Tier"
          value={filters.tier}
          onChange={(v) => handleFilterChange("tier", v)}
          options={TIER_OPTIONS}
        />

        {/* Produk Baru - Searchable Dropdown */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Produk Baru</label>
          <div className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari produk..."
                value={searchProduct}
                onChange={(e) => {
                  setSearchProduct(e.target.value);
                  setIsProductDropdownOpen(true);
                }}
                onFocus={() => setIsProductDropdownOpen(true)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
              {filters.produkBaru && (
                <button
                  onClick={() => {
                    handleFilterChange("produkBaru", "");
                    setSearchProduct("");
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Dropdown */}
            {isProductDropdownOpen && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                <div className="p-2 text-xs text-gray-500 border-b border-gray-100">
                  {PRODUK_BARU_OPTIONS.length - 1} produk tersedia
                </div>
                {filteredProducts.map((product) => (
                  <button
                    key={product.value}
                    onClick={() => {
                      handleFilterChange("produkBaru", product.value);
                      setSearchProduct(product.label);
                      setIsProductDropdownOpen(false);
                    }}
                    className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-50 transition-colors ${
                      filters.produkBaru === product.value ? "bg-blue-50 text-blue-700" : "text-gray-700"
                    }`}
                  >
                    {product.label}
                  </button>
                ))}
                {filteredProducts.length === 0 && (
                  <div className="px-3 py-4 text-sm text-gray-500 text-center">
                    Tidak ada produk yang cocok
                  </div>
                )}
              </div>
            )}
          </div>
          {filters.produkBaru && (
            <p className="text-xs text-blue-600">
              Dipilih: {PRODUK_BARU_OPTIONS.find((p) => p.value === filters.produkBaru)?.label}
            </p>
          )}
        </div>
      </div>

      {/* Active Filters Display */}
      {activeFilterCount > 0 && (
        <div className="mt-5 pt-4 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-2">Filter Aktif:</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(filters).map(([key, value]) => {
              if (!value) return null;
              let label = value;
              if (key === "segmenCustomer") {
                label = SEGMEN_CUSTOMER_OPTIONS.find((o) => o.value === value)?.label || value;
              } else if (key === "wilayah") {
                label = WILAYAH_OPTIONS.find((o) => o.value === value)?.label || value;
              } else if (key === "kategoriBaru") {
                label = KATEGORI_BARU_OPTIONS.find((o) => o.value === value)?.label || value;
              } else if (key === "tier") {
                label = TIER_OPTIONS.find((o) => o.value === value)?.label || value;
              } else if (key === "produkBaru") {
                label = PRODUK_BARU_OPTIONS.find((o) => o.value === value)?.label || value;
              }
              return (
                <span
                  key={key}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md"
                >
                  {label}
                  <button
                    onClick={() => handleFilterChange(key as keyof FilterState, "")}
                    className="hover:text-blue-900"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Reset Button */}
      <button
        onClick={handleReset}
        className="mt-5 w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
      >
        <RotateCcw className="w-4 h-4" />
        Reset Filter
      </button>

      {/* Click outside to close dropdown */}
      {isProductDropdownOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsProductDropdownOpen(false)}
        />
      )}
    </div>
  );
}
