"use client";

import { Sparkles } from "lucide-react";

interface AnswerPanelProps {
  answer: string;
  isStreaming: boolean;
}

export function AnswerPanel({ answer, isStreaming }: AnswerPanelProps) {
  if (!answer && !isStreaming) return null;

  return (
    <div className="flex flex-col rounded-lg border border-primary/20 bg-primary-muted/10 p-5 mt-6 shadow-sm">
      <div className="flex items-center gap-2 mb-3 text-primary">
        <Sparkles className="h-5 w-5" />
        <h3 className="font-semibold tracking-tight">Investigator Answer</h3>
      </div>
      <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-code-bg prose-pre:border prose-pre:border-code-border text-foreground">
        {/* If utilizing markdown, a library like react-markdown would be used here. For MVP, we render basic line breaks. */}
        {answer ? (
          <div className="whitespace-pre-wrap">{answer}</div>
        ) : (
          <div className="flex gap-1 items-center h-6 text-muted-foreground">
             <span className="animate-pulse">●</span>
             <span className="animate-pulse delay-75">●</span>
             <span className="animate-pulse delay-150">●</span>
          </div>
        )}
      </div>
      
      {isStreaming && answer.length > 0 && (
        <div className="mt-2 text-xs text-primary animate-pulse">Typing...</div>
      )}
    </div>
  );
}
