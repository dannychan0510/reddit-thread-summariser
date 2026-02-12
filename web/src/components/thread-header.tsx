import { Card, CardContent } from "@/components/ui/card";
import { ThreadMeta } from "@/lib/types";

interface ThreadHeaderProps {
  thread: ThreadMeta;
}

export function ThreadHeader({ thread }: ThreadHeaderProps) {
  return (
    <Card>
      <CardContent className="py-1">
        <h2 className="text-xl font-semibold">{thread.title}</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          r/{thread.subreddit}  &middot;  Score: {thread.score}  &middot;  {thread.num_comments} comments
        </p>
      </CardContent>
    </Card>
  );
}
