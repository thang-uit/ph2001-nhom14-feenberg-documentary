import React from "react";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { film, type ShotData } from "../data/film";
import { GRAPHICS } from "../gfx/registry";
import { ShotProvider } from "../kit/shot";
import { C } from "../kit/theme";
import { Paper } from "../kit/ui";
import { ChapterCard } from "./ChapterCard";
import { Footage } from "./Footage";
import { Subtitles } from "./Subtitles";

const MissingGraphic: React.FC<{ readonly name: string }> = ({ name }) => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", color: C.vermilion, fontSize: 60 }}>
    Missing graphic: {name}
  </AbsoluteFill>
);

/** One shot's picture (without the dissolve), with its narration-synced clock. */
export const ShotBody: React.FC<{ readonly shot: ShotData }> = ({ shot }) => {
  const { fps } = useVideoConfig();
  const body = (() => {
    if (shot.kind === "F") {
      return <Footage shot={shot} />;
    }
    if (shot.kind === "C") {
      const meta = film.chapters[shot.chapter - 1];
      return (
        <>
          <Paper chapter={shot.chapter} />
          <ChapterCard num={meta.num} name={meta.name} question={meta.question} />
        </>
      );
    }
    const Graphic = GRAPHICS[shot.ref];
    return (
      <>
        <Paper chapter={shot.chapter} />
        {Graphic ? <Graphic /> : <MissingGraphic name={shot.ref} />}
      </>
    );
  })();
  return (
    <ShotProvider words={film.words} start={shot.from / fps} duration={shot.frames / fps} chapter={shot.chapter}>
      {body}
    </ShotProvider>
  );
};

/** Dissolve: each shot fades in over the previous one, whose tail keeps playing underneath. */
const Dissolve: React.FC<{ readonly first: boolean; readonly children: React.ReactNode }> = ({ first, children }) => {
  const frame = useCurrentFrame();
  const opacity = first
    ? 1
    : interpolate(frame, [0, film.transitionFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};

export const Film: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: C.ivory }}>
      {film.shots.map((shot, i) => (
        <Sequence key={shot.id} name={`${shot.id} ${shot.ref}`} from={shot.from} durationInFrames={shot.frames + shot.tail} premountFor={fps}>
          <Dissolve first={i === 0}>
            <ShotBody shot={shot} />
          </Dissolve>
        </Sequence>
      ))}
      <Subtitles cues={film.subtitles} />
    </AbsoluteFill>
  );
};

/** Single shot (no subtitles) for stills/QA: props.index selects the shot. */
export const ShotPreview: React.FC<{ readonly index: number }> = ({ index }) => {
  const shot = film.shots[Math.min(Math.max(0, index), film.shots.length - 1)];
  return (
    <AbsoluteFill style={{ backgroundColor: C.ivory }}>
      <ShotBody shot={shot} />
    </AbsoluteFill>
  );
};
