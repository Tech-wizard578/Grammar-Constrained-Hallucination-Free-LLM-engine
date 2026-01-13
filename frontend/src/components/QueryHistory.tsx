import { QueryHistoryItem } from "@/types/api";
import { Clock, ChevronRight, History } from "lucide-react";
import { cn } from "@/lib/utils";

interface QueryHistoryProps {
  history: QueryHistoryItem[];
  onSelect: (item: QueryHistoryItem) => void;
}

export function QueryHistory({ history, onSelect }: QueryHistoryProps) {
  if (history.length === 0) {
    return (
      <div className="glass-card p-6">
        <h3 className="text-[10px] font-medium text-white/40 uppercase tracking-widest mb-4">Recent Inquiries</h3>
        <div className="text-center py-8 opacity-50">
          <History className="w-8 h-8 text-white/30 mx-auto mb-3" />
          <p className="text-sm text-white/40">No history available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <h3 className="text-[10px] font-medium text-white/40 uppercase tracking-widest mb-6">
        Recent Inquiries ({history.length})
      </h3>
      <div className="space-y-2 max-h-[400px] overflow-y-auto scrollbar-thin pr-2">
        {history.map((item, index) => (
          <button
            key={item.id}
            onClick={() => onSelect(item)}
            className={cn(
              "w-full text-left p-3 rounded-lg transition-all duration-300",
              "bg-white/[0.02] border border-transparent hover:bg-white/[0.05] hover:border-white/5 group",
              "animate-slide-up"
            )}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm text-white/80 line-clamp-2 flex-1 font-light leading-relaxed group-hover:text-white transition-colors">
                {item.question}
              </p>
              <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-[#00aaff] transition-colors flex-shrink-0 mt-0.5" />
            </div>
            <div className="flex items-center gap-3 mt-3">
              <span
                className={cn(
                  "text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider font-medium",
                  item.confidence === "High" && "bg-green-500/10 text-green-400 border border-green-500/20",
                  item.confidence === "Medium" && "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20",
                  item.confidence === "Low" && "bg-red-500/10 text-red-400 border border-red-500/20"
                )}
              >
                {item.confidence}
              </span>
              <span className="text-[10px] text-white/30">
                {formatTimeAgo(item.timestamp)}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  
  if (minutes < 1) return "JUST NOW";
  if (minutes < 60) return `${minutes}M AGO`;
  if (hours < 24) return `${hours}H AGO`;
  return date.toLocaleDateString().toUpperCase();
}
