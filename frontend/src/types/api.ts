export interface Citation {
  source_id: number;
  quote: string;
  relevance_score: number;
}

export interface QueryResponse {
  success: boolean;
  answer: string;
  reasoning: string;
  confidence: "High" | "Medium" | "Low";
  citations: Citation[];
  elapsed_time_seconds: number;
  iterations: number;
  documents_retrieved: number;
  errors: string[];
}

export interface StatsResponse {
  collection_name: string;
  total_documents: number;
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
}

export interface IngestResponse {
  success: boolean;
  chunks_indexed: number;
  message: string;
}

export interface DeleteResponse {
  success: boolean;
  message: string;
}

export interface QueryHistoryItem {
  id: string;
  question: string;
  answer: string;
  confidence: "High" | "Medium" | "Low";
  timestamp: Date;
}
