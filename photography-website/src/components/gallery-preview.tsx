'use client';

import { motion } from 'framer-motion';
import { Eye, Heart } from 'lucide-react';
import Image from 'next/image';

const galleryImages = [
  {
    id: 1,
    src: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=800&h=600&fit=crop',
    alt: 'Nuntă tradițională românească',
    category: 'Nuntă',
    description: 'Momentul solemn al schimbului inelelor'
  },
  {
    id: 2,
    src: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop',
    alt: 'Botez în familie',
    category: 'Botez',
    description: 'Prima zi a vieții în comuniune cu Dumnezeu'
  },
  {
    id: 3,
    src: 'https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=800&h=600&fit=crop',
    alt: 'Aniversare de 25 de ani',
    category: 'Aniversare',
    description: 'Celebrarea iubirii care durează o viață'
  },
  {
    id: 4,
    src: 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=800&h=600&fit=crop',
    alt: 'Primul dans al miresei',
    category: 'Nuntă',
    description: 'Dansul care deschide o nouă viață'
  },
  {
    id: 5,
    src: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
    alt: 'Botez în natură',
    category: 'Botez',
    description: 'Sărbătoarea vieții în armonie cu natura'
  },
  {
    id: 6,
    src: 'https://images.unsplash.com/photo-1519225421980-715cb0215aed?w=800&h=600&fit=crop',
    alt: 'Aniversare de 50 de ani',
    category: 'Aniversare',
    description: 'Jubileul de aur al iubirii'
  }
];

export default function GalleryPreview() {
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
              Galerie
            </span>
            <span className="text-foreground"> de momente</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            O privire asupra celor mai frumoase momente pe care le-am capturat. 
            Fiecare imagine spune o poveste de iubire, bucurie și emoție.
          </p>
        </motion.div>

        {/* Gallery grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {galleryImages.map((image, index) => (
            <motion.div
              key={image.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="group relative overflow-hidden rounded-xl bg-muted"
            >
              {/* Image */}
              <div className="aspect-[4/3] relative overflow-hidden">
                <Image
                  src={image.src}
                  alt={image.alt}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-110"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                />
                
                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium bg-primary/90 text-primary-foreground px-3 py-1 rounded-full">
                        {image.category}
                      </span>
                      <div className="flex gap-2">
                        <button className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                          <Heart className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <h3 className="text-lg font-semibold mb-1">{image.alt}</h3>
                    <p className="text-sm text-white/80">{image.description}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* View more button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
          className="text-center mt-12"
        >
          <button className="group relative px-8 py-4 border-2 border-primary text-primary font-semibold rounded-lg text-lg transition-all duration-300 hover:bg-primary hover:text-primary-foreground">
            Vezi toată galeria
            <div className="absolute inset-0 bg-primary rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <span className="relative z-10">Vezi toată galeria</span>
          </button>
        </motion.div>
      </div>
    </section>
  );
}