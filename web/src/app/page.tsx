"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { UrlForm } from "@/components/url-form";
import { TickerBadges } from "@/components/ticker-badges";
import { ProsCons } from "@/components/pros-cons";
import { SentimentChart } from "@/components/sentiment-chart";
import { ThreadHeader } from "@/components/thread-header";
import { SentimentTable } from "@/components/sentiment-table";
import { LoadingState } from "@/components/loading-state";
import { ThemeToggle } from "@/components/theme-toggle";
import { summariseThread } from "@/lib/api";
import { AnalysisResult } from "@/lib/types";

export default function Home() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await summariseThread(url);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-12 gap-8">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Reddit Thread Summariser</h1>
        <p className="text-muted-foreground">
          Paste a Reddit post URL to get AI-powered sentiment analysis
        </p>
      </div>

      <UrlForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && (
        <Alert variant="destructive" className="max-w-2xl">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isLoading && <LoadingState />}

      {result && (
        <div className="w-full max-w-4xl space-y-6">
          <ThreadHeader thread={result.thread} />
          <TickerBadges tickers={result.tickers} />

          <Card>
            <CardHeader>
              <CardTitle>Discussion Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="leading-relaxed">{result.summary}</p>
            </CardContent>
          </Card>

          <ProsCons pros={result.pros} cons={result.cons} />

          <Card>
            <CardHeader>
              <CardTitle>Sentiment Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <SentimentChart sentiments={result.commenter_sentiments} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Per-Commenter Sentiment</CardTitle>
            </CardHeader>
            <CardContent>
              <SentimentTable sentiments={result.commenter_sentiments} />
            </CardContent>
          </Card>
        </div>
      )}
    </main>
  );
}
