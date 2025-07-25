'use client';

import { motion } from 'framer-motion';
import { Heart, Baby, Calendar } from 'lucide-react';

const events = [
  {
    id: 1,
    title: 'Nuntă',
    icon: Heart,
    description: 'Capturăm magia zilei tale de nuntă, de la pregătiri până la ultimul dans. Fiecare moment devine o amintire de neprețuit.',
    features: [
      'Pregătiri și ritualuri',
      'Ceremonia religioasă',
      'Recepția și petrecerea',
      'Album foto premium'
    ],
    bgGradient: 'from-primary/20 to-secondary/20',
    borderColor: 'border-primary',
    iconColor: 'text-primary'
  },
  {
    id: 2,
    title: 'Botez',
    icon: Baby,
    description: 'Prima zi a vieții în comuniune cu Dumnezeu merită să fie păstrată pentru totdeauna. Sărbătoarea familiei tale.',
    features: [
      'Ceremonia de botez',
      'Întâlnirea cu familia',
      'Momentul cu nașii',
      'Album digital și fizic'
    ],
    bgGradient: 'from-secondary/20 to-accent/20',
    borderColor: 'border-secondary',
    iconColor: 'text-secondary'
  },
  {
    id: 3,
    title: 'Aniversare',
    icon: Calendar,
    description: 'Celebrarea iubirii care durează o viață. De la 1 an până la 50, fiecare aniversare spune o poveste frumoasă.',
    features: [
      'Decorul și atmosfera',
      'Momentul surprizelor',
      'Dansurile și bucuriile',
      'Video și foto complet'
    ],
    bgGradient: 'from-accent/20 to-primary/20',
    borderColor: 'border-accent',
    iconColor: 'text-accent'
  }
];

export default function EventsSection() {
  return (
    <section className="py-20 bg-muted">
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
              Evenimente
            </span>
            <span className="text-foreground"> speciale</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Fiecare eveniment are farmecul său unic. Noi suntem aici să capturăm 
            emoțiile pure și să transformăm momentele în amintiri de neuitat.
          </p>
        </motion.div>

        {/* Events grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {events.map((event, index) => {
            const IconComponent = event.icon;
            return (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className={`group relative p-8 rounded-2xl bg-gradient-to-br ${event.bgGradient} border-2 ${event.borderColor} hover:border-opacity-100 transition-all duration-300 hover:scale-105 hover:shadow-2xl`}
              >
                {/* Icon */}
                <div className="mb-6">
                  <div className={`w-16 h-16 rounded-full bg-background/50 flex items-center justify-center ${event.iconColor} group-hover:scale-110 transition-transform duration-300`}>
                    <IconComponent className="w-8 h-8" />
                  </div>
                </div>

                {/* Content */}
                <div className="space-y-4">
                  <h3 className="text-2xl font-bold text-foreground">{event.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{event.description}</p>
                  
                  {/* Features */}
                  <ul className="space-y-2">
                    {event.features.map((feature, featureIndex) => (
                      <motion.li
                        key={featureIndex}
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: (index * 0.2) + (featureIndex * 0.1) }}
                        viewport={{ once: true }}
                        className="flex items-center text-sm text-muted-foreground"
                      >
                        <div className={`w-2 h-2 rounded-full ${event.iconColor.replace('text-', 'bg-')} mr-3`}></div>
                        {feature}
                      </motion.li>
                    ))}
                  </ul>
                </div>

                {/* CTA Button */}
                <motion.button
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  transition={{ duration: 0.3, delay: (index * 0.2) + 0.4 }}
                  viewport={{ once: true }}
                  className={`mt-6 w-full py-3 px-6 rounded-lg border-2 ${event.borderColor} text-foreground font-semibold transition-all duration-300 hover:bg-background hover:scale-105`}
                >
                  Află mai multe
                </motion.button>
              </motion.div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <p className="text-lg text-muted-foreground mb-6">
            Nu ți-am găsit evenimentul în listă? Contactează-ne pentru o consultație personalizată.
          </p>
          <button className="group relative px-8 py-4 bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold rounded-lg text-lg transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-primary/25">
            <span className="relative z-10">Programează o consultație</span>
            <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </button>
        </motion.div>
      </div>
    </section>
  );
}