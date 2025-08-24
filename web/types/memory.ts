export interface Memory {
  id: string
  timestamp: string
  location?: string
  summary: string
  detailed_description: string
  title: string
  confidence: number
  objects_detected: string[]
  activity?: string
  colors: string[]
  people_count?: number
  image_path: string
  compressed_image_path: string
  original_image_path?: string
  created_at: string
  updated_at: string
  vector_id?: number
}

export interface MemorySearchResult {
  memory: Memory
  similarity_score: number
  timestamp_distance_minutes: number
}

export interface MemorySearchResponse {
  results: MemorySearchResult[]
  total_found: number
  search_timestamp: string
  query_timestamp: string
}

export interface ChatRequest {
  message: string
  include_images?: boolean
  max_results?: number
}

export interface ChatResponse {
  assistant_message: string
  memory_references: MemoryReference[]
  confidence: number
  search_query: string
  timestamp: string
}

export interface MemoryReference {
  id: string
  title: string
  summary: string
  timestamp: string
  location?: string
  similarity_score: number
  image_path: string
}

export interface HealthResponse {
  status: string
  timestamp: string
  memories_count: number
  last_capture_time?: string
  faiss_index_size: number
  storage_usage_mb: number
  demo_mode: boolean
}

export interface CaptureResponse {
  success: boolean
  memory_id: string
  message: string
  timestamp: string
  image_path: string
}
