import React from "react";

/**
 * AnimatedBackground - 8bit.ai style background effects
 * Includes: noise overlay, edge glow, and animated lines
 */
export function AnimatedBackground() {
  return (
    <>
      {/* Pure Black Base */}
      <div className="fixed inset-0 z-0 bg-black" />
      
      {/* Animated Lines Background */}
      <div className="animated-lines" />
      
      {/* Edge Glow / Vignette */}
      <div className="edge-glow" />
      
      {/* Film Grain Noise Overlay */}
      <div className="noise-overlay" />
    </>
  );
}
