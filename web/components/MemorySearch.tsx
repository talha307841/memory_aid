'use client'

import { useState } from 'react'
import { Search, Clock, MapPin, Calendar, Eye } from 'lucide-react'
import { searchMemories } from '@/lib/api'
import { Memory, MemorySearchResult } from '@/types/memory'

interface MemorySearchProps {
  onMemorySelect: (memory: Memory) => void
}

export function MemorySearch({ onMemorySelect }: MemorySearchProps) {
  const [searchTimestamp, setSearchTimestamp] = useState('')
  const [searchResults, setSearchResults] = useState<MemorySearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchTimestamp.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await searchMemories(searchTimestamp)
      
      if (response.data) {
        setSearchResults(response.data.results || [])
      } else if (response.error) {
        setError(response.error)
        setSearchResults([])
      }
    } catch (error) {
      setError('Failed to search memories. Please try again.')
      setSearchResults([])
    } finally {
      setIsLoading(false)
    }
  }

  const getCurrentTimestamp = () => {
    const now = new Date()
    return now.toISOString().slice(0, 16) // YYYY-MM-DDTHH:MM format
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return timestamp
    }
  }

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getSimilarityText = (score: number) => {
    if (score >= 0.8) return 'High'
    if (score >= 0.6) return 'Medium'
    return 'Low'
  }

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">🔍 Search Memories</h2>
        <p className="text-gray-600">
          Search for memories near a specific timestamp. Results are ordered by relevance and time proximity.
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="timestamp" className="block text-sm font-medium text-gray-700 mb-2">
              Search Timestamp
            </label>
            <input
              type="datetime-local"
              id="timestamp"
              value={searchTimestamp}
              onChange={(e) => setSearchTimestamp(e.target.value)}
              className="input-field"
              placeholder="Select date and time"
              max={getCurrentTimestamp()}
            />
            <p className="text-xs text-gray-500 mt-1">
              Select a date and time to search for memories around that period
            </p>
          </div>
          
          <div className="flex items-end">
            <button
              type="submit"
              disabled={!searchTimestamp.trim() || isLoading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Searching...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Search className="w-4 h-4" />
                  <span>Search</span>
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Quick Time Presets */}
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-2">Quick search:</p>
          <div className="flex flex-wrap gap-2">
            {[
              { label: 'Last Hour', hours: 1 },
              { label: 'Last 3 Hours', hours: 3 },
              { label: 'Today', hours: 24 },
              { label: 'Yesterday', hours: 48 }
            ].map((preset) => (
              <button
                key={preset.label}
                type="button"
                onClick={() => {
                  const time = new Date(Date.now() - preset.hours * 60 * 60 * 1000)
                  setSearchTimestamp(time.toISOString().slice(0, 16))
                }}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-full transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Search Results */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Search Results
          {searchResults.length > 0 && (
            <span className="text-sm font-normal text-gray-600 ml-2">
              ({searchResults.length} found)
            </span>
          )}
        </h3>

        {searchResults.length === 0 && !isLoading && !error && (
          <div className="text-center py-8 text-gray-500">
            <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No memories found for the selected timestamp.</p>
            <p className="text-sm">Try adjusting the time or search for a different period.</p>
          </div>
        )}

        {searchResults.length > 0 && (
          <div className="space-y-4">
            {searchResults.map((result) => (
              <div
                key={result.memory.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors cursor-pointer"
                onClick={() => onMemorySelect(result.memory)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">
                      {result.memory.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {result.memory.summary}
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full bg-gray-100 ${getSimilarityColor(result.similarity_score)}`}>
                      {getSimilarityText(result.similarity_score)} Match
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onMemorySelect(result.memory)
                      }}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      title="View details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatTimestamp(result.memory.timestamp)}</span>
                  </div>
                  
                  {result.memory.location && (
                    <div className="flex items-center space-x-1">
                      <MapPin className="w-3 h-3" />
                      <span>{result.memory.location}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{result.timestamp_distance_minutes} min away</span>
                  </div>
                </div>

                {/* Objects and Colors */}
                {(result.memory.objects_detected.length > 0 || result.memory.colors.length > 0) && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex flex-wrap gap-2">
                      {result.memory.objects_detected.slice(0, 3).map((obj, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {obj}
                        </span>
                      ))}
                      {result.memory.colors.slice(0, 3).map((color, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
                        >
                          {color}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
