import { useState } from "react";
import { Header } from "@/components/Header";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { Mail, MapPin, Send, Loader2, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { submitContactForm } from "@/lib/api";

export default function Contact() {
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { toast } = useToast();

  // Scroll animations
  const heroRef = useScrollAnimation<HTMLDivElement>({ type: "reveal", duration: 1 });
  const formRef = useScrollAnimation<HTMLDivElement>({ 
    type: "slideUp", 
    staggerSelector: ".form-field",
    stagger: 0.1,
    delay: 0.2
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Submit to backend API
      const response = await submitContactForm(formData);
      console.log("Message submitted:", response);
      
      toast({
        title: "Message sent!",
        description: "Thank you for reaching out. We'll get back to you soon.",
      });
      
      setFormData({ name: "", email: "", message: "" });
      setSubmitted(true);
      
      // Reset success state after 5 seconds
      setTimeout(() => setSubmitted(false), 5000);
      
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to send message";
      toast({
        title: "Failed to send",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-[#00aaff]/30 selection:text-white">
      <AnimatedBackground />
      <Header />

      <main className="relative z-10 container mx-auto px-6 lg:px-10 pt-32 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          {/* Left: Info */}
          <div ref={heroRef}>
            <p className="hero-overline mb-4">Contact</p>
            <h1 className="hero-title text-white mb-8">
              Get In<br />
              <span className="text-[#00aaff]">Touch</span>
            </h1>
            <p className="text-lg text-white/50 font-light leading-relaxed mb-12">
              Have questions about the Hallucination-Free Engine? 
              Want to integrate it into your enterprise? Let us know.
            </p>

            {/* Contact Info */}
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 border border-white/10 flex items-center justify-center">
                  <Mail className="w-5 h-5 text-[#00aaff]" />
                </div>
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Email</p>
                  <p className="text-white/80">aasheerwad009@gmail.com</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-12 h-12 border border-white/10 flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-[#00aaff]" />
                </div>
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Location</p>
                  <p className="text-white/80">Remote / Worldwide</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Form */}
          <div ref={formRef}>
            {submitted ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-16">
                <CheckCircle className="w-16 h-16 text-green-400 mb-6" />
                <h3 className="text-2xl font-light text-white mb-2">Message Sent!</h3>
                <p className="text-white/50">We'll get back to you as soon as possible.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="form-field">
                  <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="w-full bg-transparent border border-white/10 px-4 py-3 text-white placeholder:text-white/25 focus:outline-none focus:border-[#00aaff]/50 transition-colors"
                    placeholder="Your name"
                  />
                </div>

                <div className="form-field">
                  <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    className="w-full bg-transparent border border-white/10 px-4 py-3 text-white placeholder:text-white/25 focus:outline-none focus:border-[#00aaff]/50 transition-colors"
                    placeholder="your@email.com"
                  />
                </div>

                <div className="form-field">
                  <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                    Message
                  </label>
                  <textarea
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    required
                    rows={5}
                    className="w-full bg-transparent border border-white/10 px-4 py-3 text-white placeholder:text-white/25 focus:outline-none focus:border-[#00aaff]/50 transition-colors resize-none"
                    placeholder="How can we help?"
                  />
                </div>

                <div className="form-field">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex items-center justify-center gap-2 w-full px-6 py-4 bg-white text-black font-medium transition-all duration-300 hover:shadow-[0_0_40px_rgba(255,255,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <span>Send Message</span>
                        <Send className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 z-30 py-6 pointer-events-none">
        <div className="container mx-auto px-6 lg:px-10 flex items-center justify-center">
          <p className="text-xs text-white/30 pointer-events-auto">
            © 2026 HallucinationFree AI. All Rights Reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
