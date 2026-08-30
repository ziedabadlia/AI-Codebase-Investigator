// ─── Backend Entities ────────────────────────────────────────────────────
export interface Repository {
  id: string;
  url: string;
  owner: string;
  name: string;
  default_branch: string;
  commit_sha: string;
  created_at: string;
  updated_at: string | null;
}

// ─── SSE Event Shapes ────────────────────────────────────────────────────

/** Streaming status/progress updates */
export type StatusEventType =
  | "ingesting"
  | "ingested"
  | "cached"
  | "investigating"
  | "searching"
  | "reading";

export interface StatusEvent {
  type: StatusEventType;
  message?: string;
  query?: string;
  file?: string;
  repository_id?: string;
}

/** A single AI answer text token */
export interface TokenEvent {
  content: string;
}

/** A code evidence block extracted from tool results */
export interface EvidenceEvent {
  file: string;
  start_line: number;
  end_line: number;
  content: string;
}

/** Union of all SSE events */
export type InvestigationEvent =
  | { event: "status"; data: StatusEvent }
  | { event: "token"; data: TokenEvent }
  | { event: "evidence"; data: EvidenceEvent }
  | { event: "error"; data: { message: string } }
  | { event: "done"; data: Record<string, never> };

// ─── Investigation State ─────────────────────────────────────────────────
export type InvestigationPhase =
  | "idle"
  | "ingesting"
  | "investigating"
  | "done"
  | "error";

export interface InvestigationStep {
  id: string;
  label: string;
  status: "pending" | "active" | "done";
}
