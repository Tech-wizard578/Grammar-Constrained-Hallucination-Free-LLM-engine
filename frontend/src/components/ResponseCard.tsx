import { useState } from "react";
import { QueryResponse } from "@/types/api";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { CitationCard } from "./CitationCard";
import { Button } from "./ui/button";
import { 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  Clock, 
  FileText,
  Sparkles
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
    <div className="glass-card p-6 md:p-8 animate-scale-in">
      {/* Header with confidence and metadata */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <ConfidenceBadge confidence={response.confidence} />
        
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            <span>{response.elapsed_time_seconds.toFixed(2)}s</span>
          </div>
          <div className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" />
            <span>{response.documents_retrieved} docs</span>
          </div>
        </div>
      </div>

      {/* Answer */}
      <div className="relative group">
        <div className="absolute -left-4 top-0 bottom-0 w-1 bg-gradient-to-b from-primary to-accent rounded-full" />
        <p className="text-lg md:text-xl leading-relaxed text-foreground pl-2">
          {response.answer}
        </p>
        
        <Button
          variant="ghost"
          size="icon"
          className="absolute -right-2 -top-2 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={handleCopy}
        >
          {copied ? (
            <Check className="w-4 h-4 text-success" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </Button>
      </div>

      {/* Reasoning Section */}
      {response.reasoning && (
        <div className="mt-6">
          <Button
            variant="ghost"
            className="w-full justify-between text-muted-foreground hover:text-foreground"
            onClick={() => setShowReasoning(!showReasoning)}
          >
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              <span>Show Reasoning</span>
            </div>
            {showReasoning ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </Button>
          
          <div
            className={cn(
              "overflow-hidden transition-all duration-300",
              showReasoning ? "max-h-96 opacity-100 mt-4" : "max-h-0 opacity-0"
            )}
          >
            <div className="p-4 bg-muted/30 rounded-lg text-sm text-muted-foreground leading-relaxed">
              {response.reasoning}
            </div>
          </div>
        </div>
      )}

      {/* Citations */}
      {response.citations.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-muted-foreground mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Citations ({response.citations.length})
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
        <div className="mt-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
          <p className="text-sm text-destructive">
            {response.errors.join(", ")}
          </p>
        </div>
      )}
    </div>
  );
}
