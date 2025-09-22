"use client"

import Link from "next/link"
import { useState, useEffect } from "react"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Plane, Hotel, MapPin, Menu, X } from "lucide-react"

export function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const isActive = (path: string) => pathname === path

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? "bg-background/95 backdrop-blur-md shadow-sm" : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Plane className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className={`text-xl font-bold transition-colors ${isScrolled ? "text-foreground" : "text-white"}`}>
              TravelAI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              href="/flights"
              className={`flex items-center space-x-2 hover:text-primary transition-colors tab-transition flights-effect px-3 py-2 rounded-lg ${
                isScrolled ? "text-foreground" : "text-white"
              } ${isActive("/flights") ? "bg-primary/80 text-white font-semibold shadow-lg" : ""}`}
            >
              <Plane className="w-4 h-4" />
              <span>Flights</span>
            </Link>
            <Link
              href="/hotels"
              className={`flex items-center space-x-2 hover:text-primary transition-colors tab-transition hotels-effect px-3 py-2 rounded-lg ${
                isScrolled ? "text-foreground" : "text-white"
              } ${isActive("/hotels") ? "bg-primary/80 text-white font-semibold shadow-lg" : ""}`}
            >
              <Hotel className="w-4 h-4" />
              <span>Hotels</span>
            </Link>
            <Link
              href="/itinerary"
              className={`flex items-center space-x-2 hover:text-primary transition-colors tab-transition px-3 py-2 rounded-lg ${
                isScrolled ? "text-foreground" : "text-white"
              } ${isActive("/itinerary") ? "bg-primary/80 text-white font-semibold shadow-lg" : ""}`}
            >
              <MapPin className="w-4 h-4" />
              <span>Itinerary</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="sm"
            className={`md:hidden ${isScrolled ? "text-foreground" : "text-white"}`}
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-background/95 backdrop-blur-md border-t border-border">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <Link
                href="/flights"
                className={`flex items-center space-x-2 px-3 py-2 text-foreground hover:text-primary transition-colors tab-transition flights-effect rounded-lg ${
                  isActive("/flights") ? "bg-primary/80 text-white font-semibold shadow-lg" : ""
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Plane className="w-4 h-4" />
                <span>Flights</span>
              </Link>
              <Link
                href="/hotels"
                className={`flex items-center space-x-2 px-3 py-2 text-foreground hover:text-primary transition-colors tab-transition hotels-effect rounded-lg ${
                  isActive("/hotels") ? "bg-primary/80 text-white font-semibold shadow-lg" : ""
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Hotel className="w-4 h-4" />
                <span>Hotels</span>
              </Link>
              <Link
                href="/itinerary"
                className={`flex items-center space-x-2 px-3 py-2 text-foreground hover:text-primary transition-colors tab-transition rounded-lg ${
                  isActive("/itinerary") ? "bg-primary/80 text-white font-semibold shadow-lg" : ""
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <MapPin className="w-4 h-4" />
                <span>Itinerary</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
