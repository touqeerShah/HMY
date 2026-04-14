"use client";

export function NewsletterSignup() {
  return (
    <section className="bg-white py-12 text-[#2d3435] dark:bg-[#0c0f0f] dark:text-[#f2f4f4] md:py-20">
      <div className="mx-auto max-w-4xl px-4 text-center sm:px-8">
        <h2 className="mb-4 text-2xl text-[#2d3435] dark:text-white md:text-3xl">
          Join the Atelier
        </h2>
        <p className="mb-8 text-sm leading-7 text-[#5a6061] dark:text-[#a0aab2] md:mb-10 md:text-base">
          Receive early access to seasonal launches, private events, and editorial inspiration.
        </p>
        <form
          className="mx-auto flex max-w-2xl flex-col gap-0 md:flex-row"
          onSubmit={(e) => e.preventDefault()}
        >
          <input
            className="w-full flex-grow border-b border-[#adb3b4]/40 bg-[#f9f9f9] px-5 py-4 outline-none transition-colors placeholder:text-xs placeholder:uppercase placeholder:tracking-widest placeholder:text-[#5a6061]/50 focus:border-[#745b3b] dark:bg-[#0c0f0f] dark:text-white dark:focus:border-[#b08b5a] md:px-6"
            placeholder="Enter your email address"
            type="email"
          />
          <button className="w-full bg-[#2d3435] px-8 py-4 text-xs uppercase tracking-widest text-[#f9f9f9] transition-all hover:bg-[#5f5e5e] dark:bg-white dark:text-black dark:hover:bg-gray-200 md:w-auto md:px-10">
            Subscribe
          </button>
        </form>
      </div>
    </section>
  );
}
