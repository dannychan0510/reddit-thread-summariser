import { CommenterSentiment, Sentiment } from "@/lib/types";

const barConfig: Record<Sentiment, { label: string; color: string; track: string }> = {
  positive: { label: "Positive", color: "bg-green-500", track: "bg-green-500/20" },
  negative: { label: "Negative", color: "bg-red-500", track: "bg-red-500/20" },
  neutral: { label: "Neutral", color: "bg-yellow-500", track: "bg-yellow-500/20" },
};

interface SentimentChartProps {
  sentiments: CommenterSentiment[];
}

export function SentimentChart({ sentiments }: SentimentChartProps) {
  const total = sentiments.length;
  if (total === 0) return null;

  const counts: Record<Sentiment, number> = { positive: 0, negative: 0, neutral: 0 };
  for (const s of sentiments) {
    counts[s.sentiment]++;
  }

  return (
    <div className="space-y-3">
      {(["positive", "negative", "neutral"] as Sentiment[]).map((key) => {
        const { label, color, track } = barConfig[key];
        const count = counts[key];
        const pct = (count / total) * 100;

        return (
          <div key={key} className="flex items-center gap-3">
            <span className="w-20 text-sm font-medium text-right">{label}</span>
            <div className={`flex-1 h-5 rounded ${track} overflow-hidden`}>
              <div
                className={`h-full rounded ${color} transition-all duration-500`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="w-24 text-sm text-muted-foreground tabular-nums">
              {count} ({pct.toFixed(1)}%)
            </span>
          </div>
        );
      })}
    </div>
  );
}
