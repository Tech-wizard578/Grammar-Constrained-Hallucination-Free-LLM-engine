import { useEffect, useState } from "react";
import { StatsResponse } from "@/types/api";
import { getStats } from "@/lib/api";
import { Database, Layers, Settings, Cpu, AlertCircle, RefreshCw } from "lucide-react";

export function StatsPanel() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      setError("Failed to load stats");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="glass-card p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-white/5 rounded w-24" />
          <div className="h-16 bg-white/[0.02] rounded-xl" />
          <div className="h-10 bg-white/[0.02] rounded-xl" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6">
        <div className="flex items-center gap-2 text-red-400 mb-4">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">{error}</span>
        </div>
        <button 
          onClick={fetchStats}
          className="bit-button-outline text-sm py-2"
        >
          <RefreshCw className="w-4 h-4 mr-2 inline" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-[10px] font-medium text-white/40 uppercase tracking-widest">Knowledge Base</h3>
        <button 
          onClick={fetchStats} 
          className="p-2 rounded-lg hover:bg-white/5 text-white/30 hover:text-white transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Document Count - Featured */}
      <div className="text-center mb-6 p-6 bg-white/[0.02] rounded-xl border border-white/5">
        <Database className="w-8 h-8 text-[#00aaff] mx-auto mb-3" />
        <div className="text-4xl font-bold text-white mb-1 text-glow-blue">
          {stats?.total_documents ?? 0}
        </div>
        <p className="text-[10px] text-white/40 uppercase tracking-widest">Documents</p>
      </div>

      {/* Other Stats */}
      <div className="space-y-2">
        <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/[0.02] transition-all">
          <Layers className="w-4 h-4 text-white/30" />
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-white/30 uppercase tracking-wider">Collection</p>
            <p className="text-sm font-medium text-white/80 truncate">{stats?.collection_name ?? "—"}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/[0.02] transition-all">
          <Cpu className="w-4 h-4 text-white/30" />
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-white/30 uppercase tracking-wider">Model</p>
            <p className="text-sm font-medium text-white/80 truncate">{stats?.embedding_model ?? "—"}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/[0.02] transition-all">
          <Settings className="w-4 h-4 text-white/30" />
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-white/30 uppercase tracking-wider">Chunk Size</p>
            <p className="text-sm font-medium text-white/80">
              {stats ? `${stats.chunk_size} / ${stats.chunk_overlap}` : "—"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
