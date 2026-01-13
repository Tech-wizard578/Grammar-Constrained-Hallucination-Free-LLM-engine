import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { DocumentManager } from "./DocumentManager";
import { useHeaderScroll } from "@/hooks/useScrollAnimation";

/**
 * Header - 8bit.ai style minimalist header
 * Features: Fixed position, logo on left, hamburger on right
 */
export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const headerRef = useHeaderScroll();

  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      {/* Fixed Header - 8bit.ai Style */}
      <header ref={headerRef} className="fixed top-0 left-0 right-0 z-50 transition-colors duration-300">
        <div className="container mx-auto px-6 lg:px-10 h-20 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 pointer-events-auto">
            <span className="sr-only">HallucinationFree AI</span>
            <h1 className="text-base md:text-lg font-light text-white tracking-tight">
              HallucinationFree<span className="text-[#00aaff]">.ai</span>
            </h1>
          </Link>

          {/* Desktop: Document Manager */}
          <div className="hidden md:flex items-center gap-6">
            <DocumentManager />
          </div>

          {/* Hamburger Menu Button */}
          <button
            className="relative z-50 w-11 h-11 flex flex-col items-center justify-center gap-2 pointer-events-auto"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menu"
          >
            <span 
              className={`hamburger-line transition-transform ${menuOpen ? 'rotate-45 translate-y-[5px]' : ''}`} 
            />
            <span 
              className={`hamburger-line transition-transform ${menuOpen ? '-rotate-45 -translate-y-[5px]' : ''}`} 
            />
          </button>
        </div>
      </header>

      {/* Full-Screen Overlay Menu */}
      <div 
        className={`fixed inset-0 z-40 bg-black/98 backdrop-blur-xl transition-all duration-500 ${
          menuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
      >
        <div className="container mx-auto px-6 lg:px-10 pt-32 pb-12 h-full flex flex-col">
          {/* Navigation Links */}
          <nav className="flex-1 space-y-2">
            <Link 
              to="/" 
              className={`block text-5xl md:text-7xl font-light transition-colors duration-300 ${
                isActive("/") ? "text-[#00aaff]" : "text-white/40 hover:text-white"
              }`}
              onClick={() => setMenuOpen(false)}
            >
              Home
            </Link>
            <Link 
              to="/about" 
              className={`block text-5xl md:text-7xl font-light transition-colors duration-300 ${
                isActive("/about") ? "text-[#00aaff]" : "text-white/40 hover:text-white"
              }`}
              onClick={() => setMenuOpen(false)}
            >
              About
            </Link>
            <Link 
              to="/contact" 
              className={`block text-5xl md:text-7xl font-light transition-colors duration-300 ${
                isActive("/contact") ? "text-[#00aaff]" : "text-white/40 hover:text-white"
              }`}
              onClick={() => setMenuOpen(false)}
            >
              Contact
            </Link>
          </nav>

          {/* Footer in Menu */}
          <div className="pt-8 border-t border-white/10">
            <p className="text-sm text-white/40">
              © 2026 HallucinationFree AI. All Rights Reserved.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
