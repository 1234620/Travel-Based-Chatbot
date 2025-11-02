"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"
import {
  Plane,
  CalendarIcon,
  Users,
  ArrowLeftRight,
  Filter,
  Star,
  Wifi,
  Coffee,
  Utensils,
  Search,
  MapPin,
  Loader2,
  Clock,
  ArrowRight,
} from "lucide-react"

interface Airport {
  code: string
  name: string
  city: string
  country: string
}

const airports: Airport[] = [
  { code: "DEL", name: "Indira Gandhi International Airport", city: "New Delhi", country: "India" },
  { code: "BOM", name: "Chhatrapati Shivaji International Airport", city: "Mumbai", country: "India" },
  { code: "BLR", name: "Kempegowda International Airport", city: "Bangalore", country: "India" },
  { code: "MAA", name: "Chennai International Airport", city: "Chennai", country: "India" },
  { code: "CCU", name: "Netaji Subhas Chandra Bose International Airport", city: "Kolkata", country: "India" },
  { code: "HYD", name: "Rajiv Gandhi International Airport", city: "Hyderabad", country: "India" },
  { code: "GOI", name: "Goa International Airport", city: "Goa", country: "India" },
  { code: "LHR", name: "Heathrow Airport", city: "London", country: "United Kingdom" },
  { code: "JFK", name: "John F. Kennedy International Airport", city: "New York", country: "United States" },
  { code: "DXB", name: "Dubai International Airport", city: "Dubai", country: "United Arab Emirates" },
  { code: "CDG", name: "Charles de Gaulle Airport", city: "Paris", country: "France" },
  { code: "FRA", name: "Frankfurt Airport", city: "Frankfurt", country: "Germany" },
  { code: "SIN", name: "Singapore Changi Airport", city: "Singapore", country: "Singapore" },
]

const mockFlights = [
  {
    id: 1,
    airline: "Air India",
    flightNumber: "AI 131",
    departure: { time: "06:00", airport: "DEL", city: "New Delhi" },
    arrival: { time: "08:30", airport: "BOM", city: "Mumbai" },
    duration: "2h 30m",
    price: 8999,
    stops: "Non-stop",
    aircraft: "Boeing 737",
    amenities: ["wifi", "meals", "entertainment"],
    rating: 4.2,
  },
  {
    id: 2,
    airline: "IndiGo",
    flightNumber: "6E 345",
    departure: { time: "09:15", airport: "DEL", city: "New Delhi" },
    arrival: { time: "11:45", airport: "BOM", city: "Mumbai" },
    duration: "2h 30m",
    price: 6799,
    stops: "Non-stop",
    aircraft: "Airbus A320",
    amenities: ["wifi", "snacks"],
    rating: 4.5,
  },
  {
    id: 3,
    airline: "Vistara",
    flightNumber: "UK 995",
    departure: { time: "14:20", airport: "DEL", city: "New Delhi" },
    arrival: { time: "16:50", airport: "BOM", city: "Mumbai" },
    duration: "2h 30m",
    price: 12999,
    stops: "Non-stop",
    aircraft: "Airbus A321",
    amenities: ["wifi", "meals", "entertainment", "premium"],
    rating: 4.7,
  },
]

export default function FlightsPage() {
  const [tripType, setTripType] = useState<"oneway" | "roundtrip" | "multicity">("roundtrip")
  const [from, setFrom] = useState<Airport | null>(null)
  const [to, setTo] = useState<Airport | null>(null)
  const [departureDate, setDepartureDate] = useState<Date>()  
  const [returnDate, setReturnDate] = useState<Date>()
  const [passengers, setPassengers] = useState({ adults: 1, children: 0, infants: 0 })
  const [showFromDropdown, setShowFromDropdown] = useState(false)
  const [showToDropdown, setShowToDropdown] = useState(false)
  const [showDepartureDateDropdown, setShowDepartureDateDropdown] = useState(false)
  const [showReturnDateDropdown, setShowReturnDateDropdown] = useState(false)
  const [showPassengersDropdown, setShowPassengersDropdown] = useState(false)
  const [fromSearch, setFromSearch] = useState("")
  const [toSearch, setToSearch] = useState("")
  const [showResults, setShowResults] = useState(false)
  const [realFlights, setRealFlights] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const filteredFromAirports = airports.filter(
    (airport) =>
      airport.name.toLowerCase().includes(fromSearch.toLowerCase()) ||
      airport.city.toLowerCase().includes(fromSearch.toLowerCase()) ||
      airport.code.toLowerCase().includes(fromSearch.toLowerCase()),
  )

  const filteredToAirports = airports.filter(
    (airport) =>
      airport.name.toLowerCase().includes(toSearch.toLowerCase()) ||
      airport.city.toLowerCase().includes(toSearch.toLowerCase()) ||
      airport.code.toLowerCase().includes(toSearch.toLowerCase()),
  )

  const handleSearch = async () => {
    if (from && to && departureDate) {
      try {
        setLoading(true)
        setError(null)
        setShowResults(true)
        
        // Call the backend API
        const requestData = {
          origin: from.code,
          destination: to.code,
          departure_date: departureDate.toISOString().split('T')[0],
          return_date: returnDate ? returnDate.toISOString().split('T')[0] : null,
          adults: passengers.adults,
          children: passengers.children,
          infants: passengers.infants
        };
        
        console.log('Sending request to flight search API:', requestData);
        console.log('Request URL:', 'http://127.0.0.1:8000/api/search-flights');
        
        const response = await fetch('http://127.0.0.1:8000/api/search-flights', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData)
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('Flight search results:', data)
        
        if (data.success && data.outbound_flights && data.outbound_flights.length > 0) {
          setRealFlights(data.outbound_flights)
          setError(null)
          console.log('Found flights:', data.outbound_flights.length)
        } else {
          // Show more detailed error information
          const errorMessage = data.error 
            ? `Error: ${data.error}` 
            : `No flights found for ${from?.city} (${from?.code}) to ${to?.city} (${to?.code}) on ${departureDate?.toLocaleDateString()}. Please try different dates or routes.`;
          setError(errorMessage)
          console.error('API returned error or no flights:', data)
          setRealFlights([])
          
          // No fallback to demo data - show real results or no results message
        }
        
      } catch (error) {
        console.error('Error searching flights:', error)
        setError('Failed to search flights. Please check the console for details.')
        setRealFlights([])
        
        // No fallback to demo data - show real error message
      } finally {
        setLoading(false)
      }
    }
  }

  const swapAirports = () => {
    const temp = from
    setFrom(to)
    setTo(temp)
  }

  // Helper function to format real flight data
  const formatFlightData = (flight: any) => {
    const itinerary = flight.itineraries?.[0]
    const segments = itinerary?.segments || []
    const firstSegment = segments[0]
    const lastSegment = segments[segments.length - 1]
    
    // Format duration properly
    const formatDuration = (duration: string) => {
      if (!duration) return 'N/A'
      const match = duration.match(/PT(\d+)H(\d+)M?/)
      if (match) {
        const hours = parseInt(match[1])
        const minutes = parseInt(match[2] || '0')
        if (minutes === 0) {
          return `${hours}h`
        }
        return `${hours}h ${minutes}m`
      }
      return duration.replace('PT', '').replace('H', 'h ').replace('M', 'm')
    }
    
    // Fix price conversion - Amadeus API returns EUR prices
    let displayPrice = flight.price?.total ? parseFloat(flight.price.total) : 0
    let displayCurrency = flight.price?.currency || 'EUR'
    
    // If price seems too high (likely in cents), divide by 100
    if (displayCurrency === 'EUR' && displayPrice > 1000) {
      displayPrice = displayPrice / 100
    }
    
    // Convert EUR to INR (1 EUR ≈ 90 INR)
    if (displayCurrency === 'EUR') {
      displayPrice = Math.round(displayPrice * 90)
      displayCurrency = 'INR'
    }
    
    return {
      id: flight.id,
      airline: flight.validatingAirlineCodes?.[0] || 'Unknown',
      flightNumber: firstSegment ? `${firstSegment.carrierCode} ${firstSegment.number}` : 'N/A',
      departure: {
        time: firstSegment?.departure?.at ? new Date(firstSegment.departure.at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : 'N/A',
        airport: firstSegment?.departure?.iataCode || 'N/A',
        city: from?.city || 'N/A'
      },
      arrival: {
        time: lastSegment?.arrival?.at ? new Date(lastSegment.arrival.at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : 'N/A',
        airport: lastSegment?.arrival?.iataCode || 'N/A',
        city: to?.city || 'N/A'
      },
      duration: formatDuration(itinerary?.duration),
      price: displayPrice,
      currency: displayCurrency,
      stops: segments.length === 1 ? 'Non-stop' : `${segments.length - 1} stop${segments.length > 2 ? 's' : ''}`,
      aircraft: firstSegment?.aircraft?.code || 'N/A',
      amenities: ['wifi', 'meals'], // Default amenities
      rating: 4.0 // Default rating
    }
  }

  return (
    <div className="min-h-screen bg-background page-transition">
      <Navigation />

      {/* Hero Section */}
      <section className="relative pt-16 pb-8 hero-gradient">
        <div className="absolute inset-0 bg-black/20" />
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Find Your Perfect Flight</h1>
          <p className="text-xl text-white/90 mb-8">Search through thousands of flights to get the best deals</p>

          <div className="flex justify-center space-x-8 text-white/80">
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold">500+</span>
              <span>Airlines</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold">10k+</span>
              <span>Routes</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold">24/7</span>
              <span>Support</span>
            </div>
          </div>
        </div>
      </section>

      {/* Search Form */}
      <section className="relative -mt-8 z-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="shadow-2xl">
            <CardContent className="p-6 relative z-30">
              {/* Trip Type Selector */}
              <div className="flex space-x-4 mb-6">
                <Button
                  variant={tripType === "oneway" ? "default" : "outline"}
                  onClick={() => setTripType("oneway")}
                  className="flex items-center space-x-2"
                >
                  <Plane className="w-4 h-4" />
                  <span>One Way</span>
                </Button>
                <Button
                  variant={tripType === "roundtrip" ? "default" : "outline"}
                  onClick={() => setTripType("roundtrip")}
                  className="flex items-center space-x-2"
                >
                  <ArrowLeftRight className="w-4 h-4" />
                  <span>Round Trip</span>
                </Button>
                <Button
                  variant={tripType === "multicity" ? "default" : "outline"}
                  onClick={() => setTripType("multicity")}
                  className="flex items-center space-x-2"
                >
                  <MapPin className="w-4 h-4" />
                  <span>Multi-City</span>
                </Button>
              </div>

              {/* Search Fields */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
                {/* From */}
                <div className="relative">
                  <Label htmlFor="from">From</Label>
                  <Popover open={showFromDropdown} onOpenChange={setShowFromDropdown}>
                    <PopoverTrigger asChild>
                      <Button
                        id="from-button"
                        variant="outline"
                        className="w-full justify-start text-left font-normal h-12 mt-1 bg-transparent"
                        type="button"
                        onClick={() => setShowFromDropdown(true)}
                      >
                        <Plane className="w-4 h-4 mr-2 text-primary" />
                        {from ? (
                          <div>
                            <div className="font-semibold">{from.code}</div>
                            <div className="text-xs text-muted-foreground">{from.city}</div>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">Select departure</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80 p-0" align="start">
                      <div className="p-3 border-b">
                        <div className="relative">
                          <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
                          <Input
                            placeholder="Search airports..."
                            value={fromSearch}
                            onChange={(e) => setFromSearch(e.target.value)}
                            className="pl-10"
                          />
                        </div>
                      </div>
                      <div className="max-h-60 overflow-y-auto">
                        {filteredFromAirports.map((airport) => (
                          <div
                            key={airport.code}
                            className="flex items-center p-3 hover:bg-muted cursor-pointer"
                            onClick={() => {
                              setFrom(airport)
                              setShowFromDropdown(false)
                              setFromSearch("")
                            }}
                          >
                            <MapPin className="w-5 h-5 text-primary mr-3" />
                            <div className="flex-1">
                              <div className="font-semibold text-sm">{airport.code}</div>
                              <div className="text-xs text-muted-foreground">{airport.city}, {airport.country}</div>
                              <div className="text-xs text-muted-foreground">{airport.name}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>

                {/* Swap Button */}
                <div className="flex items-end justify-center">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={swapAirports}
                    className="h-12 w-12 rounded-full bg-transparent"
                  >
                    <ArrowLeftRight className="w-4 h-4" />
                  </Button>
                </div>

                {/* To */}
                <div className="relative">
                  <Label htmlFor="to">To</Label>
                  <Popover open={showToDropdown} onOpenChange={setShowToDropdown}>
                    <PopoverTrigger asChild>
                      <Button
                        id="to-button"
                        variant="outline"
                        className="w-full justify-start text-left font-normal h-12 mt-1 bg-transparent"
                        type="button"
                        onClick={() => setShowToDropdown(true)}
                      >
                        <Plane className="w-4 h-4 mr-2 text-primary rotate-90" />
                        {to ? (
                          <div>
                            <div className="font-semibold">{to.code}</div>
                            <div className="text-xs text-muted-foreground">{to.city}</div>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">Select destination</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80 p-0" align="start">
                      <div className="p-3 border-b">
                        <div className="relative">
                          <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
                          <Input
                            placeholder="Search airports..."
                            value={toSearch}
                            onChange={(e) => setToSearch(e.target.value)}
                            className="pl-10"
                          />
                        </div>
                      </div>
                      <div className="max-h-60 overflow-y-auto">
                        {filteredToAirports.map((airport) => (
                          <div
                            key={airport.code}
                            className="flex items-center p-3 hover:bg-muted cursor-pointer"
                            onClick={() => {
                              setTo(airport)
                              setShowToDropdown(false)
                              setToSearch("")
                            }}
                          >
                            <MapPin className="w-5 h-5 text-primary mr-3" />
                            <div className="flex-1">
                              <div className="font-semibold text-sm">{airport.code}</div>
                              <div className="text-xs text-muted-foreground">{airport.city}, {airport.country}</div>
                              <div className="text-xs text-muted-foreground">{airport.name}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>

                {/* Departure Date */}
                <div>
                  <Label>Departure</Label>
                  <Popover open={showDepartureDateDropdown} onOpenChange={setShowDepartureDateDropdown}>
                    <PopoverTrigger asChild>
                      <Button
                        id="departure-date-button"
                        variant="outline"
                        className="w-full justify-start text-left font-normal h-12 mt-1 bg-transparent"
                        type="button"
                        onClick={() => setShowDepartureDateDropdown(true)}
                      >
                        <CalendarIcon className="w-4 h-4 mr-2 text-primary" />
                        {departureDate ? format(departureDate, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={departureDate}
                        onSelect={(date) => {
                          setDepartureDate(date);
                          setShowDepartureDateDropdown(false);
                          // If return date is before departure date, clear it
                          if (returnDate && date && returnDate < date) {
                            setReturnDate(undefined);
                          }
                        }}
                        disabled={(date) => {
                          const today = new Date();
                          today.setHours(0, 0, 0, 0);
                          return date < today;
                        }}
                        initialFocus
                        className="rounded-md border"
                      />
                      <div className="p-3 border-t flex justify-between">
                        <Button variant="outline" size="sm" onClick={() => setDepartureDate(undefined)}>Clear</Button>
                        <Button variant="outline" size="sm" onClick={() => setDepartureDate(new Date())}>Today</Button>
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>

                {/* Return Date */}
                {tripType === "roundtrip" && (
                  <div>
                    <Label>Return</Label>
                    <Popover open={showReturnDateDropdown} onOpenChange={setShowReturnDateDropdown}>
                      <PopoverTrigger asChild>
                        <Button
                          id="return-date-button"
                          variant="outline"
                          className="w-full justify-start text-left font-normal h-12 mt-1 bg-transparent"
                          type="button"
                          onClick={() => setShowReturnDateDropdown(true)}
                        >
                          <CalendarIcon className="w-4 h-4 mr-2 text-primary" />
                          {returnDate ? format(returnDate, "PPP") : <span>Pick a date</span>}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={returnDate}
                          onSelect={(date) => {
                            setReturnDate(date);
                            setShowReturnDateDropdown(false);
                          }}
                          disabled={(date) => {
                            const today = new Date();
                            today.setHours(0, 0, 0, 0);
                            return date < (departureDate || today);
                          }}
                          initialFocus
                          className="rounded-md border"
                        />
                        <div className="p-3 border-t flex justify-between">
                          <Button variant="outline" size="sm" onClick={() => setReturnDate(undefined)}>Clear</Button>
                          <Button variant="outline" size="sm" onClick={() => setReturnDate(new Date())}>Today</Button>
                        </div>
                      </PopoverContent>
                    </Popover>
                  </div>
                )}

                {/* Passengers */}
                <div>
                  <Label>Passengers</Label>
                  <Popover open={showPassengersDropdown} onOpenChange={setShowPassengersDropdown}>
                    <PopoverTrigger asChild>
                      <Button
                        id="passengers-button"
                        variant="outline"
                        className="w-full justify-start text-left font-normal h-12 mt-1 bg-transparent"
                        type="button"
                        onClick={() => setShowPassengersDropdown(true)}
                      >
                        <Users className="w-4 h-4 mr-2 text-primary" />
                        <span>
                          {passengers.adults + passengers.children + passengers.infants} Passenger
                          {passengers.adults + passengers.children + passengers.infants > 1 ? "s" : ""}
                        </span>
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80" align="start">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">Adults</div>
                            <div className="text-sm text-muted-foreground">Age 12+ years</div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                setPassengers((prev) => ({
                                  ...prev,
                                  adults: Math.max(1, prev.adults - 1),
                                }))
                              }
                              disabled={passengers.adults <= 1}
                            >
                              -
                            </Button>
                            <span className="w-8 text-center">{passengers.adults}</span>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setPassengers((prev) => ({ ...prev, adults: prev.adults + 1 }))}
                            >
                              +
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">Children</div>
                            <div className="text-sm text-muted-foreground">Age 2-11 years</div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                setPassengers((prev) => ({
                                  ...prev,
                                  children: Math.max(0, prev.children - 1),
                                }))
                              }
                              disabled={passengers.children <= 0}
                            >
                              -
                            </Button>
                            <span className="w-8 text-center">{passengers.children}</span>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setPassengers((prev) => ({ ...prev, children: prev.children + 1 }))}
                            >
                              +
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">Infants</div>
                            <div className="text-sm text-muted-foreground">Under 2 years</div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                setPassengers((prev) => ({
                                  ...prev,
                                  infants: Math.max(0, prev.infants - 1),
                                }))
                              }
                              disabled={passengers.infants <= 0}
                            >
                              -
                            </Button>
                            <span className="w-8 text-center">{passengers.infants}</span>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setPassengers((prev) => ({ ...prev, infants: prev.infants + 1 }))}
                            >
                              +
                            </Button>
                          </div>
                        </div>
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              {/* Search Button */}
              <div className="flex justify-center">
                <Button
                  size="lg"
                  onClick={handleSearch}
                  disabled={loading || !from || !to || !departureDate}
                  className="bg-accent hover:bg-accent/90 text-accent-foreground px-12"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5 mr-2" />
                  )}
                  {loading ? 'Searching...' : 'Search Flights'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Featured Flights Section */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2">Popular Flight Routes</h2>
            <p className="text-muted-foreground">Great deals on trending destinations</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { from: "Delhi", to: "Mumbai", duration: "2h 30m", price: "3,999", discount: "15% OFF" },
              { from: "Mumbai", to: "Dubai", duration: "3h 15m", price: "12,999", discount: "20% OFF" },
              { from: "Bangalore", to: "Singapore", duration: "4h 30m", price: "15,999", discount: "10% OFF" },
              { from: "Delhi", to: "London", duration: "9h 45m", price: "35,999", discount: "25% OFF" },
              { from: "Mumbai", to: "New York", duration: "15h 30m", price: "45,999", discount: "30% OFF" },
              { from: "Chennai", to: "Bangkok", duration: "3h 45m", price: "8,999", discount: "18% OFF" },
            ].map((route, index) => (
              <Card key={index} className="card-hover relative overflow-hidden">
                <div className="absolute top-4 right-4">
                  <Badge className="bg-red-500 text-white">{route.discount}</Badge>
                </div>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{route.from}</div>
                      <div className="text-sm text-muted-foreground">Departure</div>
                    </div>
                    <div className="flex-1 flex items-center justify-center px-4">
                      <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                        <Plane className="w-6 h-6 text-primary" />
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{route.to}</div>
                      <div className="text-sm text-muted-foreground">Arrival</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-center mb-4 text-muted-foreground">
                    <Clock className="w-4 h-4 mr-2" />
                    <span>{route.duration}</span>
                  </div>
                  
                  <div className="text-center mb-4">
                    <div className="text-sm text-muted-foreground mb-1">Starting from</div>
                    <div className="text-3xl font-bold text-primary">₹{route.price}</div>
                  </div>
                  
                  <Button 
                    className="w-full bg-white hover:bg-gray-50 text-primary border border-primary"
                    onClick={() => {
                      // Auto-fill the search form with this route
                      const fromAirport = airports.find(a => a.city === route.from);
                      const toAirport = airports.find(a => a.city === route.to);
                      if (fromAirport) setFrom(fromAirport);
                      if (toAirport) setTo(toAirport);
                      // Scroll to search form
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Search Flights
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Results Section */}
      {showResults && (
        <section className="py-12">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Filters */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">
                {from?.city} to {to?.city} Flights
              </h2>
              <Button variant="outline" className="flex items-center space-x-2 bg-transparent">
                <Filter className="w-4 h-4" />
                <span>Filters</span>
              </Button>
            </div>

            {/* Filter Chips */}
            <div className="flex flex-wrap gap-2 mb-6">
              <Badge variant="secondary" className="px-3 py-1">
                Price: ₹5,000 - ₹15,000
              </Badge>
              <Badge variant="secondary" className="px-3 py-1">
                Duration: Up to 4h
              </Badge>
              <Badge variant="secondary" className="px-3 py-1">
                Airlines (3)
              </Badge>
              <Badge variant="secondary" className="px-3 py-1">
                Non-stop
              </Badge>
            </div>

            {/* Flight Results */}
            <div className="space-y-4">
              {loading && (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                  <div className="text-lg">Searching for flights...</div>
                  <div className="text-sm text-muted-foreground mt-2">Please wait while we find the best options for you</div>
                </div>
              )}
              
              {error && (
                <div className="text-center py-8">
                  <div className="text-lg text-red-500 mb-4">{error}</div>
                  <div className="text-sm text-muted-foreground max-w-md mx-auto">
                    <p className="mb-2">💡 <strong>Try these suggestions:</strong></p>
                    <ul className="text-left space-y-1">
                      <li>• Try different dates (flights may not be available on all dates)</li>
                      <li>• Search popular routes like Delhi ↔ Mumbai or Mumbai ↔ Bangalore</li>
                      <li>• Check if the route has regular flights available</li>
                      <li>• Some international routes may have limited availability</li>
                    </ul>
                  </div>
                </div>
              )}
              
              {!loading && !error && realFlights.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-lg">No flights found. Try different dates or routes.</div>
                </div>
              )}
              
              {!loading && !error && realFlights.length > 0 && realFlights.map((flight) => {
                const formattedFlight = formatFlightData(flight)
                return (
                <Card key={formattedFlight.id} className="card-hover">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-6">
                        {/* Airline Info */}
                        <div className="text-center">
                          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-2">
                            <Plane className="w-6 h-6 text-primary" />
                          </div>
                          <div className="text-sm font-medium">{formattedFlight.airline}</div>
                          <div className="text-xs text-muted-foreground">{formattedFlight.flightNumber}</div>
                        </div>

                        {/* Flight Details */}
                        <div className="flex items-center space-x-8">
                          <div className="text-center">
                            <div className="text-2xl font-bold">{formattedFlight.departure.time}</div>
                            <div className="text-sm text-muted-foreground">{formattedFlight.departure.airport}</div>
                            <div className="text-xs text-muted-foreground">{formattedFlight.departure.city}</div>
                          </div>

                          <div className="flex flex-col items-center">
                            <div className="text-sm text-muted-foreground mb-1">{formattedFlight.duration}</div>
                            <div className="w-24 h-px bg-border relative">
                              <Plane className="w-4 h-4 absolute -top-2 left-1/2 transform -translate-x-1/2 text-primary" />
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">{formattedFlight.stops}</div>
                          </div>

                          <div className="text-center">
                            <div className="text-2xl font-bold">{formattedFlight.arrival.time}</div>
                            <div className="text-sm text-muted-foreground">{formattedFlight.arrival.airport}</div>
                            <div className="text-xs text-muted-foreground">{formattedFlight.arrival.city}</div>
                          </div>
                        </div>
                      </div>

                      {/* Price and Book */}
                      <div className="text-right">
                        <div className="text-3xl font-bold text-accent mb-1">{formattedFlight.currency} {formattedFlight.price.toLocaleString()}</div>
                        <div className="text-sm text-muted-foreground mb-3">per person</div>
                        <Button className="bg-accent hover:bg-accent/90 text-accent-foreground">Book Now</Button>
                      </div>
                    </div>

                    <Separator className="my-4" />

                    {/* Additional Info */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <span className="text-sm">{formattedFlight.rating}</span>
                        </div>
                        <div className="text-sm text-muted-foreground">{formattedFlight.aircraft}</div>
                        <div className="flex items-center space-x-2">
                          {formattedFlight.amenities.includes("wifi") && <Wifi className="w-4 h-4 text-muted-foreground" />}
                          {formattedFlight.amenities.includes("meals") && <Utensils className="w-4 h-4 text-muted-foreground" />}
                          {formattedFlight.amenities.includes("entertainment") && (
                            <Coffee className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                )
              })}
            </div>
          </div>
        </section>
      )}
    </div>
  )
}