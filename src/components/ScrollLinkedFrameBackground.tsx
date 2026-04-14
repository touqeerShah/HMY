"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { useScroll, useMotionValueEvent } from "framer-motion";

interface ScrollLinkedFrameBackgroundProps {
  frameCount?: number;
  basePath?: string;
  alt?: string;
  progress?: any;
}

export function ScrollLinkedFrameBackground({
  frameCount = 132,
  basePath = "/back-gorund-frame",
  alt = "Fabric transformation",
  progress,
}: ScrollLinkedFrameBackgroundProps) {
  const [frame, setFrame] = useState(1);
  const [previousFrame, setPreviousFrame] = useState(1);
  const [fadeIn, setFadeIn] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const frameRef = useRef(1);
  const targetFrameRef = useRef(1);
  const rafRef = useRef<number | null>(null);
  const { scrollY } = useScroll();

  const updateFrame = (nextFrame: number) => {
    if (nextFrame === frameRef.current) {
      return;
    }

    setPreviousFrame(frameRef.current);
    frameRef.current = nextFrame;
    setFadeIn(false);
    setFrame(nextFrame);
    window.requestAnimationFrame(() => {
      setFadeIn(true);
    });
  };

  useMotionValueEvent(scrollY, "change", (latest) => {
    const vh = typeof window !== "undefined" ? window.innerHeight : 800;

    if (isMobile) {
      return;
    }

    const speedMultiplier = 1;
    const effectiveScrollY = latest * speedMultiplier;

    const heroHeight = vh * 1.2;
    const sectionProgress = Math.min(effectiveScrollY / heroHeight, 1);
    let currentFrame = Math.floor(sectionProgress * (frameCount - 1)) + 1;

    if (currentFrame < 1) currentFrame = 1;
    if (currentFrame > frameCount) currentFrame = frameCount;
    targetFrameRef.current = currentFrame;

    if (rafRef.current === null) {
      rafRef.current = window.requestAnimationFrame(() => {
        rafRef.current = null;
        updateFrame(targetFrameRef.current);
      });
    }
  });

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 640);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => {
      window.removeEventListener("resize", checkMobile);
      if (rafRef.current !== null) {
        window.cancelAnimationFrame(rafRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isMobile) {
      const img = new window.Image();
      img.src = "/phone-backgound/banner.png";
      return;
    }

    for (let index = 1; index <= frameCount; index += 1) {
      if (typeof window !== "undefined") {
        const img = new window.Image();
        img.src = `${basePath}/ezgif-frame-${String(index).padStart(3, "0")}.jpg`;
      }
    }
  }, [frameCount, basePath, isMobile]);

  const paddedFrame = String(frame).padStart(3, "0");
  const paddedPreviousFrame = String(previousFrame).padStart(3, "0");
  const frameSrc = `${basePath}/ezgif-frame-${paddedFrame}.jpg`;
  const previousFrameSrc = `${basePath}/ezgif-frame-${paddedPreviousFrame}.jpg`;

  if (isMobile) {
    return (
      <Image
        src="/phone-backgound/banner.png"
        alt={alt}
        fill
        className="object-contain object-top"
        unoptimized
        priority
      />
    );
  }

  return (
    <div className="relative h-full w-full overflow-hidden">
      {previousFrame !== frame && (
        <Image
          src={previousFrameSrc}
          alt=""
          aria-hidden="true"
          fill
          className="object-cover object-center"
          unoptimized
          priority
        />
      )}
      <Image
        src={frameSrc}
        alt={alt}
        fill
        className={`object-cover object-center transition-opacity duration-150 ease-linear ${
          fadeIn ? "opacity-100" : "opacity-0"
        }`}
        unoptimized
        priority
      />
    </div>
  );
}
