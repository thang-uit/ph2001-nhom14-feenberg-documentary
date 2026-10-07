// Design tokens of the film ("Hồ sơ giấy ngà · Sợi chỉ đỏ"). One typeface: Avenir Next.
export const C = {
  ivory: "#F4EFE5",
  paper: "#FCF9F3",
  charcoal: "#24282B",
  cobalt: "#1B4A89",
  vermilion: "#CD4230",
  sage: "#708475",
  inkSoft: "#606468",
  rule: "#D6CEC0",
  shadow: "#CDC6B8",
  cobaltWash: "#E7ECF4",
  vermilionWash: "#FAE4DC",
  sand: "#ECE6DA",
} as const;

export const FONT = '"Avenir Next", "Avenir", sans-serif';

// Avenir Next weights available on macOS: 400 Regular, 500 Medium, 600 Demi Bold, 700 Bold, 400 italic.
export const W = { regular: 400, medium: 500, demi: 600, bold: 700 } as const;

export const WIDTH = 1920;
export const HEIGHT = 1080;
// Graphics keep content above this line: the bottom band belongs to subtitles.
export const SAFE_BOTTOM = 860;
export const CHAPTER_COUNT = 11;

export const clamp = (x: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, x));

// Smoothstep: the same easing the V12 painters used, so timings carry over.
export const ease = (x: number) => {
  const v = clamp(x);
  return v * v * (3 - 2 * v);
};

// Expo-out for movement (positions), smoothstep for opacity.
export const easeOut = (x: number) => {
  const v = clamp(x);
  return v === 1 ? 1 : 1 - Math.pow(2, -10 * v);
};

/** 0→1 as the element appears at `at` seconds over `dur` seconds. */
export const appear = (t: number, at: number, dur = 0.55) => ease((t - at) / dur);

/** Progress of a drawn line/thread starting at `at`, lasting `dur`. */
export const draw = (t: number, at: number, dur: number) => ease((t - at) / Math.max(dur, 1e-3));
