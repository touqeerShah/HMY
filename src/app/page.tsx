import { HmyNav } from "@/components/HmyNav";
import { HmyHero } from "@/components/HmyHero";
import { NewsletterSignup } from "@/components/NewsletterSignup";
import { HmyFooter } from "@/components/HmyFooter";
import { ScrollLinkedFrameBackground } from "@/components/ScrollLinkedFrameBackground";
import { Feature108Demo } from "@/components/Feature108Demo";
import { Gallery4Demo } from "@/components/Gallery4Demo";
import { PartsPointerSection } from "@/components/PartsPointerSection";
import { BrandScrollerBand } from "@/components/BrandScrollerBand";

export default function Home() {
  return (
    <div className="relative min-h-screen text-[#2d3435] dark:text-[#f2f4f4]">
      {/* Fixed global animated background */}
      <div className="fixed inset-0 -z-50 bg-white md:inset-x-0 md:bottom-0 md:top-20">
        <ScrollLinkedFrameBackground alt="Unstitched cloth transforming into signature form" progress={undefined} />
      </div>

      <HmyNav />
      {/* 
        The main content scrolls over the fixed background
      */}
      <main className="relative z-10 pt-20 md:pt-20">
        <HmyHero />
        
        <div className="relative bg-transparent">
          {/* Shorter empty spacer section (reduced from 200vh to 80vh) */}
          <PartsPointerSection />

          <div className="relative bg-white dark:bg-[#0c0f0f]">
            <Feature108Demo />
            <Gallery4Demo />
            <BrandScrollerBand />
            <NewsletterSignup />
          </div>
        </div>
      </main>
      <div className="relative z-10 bg-white dark:bg-[#0c0f0f]">
        <HmyFooter />
      </div>
    </div>
  );
}
