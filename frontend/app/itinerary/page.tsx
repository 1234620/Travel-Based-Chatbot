"use client"

import { useState, useRef, useEffect } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, MapPin, Calendar, Users, Plane, Hotel, Camera, Utensils } from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
  suggestions?: string[]
}

const initialMessages: Message[] = [
  {
    id: "1",
    content:
      "Hello! I'm your AI travel assistant powered by advanced RAG technology. I can help you plan the perfect itinerary for your next adventure using my comprehensive travel database. Where would you like to go?",
    sender: "ai",
    timestamp: new Date(),
    suggestions: [
      "Plan a 7-day trip to Japan",
      "Weekend getaway to Paris",
      "Family vacation to Orlando",
      "Romantic trip to Santorini",
    ],
  },
]

const quickActions = [
  { icon: MapPin, label: "Destinations", color: "bg-blue-500" },
  { icon: Calendar, label: "Dates", color: "bg-green-500" },
  { icon: Users, label: "Travelers", color: "bg-purple-500" },
  { icon: Plane, label: "Flights", color: "bg-orange-500" },
  { icon: Hotel, label: "Hotels", color: "bg-pink-500" },
  { icon: Camera, label: "Activities", color: "bg-indigo-500" },
  { icon: Utensils, label: "Dining", color: "bg-red-500" },
]

export default function ItineraryPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [isConnected, setIsConnected] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsTyping(true)

    try {
      // Call the RAG API
      const response = await fetch('http://127.0.0.1:8000/rag', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Convert query to URL parameter
      })
      
      // Create URL with query parameter
      const url = new URL('http://127.0.0.1:8000/rag')
      url.searchParams.append('query', content)
      
      const ragResponse = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!ragResponse.ok) {
        throw new Error(`HTTP error! status: ${ragResponse.status}`)
      }

      const data = await ragResponse.json()
      
      // Format the RAG response
      let aiContent = data.itinerary || "I'm sorry, I couldn't generate an itinerary at this time."
      
      // If there's an error, show a helpful message
      if (data.error) {
        aiContent = `I encountered an issue: ${data.error}. Here's a general response based on your query: ${generateAIResponse(content)}`
      }

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: aiContent,
        sender: "ai",
        timestamp: new Date(),
        suggestions: generateSuggestions(content),
      }
      
      setMessages((prev) => [...prev, aiResponse])
      setIsConnected(true)
    } catch (error) {
      console.error('Error calling RAG API:', error)
      setIsConnected(false)
      
      // Fallback to mock response if RAG fails
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `I'm having trouble connecting to my travel database right now. ${generateAIResponse(content)}`,
        sender: "ai",
        timestamp: new Date(),
        suggestions: generateSuggestions(content),
      }
      
      setMessages((prev) => [...prev, aiResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase()

    if (input.includes("japan")) {
      return "Japan is an amazing destination! I'd recommend a 7-day itinerary covering Tokyo, Kyoto, and Osaka. You could start in Tokyo for 3 days exploring Shibuya, Asakusa, and modern districts, then take the shinkansen to Kyoto for 2 days of temples and traditional culture, and finish in Osaka for incredible food and nightlife. Would you like me to detail specific attractions and restaurants?"
    } else if (input.includes("paris")) {
      return "Paris is perfect for a romantic getaway! For a weekend trip, I suggest staying in the Marais district. Day 1: Visit the Eiffel Tower, Seine river cruise, and dinner in Montmartre. Day 2: Louvre Museum, stroll through Tuileries Garden, and explore Saint-Germain. Would you like restaurant recommendations or help with booking accommodations?"
    } else if (input.includes("budget")) {
      return "I'd be happy to help you plan within your budget! Could you tell me your approximate budget range and destination preferences? I can suggest cost-effective accommodations, free activities, and budget-friendly dining options."
    } else {
      return "That sounds like a wonderful trip! To create the perfect itinerary for you, I'll need a few more details. What's your travel style - adventure, relaxation, culture, or a mix? Also, what time of year are you planning to travel and what's your approximate budget range?"
    }
  }

  const generateSuggestions = (userInput: string): string[] => {
    const input = userInput.toLowerCase()

    if (input.includes("japan")) {
      return [
        "Show me Tokyo attractions",
        "Best time to visit Japan",
        "Japanese food experiences",
        "Transportation in Japan",
      ]
    } else if (input.includes("paris")) {
      return ["Best Paris neighborhoods", "Museum recommendations", "Romantic dinner spots", "Day trips from Paris"]
    } else {
      return ["What's my budget?", "Best travel dates", "Group or solo travel?", "Activity preferences"]
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion)
  }

  const handleQuickAction = (action: string) => {
    handleSendMessage(`Help me with ${action.toLowerCase()}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5 page-transition">
      <Navigation />

      <div className="container mx-auto px-4 py-8 pt-24">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-4 text-balance">Smart Itinerary Planner</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
            Let our AI travel assistant create the perfect personalized itinerary for your next adventure
          </p>
          {/* Connection Status */}
          <div className="flex items-center justify-center gap-2 mt-4">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? 'Connected to AI Travel Assistant' : 'Using offline mode'}
            </span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap justify-center gap-3 mb-8">
          {quickActions.map((action) => (
            <Button
              key={action.label}
              variant="default"
              size="sm"
              onClick={() => handleQuickAction(action.label)}
              className="flex items-center gap-2 hover:scale-105 transition-transform bg-white/90 text-gray-800 border border-gray-200 hover:bg-white hover:shadow-md"
            >
              <div className={`w-4 h-4 rounded-full ${action.color}`} />
              <action.icon className="w-4 h-4" />
              {action.label}
            </Button>
          ))}
        </div>

        {/* Chat Interface */}
        <Card className="max-w-4xl mx-auto shadow-xl">
          <CardContent className="p-0">
            {/* Messages */}
            <div className="h-[600px] overflow-y-auto p-6 space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
                >
                  <Avatar className="w-10 h-10 flex-shrink-0">
                    <AvatarFallback
                      className={
                        message.sender === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-accent text-accent-foreground"
                      }
                    >
                      {message.sender === "user" ? "U" : "AI"}
                    </AvatarFallback>
                  </Avatar>

                  <div className={`flex-1 max-w-[80%] ${message.sender === "user" ? "text-right" : "text-left"}`}>
                    <div
                      className={`inline-block p-4 rounded-2xl ${
                        message.sender === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>

                    <p className="text-xs text-muted-foreground mt-2">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>

                    {/* Suggestions */}
                    {message.suggestions && message.sender === "ai" && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {message.suggestions.map((suggestion, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex gap-4">
                  <Avatar className="w-10 h-10">
                    <AvatarFallback className="bg-accent text-accent-foreground">AI</AvatarFallback>
                  </Avatar>
                  <div className="bg-muted p-4 rounded-2xl">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                      <div
                        className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      />
                      <div
                        className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-3">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask me anything about your travel plans..."
                  className="flex-1"
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleSendMessage(inputValue)
                    }
                  }}
                />
                <Button
                  onClick={() => handleSendMessage(inputValue)}
                  disabled={!inputValue.trim() || isTyping}
                  className="px-6"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
          <Card className="text-center p-6 card-hover">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Personalized Routes</h3>
            <p className="text-sm text-muted-foreground">
              Get custom itineraries based on your interests and travel style
            </p>
          </Card>

          <Card className="text-center p-6 card-hover">
            <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-6 h-6 text-accent" />
            </div>
            <h3 className="font-semibold mb-2">Smart Scheduling</h3>
            <p className="text-sm text-muted-foreground">
              Optimize your time with intelligent activity scheduling and timing
            </p>
          </Card>

          <Card className="text-center p-6 card-hover">
            <div className="w-12 h-12 bg-orange-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-6 h-6 text-orange-500" />
            </div>
            <h3 className="font-semibold mb-2">Group Planning</h3>
            <p className="text-sm text-muted-foreground">
              Perfect for solo travelers, couples, families, and group adventures
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}
