import { useState } from "react";
import { QueryResponse } from "@/types/api";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { CitationCard } from "./CitationCard";
import { 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  Clock, 
  FileText,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ResponseCardProps {
  response: QueryResponse;
}

export function ResponseCard({ response }: ResponseCardProps) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(response.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card p-8 md:p-10 animate-slide-up max-w-3xl mx-auto">
      {/* Header with confidence and metadata */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <ConfidenceBadge confidence={response.confidence} />
        
        <div className="flex items-center gap-4 text-xs text-white/40">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            <span>{response.elapsed_time_seconds.toFixed(2)}s</span>
          </div>
          <div className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" />
            <span>{response.documents_retrieved} sources</span>
          </div>
        </div>
      </div>

      {/* Answer */}
      <div className="relative group mb-8">
        <p className="text-2xl md:text-3xl leading-relaxed text-white font-light tracking-tight">
          {response.answer}
        </p>
        
        <button
          className="absolute -right-2 top-0 opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10"
          onClick={handleCopy}
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4 text-white/40" />
          )}
        </button>
      </div>

      {/* Blue divider */}
      <div className="bit-divider mb-8" />

      {/* Reasoning Section */}
      {response.reasoning && (
        <div className="mb-8">
          <button
            className="w-full flex items-center justify-between py-3 px-4 rounded-xl bg-white/[0.02] border border-white/5 text-white/50 hover:text-white hover:bg-white/[0.04] transition-all"
            onClick={() => setShowReasoning(!showReasoning)}
          >
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#00aaff]" />
              <span className="text-sm font-medium">View Reasoning</span>
            </div>
            {showReasoning ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
          
          <div
            className={cn(
              "overflow-hidden transition-all duration-500",
              showReasoning ? "max-h-[500px] opacity-100 mt-4" : "max-h-0 opacity-0"
            )}
          >
            <div className="p-5 bg-white/[0.02] border border-white/5 rounded-xl text-sm text-white/60 leading-relaxed">
              {response.reasoning}
            </div>
          </div>
        </div>
      )}

      {/* Citations */}
      {response.citations.length > 0 && (
        <div>
          <h3 className="text-xs font-medium text-white/40 mb-4 uppercase tracking-widest flex items-center gap-2">
            <FileText className="w-3.5 h-3.5" />
            Sources ({response.citations.length})
          </h3>
          <div className="grid gap-3">
            {response.citations.map((citation, index) => (
              <CitationCard 
                key={`${citation.source_id}-${index}`} 
                citation={citation} 
                index={index}
              />
            ))}
          </div>
        </div>
      )}

      {/* Errors */}
      {response.errors.length > 0 && (
        <div className="mt-6 p-4 bg-red-500/5 border border-red-500/20 rounded-xl">
          <p className="text-sm text-red-400">
            {response.errors.join(", ")}
          </p>
        </div>
      )}
    </div>
  );
}
