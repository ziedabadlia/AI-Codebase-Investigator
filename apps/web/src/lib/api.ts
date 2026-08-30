import type { EvidenceEvent, StatusEvent, TokenEvent } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── REST client ──────────────────────────────────────────────────────────

export async function ingestRepository(url: string) {
  const res = await fetch(`${API_BASE}/api/repositories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Failed to ingest repository.");
  }
  return res.json();
}

// ─── SSE client ──────────────────────────────────────────────────────────

export interface StreamHandlers {
  onStatus: (data: StatusEvent) => void;
  onToken: (data: TokenEvent) => void;
  onEvidence: (data: EvidenceEvent) => void;
  onError: (message: string) => void;
  onDone: () => void;
}

/**
 * Opens a Server-Sent Events connection to stream the full investigation.
 * Returns a cleanup function to close the event source.
 */
export function streamInvestigation(
  repoUrl: string,
  question: string,
  handlers: StreamHandlers
): () => void {
  const params = new URLSearchParams({ repo_url: repoUrl, question });
  const url = `${API_BASE}/api/stream?${params.toString()}`;

  const source = new EventSource(url);

  source.addEventListener("status", (e) => {
    try {
      handlers.onStatus(JSON.parse(e.data) as StatusEvent);
    } catch {
      // ignore parse errors for individual events
    }
  });

  source.addEventListener("token", (e) => {
    try {
      handlers.onToken(JSON.parse(e.data) as TokenEvent);
    } catch {}
  });

  source.addEventListener("evidence", (e) => {
    try {
      handlers.onEvidence(JSON.parse(e.data) as EvidenceEvent);
    } catch {}
  });

  source.addEventListener("error", (e) => {
    // This fires for both SSE-level errors and connection errors
    if (e instanceof MessageEvent) {
      try {
        const parsed = JSON.parse(e.data);
        handlers.onError(parsed.message ?? "An unknown error occurred.");
      } catch {
        handlers.onError("Connection error.");
      }
    } else {
      // Connection dropped
      handlers.onError("Connection to the server was lost.");
      source.close();
    }
  });

  source.addEventListener("done", () => {
    handlers.onDone();
    source.close();
  });

  return () => source.close();
}
