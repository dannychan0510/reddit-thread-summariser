import { Badge } from "@/components/ui/badge";

interface TickerBadgesProps {
  tickers: string[];
}

export function TickerBadges({ tickers }: TickerBadgesProps) {
  if (tickers.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {tickers.map((ticker) => (
        <Badge key={ticker} variant="secondary" className="text-sm font-mono">
          ${ticker}
        </Badge>
      ))}
    </div>
  );
}
