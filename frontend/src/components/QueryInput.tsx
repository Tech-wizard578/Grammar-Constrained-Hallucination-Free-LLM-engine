import { useState, useRef, useEffect } from "react";
import { Loader2, ArrowRight } from "lucide-react";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

/**
 * QueryInput - 8bit.ai style search input
 * Features: Minimalist design, glow on focus, full-width
 */
export function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      {/* 8bit.ai Style Input Container */}
      <div className="relative group">
        {/* Glow Effect */}
        <div className="absolute -inset-px bg-gradient-to-r from-transparent via-[#00aaff]/20 to-transparent opacity-0 group-focus-within:opacity-100 transition-opacity duration-500 blur-sm" />
        
        {/* Input Box */}
        <div className="relative border border-white/10 bg-black/50 backdrop-blur-sm transition-all duration-300 group-focus-within:border-[#00aaff]/30 group-focus-within:shadow-[0_0_60px_rgba(0,170,255,0.08)]">
          <div className="flex items-start gap-4 p-6">
            <textarea
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your knowledge base..."
              className="flex-1 bg-transparent border-none outline-none resize-none text-white placeholder:text-white/25 min-h-[80px] text-lg leading-relaxed font-light"
              disabled={isLoading}
              rows={2}
            />
            
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-white text-black font-medium transition-all duration-300 hover:shadow-[0_0_40px_rgba(255,255,255,0.2)] disabled:opacity-20 disabled:cursor-not-allowed disabled:hover:shadow-none"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="hidden sm:inline">Search</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Helper Text */}
      <div className="flex items-center justify-center gap-4 mt-6 text-xs text-white/30">
        <span>Press <kbd className="px-2 py-0.5 border border-white/10 text-white/50">Enter</kbd> to search</span>
        <span className="w-1 h-1 rounded-full bg-white/20" />
        <span>Powered by RAG + Chain of Verification</span>
      </div>
    </form>
  );
}
