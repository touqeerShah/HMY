"use client";

import Image from "next/image";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export function PartsPointerSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  const introOpacity = useTransform(scrollYProgress, [0, 0.12], [0, 1]);
  const introY = useTransform(scrollYProgress, [0, 0.18], [24, 0]);
  const sectionOpacity = useTransform(
    scrollYProgress,
    [0, 0.12, 0.76, 0.96],
    [0, 1, 1, 0]
  );
  const imageScale = useTransform(scrollYProgress, [0.14, 0.36], [1.06, 1]);
  const leftCardX = useTransform(scrollYProgress, [0.14, 0.34], [-34, 0]);
  const rightCardX = useTransform(scrollYProgress, [0.14, 0.34], [34, 0]);
  const cardOpacity = useTransform(scrollYProgress, [0.16, 0.28], [0, 1]);
  const lineScale = useTransform(scrollYProgress, [0.18, 0.34], [0, 1]);
  const hotspotOpacity = useTransform(scrollYProgress, [0.14, 0.26], [0, 1]);

  return (
    <section ref={sectionRef} className="relative bg-transparent py-10 lg:h-[180vh] lg:py-0">
      <div className="flex items-center overflow-hidden lg:sticky lg:top-20 lg:h-[calc(100vh-5rem)]">
        <motion.div
          style={{ opacity: sectionOpacity }}
          className="mx-auto w-full max-w-[1440px] px-4 md:px-8"
        >
          <motion.div
            style={{ opacity: introOpacity, y: introY }}
            className="mb-6 max-w-3xl px-1 sm:px-2"
          >
            <p className="text-[10px] uppercase tracking-[0.35em] text-[#745b3b]">
              Crafted From Fabric
            </p>

            <h2 className="mt-3 text-2xl font-bold tracking-tight text-[#2d3435] dark:text-white md:text-4xl">
              The fabric opens into a guided <br className="hidden sm:block" />
              detail reveal
            </h2>

            <p className="mt-3 max-w-2xl text-sm leading-7 text-[#5a6061] dark:text-white/70">
              Each point maps to a real garment area so the user sees the embroidery,
              <br className="hidden sm:block" />
              hem, and dupatta finishing with clear visual anchors.
            </p>
          </motion.div>

          <div className="relative grid min-h-0 grid-cols-1 items-center gap-6 lg:min-h-[30rem] lg:grid-cols-[1fr_minmax(0,620px)_1fr] lg:gap-8">
            <motion.div
              style={{ x: leftCardX, opacity: cardOpacity }}
              className="hidden lg:grid gap-5"
            >
              <ZoomCard
                src="/parts/p2.png"
                label="Kurta details"
                title="Neck embroidery"
                description="Dense front detailing with a refined stitched opening and ornamental threadwork."
                align="left"
                className="-mt-14"
              />

              <ZoomCard
                src="/parts/p1.png"
                label="Shalwar details"
                title="Hem border"
                description="Heavy lower border with layered motifs that define the final silhouette."
                align="left"
                className="ml-10 mt-14"
              />
            </motion.div>

            <div className="relative hidden min-h-[24rem] items-center justify-center md:min-h-[34rem] lg:flex">
              <motion.div
                style={{ scale: imageScale, opacity: introOpacity }}
                className="relative w-full max-w-[620px]"
              >
                <div className="relative overflow-hidden rounded-[18px]">
                  <div className="relative aspect-[4/5] min-h-[28rem] md:min-h-[38rem]">
                    
                  </div>

                  <motion.div style={{ opacity: hotspotOpacity }}>
                    {/* P1 upper-left target */}
                    <Hotspot left="49%" top="18%" />
                    {/* P2 lower-left target */}
                    <Hotspot left="48%" top="73%" delay="0.15s" />
                    {/* P3 upper-right target */}
                    <Hotspot left="78%" top="22%" delay="0.25s" />
                  </motion.div>

                  <PointerLine
                    left="0%"
                    top="18%"
                    width="23%"
                    direction="left"
                    scale={lineScale}
                  />

                  <PointerLine
                    left="0%"
                    top="73%"
                    width="28%"
                    direction="left"
                    scale={lineScale}
                  />

                  <PointerLine
                    right="0%"
                    top="22%"
                    width="18%"
                    direction="right"
                    scale={lineScale}
                  />
                </div>
              </motion.div>
            </div>

            <motion.div
              style={{ x: rightCardX, opacity: cardOpacity }}
              className="hidden lg:grid gap-5 self-start"
            >
              <ZoomCard
                src="/parts/p3.png"
                label="Dupatta"
                title="Dupatta finish"
                description="Sheer maroon drape with embellished edge trim and final stitched polish."
                align="right"
                className="-mt-10"
              />
            </motion.div>
          </div>

          <div className="mt-2 grid gap-4 lg:hidden">
            <SmallMobileCard
              src="/parts/p2.png"
              label="Kurta details"
              title="Neck embroidery"
              description="Dense front detailing with refined stitched finishing."
            />
            <SmallMobileCard
              src="/parts/p1.png"
              label="Shalwar details"
              title="Hem border"
              description="Layered border motifs that define the lower silhouette."
            />
            <SmallMobileCard
              src="/parts/p3.png"
              label="Dupatta"
              title="Dupatta finish"
              description="Sheer maroon drape with embellished trim and finishing edge."
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Hotspot({
  left,
  top,
  delay,
}: {
  left: string;
  top: string;
  delay?: string;
}) {
  return (
    <div
      className="pointer-events-none absolute z-20"
      style={{ left, top, transform: "translate(-50%, -50%)" }}
    >
      <div className="relative flex h-4 w-4 items-center justify-center">
        <span
          className="absolute h-10 w-10 rounded-full border border-[#745b3b]/30 animate-ping"
          style={{ animationDuration: "2.2s", animationDelay: delay ?? "0s" }}
        />
        <span className="absolute h-6 w-6 rounded-full bg-[#745b3b]/12 blur-[1px]" />
        <span className="relative h-3.5 w-3.5 rounded-full border-2 border-white bg-[#745b3b] shadow-[0_0_0_6px_rgba(116,91,59,0.10)]" />
      </div>
    </div>
  );
}

function PointerLine({
  top,
  width,
  direction,
  scale,
  left,
  right,
}: {
  top: string;
  width: string;
  direction: "left" | "right";
  scale: any;
  left?: string;
  right?: string;
}) {
  const isLeft = direction === "left";

  return (
    <motion.div
      style={{
        top,
        width,
        left,
        right,
        scaleX: scale,
        transformOrigin: isLeft ? "right center" : "left center",
      }}
      className="pointer-events-none absolute z-10 hidden h-px bg-[#745b3b] lg:block"
    >
      <span
        className={[
          "absolute top-1/2 h-2.5 w-2.5 -translate-y-1/2 border-[#745b3b]",
          isLeft
            ? "right-0 rotate-45 border-r border-t"
            : "left-0 rotate-[225deg] border-r border-t",
        ].join(" ")}
      />
    </motion.div>
  );
}

function ZoomCard({
  src,
  label,
  title,
  description,
  align,
  className,
}: {
  src: string;
  label: string;
  title: string;
  description: string;
  align: "left" | "right";
  className?: string;
}) {
  return (
    <div
      className={[
        "overflow-hidden rounded-[14px] border border-[#dbcdb8] bg-white/92 shadow-[0_12px_30px_rgba(45,52,53,0.10)] backdrop-blur-sm",
        className ?? "",
      ].join(" ")}
    >
      <div className="relative aspect-[16/10] bg-[#ece3d2]">
        <Image
          src={src}
          alt={title}
          fill
          className="object-cover object-center"
          sizes="(max-width: 1024px) 100vw, 22vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/12 via-transparent to-transparent" />
        <div className="absolute left-3 top-3 rounded-sm bg-white/85 px-2 py-1 backdrop-blur-sm">
          <p className="text-[10px] uppercase tracking-[0.25em] text-[#2d3435]">
            {label}
          </p>
        </div>
      </div>

      <div className="p-4">
        <p className="text-[10px] uppercase tracking-[0.25em] text-[#745b3b]">
          {align === "left" ? "Left detail" : "Right detail"}
        </p>
        <h3 className="mt-2 text-lg font-semibold text-[#2d3435]">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-[#5a6061]">{description}</p>
      </div>
    </div>
  );
}

function SmallMobileCard({
  src,
  label,
  title,
  description,
}: {
  src: string;
  label: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4 overflow-hidden rounded-[14px] border border-[#dbcdb8] bg-white/92 p-3 shadow-[0_10px_24px_rgba(45,52,53,0.08)]">
      <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-[10px] bg-[#ece3d2]">
        <Image src={src} alt={title} fill className="object-cover object-center" sizes="96px" />
      </div>
      <div className="min-w-0 py-1">
        <p className="text-[10px] uppercase tracking-[0.25em] text-[#745b3b]">{label}</p>
        <h3 className="mt-2 text-base font-semibold text-[#2d3435]">{title}</h3>
        <p className="mt-1 text-sm leading-6 text-[#5a6061]">{description}</p>
      </div>
    </div>
  );
}
