import { products } from "@/lib/homeData";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";

export function ProductStrip() {
  return (
    <section className="py-24 text-[#2d3435] dark:bg-[#121415] dark:text-[#f2f4f4]">
      <div className="mx-auto max-w-[1400px] px-6 md:px-8">
        <div className="mb-16 flex items-end justify-between">
          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.2em] text-[#745b3b]">
              The Latest Edit
            </p>
            <h2 className="text-4xl font-semibold tracking-tight text-[#2d3435] dark:text-white">
              New Arrivals
            </h2>
          </div>
          <div className="hidden space-x-4 sm:flex">
            <button className="flex h-12 w-12 items-center justify-center border border-[#adb3b4]/30 text-[#5f5e5e] transition-all hover:bg-[#5f5e5e] hover:text-white dark:text-[#f2f4f4] dark:hover:bg-[#f2f4f4] dark:hover:text-[#121415]">
              <ChevronLeft />
            </button>
            <button className="flex h-12 w-12 items-center justify-center border border-[#adb3b4]/30 text-[#5f5e5e] transition-all hover:bg-[#5f5e5e] hover:text-white dark:text-[#f2f4f4] dark:hover:bg-[#f2f4f4] dark:hover:text-[#121415]">
              <ChevronRight />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {products.map((product) => (
            <article key={product.title} className="group cursor-pointer">
              <div className="relative mb-6 aspect-[3/4] overflow-hidden">
                <Image
                  alt={product.title}
                  src={product.image}
                  fill
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                />
                {product.badge && (
                  <span className="absolute left-4 top-4 bg-[#745b3b] px-3 py-1 text-[10px] uppercase tracking-widest text-[#f9f9f9]">
                    {product.badge}
                  </span>
                )}
              </div>
              <h3 className="mb-1 text-xs uppercase tracking-widest text-[#5a6061] dark:text-[#a0aab2]">
                {product.label}
              </h3>
              <p className="mb-2 text-base font-semibold text-[#2d3435] dark:text-white">
                {product.title}
              </p>
              <p className="text-[#745b3b] dark:text-[#b08b5a]">
                {product.price}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
