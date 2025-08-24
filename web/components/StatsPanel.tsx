'use client'

import { useState, useEffect } from 'react'
import { Activity, Database, HardDrive, Clock, TrendingUp } from 'lucide-react'
import { getHealth, getStats } from '@/lib/api'
import { HealthResponse } from '@/types/memory'

export function StatsPanel() {
  const [healthData, setHealthData] = useState<HealthResponse | null>(null)
  const [statsData, setStatsData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const [healthResponse, statsResponse] = await Promise.all([
        getHealth(),
        getStats()
      ])

      if (healthResponse.data) {
        setHealthData(healthResponse.data)
      }
      if (statsResponse.data) {
        setStatsData(statsResponse.data)
      }
      
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100'
      case 'warning':
        return 'text-yellow-600 bg-yellow-100'
      case 'initializing':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return 'Unknown'
    }
  }

  if (isLoading && !healthData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* System Status */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">System Status</h3>
          <Activity className="w-4 h-4 text-gray-400" />
        </div>
        <div className="flex items-center space-x-2">
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(healthData?.status || 'unknown')}`}>
            {healthData?.status || 'Unknown'}
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Last updated: {lastUpdate.toLocaleTimeString()}
        </p>
      </div>

      {/* Memories Count */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Total Memories</h3>
          <Database className="w-4 h-4 text-gray-400" />
        </div>
        <p className="text-2xl font-bold text-gray-900">
          {healthData?.memories_count || 0}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Stored in database
        </p>
      </div>

      {/* Storage Usage */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Storage Usage</h3>
          <HardDrive className="w-4 h-4 text-gray-400" />
        </div>
        <p className="text-2xl font-bold text-gray-900">
          {healthData?.storage_usage_mb ? `${healthData.storage_usage_mb.toFixed(1)} MB` : '0 MB'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Images & data
        </p>
      </div>

      {/* Last Capture */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Last Capture</h3>
          <Clock className="w-4 h-4 text-gray-400" />
        </div>
        <p className="text-lg font-semibold text-gray-900">
          {healthData?.last_capture_time ? formatTimestamp(healthData.last_capture_time) : 'Never'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {healthData?.demo_mode ? 'Demo mode active' : 'Production mode'}
        </p>
      </div>

      {/* Additional Stats (if available) */}
      {statsData && (
        <div className="lg:col-span-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Detailed Statistics</h3>
              <TrendingUp className="w-5 h-5 text-gray-400" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* FAISS Stats */}
              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-2">Vector Database</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Vectors:</span>
                    <span className="text-sm font-medium">{statsData.vector_database?.total_vectors || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Dimension:</span>
                    <span className="text-sm font-medium">{statsData.vector_database?.dimension || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Performance Stats */}
              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-2">Performance</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg Response:</span>
                    <span className="text-sm font-medium">
                      {statsData.performance?.average_response_time_ms || 'N/A'}ms
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Requests/min:</span>
                    <span className="text-sm font-medium">
                      {statsData.performance?.requests_per_minute || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Memory Stats */}
              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-2">Memory Analytics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg per day:</span>
                    <span className="text-sm font-medium">
                      {statsData.memories?.average_per_day || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last capture:</span>
                    <span className="text-sm font-medium">
                      {statsData.memories?.last_capture ? 
                        new Date(statsData.memories.last_capture).toLocaleDateString() : 'N/A'
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
