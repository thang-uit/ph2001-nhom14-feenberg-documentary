import React, { createContext, useContext, useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import type { Word } from "../data/film";

/** cue(phrase, fallback) → shot-relative seconds when the narration first speaks `phrase` in this shot. */
export type CueFn = (phrase: string, fallback: number) => number;

type ShotInfo = { readonly start: number; readonly duration: number; readonly cue: CueFn; readonly chapter: number };

const ShotCtx = createContext<ShotInfo | null>(null);

// Same normalisation as the Python planner: lower-case, keep letters/digits/spaces.
const norm = (s: string) => s.toLowerCase().replace(/[^\p{L}\p{N}_ ]/gu, "").trim();

export const makeCue = (words: readonly Word[], start: number, end: number): CueFn => {
  const inShot = words.filter((w) => w.t >= start - 0.05 && w.t < end).map((w) => ({ t: w.t, w: norm(w.w) }));
  const cache = new Map<string, number | null>();
  return (phrase, fallback) => {
    if (!cache.has(phrase)) {
      const target = norm(phrase).split(/\s+/).filter(Boolean);
      let found: number | null = null;
      for (let i = 0; target.length && i <= inShot.length - target.length; i++) {
        if (target.every((tok, k) => inShot[i + k].w === tok)) {
          found = Math.max(0, inShot[i].t - start);
          break;
        }
      }
      cache.set(phrase, found);
    }
    const hit = cache.get(phrase);
    return hit === null || hit === undefined ? fallback : hit;
  };
};

export const ShotProvider: React.FC<{
  readonly words: readonly Word[];
  readonly start: number;
  readonly duration: number;
  readonly chapter: number;
  readonly children: React.ReactNode;
}> = ({ words, start, duration, chapter, children }) => {
  const value = useMemo(
    () => ({ start, duration, chapter, cue: makeCue(words, start, start + duration) }),
    [words, start, duration, chapter],
  );
  return <ShotCtx.Provider value={value}>{children}</ShotCtx.Provider>;
};

/** t: seconds since the shot started; D: shot duration (s); cue: narration-synced timing. */
export const useShot = () => {
  const ctx = useContext(ShotCtx);
  if (!ctx) {
    throw new Error("useShot() must be used inside <ShotProvider>");
  }
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { t: frame / fps, D: ctx.duration, cue: ctx.cue, chapter: ctx.chapter };
};
