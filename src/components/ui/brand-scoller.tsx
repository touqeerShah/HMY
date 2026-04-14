"use client";

type BrandItem = {
  label: string;
  image: string;
};

const brandItems: BrandItem[] = [
  {
    label: "Brand 1",
    image: "/brands/Screenshot%202026-04-12%20at%2011.26.35%E2%80%AFPM.png",
  },
  {
    label: "Brand 2",
    image: "/brands/Screenshot%202026-04-12%20at%2011.27.18%E2%80%AFPM.png",
  },
  {
    label: "Brand 3",
    image: "/brands/Screenshot%202026-04-12%20at%2011.28.26%E2%80%AFPM.png",
  },
  {
    label: "Brand 4",
    image: "/brands/Screenshot%202026-04-12%20at%2011.30.03%E2%80%AFPM.png",
  },
];

function BrandMarquee({
  items,
  reverse = false,
}: {
  items: BrandItem[];
  reverse?: boolean;
}) {
  return (
    <div className="group flex max-w-full flex-row overflow-hidden py-2 [--duration:38s] [--gap:1rem] [gap:var(--gap)] [mask-image:linear-gradient(to_right,_rgba(0,_0,_0,_0),rgba(0,_0,_0,_1)_10%,rgba(0,_0,_0,_1)_90%,rgba(0,_0,_0,_0))] md:[--gap:2rem]">
      {Array(4)
        .fill(0)
        .map((_, index) => (
          <div
            className={[
              "flex shrink-0 flex-row justify-around [gap:var(--gap)] group-hover:[animation-play-state:paused]",
              reverse ? "animate-marquee-reverse" : "animate-marquee",
            ].join(" ")}
            key={index}
          >
            {items.map((item) => (
              <div
                className="flex h-20 w-36 items-center justify-center border border-black/10 bg-white px-4 dark:border-white/10 dark:bg-[#121415] md:h-24 md:w-44 md:px-5"
                key={`${index}-${item.label}`}
              >
                <img
                  src={item.image}
                  alt={item.label}
                  className="max-h-12 w-full object-contain md:max-h-16"
                />
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}

export const BrandScroller = () => {
  return <BrandMarquee items={brandItems} />;
};

export const BrandScrollerReverse = () => {
  return <BrandMarquee items={[...brandItems].reverse()} reverse />;
};
