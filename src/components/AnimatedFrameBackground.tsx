"use client";

import { useEffect, useState, useMemo } from "react";
import Image from "next/image";

interface AnimatedFrameBackgroundProps {
  frameCount?: number;
  fps?: number;
  basePath?: string;
  alt?: string;
}

export function AnimatedFrameBackground({
  frameCount = 177,
  fps = 18,
  basePath = "/back-gorund-frame",
  alt = "Fabric transforming into a stitched garment",
}: AnimatedFrameBackgroundProps) {
  const [frame, setFrame] = useState(1);

  const frameSrc = useMemo(() => {
    const padded = String(frame).padStart(3, "0");
    return `${basePath}/ezgif-frame-${padded}.jpg`;
  }, [frame, basePath]);

  useEffect(() => {
    const interval = Math.max(1000 / fps, 24);
    
    const timer = window.setInterval(() => {
      setFrame((prevFrame) => (prevFrame >= frameCount ? 1 : prevFrame + 1));
    }, interval);

    // Preload first 24 frames
    for (let index = 1; index <= Math.min(frameCount, 24); index += 1) {
      if (typeof window !== "undefined") {
        const image = new window.Image();
        image.src = `${basePath}/ezgif-frame-${String(index).padStart(3, "0")}.jpg`;
      }
    }

    return () => {
      window.clearInterval(timer);
    };
  }, [fps, frameCount, basePath]);

  return (
    <Image
      src={frameSrc}
      alt={alt}
      fill
      className="object-cover object-center"
      unoptimized // Need to disable optimization for rapidly changing frames
      priority
    />
  );
}
