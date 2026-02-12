export type Sentiment = "positive" | "negative" | "neutral";

export interface CommenterSentiment {
  author: string;
  sentiment: Sentiment;
  reason: string;
}

export interface ThreadMeta {
  title: string;
  subreddit: string;
  score: number;
  num_comments: number;
}

export interface AnalysisResult {
  tickers: string[];
  summary: string;
  pros: string[];
  cons: string[];
  commenter_sentiments: CommenterSentiment[];
  thread: ThreadMeta;
}

export interface ApiError {
  detail: string;
}
