'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, Mic, MicOff, MessageCircle, Clock, MapPin } from 'lucide-react'
import { chatWithAssistant, getChatSuggestions } from '@/lib/api'
import { Memory, MemoryReference } from '@/types/memory'

interface ChatInterfaceProps {
  onMemorySelect: (memory: Memory) => void
}

interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  memoryReferences?: MemoryReference[]
}

export function ChatInterface({ onMemorySelect }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadSuggestions()
    addWelcomeMessage()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadSuggestions = async () => {
    try {
      const response = await getChatSuggestions()
      if (response.data) {
        setSuggestions(response.data.suggestions || [])
      }
    } catch (error) {
      console.error('Failed to load suggestions:', error)
    }
  }

  const addWelcomeMessage = () => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'assistant',
      content: "Hello! I'm MemoryAid, your AI memory assistant. I can help you find and recall your visual memories. Try asking me something like 'Where did I put my keys?' or 'What happened this morning?'",
      timestamp: new Date(),
    }
    setMessages([welcomeMessage])
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await chatWithAssistant(inputValue)
      
      if (response.data) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: response.data.assistant_message,
          timestamp: new Date(),
          memoryReferences: response.data.memory_references,
        }
        setMessages(prev => [...prev, assistantMessage])
      } else if (response.error) {
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `Sorry, I encountered an error: ${response.error}`,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion)
  }

  const toggleVoiceInput = () => {
    setIsListening(!isListening)
    // TODO: Implement voice input functionality
    alert('Voice input not yet implemented in this demo')
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="card h-[600px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">💬 Memory Assistant</h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleVoiceInput}
            className={`p-2 rounded-lg transition-colors ${
              isListening
                ? 'bg-red-100 text-red-600 hover:bg-red-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={isListening ? 'Stop listening' : 'Start voice input'}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar mb-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                
                {/* Memory References */}
                {message.memoryReferences && message.memoryReferences.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs opacity-80">Related memories:</p>
                    {message.memoryReferences.map((ref) => (
                      <div
                        key={ref.id}
                        className="bg-white bg-opacity-20 rounded p-2 cursor-pointer hover:bg-opacity-30 transition-colors"
                        onClick={() => {
                          // TODO: Fetch full memory and call onMemorySelect
                          console.log('Memory reference clicked:', ref.id)
                        }}
                      >
                        <div className="flex items-center space-x-2 text-xs">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(ref.timestamp).toLocaleString()}</span>
                        </div>
                        <p className="font-medium text-sm mt-1">{ref.title}</p>
                        <p className="text-xs opacity-80 mt-1">{ref.summary}</p>
                        {ref.location && (
                          <div className="flex items-center space-x-1 mt-1">
                            <MapPin className="w-3 h-3" />
                            <span className="text-xs">{ref.location}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="text-xs opacity-60 mt-2">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <MessageCircle className="w-4 h-4 animate-pulse" />
                  <span className="loading-dots">Thinking</span>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.slice(0, 4).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask me about your memories..."
          className="flex-1 input-field"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isLoading}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  )
}
