'use client';

import { motion } from 'framer-motion';
import { Camera, Heart, Sparkles } from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20 w-32 h-32 bg-primary rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-secondary rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/3 w-24 h-24 bg-accent rounded-full blur-2xl"></div>
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          {/* Icons */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex justify-center items-center gap-4 mb-8"
          >
            <Camera className="w-8 h-8 text-primary" />
            <Heart className="w-6 h-6 text-secondary" />
            <Sparkles className="w-8 h-8 text-accent" />
          </motion.div>

          {/* Main title */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="text-4xl sm:text-5xl lg:text-7xl font-bold text-foreground mb-6 leading-tight"
          >
            <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
              Păstrăm magia
            </span>
            <br />
            <span className="text-foreground">momentelor tale</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="text-lg sm:text-xl lg:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed"
          >
            Transformăm fiecare moment special într-o poveste vizuală de neuitat. 
            De la nunți și botezuri până la aniversări, capturăm emoțiile pure 
            și bucuriile autentice ale vieții tale.
          </motion.p>

          {/* Call to action */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <button className="group relative px-8 py-4 bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold rounded-lg text-lg transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-primary/25">
              <span className="relative z-10">Vezi portofoliul</span>
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </button>
            
            <button className="px-8 py-4 border-2 border-primary text-primary font-semibold rounded-lg text-lg transition-all duration-300 hover:bg-primary hover:text-primary-foreground">
              Contactează-ne
            </button>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-6 h-10 border-2 border-primary rounded-full flex justify-center"
            >
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-1 h-3 bg-primary rounded-full mt-2"
              ></motion.div>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}