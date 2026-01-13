import { Header } from "@/components/Header";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { Brain, Cpu, Shield, Zap } from "lucide-react";

export default function About() {
  // Scroll animations
  const heroRef = useScrollAnimation<HTMLDivElement>({ type: "reveal", duration: 1 });
  const cardsRef = useScrollAnimation<HTMLDivElement>({ 
    type: "slideUp", 
    staggerSelector: ".feature-card",
    stagger: 0.12 
  });
  const techRef = useScrollAnimation<HTMLDivElement>({ type: "slideLeft", delay: 0.2 });

  return (
    <div className="min-h-screen bg-black text-white selection:bg-[#00aaff]/30 selection:text-white">
      <AnimatedBackground />
      <Header />

      <main className="relative z-10 container mx-auto px-6 lg:px-10 pt-32 pb-24">
        {/* Hero */}
        <div ref={heroRef} className="max-w-4xl mb-20">
          <p className="hero-overline mb-4">About</p>
          <h1 className="hero-title text-white mb-8">
            Hallucination-Free<br />
            <span className="text-[#00aaff]">AI Engine</span>
          </h1>
          <p className="text-lg md:text-xl text-white/50 font-light leading-relaxed">
            A revolutionary approach to AI-powered knowledge retrieval that eliminates 
            hallucinations through grammar-constrained generation and chain-of-verification.
          </p>
        </div>

        {/* Features Grid */}
        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
          <div className="feature-card glass-card p-8">
            <Brain className="w-10 h-10 text-[#00aaff] mb-6" />
            <h3 className="text-xl font-medium text-white mb-3">RAG Architecture</h3>
            <p className="text-white/50 leading-relaxed">
              Retrieval-Augmented Generation ensures every answer is grounded in 
              your actual documents, not fabricated information.
            </p>
          </div>

          <div className="feature-card glass-card p-8">
            <Shield className="w-10 h-10 text-[#00aaff] mb-6" />
            <h3 className="text-xl font-medium text-white mb-3">Chain of Verification</h3>
            <p className="text-white/50 leading-relaxed">
              Multi-step verification process validates responses against source 
              documents before delivery.
            </p>
          </div>

          <div className="feature-card glass-card p-8">
            <Cpu className="w-10 h-10 text-[#00aaff] mb-6" />
            <h3 className="text-xl font-medium text-white mb-3">Grammar Constraints</h3>
            <p className="text-white/50 leading-relaxed">
              Structured output generation ensures responses follow exact schemas, 
              preventing format errors.
            </p>
          </div>

          <div className="feature-card glass-card p-8">
            <Zap className="w-10 h-10 text-[#00aaff] mb-6" />
            <h3 className="text-xl font-medium text-white mb-3">Verifiable Citations</h3>
            <p className="text-white/50 leading-relaxed">
              Every claim is backed by specific citations from your knowledge base, 
              enabling full traceability.
            </p>
          </div>
        </div>

        {/* Tech Stack */}
        <div ref={techRef} className="border-t border-white/10 pt-12">
          <h2 className="text-xs font-medium text-white/40 uppercase tracking-widest mb-8">
            Built With
          </h2>
          <div className="flex flex-wrap gap-4">
            {["Python", "FastAPI", "ChromaDB", "LangGraph", "React", "TypeScript", "Tailwind CSS"].map((tech) => (
              <span key={tech} className="px-4 py-2 border border-white/10 text-white/60 text-sm">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
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
