'use client'

import { useState } from 'react'
import { Brain, Menu, X, Settings, Info } from 'lucide-react'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">MemoryAid</h1>
              <p className="text-sm text-gray-600">AI-Powered Memory Assistant</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a
              href="#features"
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              Features
            </a>
            <a
              href="#demo"
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              Demo
            </a>
            <a
              href="#about"
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              About
            </a>
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Demo badge */}
            <div className="hidden sm:flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              🚀 Demo Mode
            </div>

            {/* Settings button */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Settings className="w-5 h-5" />
            </button>

            {/* Info button */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Info className="w-5 h-5" />
            </button>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-4">
              <a
                href="#features"
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium px-2 py-1"
                onClick={() => setIsMenuOpen(false)}
              >
                Features
              </a>
              <a
                href="#demo"
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium px-2 py-1"
                onClick={() => setIsMenuOpen(false)}
              >
                Demo
              </a>
              <a
                href="#about"
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium px-2 py-1"
                onClick={() => setIsMenuOpen(false)}
              >
                About
              </a>
            </nav>
            
            {/* Mobile demo badge */}
            <div className="mt-4 flex items-center px-3 py-2 bg-green-100 text-green-800 rounded-lg text-sm font-medium">
              🚀 Demo Mode Active
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
