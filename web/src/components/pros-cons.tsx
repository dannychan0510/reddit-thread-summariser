import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ProsConsProps {
  pros: string[];
  cons: string[];
}

export function ProsCons({ pros, cons }: ProsConsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-green-600 dark:text-green-400">Bullish Arguments</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {pros.map((pro, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-green-600 dark:text-green-400 shrink-0">+</span>
                <span>{pro}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-red-600 dark:text-red-400">Bearish Arguments</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {cons.map((con, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-red-600 dark:text-red-400 shrink-0">-</span>
                <span>{con}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
