export interface SearchResult {
  id: string;
  source_doc_id: string;
  chunk_index: number;
  section_heading: string;
  journal: string;
  publish_year: number;
  usage_count: number;
  attributes: string[];
  link: string;
  text: string;
  score: number;
  doi?: string;
  schema_version: string;
}

export interface SimilaritySearchResponse {
  results: SearchResult[];
  total_results: number;
  query: string;
}

export interface ChatResponse {
  answer: string;
  sources: SearchResult[];
  query: string;
} 