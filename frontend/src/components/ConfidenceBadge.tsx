import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: "High" | "Medium" | "Low";
  className?: string;
}

export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  const variants = {
    High: "bit-badge-success",
    Medium: "bit-badge-warning",
    Low: "bit-badge-danger",
  };

  const dotColors = {
    High: "bg-green-400",
    Medium: "bg-yellow-400",
    Low: "bg-red-400",
  };

  return (
    <span className={cn(variants[confidence], className)}>
      <span className="relative flex h-1.5 w-1.5">
        <span
          className={cn(
            "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
            dotColors[confidence]
          )}
        />
        <span
          className={cn(
            "relative inline-flex rounded-full h-1.5 w-1.5",
            dotColors[confidence]
          )}
        />
      </span>
      {confidence}
    </span>
  );
}
