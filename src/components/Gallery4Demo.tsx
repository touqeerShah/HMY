"use client";

import { Gallery4, Gallery4Props } from "@/components/blocks/gallery4"

const newArrivalPath = "/new-arrivals";

const demoData: Gallery4Props = {
  title: "New Arrivals",
  description:
    "Discover the latest additions to our atelier. From raw silks to hand-stitched garments, these new arrivals represent the pinnacle of curated style and design.",
  items: [
    {
      id: "arrival-1",
      title: "Maroon Embroidered Suit",
      description:
        "A refined three-piece edit with dense embroidery and a polished festive finish.",
      price: "PKR 18,950",
      href: "#",
      image: `${newArrivalPath}/480625065_928057296169459_3663724997094342936_n.jpg`,
    },
    {
      id: "arrival-2",
      title: "Soft Rose Lawn Set",
      description:
        "Light seasonal fabric with delicate detailing for day-to-evening dressing.",
      price: "PKR 14,500",
      href: "#",
      image: `${newArrivalPath}/480647341_928057306169458_7314344689473003182_n.jpg`,
    },
    {
      id: "arrival-3",
      title: "Ivory Threadwork Edit",
      description:
        "Clean ivory fabric balanced with signature embroidery and an elegant drape.",
      price: "PKR 16,900",
      href: "#",
      image: `${newArrivalPath}/480675386_928057416169447_84728318707470283_n.jpg`,
    },
    {
      id: "arrival-4",
      title: "Ruby Formal Ensemble",
      description:
        "Rich ruby tones with statement placement embroidery and a composed silhouette.",
      price: "PKR 21,750",
      href: "#",
      image: `${newArrivalPath}/480729740_928057266169462_2431357962989670469_n.jpg`,
    },
    {
      id: "arrival-5",
      title: "Midnight Garden Suit",
      description:
        "Dark floral embroidery with a graceful fall and soft contrast detailing.",
      price: "PKR 19,250",
      href: "#",
      image: `${newArrivalPath}/480736967_928053082836547_8127656063091023286_n.jpg`,
    },
    {
      id: "arrival-6",
      title: "Pearl Beige Collection",
      description:
        "Neutral tones shaped with quiet embroidery for polished everyday wear.",
      price: "PKR 13,950",
      href: "#",
      image: `${newArrivalPath}/480848553_928053256169863_2509967441398721766_n.jpg`,
    },
    {
      id: "arrival-7",
      title: "Emerald Festive Set",
      description:
        "A deep emerald statement with refined motifs and a premium stitched finish.",
      price: "PKR 22,500",
      href: "#",
      image: `${newArrivalPath}/480881175_928053312836524_6038319247246367989_n.jpg`,
    },
    {
      id: "arrival-8",
      title: "Blush Heritage Suit",
      description:
        "Soft blush fabric with ornamental accents for a graceful seasonal look.",
      price: "PKR 17,800",
      href: "#",
      image: `${newArrivalPath}/480999265_928053346169854_8079560889506615890_n.jpg`,
    },
    {
      id: "arrival-9",
      title: "Charcoal Embroidered Edit",
      description:
        "A darker atelier piece finished with crisp threadwork and a clean line.",
      price: "PKR 20,950",
      href: "#",
      image: `${newArrivalPath}/481000672_928057339502788_5703346291592535344_n.jpg`,
    },
    {
      id: "arrival-10",
      title: "Classic Maroon Drape",
      description:
        "A signature maroon arrival with decorative finishing and a formal mood.",
      price: "PKR 18,250",
      href: "#",
      image: `${newArrivalPath}/481275305_928052892836566_7336247111900295498_n.jpg`,
    },
  ],
};

function Gallery4Demo() {
  return (
    <div className="bg-white dark:bg-[#0c0f0f]">
      <Gallery4 {...demoData} />
    </div>
  );
}

export { Gallery4Demo };
