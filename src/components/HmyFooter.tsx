import Image from "next/image";
import Link from "next/link";
import { footerLogoImage } from "@/lib/homeData";
import { Globe, Share2, Mail, CreditCard, Wallet, Banknote } from "lucide-react";

export function HmyFooter() {
  const columns = [
    {
      title: "Collection",
      links: ["Men's Edit", "Women's Boutique", "Home Essentials", "Bespoke Services"],
    },
    {
      title: "Client Service",
      links: ["Customer Service", "Shipping & Returns", "Size Guide", "Contact Us"],
    },
    {
      title: "Legal",
      links: ["Privacy Policy", "Terms of Use", "Cookie Preferences", "About HMY"],
    },
  ];

  return (
    <footer className=" w-full bg-[#f2f4f4] text-[#2d3435] dark:bg-[#1A1A1A] dark:text-[#f2f4f4]">
      <div className="grid w-full grid-cols-1 gap-8 px-4 py-10 sm:px-8 md:grid-cols-4 md:gap-12 md:px-12 md:py-16">
        <div className="space-y-6">
          <div className="flex items-center">
            <Image alt="HMY Logo" src={footerLogoImage} width={24} height={24} className="h-6 w-auto" />
            <span className="ml-2 text-lg font-bold text-[#2d3435] dark:text-white">
              HMY Atelier
            </span>
          </div>
          <p className="text-xs uppercase leading-relaxed tracking-[0.08em] text-[#5f5e5e] dark:text-[#adb3b4] md:tracking-widest">
            Crafting timeless elegance through contemporary silhouettes and heritage craftsmanship.
          </p>
          <div className="flex space-x-4 text-[#5f5e5e] dark:text-[#f2f4f4]">
            <Globe className="h-5 w-5 cursor-pointer hover:text-[#745b3b]" />
            <Share2 className="h-5 w-5 cursor-pointer hover:text-[#745b3b]" />
            <Mail className="h-5 w-5 cursor-pointer hover:text-[#745b3b]" />
          </div>
        </div>
        {columns.map((column) => (
          <div key={column.title}>
            <h3 className="mb-5 text-xs font-bold uppercase tracking-[0.1em] text-[#2d3435] dark:text-[#f2f4f4] md:mb-8">
              {column.title}
            </h3>
            <ul className="space-y-3 text-xs uppercase tracking-[0.05em] text-[#5f5e5e] dark:text-[#adb3b4] md:space-y-4">
              {column.links.map((link) => (
                <li key={link}>
                  <Link
                    href="#"
                    className="transition-colors duration-400 hover:text-[#2d3435] dark:hover:text-[#ffffff]"
                  >
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="flex flex-col items-center justify-between gap-4 border-t border-[#adb3b4]/10 px-4 py-8 text-center md:flex-row md:px-12 md:text-left">
        <span className="text-[10px] uppercase tracking-[0.05em] text-[#5f5e5e] dark:text-[#adb3b4]">
          © 2024 HMY Atelier. All Rights Reserved.
        </span>
        <div className="flex items-center space-x-6 opacity-50 grayscale">
          <Banknote className="h-6 w-6" />
          <CreditCard className="h-6 w-6" />
          <Wallet className="h-6 w-6" />
        </div>
      </div>
    </footer>
  );
}
