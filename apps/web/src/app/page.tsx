"use client";

import { Suspense, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { InvestigationForm } from "@/components/investigation/InvestigationForm";
import { InvestigationProgress } from "@/components/investigation/InvestigationProgress";
import { AnswerPanel } from "@/components/investigation/AnswerPanel";
import { EvidenceViewer } from "@/components/investigation/EvidenceViewer";
import { useInvestigation } from "@/hooks/useInvestigation";
import { Terminal, Loader2 } from "lucide-react";

function InvestigationApp() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const repoParam = searchParams.get("repo") || "";
  const queryParam = searchParams.get("q") || "";

  const {
    phase,
    steps,
    answer,
    evidenceList,
    error,
    startInvestigation
  } = useInvestigation();

  // Prevent double-fires in React StrictMode
  const hasStarted = useRef(false);

  useEffect(() => {
    // If URL has params on load, trigger the investigation
    if (repoParam && queryParam && phase === "idle" && !hasStarted.current) {
      hasStarted.current = true;
      startInvestigation(repoParam, queryParam);
    }
  }, [repoParam, queryParam, phase, startInvestigation]);

  const handleSubmit = (url: string, question: string) => {
    hasStarted.current = true;
    // Push state to URL for shareability
    const urlObj = new URL(window.location.href);
    urlObj.searchParams.set("repo", url);
    urlObj.searchParams.set("q", question);
    router.push(urlObj.pathname + urlObj.search);
    
    // Start locally
    startInvestigation(url, question);
  };

  const isWorking = phase === "ingesting" || phase === "investigating";

  return (
    <div className="min-h-screen max-w-5xl mx-auto p-6 pt-12 md:p-12 md:pt-20 pb-32 flex flex-col gap-10 leading-relaxed">
      
      {/* Header */}
      <header className="flex flex-col gap-3 pb-8 border-b border-border">
         <div className="flex items-center gap-3 text-primary">
            <Terminal className="h-7 w-7" />
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
               AI Codebase Investigator
            </h1>
         </div>
         <p className="text-muted-foreground">
            Provide a public GitHub repository and ask technical questions about its architecture, implementation, or dependencies.
         </p>
      </header>

      {/* Input Form */}
      <section className="flex flex-col items-center md:items-start w-full">
         <InvestigationForm 
           onSubmit={handleSubmit} 
           isLoading={isWorking} 
           initialUrl={repoParam}
           initialQuestion={queryParam}
         />
      </section>

      {/* Error State */}
      {error && (
         <div className="p-4 bg-error/10 border border-error/20 text-error rounded-md text-sm font-medium">
            Error: {error}
         </div>
      )}

      {/* Main Results Panel - Only show if not idle */}
      {phase !== "idle" && (
        <main className="flex flex-col lg:flex-row gap-10 mt-6">
          
          {/* Left Column: Progress Sidebar */}
          <aside className="w-full lg:w-1/3 shrink-0">
             <div className="sticky top-12">
               <InvestigationProgress steps={steps} />
             </div>
          </aside>

          {/* Right Column: Answers and Evidence */}
          <div className="w-full lg:w-2/3 flex flex-col min-w-0">
             <AnswerPanel answer={answer} isStreaming={isWorking} />
             
             {evidenceList.length > 0 && (
                <EvidenceViewer evidenceList={evidenceList} />
             )}
          </div>
          
        </main>
      )}
      
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    }>
      <InvestigationApp />
    </Suspense>
  );
}
