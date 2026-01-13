import { Brain, Search, FileText } from "lucide-react";

export function LoadingState() {
  return (
    <div className="glass-card p-8 animate-fade-in">
      <div className="flex flex-col items-center">
        {/* Animated brain icon */}
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/40 to-accent/40 blur-2xl rounded-full animate-pulse" />
          <div className="relative w-16 h-16 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Brain className="w-8 h-8 text-primary-foreground animate-pulse" />
          </div>
        </div>

        <h3 className="text-lg font-semibold mb-2">Analyzing your question...</h3>
        
        {/* Loading steps */}
        <div className="space-y-3 w-full max-w-sm mt-4">
          <LoadingStep icon={Search} text="Searching knowledge base" delay={0} />
          <LoadingStep icon={FileText} text="Retrieving relevant documents" delay={300} />
          <LoadingStep icon={Brain} text="Generating verified answer" delay={600} />
        </div>

        {/* Progress bar */}
        <div className="w-full max-w-sm mt-6 h-1 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary to-accent shimmer" />
        </div>
      </div>
    </div>
  );
}

function LoadingStep({ 
  icon: Icon, 
  text, 
  delay 
}: { 
  icon: React.ElementType; 
  text: string; 
  delay: number;
}) {
  return (
    <div 
      className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg animate-fade-in"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
        <Icon className="w-4 h-4 text-primary" />
      </div>
      <span className="text-sm text-muted-foreground">{text}</span>
      <div className="ml-auto flex gap-1">
        <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}
