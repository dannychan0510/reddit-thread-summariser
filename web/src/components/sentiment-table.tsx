import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { CommenterSentiment, Sentiment } from "@/lib/types";

const sentimentConfig: Record<Sentiment, { label: string; className: string }> = {
  positive: { label: "POSITIVE", className: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" },
  negative: { label: "NEGATIVE", className: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200" },
  neutral: { label: "NEUTRAL", className: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200" },
};

interface SentimentTableProps {
  sentiments: CommenterSentiment[];
}

export function SentimentTable({ sentiments }: SentimentTableProps) {
  const order: Record<Sentiment, number> = { positive: 0, negative: 1, neutral: 2 };
  const sorted = [...sentiments].sort((a, b) => order[a.sentiment] - order[b.sentiment]);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Author</TableHead>
          <TableHead>Sentiment</TableHead>
          <TableHead>Reason</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {sorted.map((s) => {
          const config = sentimentConfig[s.sentiment];
          return (
            <TableRow key={s.author}>
              <TableCell className="font-medium">u/{s.author}</TableCell>
              <TableCell>
                <Badge className={config.className}>{config.label}</Badge>
              </TableCell>
              <TableCell>{s.reason}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
