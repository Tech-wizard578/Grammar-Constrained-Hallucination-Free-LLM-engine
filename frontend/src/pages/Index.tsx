import { useState, useRef, useEffect } from "react";
import { Header } from "@/components/Header";
import { QueryInput } from "@/components/QueryInput";
import { ResponseCard } from "@/components/ResponseCard";
import { StatsPanel } from "@/components/StatsPanel";
import { QueryHistory } from "@/components/QueryHistory";
import { EmptyState } from "@/components/EmptyState";
import { LoadingState } from "@/components/LoadingState";
import { queryKnowledgeBase } from "@/lib/api";
import { QueryResponse, QueryHistoryItem } from "@/types/api";
import { useToast } from "@/hooks/use-toast";
import { AlertCircle } from "lucide-react";

export default function Index() {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const responseRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

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
    <div className="min-h-screen">
      <Header />
      
      {/* Background effects */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px] translate-y-1/2 -translate-x-1/2" />
      </div>

      <main className="container mx-auto px-4 pt-24 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
          {/* Main content */}
          <div className="space-y-8">
            {/* Hero section */}
            <div className="text-center mb-8 animate-fade-in">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Ask <span className="gradient-text">Anything</span>
              </h2>
              <p className="text-muted-foreground max-w-xl mx-auto">
                Get accurate, citation-backed answers from your knowledge base. 
                No hallucinations, just facts.
              </p>
            </div>

            {/* Query input */}
            <QueryInput onSubmit={handleQuery} isLoading={isLoading} />

            {/* Response area */}
            <div ref={responseRef}>
              {isLoading && <LoadingState />}
              
              {error && !isLoading && (
                <div className="glass-card p-6 animate-fade-in">
                  <div className="flex items-center gap-3 text-destructive">
                    <AlertCircle className="w-5 h-5" />
                    <div>
                      <p className="font-medium">Something went wrong</p>
                      <p className="text-sm text-muted-foreground mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}
              
              {response && !isLoading && <ResponseCard response={response} />}
              
              {!response && !isLoading && !error && <EmptyState />}
            </div>
          </div>

          {/* Sidebar */}
          <aside className="space-y-6">
            <StatsPanel />
            <QueryHistory history={history} onSelect={handleHistorySelect} />
          </aside>
        </div>
      </main>
    </div>
  );
}
