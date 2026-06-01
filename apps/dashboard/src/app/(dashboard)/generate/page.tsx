"use client";
import { getAuthHeaders } from "~/lib/auth";

import { useEffect, useState } from "react";
import { Sparkles, Loader2, CheckCircle, AlertCircle } from "lucide-react";

interface Trend {
  id: number;
  keyword: string;
  industry_id: number;
  designs_generated: number;
}

interface Industry {
  id: number;
  name: string;
}

const STYLES = [
  "kawaii",
  "retro_badge",
  "minimal_logo",
  "hand_drawn",
  "brewery_emblem",
  "vintage_americana",
  "holographic_ready",
  "motivational_quote",
  "novelty_meme",
  "packaging_seal",
];

export default function GeneratePage() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selectedTrends, setSelectedTrends] = useState<number[]>([]);
  const [selectedStyles, setSelectedStyles] = useState<string[]>(["kawaii"]);
  const [designsPerCombo, setDesignsPerCombo] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success?: boolean; message?: string; job_id?: string } | null>(null);

  useEffect(() => {
    fetch("/api/industries", { headers: getAuthHeaders() })
      .then((r) => r.json())
      .then((d) => setIndustries(d.industries || []));

    fetch("/api/trends", { headers: getAuthHeaders() })
      .then((r) => r.json())
      .then((d) => setTrends(d.trends || []));
  }, []);

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
      } else {
        setResult({ success: false, message: data.detail || "Generation failed" });
      }
    } catch (e) {
      setResult({ success: false, message: "Network error" });
    } finally {
      setLoading(false);
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

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Generate Products</h1>

      {result && (
        <div
          className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            result.success
              ? "bg-green-50 text-green-800 border border-green-200"
              : "bg-red-50 text-red-800 border border-red-200"
          }`}
        >
          {result.success ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          <div>
            <p className="font-medium">{result.message}</p>
            {result.job_id && <p className="text-sm opacity-75">Job ID: {result.job_id}</p>}
          </div>
        </div>
      )}

      <div className="space-y-6">
        {/* Trends */}
        <div className="rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Select Trends ({selectedTrends.length} selected)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            {trends.map((trend) => (
              <button
                key={trend.id}
                onClick={() => toggleTrend(trend.id)}
                className={`p-3 rounded-md text-sm text-left transition-colors ${
                  selectedTrends.includes(trend.id)
                    ? "bg-blue-600 text-white"
                    : "bg-gray-50 text-gray-700 hover:bg-gray-100 border"
                }`}
              >
                <div className="font-medium truncate">{trend.keyword}</div>
                <div className="text-xs opacity-75">
                  {industries.find((i) => i.id === trend.industry_id)?.name || "Unknown"}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Styles */}
        <div className="rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Select Styles ({selectedStyles.length} selected)</h2>
          <div className="flex flex-wrap gap-2">
            {STYLES.map((style) => (
              <button
                key={style}
                onClick={() => toggleStyle(style)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedStyles.includes(style)
                    ? "bg-blue-600 text-white"
                    : "bg-gray-50 text-gray-700 hover:bg-gray-100 border"
                }`}
              >
                {style.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Designs per combo */}
        <div className="rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Designs Per Combination</h2>
          <input
            type="number"
            min={1}
            max={10}
            value={designsPerCombo}
            onChange={(e) => setDesignsPerCombo(Number(e.target.value))}
            className="w-24 px-3 py-2 border rounded-md"
          />
          <p className="text-sm text-gray-500 mt-2">
            Will generate {selectedTrends.length * selectedStyles.length * designsPerCombo} total designs
          </p>
        </div>

        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={loading || selectedTrends.length === 0 || selectedStyles.length === 0}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
          {loading ? "Queueing..." : "Generate Products"}
        </button>
      </div>
    </div>
  );
}
