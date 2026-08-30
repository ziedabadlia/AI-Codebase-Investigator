"use client";

import { useEffect, useState } from "react";
import { codeToHtml } from "shiki";
import { FileCode, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface CodeBlockProps {
  code: string;
  language?: string;
  filename?: string;
  className?: string;
}

export function CodeBlock({
  code,
  language = "typescript",
  filename,
  className,
}: CodeBlockProps) {
  const [html, setHtml] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function highlight() {
      if (!code) return;
      try {
        // We use GitHub Dark as it closely matches our design system tokens
        const out = await codeToHtml(code, {
          lang: language,
          theme: "github-dark",
        });
        if (mounted) {
          setHtml(out);
        }
      } catch (e) {
        console.error("Shiki highlight error:", e);
        // Fallback to basic rendering if shiki fails for an obscure language
        if (mounted) {
           setHtml(`<pre><code>${code.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre>`);
        }
      }
    }

    highlight();

    return () => {
      mounted = false;
    };
  }, [code, language]);

  return (
    <div
      className={cn(
        "rounded-md border border-code-border bg-code-bg overflow-hidden text-sm",
        className
      )}
    >
      {filename && (
        <div className="flex items-center gap-2 border-b border-code-border bg-surface-muted px-4 py-2 text-xs text-muted-foreground font-mono">
          <FileCode className="h-4 w-4" />
          <span>{filename}</span>
        </div>
      )}
      <div className="relative w-full overflow-x-auto p-4">
        {!html ? (
          <div className="flex items-center justify-center p-4 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            <span>Parsing snippet...</span>
          </div>
        ) : (
          <div
            className="w-full text-left font-mono text-[13px] leading-relaxed [&>pre]:bg-transparent"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        )}
      </div>
    </div>
  );
}
