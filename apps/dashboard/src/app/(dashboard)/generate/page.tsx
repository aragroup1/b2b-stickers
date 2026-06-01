"use client";

import { useEffect, useState } from "react";
import { getAuthHeaders } from "~/lib/auth";
import {
  Sparkles,
  Loader2,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Zap,
  Search,
  ArrowUpDown,
  Clock,
  Image,
  CheckSquare,
  Target,
  Play,
  BarChart3,
  Package,
} from "lucide-react";

interface Trend {
  id: number;
  keyword: string;
  industry_id: number;
  industry_name: string;
  search_volume: number | null;
  trend_score: number | null;
  category: string | null;
  designs_generated: number;
  designs_allocated: number;
  product_count: number;
}

interface Category {
  category: string;
  trend_count: number;
  total_search_volume: number | null;
  avg_trend_score: number | null;
}

interface PlanAllocation {
  id: number;
  keyword: string;
  search_volume: number;
  volume_percent: number;
  target_designs: number;
  already_generated: number;
  remaining: number;
  demand_tier: string;
}

interface GenerationPlan {
  target_total: number;
  current_products: number;
  total_trends: number;
  total_search_volume: number;
  total_to_generate: number;
  estimated_cost_gbp: number;
  estimated_time_minutes: number;
  allocations: PlanAllocation[];
}

const STYLES = [
  "kawaii", "retro_badge", "minimal_logo", "hand_drawn",
  "brewery_emblem", "vintage_americana", "holographic_ready",
  "motivational_quote", "novelty_meme", "packaging_seal",
];

const DEMAND_COLORS: Record<string, string> = {
  high: "bg-emerald-100 text-emerald-800 border-emerald-200",
  medium: "bg-amber-100 text-amber-800 border-amber-200",
  low: "bg-slate-100 text-slate-800 border-slate-200",
};

export default function GeneratePage() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedTrends, setSelectedTrends] = useState<number[]>([]);
  const [selectedStyles, setSelectedStyles] = useState<string[]>(["kawaii"]);
  const [designsPerCombo, setDesignsPerCombo] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success?: boolean; message?: string; job_id?: string } | null>(null);
  const [sortBy, setSortBy] = useState("search_volume");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [filterCategory, setFilterCategory] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"explorer" | "scale" | "queue" | "gallery" | "approval">("explorer");
  const [queueStats, setQueueStats] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [galleryProducts, setGalleryProducts] = useState<any[]>([]);
  const [galleryFilter, setGalleryFilter] = useState("all");
  const [approvalProducts, setApprovalProducts] = useState<any[]>([]);
  const [selectedForApproval, setSelectedForApproval] = useState<number[]>([]);
  
  // Scale to 1000 state
  const [plan, setPlan] = useState<GenerationPlan | null>(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [scaleLoading, setScaleLoading] = useState(false);

  useEffect(() => {
    loadTrends();
    loadCategories();
    loadQueueStats();
    loadJobs();
    loadGallery();
    loadApprovalQueue();
    loadPlan();
  }, []);

  async function loadTrends() {
    const params = new URLSearchParams();
    if (sortBy) params.set("sort_by", sortBy);
    if (sortOrder) params.set("sort_order", sortOrder);
    if (filterCategory) params.set("category", filterCategory);
    params.set("has_search_volume", "true");
    params.set("limit", "100");

    const res = await fetch(`/api/trends?${params}`, { headers: getAuthHeaders() });
    const data = await res.json();
    setTrends(data.trends || []);
  }

  async function loadCategories() {
    const res = await fetch("/api/trends/categories", { headers: getAuthHeaders() });
    const data = await res.json();
    setCategories(data.categories || []);
  }

  async function loadQueueStats() {
    const res = await fetch("/api/jobs/stats", { headers: getAuthHeaders() });
    const data = await res.json();
    setQueueStats(data);
  }

  async function loadJobs() {
    const res = await fetch("/api/jobs?limit=20", { headers: getAuthHeaders() });
    const data = await res.json();
    setJobs(data.jobs || []);
  }

  async function loadGallery() {
    const res = await fetch(`/api/products/gallery?status=${galleryFilter}&limit=24`, { headers: getAuthHeaders() });
    const data = await res.json();
    setGalleryProducts(data.products || []);
  }

  async function loadApprovalQueue() {
    const res = await fetch("/api/products?status=pending_approval&limit=50", { headers: getAuthHeaders() });
    const data = await res.json();
    setApprovalProducts(data.products || []);
  }

  async function loadPlan() {
    setPlanLoading(true);
    try {
      const res = await fetch("/api/generation/plan?target_total=1000", { headers: getAuthHeaders() });
      const data = await res.json();
      setPlan(data);
    } catch (e) {
      console.error("Failed to load plan", e);
    } finally {
      setPlanLoading(false);
    }
  }

  async function handleGenerate() {
    if (selectedTrends.length === 0) {
      setResult({ success: false, message: "Select at least one trend" });
      return;
    }
    if (selectedStyles.length === 0) {
      setResult({ success: false, message: "Select at least one style" });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("/api/generation/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({
          trend_ids: selectedTrends,
          styles: selectedStyles,
          designs_per_combo: designsPerCombo,
          mode: "production",
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setResult({ success: true, message: "Generation queued!", job_id: data.job_id });
        loadQueueStats();
        loadJobs();
      } else {
        setResult({ success: false, message: data.detail || "Generation failed" });
      }
    } catch (e) {
      setResult({ success: false, message: "Network error" });
    } finally {
      setLoading(false);
    }
  }

  async function handleScaleGenerate() {
    if (!plan || plan.total_to_generate === 0) {
      setResult({ success: false, message: "Nothing to generate — target already met or no plan available" });
      return;
    }

    setScaleLoading(true);
    setResult(null);

    try {
      const res = await fetch("/api/generation/volume-weighted", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ target_total: 1000, mode: "production" }),
      });

      const data = await res.json();
      if (res.ok) {
        setResult({ success: true, message: `Scale generation queued! ${plan.total_to_generate} products`, job_id: data.job_id });
        loadQueueStats();
        loadJobs();
        loadPlan();
      } else {
        setResult({ success: false, message: data.detail || "Scale generation failed" });
      }
    } catch (e) {
      setResult({ success: false, message: "Network error" });
    } finally {
      setScaleLoading(false);
    }
  }

  async function handleBulkApprove(action: "approve" | "reject") {
    if (selectedForApproval.length === 0) return;
    const res = await fetch("/api/products/bulk-status", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ product_ids: selectedForApproval, status: action === "approve" ? "approved" : "archived" }),
    });
    if (res.ok) {
      setSelectedForApproval([]);
      loadApprovalQueue();
      loadGallery();
    }
  }

  const toggleTrend = (id: number) => {
    setSelectedTrends((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  const toggleStyle = (style: string) => {
    setSelectedStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    );
  };

  const filteredTrends = trends.filter((t) =>
    searchQuery
      ? t.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.category?.toLowerCase().includes(searchQuery.toLowerCase())
      : true
  );

  const totalVolume = trends.reduce((sum, t) => sum + (t.search_volume || 0), 0);
  const highDemandCount = trends.filter((t) => (t.search_volume || 0) >= 10000).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Product Generation Hub</h1>
        {result && (
          <div
            className={`px-4 py-2 rounded-lg flex items-center gap-2 text-sm ${
              result.success
                ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                : "bg-red-50 text-red-800 border border-red-200"
            }`}
          >
            {result.success ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            {result.message}
            {result.job_id && <span className="text-xs opacity-75">({result.job_id.slice(0, 8)}...)</span>}
          </div>
        )}
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-white border rounded-lg p-3">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Package className="w-4 h-4" />
            Products
          </div>
          <div className="text-xl font-bold">{plan?.current_products || 0}</div>
          <div className="text-xs text-gray-400">of 1,000 target</div>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <TrendingUp className="w-4 h-4" />
            Search Volume
          </div>
          <div className="text-xl font-bold">{(totalVolume / 1000).toFixed(0)}K</div>
          <div className="text-xs text-gray-400">monthly</div>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Zap className="w-4 h-4" />
            High Demand
          </div>
          <div className="text-xl font-bold">{highDemandCount}</div>
          <div className="text-xs text-gray-400">trends</div>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            Queue
          </div>
          <div className="text-xl font-bold">{queueStats?.queue?.running || 0}</div>
          <div className="text-xs text-gray-400">running</div>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <CheckSquare className="w-4 h-4" />
            Pending
          </div>
          <div className="text-xl font-bold">{approvalProducts.length}</div>
          <div className="text-xs text-gray-400">approval</div>
        </div>
      </div>

      {/* Progress to 1000 */}
      <div className="bg-gray-900 text-white rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            <span className="font-semibold">Scale to 1,000 Products</span>
          </div>
          <span className="text-sm">
            {plan?.current_products || 0} / 1,000
            {plan && (
              <span className="text-gray-400 ml-2">
                ({Math.round((plan.current_products / 1000) * 100)}%)
              </span>
            )}
          </span>
        </div>
        <div className="w-full h-2 bg-gray-700 rounded-full">
          <div
            className="h-2 bg-emerald-500 rounded-full transition-all"
            style={{ width: `${Math.min(((plan?.current_products || 0) / 1000) * 100, 100)}%` }}
          />
        </div>
        {plan && plan.total_to_generate > 0 && (
          <div className="flex items-center justify-between mt-2 text-sm text-gray-400">
            <span>{plan.total_to_generate} products needed • ~£{plan.estimated_cost_gbp} • ~{plan.estimated_time_minutes} min</span>
            <button
              onClick={() => setActiveTab("scale")}
              className="text-emerald-400 hover:text-emerald-300 font-medium"
            >
              View Plan →
            </button>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-1">
          {[
            { key: "explorer", label: "SEO Explorer", icon: Search },
            { key: "scale", label: "Scale to 1000", icon: Target },
            { key: "queue", label: "Queue", icon: Clock },
            { key: "gallery", label: "Gallery", icon: Image },
            { key: "approval", label: "Approval", icon: CheckSquare },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? "border-gray-900 text-gray-900"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* SEO Explorer Tab */}
      {activeTab === "explorer" && (
        <div className="space-y-6">
          {/* Category Demand Cards */}
          <div>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Demand by Category</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
              {categories.map((cat) => (
                <button
                  key={cat.category}
                  onClick={() => setFilterCategory(filterCategory === cat.category ? "" : cat.category)}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    filterCategory === cat.category
                      ? "bg-gray-900 text-white border-gray-900"
                      : "bg-white hover:bg-gray-50"
                  }`}
                >
                  <div className="text-xs opacity-75 truncate">{cat.category}</div>
                  <div className="font-semibold text-sm">{(cat.total_search_volume || 0).toLocaleString()}</div>
                  <div className="text-xs opacity-60">{cat.trend_count} trends</div>
                </button>
              ))}
            </div>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-3 items-center">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search trends..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm"
              />
            </div>
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setTimeout(loadTrends, 0); }}
              className="px-3 py-2 border rounded-lg text-sm"
            >
              <option value="search_volume">Search Volume</option>
              <option value="trend_score">Trend Score</option>
              <option value="created_at">Date Added</option>
              <option value="designs_generated">Generated</option>
            </select>
            <button
              onClick={() => { setSortOrder(sortOrder === "desc" ? "asc" : "desc"); setTimeout(loadTrends, 0); }}
              className="flex items-center gap-1 px-3 py-2 border rounded-lg text-sm hover:bg-gray-50"
            >
              <ArrowUpDown className="w-4 h-4" />
              {sortOrder === "desc" ? "High to Low" : "Low to High"}
            </button>
            {filterCategory && (
              <button
                onClick={() => setFilterCategory("")}
                className="px-3 py-2 bg-gray-100 rounded-lg text-sm hover:bg-gray-200"
              >
                Clear: {filterCategory}
              </button>
            )}
          </div>

          {/* Trends Grid */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Trends ({filteredTrends.length})
              </h2>
              <div className="text-sm text-gray-500">
                {selectedTrends.length} selected →{" "}
                {selectedTrends.length * selectedStyles.length * designsPerCombo} designs
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
              {filteredTrends.map((trend) => {
                const demand =
                  (trend.search_volume || 0) >= 10000
                    ? "high"
                    : (trend.search_volume || 0) >= 3000
                    ? "medium"
                    : "low";
                const isSelected = selectedTrends.includes(trend.id);
                const coverage = trend.designs_allocated > 0
                  ? Math.round((trend.designs_generated / trend.designs_allocated) * 100)
                  : 0;

                return (
                  <button
                    key={trend.id}
                    onClick={() => toggleTrend(trend.id)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isSelected
                        ? "bg-blue-600 text-white border-blue-600 shadow-md"
                        : "bg-white hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-medium text-sm truncate flex-1">{trend.keyword}</div>
                      <span
                        className={`text-xs px-1.5 py-0.5 rounded border ${
                          isSelected ? "bg-white/20 border-white/30" : DEMAND_COLORS[demand]
                        }`}
                      >
                        {(trend.search_volume || 0).toLocaleString()}
                      </span>
                    </div>
                    <div className={`text-xs mt-1 ${isSelected ? "text-blue-100" : "text-gray-500"}`}>
                      {trend.category} • {trend.industry_name}
                    </div>
                    <div className={`text-xs mt-1 flex items-center gap-2 ${isSelected ? "text-blue-100" : "text-gray-400"}`}>
                      <span>Score: {trend.trend_score?.toFixed(1) || "—"}</span>
                      <span>•</span>
                      <span>{trend.designs_generated}/{trend.designs_allocated || 0} designs</span>
                    </div>
                    {trend.designs_allocated > 0 && (
                      <div className={`mt-2 h-1 rounded-full ${isSelected ? "bg-blue-800" : "bg-gray-100"}`}>
                        <div
                          className={`h-1 rounded-full transition-all ${isSelected ? "bg-blue-300" : "bg-blue-500"}`}
                          style={{ width: `${Math.min(coverage, 100)}%` }}
                        />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Style Selector */}
          <div className="rounded-lg border p-4 bg-white">
            <h2 className="font-semibold mb-3">Styles ({selectedStyles.length} selected)</h2>
            <div className="flex flex-wrap gap-2">
              {STYLES.map((style) => (
                <button
                  key={style}
                  onClick={() => toggleStyle(style)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    selectedStyles.includes(style)
                      ? "bg-gray-900 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {style.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Generation Controls */}
          <div className="flex items-center gap-4 bg-white border rounded-lg p-4">
            <div>
              <label className="text-sm text-gray-500">Designs per combo</label>
              <input
                type="number"
                min={1}
                max={10}
                value={designsPerCombo}
                onChange={(e) => setDesignsPerCombo(Number(e.target.value))}
                className="w-20 px-2 py-1 border rounded mt-1"
              />
            </div>
            <div className="flex-1 text-sm text-gray-500">
              Generating{" "}
              <span className="font-semibold text-gray-900">
                {selectedTrends.length * selectedStyles.length * designsPerCombo}
              </span>{" "}
              designs from{" "}
              <span className="font-semibold text-gray-900">{selectedTrends.length}</span> trends ×{" "}
              <span className="font-semibold text-gray-900">{selectedStyles.length}</span> styles
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading || selectedTrends.length === 0 || selectedStyles.length === 0}
              className="flex items-center gap-2 px-5 py-2.5 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {loading ? "Queueing..." : "Generate"}
            </button>
          </div>
        </div>
      )}

      {/* Scale to 1000 Tab */}
      {activeTab === "scale" && (
        <div className="space-y-6">
          {planLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
            </div>
          ) : plan ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Current Products</div>
                  <div className="text-2xl font-bold">{plan.current_products}</div>
                </div>
                <div className="bg-white border rounded-lg p-4">
                  <div className="text-sm text-gray-500">To Generate</div>
                  <div className="text-2xl font-bold text-blue-600">{plan.total_to_generate}</div>
                </div>
                <div className="bg-white border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Est. Cost</div>
                  <div className="text-2xl font-bold">£{plan.estimated_cost_gbp}</div>
                </div>
                <div className="bg-white border rounded-lg p-4">
                  <div className="text-sm text-gray-500">Est. Time</div>
                  <div className="text-2xl font-bold">{Math.round(plan.estimated_time_minutes / 60)}h</div>
                </div>
              </div>

              {/* Generate Button */}
              <div className="bg-gray-50 border rounded-lg p-4 flex items-center justify-between">
                <div>
                  <div className="font-semibold">Volume-Weighted Generation</div>
                  <div className="text-sm text-gray-500">
                    Distributes {plan.total_to_generate} products across {plan.total_trends} trends proportional to search volume
                  </div>
                </div>
                <button
                  onClick={handleScaleGenerate}
                  disabled={scaleLoading || plan.total_to_generate === 0}
                  className="flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {scaleLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  {scaleLoading ? "Queueing..." : "Generate All"}
                </button>
              </div>

              {/* Allocation Table */}
              <div className="bg-white border rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-2 text-left font-medium text-gray-500">Trend</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-500">Volume</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-500">%</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-500">Target</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-500">Done</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-500">Remaining</th>
                      <th className="px-4 py-2 text-left font-medium text-gray-500">Tier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {plan.allocations.map((alloc) => (
                      <tr key={alloc.id} className="border-b last:border-0 hover:bg-gray-50">
                        <td className="px-4 py-2 font-medium">{alloc.keyword}</td>
                        <td className="px-4 py-2 text-right">{alloc.search_volume.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right">{alloc.volume_percent}%</td>
                        <td className="px-4 py-2 text-right">{alloc.target_designs}</td>
                        <td className="px-4 py-2 text-right text-gray-500">{alloc.already_generated}</td>
                        <td className="px-4 py-2 text-right">
                          {alloc.remaining > 0 ? (
                            <span className="font-semibold text-blue-600">{alloc.remaining}</span>
                          ) : (
                            <span className="text-emerald-600">✓</span>
                          )}
                        </td>
                        <td className="px-4 py-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${DEMAND_COLORS[alloc.demand_tier]}`}>
                            {alloc.demand_tier}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">Failed to load generation plan</div>
          )}
        </div>
      )}

      {/* Queue Tab */}
      {activeTab === "queue" && (
        <div className="space-y-4">
          {queueStats && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="bg-white border rounded-lg p-3 text-center">
                <div className="text-2xl font-bold">{queueStats.queue?.total || 0}</div>
                <div className="text-xs text-gray-500">Total Jobs</div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-blue-700">{queueStats.queue?.running || 0}</div>
                <div className="text-xs text-blue-600">Running</div>
              </div>
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-emerald-700">{queueStats.queue?.completed || 0}</div>
                <div className="text-xs text-emerald-600">Completed</div>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-red-700">{queueStats.queue?.failed || 0}</div>
                <div className="text-xs text-red-600">Failed</div>
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-amber-700">{queueStats.generation?.total_generated || 0}</div>
                <div className="text-xs text-amber-600">Generated (7d)</div>
              </div>
            </div>
          )}

          <div className="bg-white border rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-gray-500">Job</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-500">Status</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-500">Progress</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-500">Created</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium">{job.kind}</div>
                      <div className="text-xs text-gray-400">{job.id.slice(0, 8)}...</div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                          job.status === "completed"
                            ? "bg-emerald-100 text-emerald-700"
                            : job.status === "running"
                            ? "bg-blue-100 text-blue-700"
                            : job.status === "failed"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {job.progress && (
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-1.5 bg-gray-100 rounded-full">
                            <div
                              className="h-1.5 bg-blue-500 rounded-full transition-all"
                              style={{
                                width: `${Math.round(
                                  (job.progress.completed / Math.max(job.progress.total, 1)) * 100
                                )}%`,
                              }}
                            />
                          </div>
                          <span className="text-xs text-gray-500">
                            {job.progress.completed}/{job.progress.total}
                          </span>
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Gallery Tab */}
      {activeTab === "gallery" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            {["all", "pending_approval", "approved", "active", "archived"].map((f) => (
              <button
                key={f}
                onClick={() => { setGalleryFilter(f); setTimeout(loadGallery, 0); }}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-colors ${
                  galleryFilter === f
                    ? "bg-gray-900 text-white"
                    : "bg-white border hover:bg-gray-50"
                }`}
              >
                {f.replace("_", " ")}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {galleryProducts.map((product) => (
              <div key={product.id} className="bg-white border rounded-lg overflow-hidden group">
                <div className="aspect-square bg-gray-100 relative">
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.title}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <Image className="w-8 h-8" />
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    <span
                      className={`text-xs px-1.5 py-0.5 rounded ${
                        product.status === "approved"
                          ? "bg-emerald-500 text-white"
                          : product.status === "pending_approval"
                          ? "bg-amber-500 text-white"
                          : "bg-gray-500 text-white"
                      }`}
                    >
                      {product.status}
                    </span>
                  </div>
                </div>
                <div className="p-2">
                  <div className="text-xs font-medium truncate">{product.title}</div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {product.style} • Q:{product.quality_score?.toFixed(0) || "—"}
                  </div>
                  {product.search_volume && (
                    <div className="text-xs text-emerald-600 mt-0.5">
                      {(product.search_volume).toLocaleString()} vol
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Approval Tab */}
      {activeTab === "approval" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
              Pending Approval ({approvalProducts.length})
            </h2>
            {selectedForApproval.length > 0 && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleBulkApprove("approve")}
                  className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700"
                >
                  Approve {selectedForApproval.length}
                </button>
                <button
                  onClick={() => handleBulkApprove("reject")}
                  className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700"
                >
                  Reject {selectedForApproval.length}
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {approvalProducts.map((product) => {
              const isSelected = selectedForApproval.includes(product.id);
              return (
                <div
                  key={product.id}
                  className={`bg-white border rounded-lg overflow-hidden transition-all ${
                    isSelected ? "ring-2 ring-blue-500" : ""
                  }`}
                >
                  <div className="aspect-video bg-gray-100 relative">
                    {product.image_url ? (
                      <img
                        src={product.image_url}
                        alt={product.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <Image className="w-8 h-8" />
                      </div>
                    )}
                    <button
                      onClick={() =>
                        setSelectedForApproval((prev) =>
                          prev.includes(product.id)
                            ? prev.filter((id) => id !== product.id)
                            : [...prev, product.id]
                        )
                      }
                      className={`absolute top-2 left-2 w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                        isSelected
                          ? "bg-blue-500 border-blue-500 text-white"
                          : "bg-white/80 border-gray-300"
                      }`}
                    >
                      {isSelected && <CheckCircle className="w-4 h-4" />}
                    </button>
                  </div>
                  <div className="p-3">
                    <div className="font-medium text-sm">{product.title}</div>
                    <div className="text-xs text-gray-500 mt-1">{product.trend_keyword}</div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                      <span>Style: {product.style}</span>
                      <span>Quality: {product.quality_score?.toFixed(0) || "—"}</span>
                    </div>
                    {product.search_volume && (
                      <div className="mt-1 text-xs text-emerald-600">
                        Search volume: {(product.search_volume).toLocaleString()}
                      </div>
                    )}
                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={async () => {
                          await fetch(`/api/products/${product.id}/status?status=approved`, {
                            method: "PATCH",
                            headers: getAuthHeaders(),
                          });
                          loadApprovalQueue();
                          loadGallery();
                        }}
                        className="flex-1 px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs font-medium hover:bg-emerald-100"
                      >
                        Approve
                      </button>
                      <button
                        onClick={async () => {
                          await fetch(`/api/products/${product.id}/status?status=archived`, {
                            method: "PATCH",
                            headers: getAuthHeaders(),
                          });
                          loadApprovalQueue();
                          loadGallery();
                        }}
                        className="flex-1 px-2 py-1 bg-red-50 text-red-700 rounded text-xs font-medium hover:bg-red-100"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
