"use client";

import * as React from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Search } from "lucide-react";

interface InvestigationFormProps {
  onSubmit: (url: string, question: string) => void;
  isLoading: boolean;
  initialUrl?: string;
  initialQuestion?: string;
}

export function InvestigationForm({
  onSubmit,
  isLoading,
  initialUrl = "",
  initialQuestion = "",
}: InvestigationFormProps) {
  const [url, setUrl] = React.useState(initialUrl);
  const [question, setQuestion] = React.useState(initialQuestion);
  const [error, setError] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!url.trim() || !question.trim()) {
      setError("Both repository URL and question are required.");
      return;
    }

    if (!url.includes("github.com")) {
      setError("Please provide a valid GitHub repository URL.");
      return;
    }

    onSubmit(url.trim(), question.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl space-y-4">
      <div className="space-y-2">
        <label htmlFor="repo" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          GitHub Repository URL
        </label>
        <Input
          id="repo"
          placeholder="e.g., https://github.com/facebook/react"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={isLoading}
          autoComplete="off"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="question" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Your Investigation Question
        </label>
        <textarea
          id="question"
          rows={3}
          className="flex w-full rounded-md border border-border bg-surface px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
          placeholder="e.g., How does the authentication middleware manage JWT cookies?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
        />
      </div>

      {error && <p className="text-sm font-medium text-error">{error}</p>}

      <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto">
        <Search className="mr-2 w-4 h-4" />
        Investigate Codebase
      </Button>
    </form>
  );
}
