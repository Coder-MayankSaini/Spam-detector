export interface EmailAnalysis {
  is_spam: boolean;
  confidence: number;
  threshold: number;
  keywords: string[];
  text: string;
  extracted_text?: string;
  source?: 'text' | 'ocr';
  processing_notes?: string;
  timestamp?: string;
}

export interface HistoryItem {
  text: string;
  is_spam: boolean;
  timestamp: string;
}

export interface Stats {
  total_analyzed: number;
  spam_count: number;
  ham_count: number;
  spam_ratio: number;
  model_threshold: number;
}

export interface TrainingItem {
  text: string;
  label: number;
}

export type Theme = 'light' | 'dark';
