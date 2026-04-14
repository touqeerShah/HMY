import { supportCards } from "@/lib/homeData";

export function SupportCards() {
  return (
    <section className="bg-transparent py-20">
      <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-5 px-6 md:grid-cols-3 md:px-8">
        {supportCards.map((card) => (
          <article key={card.title} className="border border-[#adb3b4]/30 bg-transparent backdrop-blur-md p-8">
            <p className="text-[10px] uppercase tracking-[0.25em] text-[#745b3b] dark:text-[#b08b5a]">
              Atelier Note
            </p>
            <h2 className="mt-5 text-2xl font-bold tracking-tight text-[#2d3435] dark:text-white">
              {card.title}
            </h2>
            <p className="mt-4 text-sm leading-7 text-[#5a6061] dark:text-[#a0aab2]">
              {card.text}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
