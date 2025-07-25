'use client';

import { motion } from 'framer-motion';
import { Star, Quote } from 'lucide-react';
import Image from 'next/image';

const testimonials = [
  {
    id: 1,
    name: 'Maria și Alexandru',
    event: 'Nuntă',
    rating: 5,
    text: 'Nu am cuvinte să descriu cât de mulțumiți suntem! Ana a capturat fiecare moment special al nunții noastre cu atâta pasiune și atenție la detalii. Albumul nostru este exact cum am visat - plin de emoții pure și momente autentice. Recomandăm cu toată inima!',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face'
  },
  {
    id: 2,
    name: 'Familia Popescu',
    event: 'Botez',
    rating: 5,
    text: 'Pentru botezul fiicei noastre am ales echipa lui Ana și nu ne-am putut face o alegere mai bună. Fiecare fotografie spune o poveste, iar modul în care a capturat bucuria din ochii bătrânilor noștri ne-a făcut să plângem de fericire. Mulțumim din suflet!',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
  }
];

export default function TestimonialsSection() {
  return (
    <section className="py-20 bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Ce spun
            </span>
            <span className="text-foreground"> clienții noștri</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Bucuria și satisfacția clienților noștri sunt cea mai mare recompensă. 
            Fiecare eveniment este o nouă prietenie și o nouă poveste de succes.
          </p>
        </motion.div>

        {/* Testimonials grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="relative group"
            >
              {/* Quote icon */}
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center text-primary-foreground">
                <Quote className="w-6 h-6" />
              </div>

              {/* Testimonial card */}
              <div className="relative p-8 rounded-2xl bg-muted border border-gray-700 hover:border-primary/50 transition-all duration-300 hover:shadow-2xl">
                {/* Rating */}
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-primary text-primary" />
                  ))}
                </div>

                {/* Text */}
                <blockquote className="text-muted-foreground leading-relaxed mb-6 italic">
                  &ldquo;{testimonial.text}&rdquo;
                </blockquote>

                {/* Author */}
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full overflow-hidden relative">
                    <Image
                      src={testimonial.avatar}
                      alt={testimonial.name}
                      fill
                      className="object-cover"
                      sizes="48px"
                    />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{testimonial.name}</h4>
                    <p className="text-sm text-muted-foreground">{testimonial.event}</p>
                  </div>
                </div>

                {/* Decorative elements */}
                <div className="absolute top-4 right-4 opacity-10">
                  <Quote className="w-16 h-16 text-primary" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-8 border border-primary/20">
            <h3 className="text-2xl font-bold text-foreground mb-4">
              Vrei să fii următorul client mulțumit?
            </h3>
            <p className="text-muted-foreground mb-6">
              Contactează-ne pentru o consultație gratuită și să discutăm despre evenimentul tău special.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="group relative px-8 py-4 bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold rounded-lg text-lg transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-primary/25">
                <span className="relative z-10">Programează o întâlnire</span>
                <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
              <button className="px-8 py-4 border-2 border-primary text-primary font-semibold rounded-lg text-lg transition-all duration-300 hover:bg-primary hover:text-primary-foreground">
                Vezi mai multe recenzii
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}