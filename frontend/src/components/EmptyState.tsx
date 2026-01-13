import { Sparkles, FileQuestion, Brain } from "lucide-react";

export function EmptyState() {
  return (
    <div className="text-center py-16 animate-fade-in">
      <div className="relative inline-block mb-8">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/30 to-accent/30 blur-3xl rounded-full" />
        <div className="relative w-24 h-24 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center animate-float">
          <Brain className="w-12 h-12 text-primary-foreground" />
        </div>
      </div>
      
      <h2 className="text-2xl font-bold gradient-text mb-3">
        Hallucination-Free AI
      </h2>
      
      <p className="text-muted-foreground max-w-md mx-auto mb-8 leading-relaxed">
        Ask any question and get accurate answers backed by citations from your knowledge base. 
        Every response includes confidence scores and source references.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-lg mx-auto">
        <div className="glass-card p-4">
          <Sparkles className="w-6 h-6 text-primary mx-auto mb-2" />
          <p className="text-xs text-muted-foreground">Verified Answers</p>
        </div>
        <div className="glass-card p-4">
          <FileQuestion className="w-6 h-6 text-primary mx-auto mb-2" />
          <p className="text-xs text-muted-foreground">Source Citations</p>
        </div>
        <div className="glass-card p-4">
          <Brain className="w-6 h-6 text-primary mx-auto mb-2" />
          <p className="text-xs text-muted-foreground">Confidence Scores</p>
        </div>
      </div>
    </div>
  );
}
