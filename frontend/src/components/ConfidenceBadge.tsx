import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: "High" | "Medium" | "Low";
  className?: string;
}

export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  const variants = {
    High: "bg-success/20 text-success border-success/30",
    Medium: "bg-warning/20 text-warning border-warning/30",
    Low: "bg-destructive/20 text-destructive border-destructive/30",
  };

  const glowVariants = {
    High: "shadow-[0_0_12px_hsla(142,71%,45%,0.3)]",
    Medium: "shadow-[0_0_12px_hsla(48,96%,53%,0.3)]",
    Low: "shadow-[0_0_12px_hsla(0,72%,51%,0.3)]",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition-all duration-300",
        variants[confidence],
        glowVariants[confidence],
        className
      )}
    >
      <span className="relative flex h-2 w-2">
        <span
          className={cn(
            "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
            confidence === "High" && "bg-success",
            confidence === "Medium" && "bg-warning",
            confidence === "Low" && "bg-destructive"
          )}
        />
        <span
          className={cn(
            "relative inline-flex rounded-full h-2 w-2",
            confidence === "High" && "bg-success",
            confidence === "Medium" && "bg-warning",
            confidence === "Low" && "bg-destructive"
          )}
        />
      </span>
      {confidence} Confidence
    </span>
  );
}
