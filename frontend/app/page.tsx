import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Plane,
  Hotel,
  MapPin,
  Star,
  Clock,
  Shield,
  ArrowRight,
  Globe,
  Heart,
  Search,
  Calendar,
  Users,
  Mail,
  Quote,
  Sparkles,
} from "lucide-react"
import Link from "next/link"
import Image from "next/image"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center hero-bg bg-gray-800 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/40 to-black/60" />

        {/* Floating elements for visual interest */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-20 w-32 h-32 border-2 border-white/20 rounded-full floating" />
          <div
            className="absolute top-40 right-32 w-24 h-24 border-2 border-white/30 rounded-full floating"
            style={{ animationDelay: "1s" }}
          />
          <div
            className="absolute bottom-32 left-1/4 w-40 h-40 border-2 border-white/15 rounded-full floating"
            style={{ animationDelay: "2s" }}
          />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center fade-in">
          <div className="slide-up">
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white mb-6 text-balance drop-shadow-lg">
              Your Journey Starts <span className="text-accent drop-shadow-lg">Here</span>
            </h1>
            <p className="text-xl md:text-2xl text-white/95 mb-12 max-w-3xl mx-auto text-pretty drop-shadow-md">
              Discover amazing destinations, book flights and hotels, and create personalized itineraries with AI
              assistance
            </p>
          </div>

          {/* Quick Search Cards */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-8">
            <Link href="/flights">
              <Card className="bg-black/30 backdrop-blur-md border-white/20 card-hover cursor-pointer group">
                <CardContent className="p-6 text-center">
                  <Plane className="w-12 h-12 text-white mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 drop-shadow-lg" />
                  <h3 className="text-xl font-semibold text-white mb-2 drop-shadow-md">Book Flights</h3>
                  <p className="text-white/90 drop-shadow-sm">Find the best deals on flights worldwide</p>
                </CardContent>
              </Card>
            </Link>

            <Link href="/hotels">
              <Card className="bg-black/30 backdrop-blur-md border-white/20 card-hover cursor-pointer group">
                <CardContent className="p-6 text-center">
                  <Hotel className="w-12 h-12 text-white mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 drop-shadow-lg" />
                  <h3 className="text-xl font-semibold text-white mb-2 drop-shadow-md">Book Hotels</h3>
                  <p className="text-white/90 drop-shadow-sm">Discover perfect accommodations for your stay</p>
                </CardContent>
              </Card>
            </Link>

            <Link href="/itinerary">
              <Card className="bg-black/30 backdrop-blur-md border-white/20 card-hover cursor-pointer group">
                <CardContent className="p-6 text-center">
                  <Sparkles className="w-12 h-12 text-white mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 drop-shadow-lg" />
                  <h3 className="text-xl font-semibold text-white mb-2 drop-shadow-md">AI Itinerary</h3>
                  <p className="text-white/90 drop-shadow-sm">Get personalized travel recommendations</p>
                </CardContent>
              </Card>
            </Link>
          </div>

          <Button size="lg" className="bg-accent hover:bg-accent/90 text-accent-foreground text-lg px-8 py-4">
            Start Planning Your Trip
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Why Choose TripTactix Section */}
      <section className="py-20 section-bg-1 parallax-bg relative">
        <div className="absolute inset-0 bg-white/90" />
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 slide-up">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Why Choose TripTactix?</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Experience the future of travel planning with our AI-powered platform
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Globe,
                title: "Global Coverage",
                desc: "Access to flights and hotels worldwide with competitive prices",
                color: "primary",
              },
              {
                icon: Clock,
                title: "24/7 Support",
                desc: "Round-the-clock customer support for all your travel needs",
                color: "accent",
              },
              {
                icon: Shield,
                title: "Secure Booking",
                desc: "Your data and payments are protected with enterprise-grade security",
                color: "primary",
              },
              {
                icon: Heart,
                title: "Personalized",
                desc: "AI-powered recommendations tailored to your preferences",
                color: "accent",
              },
            ].map((feature, index) => (
              <Card
                key={index}
                className="card-hover bg-card/80 backdrop-blur-sm border-border/50 bounce-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CardContent className="p-6 text-center">
                  <div
                    className={`w-16 h-16 bg-${feature.color}/10 rounded-full flex items-center justify-center mx-auto mb-4`}
                  >
                    <feature.icon className={`w-8 h-8 text-${feature.color}`} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2 text-card-foreground">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Destinations Section */}
      <section className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 slide-up">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Popular Destinations</h2>
            <p className="text-xl text-muted-foreground">Discover the world's most amazing places</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                name: "Tokyo, Japan",
                image: "/tokyo-skyline-with-mount-fuji-in-background-at-sun.jpg",
                price: "From $899",
                rating: 4.8,
                description: "Experience the perfect blend of tradition and modernity",
              },
              {
                name: "Paris, France",
                image: "/eiffel-tower-and-paris-cityscape-at-golden-hour.jpg",
                price: "From $749",
                rating: 4.9,
                description: "The city of love and lights awaits you",
              },
              {
                name: "Bali, Indonesia",
                image: "/bali-rice-terraces-with-traditional-temples.jpg",
                price: "From $599",
                rating: 4.7,
                description: "Tropical paradise with stunning beaches and culture",
              },
              {
                name: "Santorini, Greece",
                image: "/santorini-white-buildings-and-blue-domes-overlooki.jpg",
                price: "From $829",
                rating: 4.9,
                description: "Breathtaking sunsets and Mediterranean charm",
              },
              {
                name: "Dubai, UAE",
                image: "/dubai-modern-skyline-with-burj-khalifa-at-night.jpg",
                price: "From $699",
                rating: 4.6,
                description: "Luxury shopping and architectural marvels",
              },
              {
                name: "Machu Picchu, Peru",
                image: "/machu-picchu-ancient-ruins-in-misty-mountains.jpg",
                price: "From $1299",
                rating: 4.8,
                description: "Ancient wonders in the heart of the Andes",
              },
            ].map((destination, index) => (
              <Card
                key={index}
                className="card-hover overflow-hidden bg-card border-border bounce-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="relative h-48 overflow-hidden">
                  <Image
                    src={destination.image || "/placeholder.svg"}
                    alt={destination.name}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute top-4 right-4">
                    <Badge className="bg-background/90 text-foreground">
                      <Star className="w-3 h-3 mr-1 fill-current text-yellow-500" />
                      {destination.rating}
                    </Badge>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                </div>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-semibold text-card-foreground">{destination.name}</h3>
                    <span className="text-accent font-semibold">{destination.price}</span>
                  </div>
                  <p className="text-muted-foreground">{destination.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 testimonial-bg parallax-bg relative">
        <div className="absolute inset-0 bg-black/60" />
        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 slide-up">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">What Our Travelers Say</h2>
            <p className="text-xl text-white/90">Real experiences from real adventurers</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Johnson",
                location: "New York, USA",
                image: "/happy-female-traveler-with-backpack.jpg",
                rating: 5,
                text: "TripTactix made planning my European adventure so easy! The AI recommendations were spot-on and saved me hours of research.",
              },
              {
                name: "Miguel Rodriguez",
                location: "Barcelona, Spain",
                image: "/smiling-male-traveler-with-camera.jpg",
                rating: 5,
                text: "Best travel platform I've ever used. Found amazing deals and the customer support was incredible when I needed help.",
              },
              {
                name: "Yuki Tanaka",
                location: "Tokyo, Japan",
                image: "/cheerful-asian-female-traveler.jpg",
                rating: 5,
                text: "The personalized itineraries are amazing! Every recommendation was perfect for my interests and budget.",
              },
            ].map((testimonial, index) => (
              <Card
                key={index}
                className="glass-effect border-white/20 bounce-in"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <Image
                      src={testimonial.image || "/placeholder.svg"}
                      alt={testimonial.name}
                      width={60}
                      height={60}
                      className="rounded-full mr-4 object-cover"
                    />
                    <div className="flex-1">
                      <h4 className="font-semibold text-foreground text-base">{testimonial.name}</h4>
                      <p className="text-muted-foreground text-sm">{testimonial.location}</p>
                    </div>
                  </div>
                  <div className="flex mb-3">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <Quote className="w-6 h-6 text-muted-foreground/50 mb-2" />
                  <p className="text-foreground italic leading-relaxed">{testimonial.text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stay Updated Section */}
      <section className="py-20 section-bg-2 parallax-bg relative">
        <div className="absolute inset-0 bg-primary/90" />
        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="slide-up">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Stay Updated</h2>
            <p className="text-xl text-white/90 mb-8">
              Get the latest travel deals, tips, and destination guides delivered to your inbox
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <div className="relative flex-1">
                <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <Input
                  placeholder="Enter your email"
                  className="pl-10 bg-white border-0 text-foreground placeholder:text-gray-500"
                />
              </div>
              <Button size="lg" className="bg-accent hover:bg-accent/90 text-accent-foreground whitespace-nowrap">
                Subscribe Now
              </Button>
            </div>
            <p className="text-white/70 text-sm mt-4">No spam, unsubscribe anytime. We respect your privacy.</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 hero-gradient">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center slide-up">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Ready to Start Your Adventure?</h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of travelers who trust TripTactix for their journey planning
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-accent hover:bg-accent/90 text-accent-foreground text-lg px-8 py-4">
              Book Your Flight
              <Plane className="w-5 h-5 ml-2" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-primary bg-transparent text-lg px-8 py-4"
            >
              Find Hotels
              <Hotel className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Plane className="w-5 h-5 text-primary-foreground" />
                </div>
                <span className="text-xl font-bold text-card-foreground">TripTactix</span>
              </div>
              <p className="text-muted-foreground">Your intelligent travel companion for seamless journey planning.</p>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-card-foreground">Services</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="/flights" className="hover:text-primary transition-colors">
                    Flight Booking
                  </Link>
                </li>
                <li>
                  <Link href="/hotels" className="hover:text-primary transition-colors">
                    Hotel Booking
                  </Link>
                </li>
                <li>
                  <Link href="/itinerary" className="hover:text-primary transition-colors">
                    AI Itinerary
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-card-foreground">Support</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-primary transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-primary transition-colors">
                    Contact Us
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-primary transition-colors">
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-card-foreground">Company</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-primary transition-colors">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-primary transition-colors">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-primary transition-colors">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-border mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2025 TripTactix. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
