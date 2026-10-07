import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, CHAPTER_COUNT, FONT, W, ease, HEIGHT, WIDTH } from "./theme";

type Pt = readonly [number, number];
type Weight = keyof typeof W;

// ------------------------------------------------------------------ paper
export const Spine: React.FC<{ readonly chapter: number }> = ({ chapter }) => {
  const x = 58;
  const top = 150;
  const bottom = 830;
  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0 }}>
      <line x1={x} y1={top} x2={x} y2={bottom} stroke={C.rule} strokeWidth={2} />
      {Array.from({ length: CHAPTER_COUNT }, (_, i) => {
        const y = top + ((bottom - top) * i) / (CHAPTER_COUNT - 1);
        if (i + 1 === chapter) {
          return <circle key={i} cx={x} cy={y} r={9} fill={C.vermilion} />;
        }
        if (i + 1 < chapter) {
          return <circle key={i} cx={x} cy={y} r={5} fill={C.cobalt} />;
        }
        return <circle key={i} cx={x} cy={y} r={4} fill="none" stroke="#BEB6A8" strokeWidth={2} />;
      })}
    </svg>
  );
};

export const Paper: React.FC<{ readonly chapter: number; readonly spine?: boolean }> = ({ chapter, spine = true }) => (
  <AbsoluteFill style={{ backgroundColor: C.ivory }}>
    <Img src={staticFile("paper.png")} style={{ width: WIDTH, height: HEIGHT }} />
    {spine ? <Spine chapter={chapter} /> : null}
  </AbsoluteFill>
);

// ------------------------------------------------------------------- text
type Anchor = "l" | "c" | "r";
type VAnchor = "t" | "m" | "b";

export type TxtProps = {
  readonly x: number;
  readonly y: number;
  readonly size: number;
  readonly weight?: Weight;
  readonly color?: string;
  readonly p?: number;
  readonly rise?: number;
  readonly anchor?: Anchor;
  readonly v?: VAnchor;
  readonly maxW?: number;
  readonly lh?: number;
  readonly italic?: boolean;
  readonly upper?: boolean;
  readonly track?: number;
  readonly align?: "left" | "center" | "right";
  readonly children: React.ReactNode;
};

const TX: Record<Anchor, string> = { l: "0%", c: "-50%", r: "-100%" };
const TY: Record<VAnchor, string> = { t: "0%", m: "-50%", b: "-100%" };

/** Absolutely positioned text. (x, y) is the anchor point; `p` fades it in, `rise` lifts it while appearing. */
export const Txt: React.FC<TxtProps> = ({
  x, y, size, weight = "medium", color = C.charcoal, p = 1, rise = 0, anchor = "l", v = "t", maxW, lh = 1.25,
  italic = false, upper = false, track = 0, align, children,
}) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      translate: `${TX[anchor]} ${TY[v]}`,
      transform: rise ? `translateY(${(1 - ease(p)) * rise}px)` : undefined,
      opacity: p,
      fontFamily: FONT,
      fontSize: size,
      fontWeight: W[weight],
      fontStyle: italic ? "italic" : "normal",
      lineHeight: lh,
      letterSpacing: track ? `${track}em` : undefined,
      textTransform: upper ? "uppercase" : undefined,
      color,
      width: maxW,
      textAlign: align ?? (anchor === "c" ? "center" : anchor === "r" ? "right" : "left"),
      // text-wrap and white-space share the text-wrap-mode longhand: emit exactly one of them,
      // never an `undefined` key (React writes it as "" and that resets nowrap).
      ...(maxW ? { textWrap: "pretty" as const } : { whiteSpace: "nowrap" as const }),
    }}
  >
    {children}
  </div>
);

export const Kicker: React.FC<{ readonly label: string; readonly p?: number; readonly x?: number; readonly y?: number }> = ({
  label, p = 1, x = 130, y = 92,
}) => (
  <div style={{ position: "absolute", left: x, top: y, opacity: p, display: "flex", alignItems: "center", gap: 16 }}>
    <div style={{ width: 10, height: 26, backgroundColor: C.vermilion }} />
    <div style={{ fontFamily: FONT, fontSize: 24, fontWeight: W.demi, color: C.cobalt, textTransform: "uppercase", letterSpacing: "0.02em" }}>
      {label}
    </div>
  </div>
);

/** Section title (display weight) at the standard position. */
export const Title: React.FC<{ readonly text: string; readonly p?: number; readonly x?: number; readonly y?: number; readonly size?: number; readonly maxW?: number }> = ({
  text, p = 1, x = 130, y = 142, size = 57, maxW = 1640,
}) => (
  <Txt x={x} y={y} size={size} weight="demi" p={p} rise={18} maxW={maxW} lh={1.15}>
    {text}
  </Txt>
);

export const SourceLine: React.FC<{ readonly text: string; readonly p?: number; readonly y?: number; readonly x?: number }> = ({
  text, p = 1, y = 818, x = 130,
}) => (
  <Txt x={x} y={y} size={22} weight="medium" color={C.inkSoft} p={p}>
    {text}
  </Txt>
);

// ------------------------------------------------------------------ cards
type CardStyle = {
  readonly p?: number;
  readonly accent?: string;
  readonly fill?: string;
  readonly children?: React.ReactNode;
  readonly pad?: number | string;
  readonly style?: React.CSSProperties;
};

const cardFace = (accent: string, fill: string): React.CSSProperties => ({
  position: "relative",
  backgroundColor: fill,
  border: `2px solid ${accent}D9`,
  borderRadius: 14,
  boxShadow: `6px 8px 0 ${C.shadow}`,
  boxSizing: "border-box",
});

const AccentBar: React.FC<{ readonly accent: string }> = ({ accent }) => (
  <div style={{ position: "absolute", left: -2, top: 14, bottom: 14, width: 7, backgroundColor: accent }} />
);

/** Card at an absolute box (x0, y0)–(x1, y1), as in the V12 painters. */
export const Card: React.FC<CardStyle & { readonly x0: number; readonly y0: number; readonly x1: number; readonly y1: number }> = ({
  x0, y0, x1, y1, p = 1, accent = C.cobalt, fill = C.paper, children, pad = 0, style,
}) => (
  <div
    style={{
      ...cardFace(accent, fill),
      position: "absolute",
      left: x0,
      top: y0,
      width: x1 - x0,
      height: y1 - y0,
      opacity: p,
      padding: pad,
      ...style,
    }}
  >
    <AccentBar accent={accent} />
    {children}
  </div>
);

/** Card that takes part in flex/grid layout (height from content). */
export const FlowCard: React.FC<CardStyle> = ({ p = 1, accent = C.cobalt, fill = C.paper, children, pad = "30px 34px", style }) => (
  <div style={{ ...cardFace(accent, fill), opacity: p, padding: pad, ...style }}>
    <AccentBar accent={accent} />
    {children}
  </div>
);

// -------------------------------------------------------------------- svg
export const Svg: React.FC<{ readonly children: React.ReactNode }> = ({ children }) => (
  <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
    {children}
  </svg>
);

const dist = (a: Pt, b: Pt) => Math.hypot(b[0] - a[0], b[1] - a[1]);

/** Point at fraction `p` along the polyline, plus the drawn sub-polyline. */
const partial = (pts: readonly Pt[], p: number): Pt[] => {
  const seg = pts.slice(1).map((b, i) => dist(pts[i], b));
  let target = seg.reduce((s, x) => s + x, 0) * p;
  const out: Pt[] = [pts[0]];
  for (let i = 0; i < seg.length; i++) {
    if (target >= seg[i]) {
      out.push(pts[i + 1]);
      target -= seg[i];
      continue;
    }
    const r = target / Math.max(seg[i], 1e-6);
    out.push([pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r]);
    break;
  }
  return out;
};

/** The film's red participation thread: a polyline drawn progressively, with a round head. `p` is eased already. */
export const Thread: React.FC<{ readonly pts: readonly Pt[]; readonly p: number; readonly color?: string; readonly width?: number }> = ({
  pts, p, color = C.vermilion, width = 5,
}) => {
  if (p <= 0 || pts.length < 2) {
    return null;
  }
  const drawn = partial(pts, Math.min(1, p));
  const head = drawn[drawn.length - 1];
  return (
    <g>
      <polyline points={drawn.map((q) => q.join(",")).join(" ")} fill="none" stroke={color} strokeWidth={width} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={head[0]} cy={head[1]} r={width} fill={color} />
    </g>
  );
};

/** Straight arrow drawn from a to b; the head appears in the last 10%. `p` is eased already. */
export const Arrow: React.FC<{ readonly a: Pt; readonly b: Pt; readonly p: number; readonly color?: string; readonly width?: number; readonly head?: number }> = ({
  a, b, p, color = C.vermilion, width = 5, head = 16,
}) => {
  if (p <= 0) {
    return null;
  }
  const q: Pt = [a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p];
  const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
  const p1: Pt = [q[0] - head * Math.cos(ang - 0.5), q[1] - head * Math.sin(ang - 0.5)];
  const p2: Pt = [q[0] - head * Math.cos(ang + 0.5), q[1] - head * Math.sin(ang + 0.5)];
  return (
    <g>
      <line x1={a[0]} y1={a[1]} x2={q[0]} y2={q[1]} stroke={color} strokeWidth={width} strokeLinecap="round" />
      {p > 0.9 ? <polygon points={[q, p1, p2].map((v) => v.join(",")).join(" ")} fill={color} /> : null}
    </g>
  );
};

/** Underline that draws itself left→right (for highlighted phrases, strikes). */
export const DrawLine: React.FC<{ readonly a: Pt; readonly b: Pt; readonly p: number; readonly color?: string; readonly width?: number }> = ({
  a, b, p, color = C.vermilion, width = 5,
}) => (p <= 0 ? null : <line x1={a[0]} y1={a[1]} x2={a[0] + (b[0] - a[0]) * p} y2={a[1] + (b[1] - a[1]) * p} stroke={color} strokeWidth={width} strokeLinecap="round" />);

/** Inline highlight: text whose underline grows when `p` goes 0→1 (works inside wrapped paragraphs). */
export const Mark: React.FC<{ readonly p: number; readonly color?: string; readonly children: React.ReactNode }> = ({
  p, color = C.vermilion, children,
}) => (
  <span
    style={{
      backgroundImage: `linear-gradient(${color}, ${color})`,
      backgroundRepeat: "no-repeat",
      backgroundPosition: "0 92%",
      backgroundSize: `${Math.max(0, Math.min(1, p)) * 100}% 5px`,
      paddingBottom: 2,
    }}
  >
    {children}
  </span>
);
