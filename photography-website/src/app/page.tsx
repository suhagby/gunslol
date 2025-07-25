import HeroSection from '@/components/hero-section';
import GalleryPreview from '@/components/gallery-preview';
import EventsSection from '@/components/events-section';
import TestimonialsSection from '@/components/testimonials-section';
import Footer from '@/components/footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <HeroSection />
      <GalleryPreview />
      <EventsSection />
      <TestimonialsSection />
      <Footer />
    </main>
  );
}
