'use client'

import { useState } from 'react'
import { X, Clock, MapPin, Eye, Download, Tag, Palette, Users } from 'lucide-react'
import { Memory } from '@/types/memory'
import { getImageUrl, getThumbnailUrl } from '@/lib/api'

interface MemoryModalProps {
  memory: Memory
  isOpen: boolean
  onClose: () => void
}

export function MemoryModal({ memory, isOpen, onClose }: MemoryModalProps) {
  const [selectedImageType, setSelectedImageType] = useState<'compressed' | 'original'>('compressed')
  const [imageError, setImageError] = useState(false)

  if (!isOpen) return null

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return timestamp
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.6) return 'Medium'
    return 'Low'
  }

  const handleImageError = () => {
    setImageError(true)
  }

  const getImageUrl = () => {
    if (selectedImageType === 'original' && memory.original_image_path) {
      return memory.original_image_path
    }
    return memory.compressed_image_path
  }

  const downloadImage = () => {
    const link = document.createElement('a')
    link.href = getImageUrl()
    link.download = `memory_${memory.id}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        ></div>

        {/* Modal content */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{memory.title}</h3>
                <p className="text-sm text-gray-600">Memory ID: {memory.id}</p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Image Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-md font-medium text-gray-900">Image</h4>
                  <div className="flex items-center space-x-2">
                    <select
                      value={selectedImageType}
                      onChange={(e) => setSelectedImageType(e.target.value as 'compressed' | 'original')}
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="compressed">Compressed</option>
                      {memory.original_image_path && (
                        <option value="original">Original</option>
                      )}
                    </select>
                    <button
                      onClick={downloadImage}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      title="Download image"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  {imageError ? (
                    <div className="h-64 bg-gray-100 flex items-center justify-center">
                      <div className="text-center text-gray-500">
                        <Eye className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                        <p>Image not available</p>
                      </div>
                    </div>
                  ) : (
                    <img
                      src={getImageUrl()}
                      alt={memory.title}
                      className="w-full h-64 object-cover"
                      onError={handleImageError}
                    />
                  )}
                </div>

                {/* Image Info */}
                <div className="text-xs text-gray-500 space-y-1">
                  <p>Type: {selectedImageType === 'original' ? 'Original' : 'Compressed'}</p>
                  <p>Path: {getImageUrl()}</p>
                </div>
              </div>

              {/* Details Section */}
              <div className="space-y-4">
                {/* Basic Info */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Memory Details</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {formatTimestamp(memory.timestamp)}
                      </span>
                    </div>
                    
                    {memory.location && (
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{memory.location}</span>
                      </div>
                    )}

                    <div className="flex items-center space-x-2">
                      <Tag className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        Confidence: 
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(memory.confidence)}`}>
                          {getConfidenceText(memory.confidence)} ({Math.round(memory.confidence * 100)}%)
                        </span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">Summary</h4>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {memory.summary}
                  </p>
                </div>

                {/* Detailed Description */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">Detailed Description</h4>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {memory.detailed_description}
                  </p>
                </div>

                {/* Objects Detected */}
                {memory.objects_detected.length > 0 && (
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-2">Objects Detected</h4>
                    <div className="flex flex-wrap gap-2">
                      {memory.objects_detected.map((obj, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {obj}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Colors */}
                {memory.colors.length > 0 && (
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-2">Colors</h4>
                    <div className="flex flex-wrap gap-2">
                      {memory.colors.map((color, index) => (
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

                {/* Activity */}
                {memory.activity && (
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-2">Activity</h4>
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                      {memory.activity}
                    </p>
                  </div>
                )}

                {/* People Count */}
                {memory.people_count !== undefined && (
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-600">
                      People detected: {memory.people_count}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h4 className="text-md font-medium text-gray-900 mb-2">Metadata</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500">
                <div>
                  <p className="font-medium">Created:</p>
                  <p>{formatTimestamp(memory.created_at)}</p>
                </div>
                <div>
                  <p className="font-medium">Updated:</p>
                  <p>{formatTimestamp(memory.updated_at)}</p>
                </div>
                <div>
                  <p className="font-medium">Vector ID:</p>
                  <p>{memory.vector_id || 'N/A'}</p>
                </div>
                <div>
                  <p className="font-medium">Image Path:</p>
                  <p className="truncate" title={memory.image_path}>
                    {memory.image_path}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
            <div className="flex justify-end space-x-3">
              <button
                onClick={onClose}
                className="btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
