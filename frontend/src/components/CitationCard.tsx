import { Citation } from "@/types/api";
import { Quote } from "lucide-react";

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const relevancePercentage = Math.round(citation.relevance_score * 100);
  
  return (
    <div 
      className="glass-card p-4 animate-fade-in"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
          <span className="text-xs font-bold text-primary">
            {citation.source_id}
          </span>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <Quote className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">Source Quote</span>
          </div>
          
          <p className="text-sm text-foreground/90 italic leading-relaxed">
            "{citation.quote}"
          </p>
          
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Relevance</span>
              <span className="text-primary font-medium">{relevancePercentage}%</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500"
                style={{ width: `${relevancePercentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
