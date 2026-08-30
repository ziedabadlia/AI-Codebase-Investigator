"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { streamInvestigation } from "@/lib/api";
import type { InvestigationPhase, InvestigationStep, EvidenceEvent } from "@/types";

export function useInvestigation() {
  const [phase, setPhase] = useState<InvestigationPhase>("idle");
  const [steps, setSteps] = useState<InvestigationStep[]>([]);
  const [answer, setAnswer] = useState("");
  const [evidenceList, setEvidenceList] = useState<EvidenceEvent[]>([]);
  const [error, setError] = useState("");
  
  const abortControllerRef = useRef<(() => void) | null>(null);

  // Helper to add or update steps in the UI safely.
  const updateStep = (id: string, label: string, status: "pending" | "active" | "done") => {
    setSteps((prev) => {
      const idx = prev.findIndex((s) => s.id === id);
      if (idx !== -1) {
        const next = [...prev];
        next[idx] = { id, label, status };
        return next;
      }
      return [...prev, { id, label, status }];
    });
  };

  const startInvestigation = useCallback((url: string, question: string) => {
    // Reset state
    setPhase("ingesting");
    setSteps([]);
    setAnswer("");
    setEvidenceList([]);
    setError("");

    if (abortControllerRef.current) {
      abortControllerRef.current();
    }

    const cleanup = streamInvestigation(url, question, {
      onStatus: (data) => {
        if (data.type === "ingesting") {
           setPhase("ingesting");
           updateStep("ingest", data.message || "Indexing repository...", "active");
        } else if (data.type === "cached" || data.type === "ingested") {
           updateStep("ingest", "Repository indexed.", "done");
           setPhase("investigating");
        } else if (data.type === "investigating") {
           setPhase("investigating");
           updateStep("investigate", "Starting AI investigation...", "active");
        } else if (data.type === "searching") {
           updateStep("investigate", "Searching codebase...", "active");
           updateStep(`search-${Date.now()}`, `Search: ${data.query}`, "done");
        } else if (data.type === "reading") {
           updateStep("investigate", "Inspecting files...", "active");
           updateStep(`read-${Date.now()}`, `Read: ${data.file}`, "done");
        }
      },
      onToken: (data) => {
        // Mark investigation step as done once we start writing the answer
        updateStep("investigate", "Investigation complete.", "done");
        updateStep("answer", "Generating answer...", "active");
        setAnswer((prev) => prev + data.content);
      },
      onEvidence: (data) => {
        setEvidenceList((prev) => [...prev, data]);
      },
      onError: (msg) => {
         setError(msg);
         setPhase("error");
      },
      onDone: () => {
         updateStep("answer", "Answer completed.", "done");
         setPhase("done");
      }
    });

    abortControllerRef.current = cleanup;
  }, []);

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current();
      }
    };
  }, []);

  return {
    phase,
    steps,
    answer,
    evidenceList,
    error,
    startInvestigation,
  };
}
