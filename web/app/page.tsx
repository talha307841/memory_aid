'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/Header'
import { ChatInterface } from '@/components/ChatInterface'
import { MemorySearch } from '@/components/MemorySearch'
import { CaptureControl } from '@/components/CaptureControl'
import { StatsPanel } from '@/components/StatsPanel'
import { MemoryModal } from '@/components/MemoryModal'
import { Memory } from '@/types/memory'

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'search' | 'capture'>('chat')
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleMemorySelect = (memory: Memory) => {
    setSelectedMemory(memory)
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setSelectedMemory(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm mb-6">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'chat'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            💬 Chat Assistant
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'search'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            🔍 Search Memories
          </button>
          <button
            onClick={() => setActiveTab('capture')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'capture'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            📸 Capture Control
          </button>
        </div>

        {/* Stats Panel */}
        <StatsPanel />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Interface */}
          <div className="lg:col-span-2">
            {activeTab === 'chat' && (
              <ChatInterface onMemorySelect={handleMemorySelect} />
            )}
            {activeTab === 'search' && (
              <MemorySearch onMemorySelect={handleMemorySelect} />
            )}
            {activeTab === 'capture' && (
              <CaptureControl />
            )}
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => setActiveTab('capture')}
                  className="w-full btn-primary"
                >
                  📸 Simulate Capture
                </button>
                <button
                  onClick={() => setActiveTab('search')}
                  className="w-full btn-secondary"
                >
                  🔍 Search by Time
                </button>
                <button
                  onClick={() => setActiveTab('chat')}
                  className="w-full btn-secondary"
                >
                  💬 Ask Assistant
                </button>
              </div>
            </div>

            {/* Demo Info */}
            <div className="card bg-blue-50 border-blue-200">
              <h3 className="text-lg font-semibold mb-2 text-blue-800">Demo Mode</h3>
              <p className="text-blue-700 text-sm">
                This is a demonstration of MemoryAid. The system automatically creates
                simulated photo captures and processes them with AI.
              </p>
              <div className="mt-3 text-xs text-blue-600">
                <p>• Captures every 30 seconds</p>
                <p>• AI-powered image analysis</p>
                <p>• Vector-based memory search</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Memory Modal */}
      {isModalOpen && selectedMemory && (
        <MemoryModal
          memory={selectedMemory}
          isOpen={isModalOpen}
          onClose={closeModal}
        />
      )}
    </div>
  )
}
