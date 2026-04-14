import Image from "next/image";
import Link from "next/link";
import { logoImage } from "@/lib/homeData";
import { Search, User, ShoppingCart } from "lucide-react";

export function HmyNav() {
  const navItems = ["Home", "Product", "New Deals", "New Articles"];

  return (
    <nav className="fixed top-0 z-50 w-full max-w-full bg-[#f9f9f9] px-4 py-3 shadow-sm dark:bg-[#1A1A1A] md:flex md:items-center md:justify-between md:px-8 md:py-4">
      <div className="flex items-center justify-between gap-5 md:justify-start md:gap-8">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center" aria-label="HMY homepage">
            <Image alt="HMY Logo" src={logoImage} width={32} height={32} className="h-8 w-auto" />
          </Link>
          <div className="hidden items-center space-x-8 text-base tracking-tight text-[#5f5e5e] dark:text-[#f2f4f4] md:flex">
            {navItems.map((item) => (
              <Link
                key={item}
                className={`transition-colors duration-400 hover:text-[#745b3b] ${
                  item === "Home"
                    ? "border-b-2 border-[#745b3b] pb-1 text-[#745b3b]"
                    : "text-[#2d3435] dark:text-[#adb3b4]"
                }`}
                href="#"
              >
                {item}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center space-x-4 text-[#2d3435] dark:text-[#f2f4f4] md:hidden">
          <Search className="h-5 w-5 cursor-pointer transition-colors hover:text-[#745b3b]" />
          <User className="h-5 w-5 cursor-pointer transition-colors hover:text-[#745b3b]" />
          <ShoppingCart className="h-5 w-5 cursor-pointer transition-colors hover:text-[#745b3b]" />
        </div>
      </div>
      <div className="mt-3 flex gap-5 overflow-x-auto whitespace-nowrap border-t border-black/10 pt-3 text-sm text-[#5f5e5e] dark:border-white/10 dark:text-[#adb3b4] md:hidden">
        {navItems.map((item) => (
          <Link
            key={item}
            className={`shrink-0 transition-colors hover:text-[#745b3b] ${
              item === "Home" ? "text-[#745b3b]" : ""
            }`}
            href="#"
          >
            {item}
          </Link>
        ))}
      </div>
      <div className="hidden items-center space-x-5 text-[#2d3435] dark:text-[#f2f4f4] md:flex md:space-x-6">
        <Search className="h-6 w-6 cursor-pointer transition-colors hover:text-[#745b3b]" />
        <User className="h-6 w-6 cursor-pointer transition-colors hover:text-[#745b3b]" />
        <ShoppingCart className="h-6 w-6 cursor-pointer transition-colors hover:text-[#745b3b]" />
      </div>
    </nav>
  );
}
