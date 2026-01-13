import { useState, useRef, useEffect } from "react";
import { Header } from "@/components/Header";
import { QueryInput } from "@/components/QueryInput";
import { ResponseCard } from "@/components/ResponseCard";
import { StatsPanel } from "@/components/StatsPanel";
import { QueryHistory } from "@/components/QueryHistory";
import { EmptyState } from "@/components/EmptyState";
import { LoadingState } from "@/components/LoadingState";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { queryKnowledgeBase } from "@/lib/api";
import { QueryResponse, QueryHistoryItem } from "@/types/api";
import { useToast } from "@/hooks/use-toast";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { AlertCircle } from "lucide-react";

const HISTORY_STORAGE_KEY = "hallucination_free_history";

// Load history from localStorage
const loadHistory = (): QueryHistoryItem[] => {
  try {
    const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Convert timestamp strings back to Date objects
      return parsed.map((item: any) => ({
        ...item,
        timestamp: new Date(item.timestamp),
      }));
    }
  } catch (e) {
    console.error("Failed to load history:", e);
  }
  return [];
};

// Save history to localStorage
const saveHistory = (history: QueryHistoryItem[]) => {
  try {
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    console.error("Failed to save history:", e);
  }
};

export default function Index() {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistoryItem[]>(() => loadHistory());
  const responseRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Scroll animations
  const heroRef = useScrollAnimation<HTMLDivElement>({ type: "reveal", duration: 1 });
  const queryRef = useScrollAnimation<HTMLDivElement>({ type: "slideUp", delay: 0.3 });
  const sidebarRef = useScrollAnimation<HTMLDivElement>({ 
    type: "slideUp", 
    staggerSelector: ".sidebar-item",
    stagger: 0.15,
    delay: 0.5 
  });

  // Persist history to localStorage whenever it changes
  useEffect(() => {
    saveHistory(history);
  }, [history]);

  const handleQuery = async (question: string) => {
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await queryKnowledgeBase(question);
      setResponse(result);

      // Add to history
      const historyItem: QueryHistoryItem = {
        id: crypto.randomUUID(),
        question,
        answer: result.answer,
        confidence: result.confidence,
        timestamp: new Date(),
      };
      setHistory((prev) => [historyItem, ...prev.slice(0, 9)]);

      // Scroll to response
      setTimeout(() => {
        responseRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to get response";
      setError(message);
      toast({
        title: "Query failed",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleHistorySelect = (item: QueryHistoryItem) => {
    handleQuery(item.question);
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-[#00aaff]/30 selection:text-white">
      {/* 8bit.ai Animated Background */}
      <AnimatedBackground />

      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-6 lg:px-10 pt-32 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-16">
          {/* Main content */}
          <div className="space-y-16">
            {/* Hero section - 8bit.ai Style */}
            <div ref={heroRef}>
              <p className="hero-overline mb-4">Accelerating</p>
              <h2 className="hero-title text-white mb-8">
                Enterprise<br />
                <span className="text-[#00aaff]">Superintelligence</span>
              </h2>
              <p className="text-lg md:text-xl text-white/50 max-w-2xl font-light leading-relaxed">
                Experience hallucination-free knowledge retrieval. 
                Deterministic answers backed by verifiable citations from your enterprise data.
              </p>
            </div>

            {/* Query input */}
            <div ref={queryRef}>
              <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
            </div>

            {/* Response area */}
            <div ref={responseRef} className="min-h-[200px]">
              {isLoading && <LoadingState />}
              
              {error && !isLoading && (
                <div className="glass-card p-6 animate-fade-in border-red-500/20 bg-red-500/5">
                  <div className="flex items-center gap-3 text-red-400">
                    <AlertCircle className="w-5 h-5" />
                    <div>
                      <p className="font-medium">System Error</p>
                      <p className="text-sm text-white/50 mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}
              
              {response && !isLoading && <ResponseCard response={response} />}
              
              {!response && !isLoading && !error && <EmptyState />}
            </div>
          </div>

          {/* Sidebar */}
          <aside ref={sidebarRef} className="space-y-8 lg:pt-8">
            <div className="sidebar-item">
              <StatsPanel />
            </div>
            <div className="sidebar-item">
              <QueryHistory history={history} onSelect={handleHistorySelect} />
            </div>
          </aside>
        </div>
      </main>

      {/* Footer - 8bit.ai Style */}
      <footer className="fixed bottom-0 left-0 right-0 z-30 py-6 pointer-events-none">
        <div className="container mx-auto px-6 lg:px-10 flex items-center justify-center">
          <p className="text-xs text-white/30 pointer-events-auto">
            © 2026 HallucinationFree AI. All Rights Reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
