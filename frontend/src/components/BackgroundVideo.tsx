import React from "react";

export function BackgroundVideo() {
  return (
    <div className="fixed inset-0 z-[-1] overflow-hidden bg-black pointer-events-none">
      {/* Screen Glow */}
      <div className="screen-glow" />
      
      {/* Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-[0.1]"
        style={{
          backgroundImage: `linear-gradient(#00aaff 1px, transparent 1px), linear-gradient(90deg, #00aaff 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
          maskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)'
        }}
      />

      {/* Data Streaks */}
      <div className="absolute inset-0">
        <div className="data-streak left-[10%]" style={{ animationDelay: '0s' }} />
        <div className="data-streak left-[30%]" style={{ animationDelay: '2s' }} />
        <div className="data-streak left-[50%]" style={{ animationDelay: '1s' }} />
        <div className="data-streak left-[70%]" style={{ animationDelay: '3s' }} />
        <div className="data-streak left-[90%]" style={{ animationDelay: '1.5s' }} />
      </div>

      {/* Corner Accents */}
      <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-[#00aaff]/10 to-transparent blur-3xl" />
      <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-[#00aaff]/10 to-transparent blur-3xl" />
    </div>
  );
}
