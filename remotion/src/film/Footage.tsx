
import React from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT, W } from "../kit/theme";
import type { ShotData } from "../data/film";

// AI clips: crop 1680×945 at (20,10) to remove the provider mark, then fill 1920×1080 (same as V11/V12).
const AI_SCALE = 1920 / 1680;
const TAG_SECONDS = 4;

const ChapterTag: React.FC<{ readonly label: string }> = ({ label }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [(TAG_SECONDS - 0.4) * fps, TAG_SECONDS * fps], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 70,
        top: 64,
        height: 54,
        padding: "0 30px 0 16px",
        display: "flex",
        alignItems: "center",
        gap: 16,
        borderRadius: 10,
        backgroundColor: "rgba(252, 249, 243, 0.9)",
        opacity,
      }}
    >
      <div style={{ width: 8, height: 26, backgroundColor: C.vermilion }} />
      <div style={{ fontFamily: FONT, fontSize: 26, fontWeight: W.demi, color: C.cobalt }}>{label}</div>
    </div>
  );
};

const AiLabel: React.FC = () => (
  <div
    style={{
      position: "absolute",
      right: 70,
      top: 68,
      height: 38,
      padding: "0 18px",
      display: "flex",
      alignItems: "center",
      borderRadius: 8,
      backgroundColor: "rgba(20, 22, 24, 0.59)",
      fontFamily: FONT,
      fontSize: 20,
      fontWeight: W.demi,
      color: "rgba(250, 246, 238, 0.92)",
      letterSpacing: "0.03em",
    }}
  >
    MINH HỌA BẰNG AI
  </div>
);

export const Footage: React.FC<{ readonly shot: ShotData }> = ({ shot }) => {
  const { fps } = useVideoConfig();
  const media: React.CSSProperties = shot.ai
    ? {
        position: "absolute",
        width: 1920 * AI_SCALE,
        height: 1080 * AI_SCALE,
        left: -20 * AI_SCALE,
        top: -10 * AI_SCALE,
        filter: "contrast(1.035) brightness(1.006) saturate(0.965)",
      }
    : {
        position: "absolute",
        width: 1920,
        height: 1080,
        objectFit: "cover",
        filter: "contrast(1.025) brightness(1.008) saturate(1.015)",
      };
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      {/* No digital zoom: footage stays at native 1080p sharpness. */}
      <OffthreadVideo src={staticFile(shot.ref)} trimBefore={Math.round(shot.srcStart * fps)} muted style={media} />
      {shot.tag ? <ChapterTag label={shot.tag} /> : null}
      {shot.ai ? <AiLabel /> : null}
    </AbsoluteFill>
  );
};
