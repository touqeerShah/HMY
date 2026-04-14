import {
  BrandScroller,
  BrandScrollerReverse,
} from "@/components/ui/brand-scoller";

export function BrandScrollerBand() {
  return (
    <section className="bg-white py-10 text-[#2d3435] dark:bg-[#0c0f0f] dark:text-[#f2f4f4] md:py-14">
      <div className="mx-auto max-w-[1400px] px-4 sm:px-6 md:px-8">
        <div className="mb-8 max-w-2xl">
          <p className="mb-2 text-xs uppercase tracking-[0.2em] text-[#745b3b] dark:text-[#b08b5a]">
            Explore HMY
          </p>
          <h2 className="text-2xl font-medium tracking-tight text-[#2d3435] dark:text-white md:text-4xl">
            Brands, Products, and stories in motion
          </h2>
        </div>
      </div>
      <div className="space-y-3">
        <BrandScroller />
        <BrandScrollerReverse />
      </div>
    </section>
  );
}
