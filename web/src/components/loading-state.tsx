"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const STATUS_MESSAGES = [
  "Fetching thread from Reddit...",
  "Scraping comments and replies...",
  "Sorting through the hot takes...",
  "Feeding everything to Gemini...",
  "Summarising the discussion...",
  "Extracting stock tickers...",
  "Weighing the bull and bear cases...",
  "Gauging commenter sentiment...",
  "Crunching the final results...",
  "Almost there, hang tight...",
];

export function LoadingState() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [previousIndex, setPreviousIndex] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => {
        setPreviousIndex(prev);
        const next = prev + 1;
        return next >= STATUS_MESSAGES.length ? 1 : next;
      });
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  // Clear the outgoing message after animation completes
  useEffect(() => {
    if (previousIndex !== null) {
      const timeout = setTimeout(() => setPreviousIndex(null), 500);
      return () => clearTimeout(timeout);
    }
  }, [previousIndex]);

  return (
    <div className="w-full max-w-4xl space-y-6">
      <div className="text-center space-y-2">
        <div
          className="relative h-7 overflow-hidden mx-auto"
          style={{ perspective: "600px" }}
        >
          {previousIndex !== null && (
            <p
              key={`out-${previousIndex}`}
              className="text-lg font-medium animate-dial-out absolute inset-x-0"
            >
              {STATUS_MESSAGES[previousIndex]}
            </p>
          )}
          <p
            key={`in-${currentIndex}`}
            className={`text-lg font-medium absolute inset-x-0 ${
              previousIndex !== null ? "animate-dial-in" : ""
            }`}
          >
            {STATUS_MESSAGES[currentIndex]}
          </p>
        </div>
        <p className="text-sm text-muted-foreground">
          This usually takes 10-20 seconds.
        </p>
      </div>

      {/* Ticker skeleton */}
      <div className="flex gap-2">
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-16" />
      </div>

      {/* Summary skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>

      {/* Pros/cons skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
