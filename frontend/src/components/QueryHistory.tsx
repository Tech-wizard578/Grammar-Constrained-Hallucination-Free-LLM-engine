import { QueryHistoryItem } from "@/types/api";
import { Clock, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface QueryHistoryProps {
  history: QueryHistoryItem[];
  onSelect: (item: QueryHistoryItem) => void;
}

export function QueryHistory({ history, onSelect }: QueryHistoryProps) {
  if (history.length === 0) {
    return (
      <div className="glass-card p-6">
        <h3 className="text-sm font-semibold text-muted-foreground mb-4">Recent Queries</h3>
        <div className="text-center py-8">
          <Clock className="w-8 h-8 text-muted-foreground/50 mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No queries yet</p>
          <p className="text-xs text-muted-foreground/70 mt-1">
            Your query history will appear here
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-muted-foreground mb-4">
        Recent Queries ({history.length})
      </h3>
      <div className="space-y-2 max-h-[400px] overflow-y-auto scrollbar-thin">
        {history.map((item, index) => (
          <button
            key={item.id}
            onClick={() => onSelect(item)}
            className={cn(
              "w-full text-left p-3 rounded-lg transition-all duration-200",
              "bg-muted/30 hover:bg-muted/50 group",
              "animate-slide-in-right"
            )}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm text-foreground line-clamp-2 flex-1">
                {item.question}
              </p>
              <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-0.5" />
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span
                className={cn(
                  "text-xs px-2 py-0.5 rounded-full",
                  item.confidence === "High" && "bg-success/20 text-success",
                  item.confidence === "Medium" && "bg-warning/20 text-warning",
                  item.confidence === "Low" && "bg-destructive/20 text-destructive"
                )}
              >
                {item.confidence}
              </span>
              <span className="text-xs text-muted-foreground">
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
  
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}
