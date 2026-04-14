import { AnimatedFrameBackground } from "./AnimatedFrameBackground";

export function CraftSection() {
  return (
    <section className="mx-auto grid max-w-[1400px] grid-cols-1 gap-10 px-6 py-24 md:grid-cols-[0.9fr_1.1fr] md:px-8">
      <div className="flex flex-col justify-center">
        <p className="mb-4 text-xs uppercase tracking-[0.3em] text-[#745b3b]">
          Craft Section
        </p>
        <p className="mt-7 max-w-xl text-base leading-8 text-[#5a6061] dark:text-[#a0aab2]">
          The sequence stays calm so the eye follows the fabric: first the cloth, then the fall, then the final stitched form.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <span className="border border-[#adb3b4]/30 px-4 py-2 text-[10px] uppercase tracking-widest text-[#5f5e5e] dark:text-white">
            Unstitched
          </span>
          <span className="border border-[#adb3b4]/30 px-4 py-2 text-[10px] uppercase tracking-widest text-[#5f5e5e] dark:text-white">
            Measured
          </span>
          <span className="border border-[#adb3b4]/30 px-4 py-2 text-[10px] uppercase tracking-widest text-[#5f5e5e] dark:text-white">
            Stitched
          </span>
        </div>
      </div>
      <div className="relative min-h-[560px] overflow-hidden bg-[#0c0f0f] border border-white/20">
        <AnimatedFrameBackground alt="Atelier craft transformation preview" fps={12} />
        <div className="absolute inset-0 bg-black/25"></div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-8">
          <p className="text-xs uppercase tracking-[0.25em] text-[#f9f9f9]/70">
            Signature Motion
          </p>
        </div>
      </div>
    </section>
  );
}
