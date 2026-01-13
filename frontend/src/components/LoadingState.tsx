import { Brain, Search, FileText, Cpu } from "lucide-react";

export function LoadingState() {
  return (
    <div className="p-8 max-w-xl mx-auto animate-fade-in">
      <div className="flex flex-col items-center">
        {/* Animated icon */}
        <div className="relative mb-8">
          <div className="absolute inset-0 bg-[#00aaff]/20 blur-[50px] rounded-full animate-pulse-glow" />
          <div className="relative w-16 h-16 rounded-xl bg-white/[0.03] border border-white/10 flex items-center justify-center">
            <Cpu className="w-8 h-8 text-[#00aaff] animate-pulse" />
          </div>
        </div>

        <h3 className="text-xl font-bold text-white mb-8 tracking-tight">Processing Inquiry...</h3>
        
        {/* Loading steps */}
        <div className="space-y-4 w-full">
          <LoadingStep icon={Search} text="Scanning knowledge vectors..." delay={0} />
          <LoadingStep icon={FileText} text="Retrieving context chunks..." delay={300} />
          <LoadingStep icon={Brain} text="Synthesizing verified output..." delay={600} />
        </div>

        {/* Binary Progress bar */}
        <div className="w-full mt-8 h-px bg-white/10 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-transparent via-[#00aaff] to-transparent w-1/2 animate-[shimmer_1.5s_infinite]" />
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
      className="flex items-center gap-4 p-4 border border-white/5 bg-white/[0.01] rounded-xl animate-fade-in"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="w-8 h-8 rounded-lg bg-[#00aaff]/10 flex items-center justify-center border border-[#00aaff]/20">
        <Icon className="w-4 h-4 text-[#00aaff]" />
      </div>
      <span className="text-sm text-white/60 font-mono tracking-tight">{text}</span>
      <div className="ml-auto flex gap-1">
        <div className="w-1 h-1 bg-[#00aaff] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-1 h-1 bg-[#00aaff] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-1 h-1 bg-[#00aaff] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}
