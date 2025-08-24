'use client'

import { useState } from 'react'
import { Camera, Play, Pause, RotateCcw, Settings, Clock, Activity } from 'lucide-react'
import { simulateCapture } from '@/lib/api'

export function CaptureControl() {
  const [isCapturing, setIsCapturing] = useState(false)
  const [lastCapture, setLastCapture] = useState<Date | null>(null)
  const [captureHistory, setCaptureHistory] = useState<Array<{ id: string; timestamp: Date; status: 'success' | 'error' }>>([])
  const [autoCaptureEnabled, setAutoCaptureEnabled] = useState(false)
  const [captureInterval, setCaptureInterval] = useState(30)

  const handleManualCapture = async () => {
    if (isCapturing) return

    setIsCapturing(true)
    
    try {
      const response = await simulateCapture()
      
      if (response.data) {
        const capture = {
          id: response.data.memory_id,
          timestamp: new Date(),
          status: 'success' as const
        }
        
        setCaptureHistory(prev => [capture, ...prev.slice(0, 9)]) // Keep last 10
        setLastCapture(new Date())
        
        // Show success message
        alert(`Capture successful! Memory ID: ${response.data.memory_id}`)
      } else {
        throw new Error(response.error || 'Capture failed')
      }
    } catch (error) {
      const capture = {
        id: `error_${Date.now()}`,
        timestamp: new Date(),
        status: 'error' as const
      }
      
      setCaptureHistory(prev => [capture, ...prev.slice(0, 9)])
      alert(`Capture failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsCapturing(false)
    }
  }

  const toggleAutoCapture = () => {
    setAutoCaptureEnabled(!autoCaptureEnabled)
    // In a real implementation, this would communicate with the backend
    alert(`Auto-capture ${!autoCaptureEnabled ? 'enabled' : 'disabled'}. This is a demo - the backend handles the actual scheduling.`)
  }

  const resetCaptureHistory = () => {
    setCaptureHistory([])
    setLastCapture(null)
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleString()
  }

  const getTimeSinceLastCapture = () => {
    if (!lastCapture) return 'Never'
    
    const now = new Date()
    const diffMs = now.getTime() - lastCapture.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hours ago`
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} days ago`
  }

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">📸 Capture Control</h2>
        <p className="text-gray-600">
          Manually trigger memory captures and monitor the capture system. In demo mode, 
          the system automatically captures memories every 30 seconds.
        </p>
      </div>

      {/* Capture Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Manual Capture */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Manual Capture</h3>
          
          <button
            onClick={handleManualCapture}
            disabled={isCapturing}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed h-16 text-lg"
          >
            {isCapturing ? (
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Capturing...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Camera className="w-6 h-6" />
                <span>Simulate Capture</span>
              </div>
            )}
          </button>

          <div className="text-center">
            <p className="text-sm text-gray-600">Last capture:</p>
            <p className="text-lg font-semibold text-gray-900">
              {getTimeSinceLastCapture()}
            </p>
          </div>
        </div>

        {/* Auto Capture Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Auto Capture</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${autoCaptureEnabled ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                <span className="text-sm font-medium">
                  {autoCaptureEnabled ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Interval:</span>
              <span className="text-sm font-medium">{captureInterval} seconds</span>
            </div>

            <button
              onClick={toggleAutoCapture}
              className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                autoCaptureEnabled
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : 'bg-green-100 text-green-700 hover:bg-green-200'
              }`}
            >
              {autoCaptureEnabled ? (
                <div className="flex items-center justify-center space-x-2">
                  <Pause className="w-4 h-4" />
                  <span>Stop Auto-Capture</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Play className="w-4 h-4" />
                  <span>Start Auto-Capture</span>
                </div>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Capture History */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Capture History</h3>
          <button
            onClick={resetCaptureHistory}
            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Clear</span>
          </button>
        </div>

        {captureHistory.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Camera className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No captures yet.</p>
            <p className="text-sm">Trigger a manual capture to see history.</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
            {captureHistory.map((capture) => (
              <div
                key={capture.id}
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  capture.status === 'success'
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      capture.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  ></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {capture.status === 'success' ? 'Capture Successful' : 'Capture Failed'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatTimestamp(capture.timestamp)}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-xs font-mono text-gray-600">
                    {capture.id.length > 20 ? `${capture.id.slice(0, 20)}...` : capture.id}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Demo Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-800 mb-1">Demo Mode Active</h4>
            <p className="text-sm text-blue-700 mb-2">
              The backend automatically simulates photo captures every 30 seconds. 
              You can also manually trigger captures using the button above.
            </p>
            <div className="text-xs text-blue-600 space-y-1">
              <p>• Automatic captures: Every 30 seconds</p>
              <p>• Manual triggers: Instant simulation</p>
              <p>• AI processing: OpenAI Vision + Embeddings</p>
              <p>• Storage: Local filesystem + FAISS vectors</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
