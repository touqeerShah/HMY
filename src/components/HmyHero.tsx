"use client";

import { useScroll, useTransform, motion } from "framer-motion";
import { useRef } from "react";

export function HmyHero() {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Track scroll over the height of this specific section
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  // Fade out the text content as you scroll down
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  const steps = [
    "Unstitched fabric is selected",
    "Craft marks the measurements",
    "Signature form is finished",
  ];

  return (
    <section 
      ref={containerRef}
      className="relative h-[82svh] w-full text-[#2d3435] md:h-[120vh]" 
    >
      <div className="sticky top-20 flex h-[calc(100svh-5rem)] w-full items-start justify-center overflow-hidden md:top-0 md:h-screen md:items-center">
        <motion.div 
          style={{ opacity }}
          className="relative z-10 mx-auto grid h-full w-full max-w-[1440px] grid-cols-1 items-start gap-8 px-4 pb-6 pt-4 sm:px-6 md:grid-cols-[minmax(0,1fr)_380px] md:items-center md:px-10 md:pb-10 md:pt-10 lg:px-14"
        >
          <div className="max-w-2xl self-start md:self-center">
            <p className="mb-4 inline-block bg-white/65 px-3 py-2 text-[10px] uppercase tracking-[0.22em] text-[#745b3b] shadow-sm backdrop-blur-sm md:mb-5 md:text-xs md:tracking-[0.3em]">
              Crafted From Fabric
            </p>
            <h1 className="max-w-3xl text-[2.65rem] font-bold leading-[1.02] tracking-tight text-[#2d3435] [text-shadow:0_1px_18px_rgba(255,255,255,0.72)] sm:text-5xl md:text-7xl md:leading-[0.98] lg:text-8xl">
              From unstitched cloth to signature form
            </h1>
            <p className="mt-6 max-w-xl px-0 py-0 text-sm leading-7 text-[#2d3435] backdrop-blur-sm sm:bg-white/45 sm:px-4 sm:py-3 md:mt-8 md:text-lg md:leading-8">
              A couture transformation in motion, shaped by quiet measurements, hand-finished detail, and fabric chosen for the way it lives.
            </p>
            <div className="mt-6 flex flex-row gap-2 sm:gap-3 md:mt-10">
              <button className="flex-1 bg-[#2d3435] px-3 py-3 text-[10px] uppercase tracking-[0.12em] text-white transition-all duration-400 hover:bg-[#745b3b] sm:flex-none sm:px-6 sm:py-4 sm:text-xs sm:tracking-widest md:px-10">
                New Articles
              </button>
              <button className="flex-1 border border-[#2d3435]/30 bg-white/75 px-3 py-3 text-[10px] uppercase tracking-[0.12em] text-[#2d3435] backdrop-blur-md transition-all duration-400 hover:bg-[#2d3435] hover:text-white sm:flex-none sm:px-6 sm:py-4 sm:text-xs sm:tracking-widest md:px-10">
                New Deals
              </button>
            </div>
          </div>

          <aside className="hidden self-center border border-white/20 bg-black/60 p-6 text-white shadow-2xl backdrop-blur-md md:block md:p-8 rounded-xl">
            <p className="text-[10px] uppercase tracking-[0.3em] text-white/80">
              Motion Map
            </p>
            <h2 className="mt-4 text-2xl font-bold">A single vertical reveal</h2>
            <div className="mt-8 space-y-6">
              {steps.map((step, index) => (
                <div key={step} className="flex gap-4">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center border border-white/40 text-[10px]">
                    0{index + 1}
                  </span>
                  <p className="pt-1 text-sm leading-6 text-white/90">{step}</p>
                </div>
              ))}
            </div>
            <div className="mt-8 h-px bg-white/30"></div>
            <p className="mt-6 text-xs uppercase leading-6 tracking-[0.18em] text-white/80">
              Keep the center open. Let the garment arrive in the final quarter.
            </p>
          </aside>
        </motion.div>
      </div>
    </section>
  );
}
