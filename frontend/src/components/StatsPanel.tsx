import { useEffect, useState } from "react";
import { StatsResponse } from "@/types/api";
import { getStats } from "@/lib/api";
import { Database, Layers, Settings, Cpu, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";

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
      <div className="glass-card p-6 animate-pulse">
        <div className="h-4 bg-muted rounded w-24 mb-4" />
        <div className="space-y-3">
          <div className="h-12 bg-muted rounded" />
          <div className="h-8 bg-muted rounded" />
          <div className="h-8 bg-muted rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6">
        <div className="flex items-center gap-2 text-destructive mb-4">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
        <Button variant="outline" size="sm" onClick={fetchStats}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-semibold text-muted-foreground">Knowledge Base</h3>
        <Button variant="ghost" size="icon" onClick={fetchStats} className="h-8 w-8">
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* Document Count - Featured */}
      <div className="text-center mb-6 p-4 bg-gradient-to-br from-primary/10 to-accent/10 rounded-xl border border-primary/20">
        <Database className="w-8 h-8 text-primary mx-auto mb-2" />
        <div className="text-4xl font-bold gradient-text mb-1">
          {stats?.total_documents ?? 0}
        </div>
        <p className="text-xs text-muted-foreground">Total Documents</p>
      </div>

      {/* Other Stats */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
          <Layers className="w-5 h-5 text-muted-foreground" />
          <div className="flex-1">
            <p className="text-xs text-muted-foreground">Collection</p>
            <p className="text-sm font-medium truncate">{stats?.collection_name ?? "—"}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
          <Cpu className="w-5 h-5 text-muted-foreground" />
          <div className="flex-1">
            <p className="text-xs text-muted-foreground">Embedding Model</p>
            <p className="text-sm font-medium truncate">{stats?.embedding_model ?? "—"}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
          <Settings className="w-5 h-5 text-muted-foreground" />
          <div className="flex-1">
            <p className="text-xs text-muted-foreground">Chunk Settings</p>
            <p className="text-sm font-medium">
              {stats ? `${stats.chunk_size} / ${stats.chunk_overlap}` : "—"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
