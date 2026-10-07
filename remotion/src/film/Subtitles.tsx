import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT, W } from "../kit/theme";
import type { Cue } from "../data/film";

// Lines are pre-broken by the planner with the same Avenir Next Demi 40 metrics (≤2 lines, ≤1560 px).
export const Subtitles: React.FC<{ readonly cues: readonly Cue[] }> = ({ cues }) => {
  const frame = useCurrentFrame();
  const cue = cues.find((c) => frame >= c.from && frame < c.to);
  if (!cue) {
    return null;
  }
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 70,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          padding: "10px 32px 14px",
          borderRadius: 14,
          backgroundColor: "rgba(18, 20, 22, 0.71)",
          fontFamily: FONT,
          fontSize: 40,
          fontWeight: W.demi,
          lineHeight: "52px",
          color: "rgb(250, 247, 240)",
          textAlign: "center",
        }}
      >
        {cue.lines.map((line, i) => (
          <div key={i} style={{ whiteSpace: "nowrap" }}>
            {line}
          </div>
        ))}
      </div>
    </div>
  );
};
