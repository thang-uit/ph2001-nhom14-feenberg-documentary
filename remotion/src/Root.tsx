import React from "react";
import { Composition, type CalculateMetadataFunction } from "remotion";
import { film } from "./data/film";
import { Film, ShotPreview } from "./film/Film";

type PreviewProps = { readonly index: number };

// The preview lasts exactly as long as the selected shot.
const previewMetadata: CalculateMetadataFunction<PreviewProps> = ({ props }) => {
  const shot = film.shots[Math.min(Math.max(0, props.index), film.shots.length - 1)];
  return { durationInFrames: shot.frames + shot.tail };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Film"
        component={Film}
        durationInFrames={film.durationInFrames}
        fps={film.fps}
        width={film.width}
        height={film.height}
      />
      <Composition
        id="Shot"
        component={ShotPreview}
        durationInFrames={150}
        fps={film.fps}
        width={film.width}
        height={film.height}
        defaultProps={{ index: 0 }}
        calculateMetadata={previewMetadata}
      />
    </>
  );
};
