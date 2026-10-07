import React from "react";
import { useShot } from "../kit/shot";
import { C, FONT, W, appear, clamp, draw } from "../kit/theme";
import { Arrow, FlowCard, Kicker, Mark, SourceLine, Svg, Thread, Txt } from "../kit/ui";

// ------------------------------------------------------------------ shared
const BODY: React.CSSProperties = { fontFamily: FONT, color: C.charcoal };

/** Flow-layout column filling the content area (x 130–1790, y 142–800). */
const Stage: React.FC<{ readonly children: React.ReactNode; readonly top?: number; readonly bottom?: number; readonly gap?: number }> = ({
  children, top = 142, bottom = 800, gap = 0,
}) => (
  <div style={{ position: "absolute", left: 130, top, width: 1660, height: bottom - top, display: "flex", flexDirection: "column", gap }}>
    {children}
  </div>
);

const FlowTitle: React.FC<{ readonly p: number; readonly children: React.ReactNode; readonly size?: number }> = ({ p, children, size = 52 }) => (
  <div style={{ ...BODY, fontSize: size, fontWeight: W.demi, lineHeight: 1.15, opacity: p, translate: `0 ${(1 - p) * 18}px` }}>{children}</div>
);

/** Renders `text` with each highlight phrase wrapped in an underline that grows when the phrase is spoken. */
const Highlighted: React.FC<{ readonly text: string; readonly marks: readonly { phrase: string; p: number }[] }> = ({ text, marks }) => {
  const spans: { start: number; end: number; p: number }[] = [];
  for (const m of marks) {
    const i = text.toLowerCase().indexOf(m.phrase.toLowerCase());
    if (i >= 0) {
      spans.push({ start: i, end: i + m.phrase.length, p: m.p });
    }
  }
  spans.sort((a, b) => a.start - b.start);
  const out: React.ReactNode[] = [];
  let at = 0;
  spans.forEach((s, k) => {
    if (s.start < at) {
      return;
    }
    out.push(text.slice(at, s.start));
    out.push(
      <Mark key={k} p={s.p}>
        {text.slice(s.start, s.end)}
      </Mark>,
    );
    at = s.end;
  });
  out.push(text.slice(at));
  return <>{out}</>;
};

const Footer: React.FC<{ readonly text: string; readonly p: number; readonly y?: number; readonly color?: string; readonly size?: number; readonly center?: boolean }> = ({
  text, p, y = 776, color = C.vermilion, size = 39, center = false,
}) => (
  <Txt x={center ? 960 : 150} y={y} size={size} weight="bold" color={color} p={p} rise={12} anchor={center ? "c" : "l"} maxW={center ? 1600 : 1620} lh={1.2}>
    {text}
  </Txt>
);

// ---------------------------------------------------------------- pillars
type Col = { readonly head: string; readonly body: string; readonly key: string };

const pillars = (kick: string, heading: string, cols: readonly Col[], opts: { banner?: [string, string]; source?: string } = {}): React.FC => {
  const Pillars: React.FC = () => {
    const { t, cue } = useShot();
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        <Stage top={142} bottom={opts.source ? 790 : 800}>
          <FlowTitle p={appear(t, 0.2)}>{heading}</FlowTitle>
          {opts.banner ? (
            <div
              style={{
                ...BODY, marginTop: 30, padding: "16px 0", borderRadius: 12, backgroundColor: C.cobaltWash, color: C.cobalt,
                fontSize: 32, fontWeight: W.demi, textAlign: "center", opacity: appear(t, cue(opts.banner[1], 0.6)),
              }}
            >
              {opts.banner[0]}
            </div>
          ) : null}
          <div style={{ flex: 1, display: "flex", alignItems: "center" }}>
            <div style={{ display: "flex", gap: 40, width: "100%", alignItems: "stretch" }}>
              {cols.map((c, i) => {
                const p = appear(t, cue(c.key, 1.0 + i * 1.5));
                const accent = i % 2 ? C.vermilion : C.cobalt;
                return (
                  <FlowCard key={c.head} p={p} accent={accent} style={{ flex: 1, translate: `0 ${(1 - p) * 16}px` }}>
                    <div style={{ ...BODY, fontSize: cols.length > 3 ? 34 : 39, fontWeight: W.bold, color: accent, lineHeight: 1.15 }}>{c.head}</div>
                    <div style={{ ...BODY, fontSize: 31, fontWeight: W.medium, lineHeight: 1.32, marginTop: 18, textWrap: "pretty" }}>{c.body}</div>
                  </FlowCard>
                );
              })}
            </div>
          </div>
        </Stage>
        {opts.source ? <SourceLine text={opts.source} p={appear(t, 1.0)} y={812} /> : null}
      </>
    );
  };
  return Pillars;
};

// ------------------------------------------------------------------ quote
const quote = (kick: string, text: string, src: string, highlights: readonly string[] = [], size = 46, footer?: [string, string]): React.FC => {
  const Quote: React.FC = () => {
    const { t, D, cue } = useShot();
    const p = appear(t, 0.3, 0.8);
    const marks = highlights.map((h) => ({ phrase: h, p: draw(t, cue(h, 1e6), 0.7) }));
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        <div style={{ position: "absolute", left: 214, top: 190, width: 1500, height: footer ? 520 : 600, display: "flex", alignItems: "center" }}>
          <div style={{ display: "flex", gap: 38, alignItems: "stretch" }}>
            <div style={{ width: 8, backgroundColor: C.vermilion, scale: `1 ${p}`, transformOrigin: "top", flexShrink: 0 }} />
            <div style={{ opacity: p, translate: `0 ${(1 - p) * 12}px` }}>
              <div style={{ ...BODY, fontSize: size, fontStyle: "italic", fontWeight: W.regular, lineHeight: 1.42, textWrap: "pretty" }}>
                <Highlighted text={text} marks={marks} />
              </div>
              <div style={{ ...BODY, marginTop: 26, fontSize: 28, fontWeight: W.demi, color: C.cobalt, opacity: appear(t, 0.8) }}>— {src}</div>
            </div>
          </div>
        </div>
        {footer ? <Footer text={footer[0]} p={appear(t, cue(footer[1], D - 3))} /> : null}
      </>
    );
  };
  return Quote;
};

// --------------------------------------------------------------- document
type Row = { readonly art: string; readonly text: string; readonly key: string };

const documentCard = (kick: string, heading: string, rows: readonly Row[], src: string): React.FC => {
  const Doc: React.FC = () => {
    const { t, cue } = useShot();
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        <Stage top={142} bottom={800}>
          <FlowTitle p={appear(t, 0.2)}>{heading}</FlowTitle>
          <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <FlowCard p={appear(t, 0.3)} pad="34px 46px 34px 46px">
              <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", columnGap: 44, rowGap: 26 }}>
                {rows.map((r, i) => {
                  const p = appear(t, cue(r.key, 0.8 + i * 2.0));
                  return (
                    <React.Fragment key={r.art}>
                      <div style={{ ...BODY, fontSize: 28, fontWeight: W.bold, color: C.vermilion, opacity: p, paddingTop: 4, whiteSpace: "nowrap" }}>{r.art}</div>
                      <div style={{ ...BODY, fontSize: 32, fontWeight: W.medium, lineHeight: 1.3, opacity: p, textWrap: "pretty" }}>{r.text}</div>
                    </React.Fragment>
                  );
                })}
              </div>
            </FlowCard>
            <div style={{ ...BODY, marginTop: 22, fontSize: 22, fontWeight: W.medium, color: C.inkSoft, opacity: appear(t, 0.5) }}>{src}</div>
          </div>
        </Stage>
      </>
    );
  };
  return Doc;
};

// -------------------------------------------------------------- checklist
type Item = { readonly label: string; readonly key: string };
type Mode = "check" | "strike" | "number" | "question";

const CheckMark: React.FC<{ readonly size: number; readonly p: number }> = ({ size, p }) => (
  <svg width={size * 0.95} height={size} viewBox="0 0 38 40" style={{ opacity: p, flexShrink: 0, marginTop: size * 0.12 }}>
    <polyline points="3,22 14,32 35,8" fill="none" stroke={C.cobalt} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const checklist = (
  kick: string, heading: string, items: readonly Item[],
  opts: { mode?: Mode; footer?: [string, string]; size?: number; cols?: number } = {},
): React.FC => {
  const { mode = "check", size = 38, cols = 1 } = opts;
  const List: React.FC = () => {
    const { t, D, cue } = useShot();
    const perCol = Math.ceil(items.length / cols);
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        <Stage top={heading ? 142 : 160} bottom={opts.footer ? 740 : 800}>
          {heading ? <FlowTitle p={appear(t, 0.2)} size={heading.length > 60 ? 44 : 52}>{heading}</FlowTitle> : null}
          <div style={{ flex: 1, display: "flex", alignItems: "center", paddingLeft: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gridTemplateRows: `repeat(${perCol}, auto)`, gridAutoFlow: "column", columnGap: 60, rowGap: Math.round(size * 0.62), width: "100%" }}>
              {items.map((it, i) => {
                const at = cue(it.key, 0.9 + i * 0.9);
                const p = appear(t, at);
                const strike = mode === "strike" ? draw(t, at + 0.5, 0.5) : 0;
                return (
                  <div key={it.label} style={{ display: "flex", gap: 26, alignItems: "flex-start", opacity: p, translate: `${(1 - p) * -14}px 0` }}>
                    {mode === "check" ? <CheckMark size={size} p={1} /> : null}
                    {mode === "number" ? <div style={{ ...BODY, fontSize: size, fontWeight: W.bold, color: C.vermilion, lineHeight: 1.2, minWidth: size * 1.4 }}>{String(i + 1).padStart(2, "0")}</div> : null}
                    {mode === "question" ? <div style={{ ...BODY, fontSize: size + 4, fontWeight: W.bold, color: C.vermilion, lineHeight: 1.1, minWidth: size * 0.8 }}>?</div> : null}
                    {mode === "strike" ? <div style={{ ...BODY, fontSize: size, fontWeight: W.bold, color: C.vermilion, lineHeight: 1.2, minWidth: size * 0.9 }}>≠</div> : null}
                    <div style={{ position: "relative", ...BODY, fontSize: size, fontWeight: W.medium, lineHeight: 1.2, textWrap: "pretty" }}>
                      {it.label}
                      {mode === "strike" ? (
                        <div style={{ position: "absolute", left: -4, right: -4, top: "54%", height: 4, borderRadius: 2, backgroundColor: C.vermilion, scale: `${strike} 1`, transformOrigin: "left" }} />
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </Stage>
        {opts.footer ? <Footer text={opts.footer[0]} p={appear(t, cue(opts.footer[1], D - 3))} /> : null}
      </>
    );
  };
  return List;
};

// -------------------------------------------------------------- statement
const statement = (kick: string, text: string, highlights: readonly string[] = [], size = 54): React.FC => {
  const Statement: React.FC = () => {
    const { t, cue } = useShot();
    const p = appear(t, 0.3, 0.9);
    const marks = highlights.map((h) => ({ phrase: h, p: draw(t, cue(h, 1e6), 0.6) }));
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        <div style={{ position: "absolute", left: 180, top: 180, width: 1560, height: 600, display: "flex", alignItems: "center" }}>
          <div style={{ ...BODY, fontSize: size, fontWeight: W.demi, lineHeight: 1.34, opacity: p, translate: `0 ${(1 - p) * 14}px`, textWrap: "pretty" }}>
            <Highlighted text={text} marks={marks} />
          </div>
        </div>
      </>
    );
  };
  return Statement;
};

// --------------------------------------------------------------- split ≠
const splitNeq = (
  kick: string, left: [string, string], right: [string, string], keys: [string, string],
  note?: [string, string], sign = "≠",
): React.FC => {
  const Split: React.FC = () => {
    const { t, D, cue } = useShot();
    const sides = [left, right];
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        {sides.map(([head, body], i) => {
          const p = appear(t, cue(keys[i], 0.6 + i * 2));
          const accent = i === 0 ? C.cobalt : C.vermilion;
          return (
            <FlowCard key={head} p={p} accent={accent} pad="40px 44px" style={{ position: "absolute", left: 150 + i * 880, top: 200, width: 740, height: 480, translate: `0 ${(1 - p) * 16}px` }}>
              <div style={{ ...BODY, fontSize: 46, fontWeight: W.bold, color: accent, lineHeight: 1.12 }}>{head}</div>
              <div style={{ ...BODY, fontSize: 32, fontWeight: W.medium, lineHeight: 1.34, marginTop: 30, textWrap: "pretty" }}>{body}</div>
            </FlowCard>
          );
        })}
        <Txt x={960} y={440} size={110} weight="bold" color={C.vermilion} p={appear(t, cue(keys[1], 2.6))} anchor="c" v="m">
          {sign}
        </Txt>
        {note ? <Footer text={note[0]} p={appear(t, cue(note[1], D - 3))} y={740} color={C.charcoal} size={40} center /> : null}
      </>
    );
  };
  return Split;
};

// --------------------------------------------------------------- sediment
const sediment = (kick: string, topText: string, layers: readonly Item[], bottomKey: string): React.FC => {
  const Sediment: React.FC = () => {
    const { t, D, cue } = useShot();
    const palette = [C.cobalt, C.vermilion, C.sage, C.charcoal];
    const q = appear(t, cue(bottomKey, D - 3));
    return (
      <>
        <Kicker label={kick} p={appear(t, 0.1)} />
        <Txt x={960} y={300} size={48} weight="bold" color={C.vermilion} p={q} anchor="c" v="m">
          {topText}
        </Txt>
        <div style={{ position: "absolute", left: 420, top: 357, width: 1080, height: 6, backgroundColor: C.charcoal, opacity: q }} />
        {layers.map((l, i) => {
          const at = cue(l.key, 0.6 + i * 1.0);
          const p = appear(t, at, 0.9);
          const yFinal = 380 + i * 100;
          const y = 180 + (yFinal - 180) * clamp(1 - Math.pow(1 - clamp((t - at) / 1.2), 3));
          const color = palette[i % palette.length];
          return (
            <div
              key={l.label}
              style={{
                position: "absolute", left: 420, top: y, width: 1080, height: 82, borderRadius: 10, boxSizing: "border-box",
                border: `3px solid ${color}`, backgroundColor: C.sand, opacity: p, display: "flex", alignItems: "center", justifyContent: "center",
                ...BODY, fontSize: 32, fontWeight: W.demi, color,
              }}
            >
              {l.label}
            </div>
          );
        })}
      </>
    );
  };
  return Sediment;
};

// -------------------------------------------------------- new V13 graphics
/** Rights × participation-level matrix (Group 14's analytic frame). */
const RightsMatrix: React.FC = () => {
  const { t, D, cue } = useShot();
  const levels = [
    { name: "Chưa có", key: "chưa có", color: C.inkSoft },
    { name: "Hình thức", key: "hình thức", color: C.sage },
    { name: "Có hiệu lực", key: "có hiệu lực", color: C.cobalt },
  ];
  const rows = [
    { right: "Được biết", key: "được biết", cells: ["Không công bố", "Công bố khó hiểu, khó tìm", "Đủ để hiểu: dữ liệu nào, để làm gì, ai xem"] },
    { right: "Được tham vấn", key: "được tham vấn", cells: ["Không hỏi ý kiến", "Hỏi nhưng không trả lời", "Tham vấn sớm, trả lời có lý do"] },
    { right: "Được cùng quyết định", key: "được cùng quyết định", cells: ["Không có tiếng nói", "Biểu quyết sau khi đã chốt", "Ý kiến có sức nặng trong phạm vi được trao"] },
    { right: "Được giám sát, yêu cầu sửa đổi", key: "được giám sát", cells: ["Không có kênh", "Có kênh, không có hạn trả lời", "Kết quả giám sát buộc phải khắc phục"] },
  ];
  const x0 = 130;
  const top = 196;
  const headW = 380;
  const colW = 410;
  const headH = 64;
  const rowH = 128;
  const gap = 10;
  const colsAt = levels.map((l, j) => cue(l.key, 3 + j * 0.6));
  const emph = cue("tham vấn có trả lời", D - 6);
  const pe = appear(t, emph);
  const pd = appear(t, cue("hai quyền khác nhau", emph + 2));
  const cellX = (j: number) => x0 + headW + gap + j * (colW + gap);
  const rowY = (i: number) => top + headH + gap + i * (rowH + gap);
  return (
    <>
      <Kicker label="Ma trận quyền × mức độ tham gia — khung phân tích của Nhóm 14" p={appear(t, 0.1)} />
      {levels.map((l, j) => (
        <div key={l.name} style={{ position: "absolute", left: cellX(j), top, width: colW, height: headH, borderRadius: 10, backgroundColor: l.color, opacity: appear(t, colsAt[j]), display: "flex", alignItems: "center", justifyContent: "center", ...BODY, fontSize: 28, fontWeight: W.demi, color: C.paper, letterSpacing: "0.02em" }}>
          {l.name.toUpperCase()}
        </div>
      ))}
      {rows.map((r, i) => {
        const pr = appear(t, cue(r.key, 0.8 + i * 0.7));
        return (
          <React.Fragment key={r.right}>
            <div style={{ position: "absolute", left: x0, top: rowY(i), width: headW, height: rowH, boxSizing: "border-box", borderLeft: `7px solid ${i === 2 ? C.vermilion : C.cobalt}`, padding: "0 22px", display: "flex", alignItems: "center", opacity: pr, ...BODY, fontSize: 32, fontWeight: W.bold, lineHeight: 1.15 }}>
              {r.right}
            </div>
            {r.cells.map((c, j) => {
              const pc = Math.min(pr, appear(t, colsAt[j] + 0.2));
              const hot = i === 1 && j === 2;
              return (
                <div
                  key={c}
                  style={{
                    position: "absolute", left: cellX(j), top: rowY(i), width: colW, height: rowH, boxSizing: "border-box", borderRadius: 10,
                    backgroundColor: j === 2 ? C.cobaltWash : C.paper, border: `2px solid ${hot && pe > 0 ? C.vermilion : C.rule}`,
                    boxShadow: hot ? `0 0 0 ${4 * pe}px ${C.vermilion}` : undefined, padding: "0 24px", display: "flex", alignItems: "center",
                    opacity: pc, ...BODY, fontSize: 26, fontWeight: W.medium, lineHeight: 1.25, color: j === 0 ? C.inkSoft : C.charcoal, textWrap: "pretty",
                  }}
                >
                  {c}
                </div>
              );
            })}
          </React.Fragment>
        );
      })}
      {/* "Consultation with answers" (row 2, top level) is not co-decision (row 3): two different rights. */}
      <div style={{ position: "absolute", left: x0 - 4, top: rowY(2) - 4, width: headW + 3 * (colW + gap) + 8, height: rowH + 8, borderRadius: 12, border: `3px dashed ${C.vermilion}`, opacity: pe * 0.9, boxSizing: "border-box" }} />
      <Txt x={960} y={rowY(3) + rowH + 30} size={34} weight="bold" color={C.vermilion} p={pd} anchor="c">
        Tham vấn có trả lời ≠ cùng quyết định — hai quyền khác nhau
      </Txt>
    </>
  );
};

/** Four-question test for a design change; with `answers`, the AIDS case fills them in. */
const changeTest = (answers?: readonly { text: string; key: string }[]): React.FC => {
  const Test: React.FC = () => {
    const { t, D, cue } = useShot();
    const qs = [
      { q: "Từ kinh nghiệm của ai?", key: "kinh nghiệm của ai" },
      { q: "Qua quy trình nào?", key: "quy trình nào" },
      { q: "Vì lợi ích của ai?", key: "lợi ích của ai" },
      { q: "Ai giải trình?", key: "giải trình" },
    ];
    const risks = [
      { label: "Ý muốn của người quản lý", key: "ý muốn" },
      { label: "Nhóm có tiếng nói mạnh nhất", key: "tiếng nói mạnh nhất" },
      { label: "Làm hại nhóm yếu thế", key: "nhóm yếu thế" },
    ];
    const finale = answers ? appear(t, cue("con đường từ phản hồi", D - 3)) : 0;
    return (
      <>
        <Kicker label={answers ? "Đặt tình huống vào phép thử bốn câu hỏi" : "Một thay đổi thiết kế chưa tự chứng minh tính dân chủ"} p={appear(t, 0.1)} />
        <Txt x={130} y={142} size={52} weight="demi" p={appear(t, 0.2)} rise={18}>
          {answers ? "Vì sao đây là dân chủ hóa?" : "Phép thử bốn câu hỏi"}
        </Txt>
        {!answers ? (
          <div style={{ position: "absolute", left: 130, top: 236, display: "flex", gap: 18, alignItems: "center" }}>
            <div style={{ ...BODY, fontSize: 26, fontWeight: W.demi, color: C.inkSoft, opacity: appear(t, cue(risks[0].key, 1)) }}>Thay đổi có thể chỉ đến từ:</div>
            {risks.map((r, i) => (
              <div key={r.label} style={{ ...BODY, fontSize: 26, fontWeight: W.demi, color: C.vermilion, padding: "8px 18px", borderRadius: 999, border: `2px solid ${C.vermilion}`, backgroundColor: C.vermilionWash, opacity: appear(t, cue(r.key, 1.5 + i)) }}>
                {r.label}
              </div>
            ))}
          </div>
        ) : null}
        <div style={{ position: "absolute", left: 130, top: answers ? 250 : 320, width: 1660, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 30 }}>
          {qs.map((q, i) => {
            const pq = appear(t, answers ? 0.4 + i * 0.25 : cue(q.key, 4 + i));
            const a = answers?.[i];
            const pa = a ? appear(t, cue(a.key, 1.5 + i * 2.5)) : 0;
            return (
              <FlowCard key={q.q} p={pq} accent={i % 2 ? C.vermilion : C.cobalt} pad="28px 28px 30px 32px" style={{ minHeight: answers ? 360 : 300, translate: `0 ${(1 - pq) * 16}px` }}>
                <div style={{ ...BODY, fontSize: 30, fontWeight: W.bold, color: C.vermilion }}>{String(i + 1).padStart(2, "0")}</div>
                <div style={{ ...BODY, fontSize: 36, fontWeight: W.bold, lineHeight: 1.18, marginTop: 10 }}>{q.q}</div>
                {a ? (
                  <div style={{ display: "flex", gap: 12, marginTop: 22, opacity: pa }}>
                    <CheckMark size={30} p={1} />
                    <div style={{ ...BODY, fontSize: 27, fontWeight: W.medium, lineHeight: 1.3, color: C.cobalt, textWrap: "pretty" }}>{a.text}</div>
                  </div>
                ) : null}
              </FlowCard>
            );
          })}
        </div>
        {answers ? (
          <>
            <Svg>
              <Thread pts={[[470, 712], [1450, 712]]} p={draw(t, cue("con đường từ phản hồi", D - 3), 1.2)} />
            </Svg>
            <Txt x={440} y={712} size={34} weight="bold" color={C.cobalt} p={finale} anchor="r" v="m">PHẢN HỒI</Txt>
            <Txt x={1480} y={712} size={34} weight="bold" color={C.vermilion} p={finale} anchor="l" v="m">SỬA THIẾT KẾ</Txt>
          </>
        ) : (
          <Footer text="Thay đổi thiết kế ≠ bằng chứng dân chủ" p={appear(t, cue("ai chịu trách nhiệm giải trình", D - 2.5))} y={700} />
        )}
      </>
    );
  };
  return Test;
};

/** Public power exercised through technical systems: activities → technical rules → consequences. */
const PowerBridge: React.FC = () => {
  const { t, D, cue } = useShot();
  const cols = [
    { head: "Quyền lực công", color: C.cobalt, items: [["Xác thực danh tính", "xác thực danh tính"], ["Cấp giấy tờ", "cấp giấy tờ"], ["Xét điều kiện hưởng chính sách", "xét điều kiện"], ["Xử lý dữ liệu công dân", "xử lý dữ liệu"]] },
    { head: "Quy tắc kỹ thuật", color: C.vermilion, items: [["Trường dữ liệu bắt buộc", "trường dữ liệu bắt buộc"], ["Tiêu chí phân loại", "tiêu chí phân loại"], ["Mức phân quyền", "mức phân quyền"]] },
    { head: "Hệ quả với người dân", color: C.charcoal, items: [["Ai được phục vụ", "ai được phục vụ"], ["Ai bị từ chối", "bị từ chối"], ["Ai được xem dữ liệu", "được xem dữ liệu"], ["Ai có thể khiếu nại", "có thể khiếu nại"]] },
  ] as const;
  const colX = [150, 735, 1320];
  const colW = 450;
  return (
    <>
      <Kicker label="Cầu nối: quyền lực công đi qua hệ thống kỹ thuật" p={appear(t, 0.1)} />
      {cols.map((c, j) => {
        const first = cue(c.items[0][1], 0.6 + j * 3);
        return (
          <React.Fragment key={c.head}>
            <Txt x={colX[j]} y={170} size={30} weight="bold" color={c.color} p={appear(t, first - 0.2)} upper track={0.03}>
              {c.head}
            </Txt>
            {c.items.map(([label, key], i) => {
              const p = appear(t, cue(key, first + i * 0.8));
              return (
                <FlowCard key={label} p={p} accent={c.color === C.charcoal ? C.cobalt : c.color} pad="0 26px" style={{ position: "absolute", left: colX[j], top: 228 + i * 116, width: colW, height: 92, display: "flex", alignItems: "center" }}>
                  <div style={{ ...BODY, fontSize: 30, fontWeight: W.demi, lineHeight: 1.15 }}>{label}</div>
                </FlowCard>
              );
            })}
          </React.Fragment>
        );
      })}
      <Svg>
        <Arrow a={[612, 390]} b={[722, 390]} p={draw(t, cue(cols[1].items[0][1], 4), 0.6)} color={C.vermilion} />
        <Arrow a={[1197, 390]} b={[1307, 390]} p={draw(t, cue(cols[2].items[0][1], 7), 0.6)} color={C.vermilion} />
      </Svg>
      <Footer text="Quy tắc kỹ thuật tác động như một quyết định quản lý." p={appear(t, cue("tác động như", D - 3))} y={730} center />
    </>
  );
};

/** Feenberg 1992 p. 301 + the group's own step from Lenin's definition. */
const FeenPower: React.FC = () => {
  const { t, D, cue } = useShot();
  const p = appear(t, 0.3, 0.8);
  const pa = appear(t, cue("nhóm em lập luận", D * 0.45));
  const pb = appear(t, cue("vươn tới", D * 0.6));
  return (
    <>
      <Kicker label="Feenberg (1992) · Subversive Rationalization, Inquiry 35, tr. 301" p={appear(t, 0.1)} />
      <div style={{ position: "absolute", left: 214, top: 170, width: 1500, display: "flex", gap: 38 }}>
        <div style={{ width: 8, backgroundColor: C.vermilion, scale: `1 ${p}`, transformOrigin: "top" }} />
        <div style={{ opacity: p }}>
          <div style={{ ...BODY, fontSize: 52, fontStyle: "italic", lineHeight: 1.3 }}>
            Công nghệ là một trong những nguồn <Mark p={draw(t, cue("nguồn quyền lực công", 1e6), 0.7)}>quyền lực công</Mark> chủ yếu của xã hội hiện đại.
          </div>
          <div style={{ ...BODY, marginTop: 16, fontSize: 26, fontStyle: "italic", color: C.inkSoft }}>
            “Technology is one of the major sources of public power in modern societies.”
          </div>
        </div>
      </div>
      <Txt x={150} y={500} size={24} weight="demi" color={C.cobalt} p={pa} upper track={0.04}>
        Lập luận của Nhóm 14
      </Txt>
      <FlowCard p={pa} accent={C.cobalt} pad="0 30px" style={{ position: "absolute", left: 150, top: 548, width: 690, height: 150, display: "flex", alignItems: "center" }}>
        <div style={{ ...BODY, fontSize: 31, fontWeight: W.demi, lineHeight: 1.25 }}>Dân chủ: quyền ngang nhau của công dân trong quản lý nhà nước (Lênin)</div>
      </FlowCard>
      <Svg>
        <Arrow a={[862, 623]} b={[1040, 623]} p={draw(t, cue("vươn tới", D * 0.6), 0.6)} color={C.vermilion} width={6} />
      </Svg>
      <FlowCard p={pb} accent={C.vermilion} pad="0 30px" style={{ position: "absolute", left: 1062, top: 548, width: 710, height: 150, display: "flex", alignItems: "center" }}>
        <div style={{ ...BODY, fontSize: 31, fontWeight: W.demi, lineHeight: 1.25 }}>Phải vươn tới cả hệ thống kỹ thuật mà qua đó quyền lực công được thực hiện</div>
      </FlowCard>
    </>
  );
};

/** Participant interests and Feenberg's three paths of democratic intervention. */
const Paths: React.FC = () => {
  const { t, cue } = useShot();
  const pc = appear(t, cue("lợi ích của người tham gia", 0.5));
  const paths = [
    { head: "Tranh luận công khai", body: "về công nghệ, buộc thiết kế phải thay đổi", key: "tranh luận công khai" },
    { head: "Đối thoại chuyên gia – người dùng", body: "như trong thiết kế có sự tham gia", key: "đối thoại" },
    { head: "Chiếm dụng sáng tạo", body: "người dùng tạo chức năng mới cho công nghệ sẵn có", key: "chiếm dụng sáng tạo" },
  ];
  const ys = [190, 380, 570];
  return (
    <>
      <Kicker label="Feenberg · lợi ích của người tham gia và ba con đường" p={appear(t, 0.1)} />
      <FlowCard p={pc} accent={C.vermilion} fill={C.vermilionWash} pad="34px 36px" style={{ position: "absolute", left: 150, top: 300, width: 560, height: 280, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ ...BODY, fontSize: 42, fontWeight: W.bold, lineHeight: 1.15 }}>Lợi ích của người tham gia</div>
        <div style={{ ...BODY, fontSize: 28, fontWeight: W.medium, lineHeight: 1.3, marginTop: 16, color: C.inkSoft, opacity: appear(t, cue("vị trí ấy", 2)) }}>
          nảy sinh từ chính vị trí của họ trong hệ thống kỹ thuật
        </div>
      </FlowCard>
      <Svg>
        {paths.map((pa, i) => (
          <Thread key={pa.key} pts={[[712, 440], [800, 440], [800, ys[i] + 75], [880, ys[i] + 75]]} p={draw(t, cue(pa.key, 3 + i * 2), 0.8)} />
        ))}
      </Svg>
      {paths.map((pa, i) => {
        const p = appear(t, cue(pa.key, 3 + i * 2) + 0.4);
        return (
          <FlowCard key={pa.key} p={p} accent={C.cobalt} pad="0 32px" style={{ position: "absolute", left: 890, top: ys[i], width: 880, height: 150, display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div style={{ ...BODY, fontSize: 36, fontWeight: W.bold, color: C.cobalt }}>{`${i + 1}. ${pa.head}`}</div>
            <div style={{ ...BODY, fontSize: 28, fontWeight: W.medium, marginTop: 8 }}>{pa.body}</div>
          </FlowCard>
        );
      })}
      <SourceLine text="Feenberg (1992), Philosophical Forum 23(3), tr. 217–218 · Bakardjieva & Feenberg (2002), The Information Society 18(3), tr. 187" p={appear(t, 1)} y={770} />
    </>
  );
};

/** AIDS case, part 1: the original trial design (Feenberg's analysis). */
const CaseBefore: React.FC = () => {
  const { t, D, cue } = useShot();
  const pBox = appear(t, cue("thử nghiệm lâm sàng", 0.6));
  const chips = [
    { label: "Rất ít chỗ", key: "số chỗ" },
    { label: "Điều kiện tham gia rất chặt", key: "điều kiện tham gia" },
    { label: "Một phần nhận giả dược", key: "giả dược" },
  ];
  const outside = Array.from({ length: 24 }, (_, k) => [1250 + (k % 6) * 72, 300 + Math.floor(k / 6) * 72] as const);
  const pOut = appear(t, cue("đối tượng thụ động", D * 0.6));
  return (
    <>
      <Kicker label="Mỹ, cuối thập niên 1980 · tình huống do Feenberg phân tích" p={appear(t, 0.1)} />
      <Txt x={130} y={142} size={50} weight="demi" p={appear(t, 0.2)} rise={18}>
        Thiết kế ban đầu của thử nghiệm thuốc
      </Txt>
      <FlowCard p={pBox} accent={C.cobalt} pad="26px 30px" style={{ position: "absolute", left: 150, top: 250, width: 900, height: 330 }}>
        <div style={{ ...BODY, fontSize: 30, fontWeight: W.bold, color: C.cobalt }}>Thử nghiệm lâm sàng có đối chứng</div>
        <div style={{ display: "flex", gap: 24, marginTop: 24 }}>
          {["Nhóm dùng thuốc thử", "Nhóm giả dược"].map((g, i) => (
            <div key={g} style={{ flex: 1, height: 150, borderRadius: 10, border: `2px dashed ${i ? C.vermilion : C.cobalt}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14, opacity: i ? appear(t, cue("giả dược", 3)) : 1 }}>
              <div style={{ display: "flex", gap: 12 }}>
                {[0, 1, 2].map((k) => (
                  <div key={k} style={{ width: 22, height: 22, borderRadius: 11, backgroundColor: i ? C.vermilion : C.cobalt }} />
                ))}
              </div>
              <div style={{ ...BODY, fontSize: 26, fontWeight: W.demi }}>{g}</div>
            </div>
          ))}
        </div>
      </FlowCard>
      <div style={{ position: "absolute", left: 150, top: 612, display: "flex", gap: 16 }}>
        {chips.map((c, i) => (
          <div key={c.label} style={{ ...BODY, fontSize: 26, fontWeight: W.demi, color: C.charcoal, padding: "10px 20px", borderRadius: 999, backgroundColor: C.sand, border: `2px solid ${C.rule}`, opacity: appear(t, cue(c.key, 2 + i)) }}>
            {c.label}
          </div>
        ))}
      </div>
      <Svg>
        <line x1={1170} y1={260} x2={1170} y2={580} stroke={C.charcoal} strokeWidth={4} strokeDasharray="14 10" opacity={pOut} />
        {outside.map(([x, y], k) => (
          <circle key={k} cx={x} cy={y} r={14} fill="none" stroke={C.inkSoft} strokeWidth={3} opacity={appear(t, cue("đối tượng thụ động", D * 0.6) - 0.6 + k * 0.03)} />
        ))}
      </Svg>
      <Txt x={1490} y={600} size={26} weight="demi" color={C.inkSoft} p={pOut} anchor="c">
        Người bệnh ngoài thử nghiệm
      </Txt>
      <Footer text="Người bệnh: đối tượng thụ động · mong muốn tham gia bị coi là không hợp lý" p={appear(t, cue("không hợp lý", D - 2.5))} y={700} size={34} />
      <SourceLine text="Feenberg (1992), Philosophical Forum 23(3), tr. 214–216 · Feenberg (2008), Social Epistemology 22(1), tr. 25" p={appear(t, 1)} y={790} />
    </>
  );
};

/** AIDS case, part 2: channels of voice and the dated institutional changes. */
const CaseTimeline: React.FC = () => {
  const { t, cue } = useShot();
  const voices = [
    { label: "Tự học về thuốc và quy trình", key: "tự học" },
    { label: "Yêu cầu cụ thể tới cơ quan quản lý", key: "yêu cầu cụ thể" },
    { label: "Biểu tình trước trụ sở FDA (10/1988)", key: "biểu tình" },
  ];
  const events = [
    { year: "1987", x: 380, text: "Quy định cho dùng thuốc đang thử nghiệm để điều trị, ngoài thử nghiệm chính thức", key: "năm 1987" },
    { year: "10/1988", x: 900, text: "Hơn một nghìn người tập trung trước trụ sở FDA", key: "tháng 10 năm 1988" },
    { year: "1992", x: 1450, text: "“Đường song song” cho người ngoài thử nghiệm + cơ chế phê duyệt nhanh", key: "năm 1992" },
  ];
  const axisY = 520;
  const tEnd = cue("năm 1992", 20);
  return (
    <>
      <Kicker label="Từ kinh nghiệm đến thay đổi thể chế" p={appear(t, 0.1)} />
      <Txt x={130} y={142} size={34} weight="demi" color={C.cobalt} p={appear(t, cue(voices[0].key, 0.5))} upper track={0.03}>
        Người bệnh lên tiếng tập thể
      </Txt>
      <div style={{ position: "absolute", left: 130, top: 200, display: "flex", gap: 22 }}>
        {voices.map((v, i) => (
          <FlowCard key={v.label} p={appear(t, cue(v.key, 1 + i * 1.5))} accent={C.vermilion} pad="18px 26px" style={{ width: 520 }}>
            <div style={{ ...BODY, fontSize: 28, fontWeight: W.demi, lineHeight: 1.2 }}>{v.label}</div>
          </FlowCard>
        ))}
      </div>
      <Txt x={130} y={392} size={30} weight="demi" color={C.inkSoft} p={appear(t, cue("dưới sức ép", 8))}>
        Dưới sức ép chính trị (Feenberg: 1987–1989), thể chế thay đổi từng bước
      </Txt>
      <Svg>
        <line x1={150} y1={axisY} x2={1770} y2={axisY} stroke={C.rule} strokeWidth={4} />
        <Thread pts={[[150, axisY], [1770, axisY]]} p={draw(t, cue("năm 1987", 9), Math.max(1, tEnd - cue("năm 1987", 9) + 0.8))} />
        {events.map((e) => (
          <circle key={e.year} cx={e.x} cy={axisY} r={16} fill={C.paper} stroke={C.vermilion} strokeWidth={5} opacity={appear(t, cue(e.key, 9))} />
        ))}
      </Svg>
      {events.map((e) => {
        const p = appear(t, cue(e.key, 9));
        return (
          <React.Fragment key={e.year}>
            <Txt x={e.x} y={axisY - 34} size={40} weight="bold" color={C.vermilion} p={p} anchor="c" v="b">
              {e.year}
            </Txt>
            <Txt x={e.x} y={axisY + 40} size={27} weight="medium" p={p} rise={10} anchor="c" maxW={440} lh={1.3}>
              {e.text}
            </Txt>
          </React.Fragment>
        );
      })}
      <SourceLine text="Nguồn: FDA; Federal Register 52 FR 19466 (1987), 57 FR 13250 và 57 FR 58942 (1992); Feenberg (1992), Philosophical Forum, tr. 215" p={appear(t, 1)} y={790} />
    </>
  );
};

/** AIDS case, part 3: Feenberg's verdict and its limits. */
const CaseQuote: React.FC = () => {
  const { t, D, cue } = useShot();
  const p = appear(t, 0.3, 0.8);
  const text =
    "Vì không thể có được sự hợp tác ổn định của người bệnh theo các quy trình đang áp dụng, người bệnh cuối cùng đã buộc thiết kế thử nghiệm phải thay đổi, thêm mục tiêu chăm sóc số đông người bệnh vào mục đích khoa học. Những thay đổi như vậy mang tính dân chủ và tiến bộ.";
  const marks = [
    { phrase: "buộc thiết kế thử nghiệm phải thay đổi", p: draw(t, cue("buộc thiết kế", 1e6), 0.7) },
    { phrase: "mang tính dân chủ và tiến bộ", p: draw(t, cue("dân chủ và tiến bộ", 1e6), 0.7) },
  ];
  const pl = appear(t, cue("không phải chiến thắng", D * 0.6));
  return (
    <>
      <Kicker label="Feenberg (2008) · Social Epistemology 22(1), tr. 25 — lược dịch" p={appear(t, 0.1)} />
      <div style={{ position: "absolute", left: 214, top: 175, width: 1500, display: "flex", gap: 38 }}>
        <div style={{ width: 8, backgroundColor: C.vermilion, scale: `1 ${p}`, transformOrigin: "top", flexShrink: 0 }} />
        <div style={{ ...BODY, opacity: p, fontSize: 40, fontStyle: "italic", lineHeight: 1.42, textWrap: "pretty" }}>
          <Highlighted text={text} marks={marks} />
        </div>
      </div>
      <FlowCard p={pl} accent={C.charcoal} fill={C.sand} pad="22px 34px" style={{ position: "absolute", left: 214, top: 600, width: 1520 }}>
        <div style={{ ...BODY, fontSize: 26, fontWeight: W.demi, color: C.inkSoft, letterSpacing: "0.03em" }}>GIỚI HẠN</div>
        <div style={{ ...BODY, fontSize: 30, fontWeight: W.medium, lineHeight: 1.3, marginTop: 6 }}>
          Giới nghiên cứu lo dữ liệu kém tin cậy hơn · tranh luận giữa tiếp cận nhanh và kiểm chứng khoa học vẫn tiếp diễn
        </div>
      </FlowCard>
    </>
  );
};

/** Efficient management and rights protection are not always opposed. */
const WinWin: React.FC = () => {
  const { t, D, cue } = useShot();
  const rows = [
    { choice: "Thu dữ liệu tối thiểu", gov: "Ít chi phí lưu trữ", rights: "Ít rủi ro lộ dữ liệu", key: "thu ít hơn" },
    { choice: "Nhật ký truy cập", gov: "Phát hiện tra cứu trái phép", rights: "Biết ai đã xem hồ sơ", key: "nhật ký truy cập" },
    { choice: "Kênh sửa dữ liệu sai", gov: "Cơ sở dữ liệu chính xác hơn", rights: "Được sửa sai", key: "kênh sửa dữ liệu" },
  ];
  const ph = appear(t, cue("cải thiện cả hai", 1));
  const top = 320;
  const rowH = 128;
  return (
    <>
      <Kicker label="Quản lý hiệu quả và bảo vệ quyền: không luôn đối lập" p={appear(t, 0.1)} />
      <Txt x={130} y={142} size={52} weight="demi" p={ph} rise={18}>
        Thiết kế tốt có thể cải thiện cả hai
      </Txt>
      <Txt x={1040} y={270} size={26} weight="bold" color={C.cobalt} p={ph} anchor="c" upper track={0.03}>Quản lý hiệu quả</Txt>
      <Txt x={1520} y={270} size={26} weight="bold" color={C.vermilion} p={ph} anchor="c" upper track={0.03}>Bảo vệ quyền người dân</Txt>
      {rows.map((r, i) => {
        const at = cue(r.key, 3 + i * 4);
        const p = appear(t, at);
        const y = top + i * (rowH + 16);
        return (
          <React.Fragment key={r.choice}>
            <FlowCard p={p} accent={C.charcoal} pad="0 28px" style={{ position: "absolute", left: 150, top: y, width: 560, height: rowH, display: "flex", alignItems: "center" }}>
              <div style={{ ...BODY, fontSize: 34, fontWeight: W.bold }}>{r.choice}</div>
            </FlowCard>
            {[r.gov, r.rights].map((txt, k) => (
              <div key={txt} style={{ position: "absolute", left: 820 + k * 480, top: y + 14, width: 440, height: rowH - 28, borderRadius: 12, backgroundColor: k ? C.vermilionWash : C.cobaltWash, display: "flex", alignItems: "center", gap: 14, padding: "0 22px", boxSizing: "border-box", opacity: appear(t, at + 0.4 + k * 0.4) }}>
                <CheckMark size={30} p={1} />
                <div style={{ ...BODY, fontSize: 29, fontWeight: W.demi, lineHeight: 1.2 }}>{txt}</div>
              </div>
            ))}
          </React.Fragment>
        );
      })}
      <Svg>
        {rows.map((r, i) => {
          const at = cue(r.key, 3 + i * 4);
          const y = top + i * (rowH + 16) + rowH / 2;
          return <Arrow key={r.key} a={[716, y]} b={[808, y]} p={draw(t, at + 0.2, 0.4)} color={C.vermilion} />;
        })}
      </Svg>
      <SourceLine text="Thu thập đúng phạm vi, mục đích: Luật 91/2025/QH15, Điều 3 k.2 · Xung đột thật: Hiến pháp 2013, Điều 14 k.2 (hạn chế quyền chỉ theo luật, khi cần thiết)" p={appear(t, cue("xung đột thật", D - 4))} y={770} />
    </>
  );
};

/** Who supervises / who may request changes / who must remedy (current law). */
const Accountability: React.FC = () => {
  const { t, cue } = useShot();
  const cols = [
    { head: "Ai giám sát?", color: C.cobalt, items: [["Quốc hội, Hội đồng nhân dân", "quốc hội"], ["Mặt trận Tổ quốc", "mặt trận tổ quốc"], ["Cơ quan chuyên trách bảo vệ dữ liệu cá nhân", "cơ quan chuyên trách"], ["Ban Thanh tra nhân dân (cấp xã)", "ban thanh tra"]] },
    { head: "Ai có quyền yêu cầu sửa đổi?", color: C.vermilion, items: [["Người dân: yêu cầu điều chỉnh thông tin (Luật Căn cước)", "luật căn cước"], ["Chủ thể dữ liệu: yêu cầu chỉnh sửa dữ liệu cá nhân", "chỉnh sửa dữ liệu"], ["Khiếu nại và kiến nghị", "khiếu nại và kiến nghị"]] },
    { head: "Ai chịu trách nhiệm khắc phục?", color: C.charcoal, items: [["Cơ quan quản lý căn cước, bên kiểm soát dữ liệu: sửa sai", "cơ quan quản lý căn cước"], ["Người giải quyết khiếu nại: trả lời trong thời hạn luật định", "người giải quyết khiếu nại"], ["Nhà nước bồi thường khi hành vi trái luật gây thiệt hại", "bồi thường"]] },
  ] as const;
  return (
    <>
      <Kicker label="Bản đồ trách nhiệm — theo pháp luật hiện hành" p={appear(t, 0.1)} />
      <div style={{ position: "absolute", left: 130, top: 150, width: 1660, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 30 }}>
        {cols.map((c, j) => {
          const first = cue(c.items[0][1], 1 + j * 8);
          return (
            <div key={c.head} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div style={{ ...BODY, fontSize: 32, fontWeight: W.bold, color: c.color === C.charcoal ? C.charcoal : c.color, borderBottom: `5px solid ${c.color}`, paddingBottom: 10, opacity: appear(t, first - 0.6) }}>{c.head}</div>
              {c.items.map(([label, key], i) => (
                <FlowCard key={label} p={appear(t, cue(key, first + i))} accent={c.color === C.charcoal ? C.cobalt : c.color} pad="16px 22px 16px 26px">
                  <div style={{ ...BODY, fontSize: 27, fontWeight: W.demi, lineHeight: 1.25 }}>{label}</div>
                </FlowCard>
              ))}
            </div>
          );
        })}
      </div>
      <SourceLine text="Căn cứ: Hiến pháp Đ.9, 28, 30, 69 · Luật 91/2025 Đ.4, 33, 37 · NĐ 356/2025 · Luật Căn cước Đ.5, 41 · Luật THDC Đ.38 · Luật Khiếu nại · Luật TNBTCNN" p={appear(t, 1)} y={790} />
    </>
  );
};

// ---------------------------------------------------------- configuration
export const GFX_CORE: Record<string, React.FC> = {
  dimensions: pillars(
    "Quan điểm Mác – Lênin · Giáo trình CNXHKH (2021)", "Dân chủ được hiểu trên ba phương diện",
    [
      { head: "Quyền lực", body: "Quyền lực thuộc về nhân dân; nhân dân là chủ nhân của nhà nước.", key: "về quyền lực" },
      { head: "Chế độ xã hội, chính trị", body: "Một hình thức, hay hình thái nhà nước.", key: "về chế độ xã hội" },
      { head: "Tổ chức, quản lý xã hội", body: "Một nguyên tắc: nguyên tắc dân chủ.", key: "về tổ chức và quản lý" },
    ],
    { banner: ["Một giá trị xã hội phản ánh những quyền cơ bản của con người", "giá trị xã hội"], source: "Nguồn: Bộ GD&ĐT, Giáo trình Chủ nghĩa xã hội khoa học (2021), chương IV" },
  ),
  lenin: quote(
    "V.I. Lênin · Nhà nước và cách mạng (1917), ch. V",
    "Chế độ dân chủ là một hình thức nhà nước, một trong những hình thái của nhà nước. […] Nhưng mặt khác, chế độ dân chủ có nghĩa là chính thức thừa nhận quyền bình đẳng giữa những công dân, thừa nhận cho mọi người được quyền ngang nhau trong việc xác định cơ cấu nhà nước và quản lý nhà nước.",
    "V.I. Lênin Toàn tập, t. 33, tr. 123–124", ["quyền ngang nhau", "quản lý nhà nước"], 40,
    ["Nhóm 14 giữ lại: quyền ngang nhau trong tổ chức và thực hiện quyền lực công", "điều nhóm em giữ lại"],
  ),
  hcm: quote("Hồ Chí Minh · “Dân vận”, 1949", "Nước ta là nước dân chủ. Bao nhiêu lợi ích đều vì dân. Bao nhiêu quyền hạn đều của dân.",
    "Báo Sự thật, số 120, 15/10/1949 · Hồ Chí Minh Toàn tập, t. 6, tr. 232", ["quyền hạn đều của dân"], 54),
  constitution: documentCard("Hiến pháp 2013 (sửa đổi, bổ sung 2025)", "Khung pháp lý hiện hành", [
    { art: "Điều 2", text: "Tất cả quyền lực nhà nước thuộc về Nhân dân.", key: "tất cả quyền lực" },
    { art: "Điều 28", text: "Công dân có quyền tham gia quản lý nhà nước và xã hội, thảo luận và kiến nghị; Nhà nước công khai, minh bạch trong việc tiếp nhận, phản hồi ý kiến, kiến nghị của công dân.", key: "tham gia quản lý" },
  ], "Nguồn: Hiến pháp nước CHXHCN Việt Nam năm 2013, Điều 2 khoản 2, Điều 28"),
  check_test: checklist("Lịch sử – cụ thể, không tương đối", "Ở đâu, dân chủ cũng phải trả lời được:", [
    { label: "Người dân có được biết?", key: "được biết" }, { label: "Được bàn?", key: "được bàn" },
    { label: "Được quyết định?", key: "được quyết định" }, { label: "Được giám sát?", key: "được giám sát" },
    { label: "Được bảo vệ?", key: "được bảo vệ" },
  ], { mode: "question", footer: ["Đa số biểu quyết, biểu mẫu góp ý: chưa phải là dân chủ", "đa số biểu quyết"], size: 40 }),
  law_levels: documentCard("Luật Thực hiện dân chủ ở cơ sở 2022", "Dân chủ được tách thành nhiều nấc", [
    { art: "Biết", text: "Những nội dung phải công khai để người dân biết.", key: "công khai" },
    { art: "Bàn, quyết định", text: "Những nội dung Nhân dân bàn và quyết định.", key: "bàn và quyết định" },
    { art: "Tham gia ý kiến", text: "Trước khi cơ quan có thẩm quyền quyết định.", key: "tham gia ý kiến" },
    { art: "Kiểm tra, giám sát", text: "Nội dung kiểm tra, giám sát.", key: "kiểm tra giám sát" },
  ], "Nguồn: Luật số 10/2022/QH15, Điều 3; Chương II, Mục 1–4 (sửa đổi, bổ sung năm 2024, 2025)"),
  myths: checklist("Dân chủ hóa KHÔNG đồng nghĩa với", "", [
    { label: "Ai cũng được dùng ứng dụng", key: "dùng một ứng dụng" }, { label: "Ai cũng được gửi ý kiến", key: "gửi ý kiến" },
    { label: "Số hóa thủ tục giấy", key: "số hóa" }, { label: "Thay chuyên môn bằng biểu quyết", key: "thay chuyên môn" },
    { label: "Công khai mọi dữ liệu cá nhân", key: "công khai mọi dữ liệu" },
  ], { mode: "strike", size: 44 }),
  conditions: checklist("Tham gia chỉ có hiệu lực khi có đủ", "", [
    { label: "Thông tin đủ để hiểu", key: "thông tin đủ" }, { label: "Kênh tiếp cận cho cả người yếu thế", key: "người yếu thế" },
    { label: "Nói mà không sợ bị trả đũa", key: "trả đũa" }, { label: "Phản hồi có lý do", key: "phản hồi có lý do" },
    { label: "Đường kháng nghị", key: "đường kháng nghị" }, { label: "Người chịu trách nhiệm", key: "người chịu trách nhiệm" },
    { label: "Có thể sửa quy tắc, thiết kế", key: "sửa quy tắc" },
  ], { mode: "check", size: 38, cols: 2 }),
  rights_matrix: RightsMatrix,
  change_test: changeTest(),
  power_bridge: PowerBridge,
  feen_power: FeenPower,
  three_terms: pillars("Định nghĩa làm việc", "Công nghệ · Thiết kế · Quản trị · Giá trị", [
    { head: "Công nghệ", body: "Hệ thống xã hội – kỹ thuật: máy móc, phần mềm, dữ liệu, tiêu chuẩn, quy trình, con người, thiết chế.", key: "công nghệ không chỉ" },
    { head: "Thiết kế", body: "Chọn cấu trúc, chức năng, dữ liệu, tiêu chuẩn, quyền truy cập, không chỉ trang trí giao diện.", key: "thiết kế công nghệ là" },
    { head: "Quản trị", body: "Phân bổ quyền quyết định, trách nhiệm, giám sát, sửa đổi, kháng nghị trong cả vòng đời.", key: "quản trị công nghệ là" },
    { head: "Giá trị", body: "Ưu tiên như hiệu quả, an toàn, công bằng, riêng tư, phẩm giá, thành lựa chọn kỹ thuật.", key: "giá trị công nghệ" },
  ]),
  code: sediment("Ý 2 · Mã kỹ thuật (technical code) ≠ mã nguồn", "“Tất yếu kỹ thuật”?", [
    { label: "Quan hệ xã hội", key: "quan hệ xã hội" }, { label: "Lợi ích", key: "lợi ích" },
    { label: "Chân trời văn hóa", key: "chân trời văn hóa" }, { label: "Lắng thành tham số thiết kế", key: "tham số thiết kế" },
  ], "tất yếu kỹ thuật"),
  email: quote("Ý 3 · Năng lực hành động của người dùng",
    "Thư điện tử trên Internet do những người dùng thành thạo đưa vào, vốn không có trong kế hoạch ban đầu của các nhà thiết kế; vậy mà nay nó là chức năng được dùng nhiều nhất của Internet.",
    "Feenberg, What Is Philosophy of Technology? (bài giảng 6/2003), tr. 10 — lược dịch", ["không có trong kế hoạch"], 46),
  paths: Paths,
  extend: quote("Feenberg (1992) · Subversive Rationalization, tr. 301–302",
    "Feenberg thuật lại Mác: dân chủ phải được mở rộng từ lĩnh vực chính trị sang thế giới lao động. Feenberg: nếu dân chủ không vươn tới những lĩnh vực đời sống được công nghệ trung giới, giá trị sử dụng của nó sẽ suy giảm và sự tham gia sẽ tàn lụi.",
    "Inquiry 35(3–4) — lược dịch", ["mở rộng", "công nghệ trung giới"], 42),
  initiative: splitNeq("Feenberg: dân chủ hóa công nghệ là gì? · S01 tr. 10 · S03 tr. 318",
    ["Không phải", "Bầu cử giữa các thiết bị hay các bản thiết kế. Không chủ yếu là quyền pháp lý."],
    ["Mà là", "Sáng kiến và sự tham gia, xuất phát từ kinh nghiệm và nhu cầu của những người đang kháng cự một bá quyền kỹ thuật."],
    ["bầu cử", "sáng kiến"], ["Thiếu điều đó, hình thức pháp lý sẽ trống rỗng.", "trống rỗng"]),
  case_before: CaseBefore,
  case_timeline: CaseTimeline,
  case_quote: CaseQuote,
  case_test: changeTest([
    { text: "Chính người chịu tác động: người bệnh", key: "kinh nghiệm của chính" },
    { text: "Tranh luận công khai, đối thoại với chuyên gia", key: "tranh luận công khai" },
    { text: "Số đông người bệnh, vẫn giữ kiểm chứng khoa học", key: "số đông" },
    { text: "Thể chế hóa thành quy định, có cơ quan chịu trách nhiệm", key: "thể chế hóa" },
  ]),
  vneid: documentCard("Ví dụ phân tích · VNeID", "Ứng dụng định danh quốc gia", [
    { art: "Luật định nghĩa", text: "Ứng dụng trên thiết bị số để phục vụ định danh điện tử và xác thực điện tử trong giải quyết thủ tục hành chính, dịch vụ công và các giao dịch khác trên môi trường điện tử.", key: "định nghĩa" },
  ], "Nguồn: Luật Căn cước số 26/2023/QH15 (sửa đổi, bổ sung 2025), Điều 3 khoản 18 · Hình minh họa, không phải giao diện thật"),
  scope: statement("Phạm vi phân tích",
    "Một ví dụ phân tích: không kết luận VNeID “là dân chủ” hay “không dân chủ”, và không đại diện cho toàn bộ nền dân chủ Việt Nam.", ["không đại diện"], 56),
  questions: checklist("Đặt ma trận vào hệ thống", "", [
    { label: "Dữ liệu nào, để làm gì, ai được truy cập?", key: "được biết dữ liệu" },
    { label: "Tham gia từ khi xác định nhu cầu?", key: "xác định nhu cầu" },
    { label: "Dữ liệu sai: có đường kháng nghị?", key: "kháng nghị" },
    { label: "Ai kiểm tra người vận hành?", key: "kiểm tra người vận hành" },
  ], { mode: "question", size: 42 }),
  privacy_law: documentCard("Pháp luật hiện hành", "Quyền được bảo vệ, và giới hạn của sự đồng ý", [
    { art: "Hiến pháp Đ.21", text: "Quyền bất khả xâm phạm về đời sống riêng tư, bí mật cá nhân.", key: "đời sống riêng tư" },
    { art: "Luật BVDLCN Đ.4", text: "Được biết; đồng ý, rút lại đồng ý; xem, yêu cầu chỉnh sửa; khiếu nại, khởi kiện.", key: "được biết về việc" },
    { art: "Luật BVDLCN Đ.19", text: "Xử lý không cần đồng ý khi phục vụ quản lý nhà nước theo luật; phải có cơ chế giám sát.", key: "không cần sự đồng ý" },
  ], "Nguồn: Hiến pháp 2013; Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 (hiệu lực 01/01/2026)"),
  whose: sediment("Đọc theo Feenberg", "Kinh nghiệm của ai được tính đến?", [
    { label: "Trường dữ liệu bắt buộc", key: "trường dữ liệu" }, { label: "Phương thức xác thực", key: "phương thức xác thực" },
    { label: "Phân quyền xem", key: "phân quyền xem" }, { label: "Thời hạn lưu nhật ký", key: "lưu nhật ký" },
  ], "kinh nghiệm của ai"),
  winwin: WinWin,
  four_terms: pillars("Bốn khái niệm hay bị dùng lẫn", "Liên quan, nhưng không như nhau", [
    { head: "Riêng tư", body: "Quyền con người.", key: "quyền riêng tư" },
    { head: "Bảo vệ dữ liệu", body: "Quy tắc xử lý dữ liệu.", key: "bảo vệ dữ liệu cá nhân" },
    { head: "An toàn thông tin", body: "Chống truy cập trái phép.", key: "an toàn thông tin" },
    { head: "Phân quyền", body: "Ai được xem gì.", key: "phân quyền là" },
  ]),
  ip_law: documentCard("Luật Sở hữu trí tuệ, Điều 6", "Căn cứ phát sinh, xác lập quyền", [
    { art: "Quyền tác giả", text: "Phát sinh khi tác phẩm được sáng tạo và thể hiện dưới hình thức vật chất nhất định, không phân biệt đã đăng ký hay chưa.", key: "quyền tác giả" },
    { art: "Sáng chế", text: "Xác lập trên cơ sở quyết định cấp văn bằng bảo hộ.", key: "sáng chế" },
  ], "Nguồn: Luật Sở hữu trí tuệ, Điều 6 khoản 1, khoản 3 điểm a (sửa đổi, bổ sung năm 2019)"),
  ip_split: splitNeq("Sở hữu trí tuệ và dân chủ",
    ["Bảo vệ quyền sở hữu", "Bình đẳng quyền của người sáng tạo trước pháp luật; chống xâm phạm là bảo vệ quyền ấy."],
    ["Tham gia quyết định thiết kế", "Thủ tục tiếp cận được với người ít nguồn lực; tri thức không bị tập trung."],
    ["biểu hiện của dân chủ", "cần thêm điều kiện"], ["Nền tảng, và bước tiếp theo.", "nền tảng"], "+"),
  ai_law: documentCard("Trí tuệ nhân tạo", "Luật sửa đổi năm 2025", [
    { art: "Điều 6 k.5", text: "Chính phủ quy định việc phát sinh, xác lập quyền khi đối tượng được tạo ra có sử dụng hệ thống trí tuệ nhân tạo.", key: "giao chính phủ" },
  ], "Nguồn: Luật số 131/2025/QH15 (hiệu lực 01/4/2026) · Nhóm không kết luận chung cho mọi trường hợp"),
  thesis: statement("Luận điểm của Nhóm 14 — không phải trích dẫn Feenberg",
    "Dân chủ hóa công nghệ đòi hỏi người chịu tác động có kênh tham gia có ý nghĩa vào vấn đề, tiêu chí, dữ liệu, quyền lực, bảo mật, giám sát và kháng nghị, với phản hồi có thể kiểm chứng.",
    ["phản hồi có thể kiểm chứng"], 52),
  should: checklist("Nên", "", [
    { label: "Xác định người chịu tác động trước khi thiết kế", key: "xác định người chịu tác động" },
    { label: "Công khai mục đích, dữ liệu, trách nhiệm", key: "công khai mục đích" },
    { label: "Tham vấn sớm, trả lời có lý do", key: "tham vấn sớm" },
    { label: "Phân quyền tối thiểu, nhật ký, kháng nghị", key: "phân quyền tối thiểu" },
    { label: "Đánh giá tác động trước và sau", key: "đánh giá tác động" },
  ], { mode: "check", size: 40 }),
  should_not: checklist("Không nên", "", [
    { label: "Đồng nhất tải ứng dụng với dân chủ hóa", key: "tải ứng dụng" }, { label: "Góp ý tượng trưng", key: "tượng trưng" },
    { label: "Nhân danh hiệu quả để đóng kênh kiểm tra", key: "nhân danh hiệu quả" },
    { label: "Nhân danh minh bạch để lộ dữ liệu cá nhân", key: "nhân danh minh bạch" },
    { label: "Lấy biểu quyết thay kiểm chứng kỹ thuật", key: "biểu quyết" },
  ], { mode: "strike", size: 40 }),
  obstacles: checklist("Làm được không? Được, nhưng không dễ", "Bốn trở ngại", [
    { label: "Chi phí và thời gian để tham vấn", key: "chi phí" },
    { label: "Khoảng cách số: người cao tuổi, thiếu thiết bị, thiếu kỹ năng", key: "khoảng cách số" },
    { label: "An toàn hệ thống: mở kênh càng rộng, bảo vệ càng chặt", key: "an toàn hệ thống" },
    { label: "Bất cân xứng thông tin; giới hạn pháp lý về bí mật, an ninh", key: "bất cân xứng" },
  ], { mode: "number", footer: ["Đi từng bước, có lộ trình, có người chịu trách nhiệm.", "từng bước"], size: 38 }),
  accountability: Accountability,
  proposals: checklist("Đề xuất bổ sung của Nhóm 14 — chưa phải quy định hiện hành", "", [
    { label: "Kiểm toán kỹ thuật độc lập định kỳ, công bố bản tóm tắt", key: "kiểm toán" },
    { label: "Nhật ký thay đổi công khai cho mỗi phiên bản", key: "nhật ký thay đổi" },
    { label: "Cho người dân biết ai đã xem dữ liệu của mình", key: "ai đã xem" },
    { label: "Chỉ số: phản hồi có lý do · thời gian kháng nghị · thay đổi thiết kế", key: "bộ chỉ số" },
  ], { mode: "number", size: 38, footer: ["Xung đột được nhìn thấy, được tranh luận, có người chịu trách nhiệm.", "nhìn thấy"] }),
  answer: checklist("Trả lời câu hỏi ban đầu", "Dân chủ nằm ở chỗ người chịu tác động", [
    { label: "Được biết", key: "được biết" }, { label: "Được tham vấn có trả lời", key: "tham vấn có trả lời" },
    { label: "Được tham gia quyết định trong phạm vi phù hợp", key: "tham gia quyết định" },
    { label: "Được giám sát và yêu cầu sửa đổi", key: "yêu cầu sửa đổi" },
    { label: "Có người chịu trách nhiệm khắc phục khi hệ thống sai", key: "khắc phục" },
  ], { mode: "check", size: 40 }),
  vn_values: checklist("Giá trị dân chủ trong phạm vi Việt Nam · Văn kiện Đại hội XIII", "Phương châm sáu “dân”", [
    { label: "Dân biết", key: "dân biết" }, { label: "Dân bàn", key: "dân bàn" }, { label: "Dân làm", key: "dân làm" },
    { label: "Dân kiểm tra", key: "dân kiểm tra" }, { label: "Dân giám sát", key: "dân giám sát" }, { label: "Dân thụ hưởng", key: "dân thụ hưởng" },
  ], { mode: "check", cols: 2, size: 42, footer: ["Thách thức: đưa vào thiết kế và quản trị hệ thống số.", "thách thức"] }),
};
