const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.NEXT_PUBLIC_MEMORY_API_KEY || 'demo_key'

interface ApiResponse<T> {
  data?: T
  error?: string
}

class ApiClient {
  private baseUrl: string
  private apiKey: string

  constructor() {
    this.baseUrl = API_BASE_URL
    this.apiKey = API_KEY
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      
      const config: RequestInit = {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      }

      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      console.error('API request failed:', error)
      return { error: error instanceof Error ? error.message : 'Unknown error' }
    }
  }

  // Health and status endpoints
  async getHealth(): Promise<ApiResponse<any>> {
    return this.request('/health')
  }

  async getStats(): Promise<ApiResponse<any>> {
    return this.request('/health/stats')
  }

  // Memory endpoints
  async searchMemories(timestamp: string): Promise<ApiResponse<any>> {
    return this.request(`/memory/search?timestamp=${encodeURIComponent(timestamp)}`)
  }

  async getMemory(memoryId: string): Promise<ApiResponse<any>> {
    return this.request(`/memory/${memoryId}`)
  }

  async getMemoryImage(memoryId: string, original = false): Promise<string> {
    const url = `${this.baseUrl}/memory/${memoryId}/image${original ? '?original=true' : ''}`
    return `${url}&api_key=${this.apiKey}`
  }

  async getMemoryThumbnail(memoryId: string, size = 200): Promise<string> {
    const url = `${this.baseUrl}/memory/${memoryId}/thumbnail?size=${size}`
    return `${url}&api_key=${this.apiKey}`
  }

  // Chat endpoints
  async chatWithAssistant(message: string, maxResults = 5): Promise<ApiResponse<any>> {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        include_images: true,
        max_results: maxResults,
      }),
    })
  }

  async getChatSuggestions(): Promise<ApiResponse<any>> {
    return this.request('/chat/suggestions')
  }

  // Capture endpoints
  async simulateCapture(): Promise<ApiResponse<any>> {
    return this.request('/simulate/capture', {
      method: 'POST',
    })
  }

  // Utility methods
  getImageUrl(memoryId: string, original = false): string {
    return this.getMemoryImage(memoryId, original)
  }

  getThumbnailUrl(memoryId: string, size = 200): string {
    return this.getMemoryThumbnail(memoryId, size)
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient()

// Export individual methods for convenience
export const {
  getHealth,
  getStats,
  searchMemories,
  getMemory,
  chatWithAssistant,
  getChatSuggestions,
  simulateCapture,
  getImageUrl,
  getThumbnailUrl,
} = apiClient
