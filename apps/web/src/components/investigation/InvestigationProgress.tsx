"use client";

import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { InvestigationStep } from "@/types";
import { cn } from "@/lib/utils";

interface InvestigationProgressProps {
  steps: InvestigationStep[];
}

export function InvestigationProgress({ steps }: InvestigationProgressProps) {
  if (steps.length === 0) return null;

  return (
    <div className="flex flex-col space-y-3 rounded-lg border border-border bg-surface p-5">
      <h3 className="text-sm font-semibold tracking-tight text-foreground uppercase">
        Investigation Progress
      </h3>
      <div className="flex flex-col gap-2 relative pl-1">
        {/* Decorative left line */}
        <div className="absolute left-3 top-2 bottom-2 w-px bg-border-muted z-0" />
        
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-3 z-10">
            <div className="bg-surface flex items-center justify-center py-1">
              {step.status === "done" && (
                <CheckCircle2 className="h-4 w-4 text-success" />
              )}
              {step.status === "active" && (
                <Loader2 className="h-4 w-4 text-primary animate-spin" />
              )}
              {step.status === "pending" && (
                <Circle className="h-4 w-4 text-muted-foreground opacity-50" />
              )}
            </div>
            <span
              className={cn(
                "text-sm",
                step.status === "active"
                  ? "text-foreground font-medium"
                  : step.status === "done"
                  ? "text-muted-foreground"
                  : "text-muted-foreground opacity-50"
              )}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
