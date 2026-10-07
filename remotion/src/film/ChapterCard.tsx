import React from "react";
import { useShot } from "../kit/shot";
import { C, appear, draw } from "../kit/theme";
import { Svg, Thread, Txt } from "../kit/ui";

export const ChapterCard: React.FC<{ readonly num: number; readonly name: string; readonly question: string }> = ({ num, name, question }) => {
  const { t } = useShot();
  const p = appear(t, 0.15, 0.7);
  const label = String(num).padStart(2, "0");
  const tx = 640;
  return (
    <>
      <Txt x={140} y={190} size={300} weight="bold" color={C.vermilion} p={p * 0.95} rise={30} lh={1}>
        {label}
      </Txt>
      <Txt x={tx} y={298} size={26} weight="demi" color={C.cobalt} p={appear(t, 0.35)} upper track={0.06}>
        Chương
      </Txt>
      <Txt x={tx} y={340} size={75} weight="bold" p={appear(t, 0.45)} rise={20} maxW={1880 - tx - 60} lh={1.12}>
        {name}
      </Txt>
      <Svg>
        <Thread pts={[[140, 640], [1780, 640]]} p={draw(t, 0.6, 1.6)} />
      </Svg>
      <Txt x={140} y={680} size={36} weight="medium" color={C.cobalt} p={appear(t, 1.2)} maxW={1500} lh={1.3}>
        {question}
      </Txt>
    </>
  );
};
