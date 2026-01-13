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
      className="p-4 bg-white/[0.02] border border-white/5 rounded-xl animate-fade-in hover:border-[#00aaff]/20 transition-all group"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-xs font-mono text-white/50">
          {citation.source_id}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <Quote className="w-3.5 h-3.5 text-white/30" />
            <span className="text-[10px] text-white/30 uppercase tracking-widest">Source Quote</span>
          </div>
          
          <p className="text-sm text-white/70 italic leading-relaxed">
            "{citation.quote}"
          </p>
          
          <div className="mt-3 flex items-center gap-3">
            <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-[#00aaff] to-[#0066cc] rounded-full transition-all duration-500"
                style={{ width: `${relevancePercentage}%` }}
              />
            </div>
            <span className="text-xs text-[#00aaff] font-mono">{relevancePercentage}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
