import { Zap, FileCheck, ShieldCheck, Cpu } from "lucide-react";

export function EmptyState() {
  return (
    <div className="text-center py-12 animate-fade-in opacity-80">
      <div className="relative inline-block mb-8">
        <div className="absolute inset-0 bg-[#00aaff]/20 blur-[60px] rounded-full" />
        <div className="relative w-20 h-20 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center animate-glow-pulse box-shadow-[0_0_40px_rgba(0,170,255,0.1)]">
          <Cpu className="w-10 h-10 text-[#00aaff]" />
        </div>
      </div>
      
      <h2 className="text-xl font-bold text-white mb-2 tracking-tight">
        Ready for Inquiry
      </h2>
      
      <p className="text-white/40 max-w-sm mx-auto mb-10 text-sm font-light leading-relaxed">
        Engine loaded with hallucination-free protocols. 
        Awaiting input for deterministic retrieval.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
        <div className="p-4 border border-white/5 bg-white/[0.01] rounded-xl hover:bg-white/[0.03] transition-all group">
          <ShieldCheck className="w-5 h-5 text-white/20 group-hover:text-[#00aaff] mx-auto mb-3 transition-colors" />
          <p className="text-[10px] text-white/40 uppercase tracking-widest">Verifiable</p>
        </div>
        <div className="p-4 border border-white/5 bg-white/[0.01] rounded-xl hover:bg-white/[0.03] transition-all group">
          <FileCheck className="w-5 h-5 text-white/20 group-hover:text-[#00aaff] mx-auto mb-3 transition-colors" />
          <p className="text-[10px] text-white/40 uppercase tracking-widest">Cited Sources</p>
        </div>
        <div className="p-4 border border-white/5 bg-white/[0.01] rounded-xl hover:bg-white/[0.03] transition-all group">
          <Zap className="w-5 h-5 text-white/20 group-hover:text-[#00aaff] mx-auto mb-3 transition-colors" />
          <p className="text-[10px] text-white/40 uppercase tracking-widest">High Speed</p>
        </div>
      </div>
    </div>
  );
}
