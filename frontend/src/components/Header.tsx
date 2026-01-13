import { Brain, Github, BookOpen } from "lucide-react";
import { Button } from "./ui/button";
import { DocumentManager } from "./DocumentManager";

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center glow-primary">
            <Brain className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold gradient-text">HallucinationFree</h1>
            <p className="text-xs text-muted-foreground">LLM Engine</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <DocumentManager />
          
          <Button variant="ghost" size="icon" asChild>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              <Github className="w-4 h-4" />
            </a>
          </Button>
          
          <Button variant="ghost" size="icon">
            <BookOpen className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
