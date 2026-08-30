"use client";

import { EvidenceEvent } from "@/types";
import { CodeBlock } from "@/components/ui/CodeBlock";
import { BookOpen } from "lucide-react";

interface EvidenceViewerProps {
  evidenceList: EvidenceEvent[];
}

export function EvidenceViewer({ evidenceList }: EvidenceViewerProps) {
  if (evidenceList.length === 0) return null;

  return (
    <div className="flex flex-col mt-8 space-y-4">
      <div className="flex items-center gap-2 text-foreground mb-2">
        <BookOpen className="h-5 w-5 opacity-80" />
        <h3 className="font-semibold tracking-tight text-lg">Code Evidence</h3>
      </div>
      
      <div className="grid gap-6">
        {evidenceList.map((evidence, idx) => (
          <div key={idx} className="flex flex-col gap-2">
             <CodeBlock 
               code={evidence.content} 
               filename={`${evidence.file} (Lines ${evidence.start_line}-${evidence.end_line})`}
             />
          </div>
        ))}
      </div>
    </div>
  );
}
