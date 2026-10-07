import React from "react";
import { useShot } from "../kit/shot";
import { C, FONT, W, appear, draw } from "../kit/theme";
import { Arrow, Card, Kicker, Svg, Thread, Title, Txt } from "../kit/ui";

// V12 "serif(size)" faces were Avenir Next at 92% of the nominal size.
const sf = (size: number) => Math.round(size * 0.92);

/** Ring fill used by the V12 painters (slightly warmer than the card paper). */
const RING_FILL = "#F8F4EC";

// ------------------------------------------------------------- film_title
const FilmTitle: React.FC = () => {
  const { t } = useShot();
  const p = appear(t, 0.2, 0.8);
  const q = appear(t, 1.0, 0.8);
  return (
    <>
      <Txt x={960} y={250} size={28} weight="demi" color={C.cobalt} anchor="c" v="m" p={p} track={0.02}>
        NHÓM 14 · TRIẾT HỌC
      </Txt>
      <Txt x={960} y={330} size={sf(96)} weight="bold" anchor="c" p={p} rise={20} lh={1.12}>
        Dân chủ hóa thiết kế
        <br />
        và quản trị công nghệ
      </Txt>
      <Txt x={960} y={600} size={sf(54)} weight="medium" color={C.vermilion} anchor="c" v="m" p={q} rise={12}>
        theo Andrew Feenberg
      </Txt>
      <Svg>
        <Thread pts={[[560, 680], [1360, 680]]} p={draw(t, 1.2, 1.8)} width={4} />
      </Svg>
    </>
  );
};

// ----------------------------------------------------------- two_concepts
const TwoConcepts: React.FC = () => {
  const { t, D, cue } = useShot();
  const concepts = [
    { word: "Dân chủ", at: cue("dân chủ là gì", 0.4), accent: C.cobalt },
    { word: "Dân chủ hóa", at: cue("dân chủ hóa là gì", 1.2), accent: C.vermilion },
  ];
  const pf = appear(t, cue("khẩu hiệu", D - 2.5));
  return (
    <>
      <Kicker label="Hai câu hỏi nền tảng" p={appear(t, 0.1)} />
      {concepts.map(({ word, at, accent }, i) => {
        const p = appear(t, at);
        const x0 = 230 + i * 760;
        return (
          <React.Fragment key={word}>
            <Card x0={x0} y0={250} x1={x0 + 680} y1={640} p={p} accent={accent} />
            <Txt x={x0 + 340} y={400} size={sf(80)} weight="bold" anchor="c" v="m" p={p} rise={14}>
              {word}
            </Txt>
            <Txt x={x0 + 340} y={500} size={sf(54)} weight="medium" color={accent} anchor="c" v="m" p={p} rise={14}>
              là gì?
            </Txt>
          </React.Fragment>
        );
      })}
      <Txt x={960} y={750} size={34} weight="medium" color={C.inkSoft} anchor="c" v="m" p={pf} rise={12}>
        Không có định nghĩa, “dân chủ hóa công nghệ” dễ thành khẩu hiệu.
      </Txt>
    </>
  );
};

// ------------------------------------------------------------- data_trace
const DataTrace: React.FC = () => {
  const { t, cue } = useShot();
  const p = appear(t, 0.2);
  const labels = [
    { label: "Ai xác thực", at: cue("ai xác thực", 1.0) },
    { label: "Vào lúc nào", at: cue("vào lúc nào", 1.7) },
    { label: "Cho thủ tục gì", at: cue("thủ tục gì", 2.4) },
  ];
  const kept = cue("lưu giữ", 4.5);
  const q = appear(t, kept);
  return (
    <>
      <Kicker label="Một thao tác, hai chiều" p={appear(t, 0.1)} />
      {/* Abstract phone outline: no real interface is shown. */}
      <Svg>
        <g opacity={p}>
          <rect x={263} y={263} width={254} height={494} rx={34} fill={C.paper} stroke={C.charcoal} strokeWidth={6} />
          <rect x={300} y={330} width={180} height={190} rx={12} fill={C.cobalt} fillOpacity={0.85} />
          <circle cx={390} cy={615} r={22.5} fill="none" stroke={C.vermilion} strokeWidth={5} />
        </g>
        {labels.map(({ label, at }, i) => {
          const y = 330 + i * 150;
          return (
            <g key={label} opacity={appear(t, at)}>
              <Arrow a={[540, 510]} b={[896, y + 35]} p={draw(t, at, 0.6)} width={4} />
            </g>
          );
        })}
        {labels.map(({ label }, i) => (
          // Heads land on separate points of the data card so the three arrows stay distinguishable.
          <Arrow key={label} a={[1316, 365 + i * 150]} b={[1458, 480 + i * 40]} p={draw(t, kept, 0.8)} color={C.cobalt} width={4} />
        ))}
      </Svg>
      {labels.map(({ label, at }, i) => {
        const r = appear(t, at);
        const y = 330 + i * 150;
        return (
          <React.Fragment key={label}>
            <Card x0={910} y0={y} x1={1300} y1={y + 70} p={r} accent={C.vermilion} />
            <Txt x={935} y={y + 35} size={30} weight="demi" v="m" upper p={r}>
              {label}
            </Txt>
          </React.Fragment>
        );
      })}
      <Card x0={1470} y0={430} x1={1790} y1={610} p={q} accent={C.cobalt} />
      <Txt x={1630} y={495} size={32} weight="bold" color={C.cobalt} anchor="c" v="m" p={q}>
        DỮ LIỆU
      </Txt>
      <Txt x={1630} y={545} size={28} weight="medium" anchor="c" v="m" p={q}>
        về con người
      </Txt>
    </>
  );
};

// -------------------------------------------------------- three_questions
const ThreeQuestions: React.FC = () => {
  const { t, D, cue } = useShot();
  const items = [
    { label: "Được dùng?", key: "được dùng" },
    { label: "Được gửi góp ý?", key: "gửi góp ý" },
    { label: "Được tham gia, và làm thay đổi thiết kế, quản trị?", key: "thật sự được tham gia" },
  ];
  return (
    <>
      <Kicker label="Câu hỏi trung tâm" p={appear(t, 0.1)} />
      <Title text="Dân chủ nằm ở đâu?" p={appear(t, 0.2)} size={sf(72)} />
      {items.map(({ label, key }, i) => {
        const p = appear(t, cue(key, 1 + i * 1.4));
        const y = 330 + i * 130;
        const isLast = i === 2;
        const color = isLast ? C.vermilion : C.cobalt;
        return (
          <React.Fragment key={key}>
            <div
              style={{
                position: "absolute",
                left: 150,
                top: y + 8,
                width: 36,
                height: 36,
                borderRadius: "50%",
                border: `4px solid ${color}`,
                boxSizing: "border-box",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                opacity: p,
                fontFamily: FONT,
                fontSize: 22,
                fontWeight: W.bold,
                color,
              }}
            >
              {i + 1}
            </div>
            <Txt x={220} y={y + 26} size={sf(isLast ? 50 : 54)} weight="demi" color={isLast ? C.vermilion : C.charcoal} v="m" p={p} rise={10}>
              {label}
            </Txt>
          </React.Fragment>
        );
      })}
      <Svg>
        <Thread pts={[[168, 740], [900, 740], [1700, 740]]} p={draw(t, cue("thiết kế và quản trị", D - 2), 1.4)} />
      </Svg>
    </>
  );
};

// -------------------------------------------------------------- etymology
const Etymology: React.FC = () => {
  const { t, D, cue } = useShot();
  const p1 = appear(t, cue("demos", 0.6));
  const p2 = appear(t, cue("kratos", 1.6));
  const at3 = cue("quyền lực thuộc về nhân dân", D - 3);
  const parts = [
    { word: "demos", gloss: "dân", cx: 540, p: p1, accent: C.cobalt, glossSize: sf(56) },
    { word: "kratos", gloss: "cai trị, quyền lực", cx: 1380, p: p2, accent: C.vermilion, glossSize: sf(52) },
  ];
  return (
    <>
      <Kicker label="Nghĩa gốc" p={appear(t, 0.1)} />
      {parts.map(({ word, gloss, cx, p, accent, glossSize }) => (
        <React.Fragment key={word}>
          <Card x0={cx - 290} y0={230} x1={cx + 290} y1={540} p={p} accent={accent} />
          <Txt x={cx} y={330} size={sf(96)} weight="bold" color={accent} anchor="c" v="m" p={p} rise={14}>
            {word}
          </Txt>
          <Txt x={cx} y={450} size={glossSize} weight="medium" anchor="c" v="m" p={p} rise={14}>
            {gloss}
          </Txt>
        </React.Fragment>
      ))}
      <Txt x={960} y={385} size={sf(110)} weight="medium" color={C.inkSoft} anchor="c" v="m" p={Math.min(p1, p2)}>
        +
      </Txt>
      <Svg>
        <Thread pts={[[540, 600], [540, 640], [1380, 640], [1380, 600]]} p={draw(t, at3, 1.0)} />
      </Svg>
      <Txt x={960} y={730} size={sf(68)} weight="bold" anchor="c" v="m" p={appear(t, at3)} rise={14}>
        Quyền lực thuộc về nhân dân
      </Txt>
    </>
  );
};

// ------------------------------------------------------------------ rings
const Rings: React.FC = () => {
  const { t, cue } = useShot();
  const cx = 560;
  const cy = 480;
  const layers = [
    { r: 330, label: "GIÁ TRỊ", head: "Giá trị", body: "Bình đẳng · phẩm giá · bảo vệ quyền con người · khả\u00A0năng phản\u00A0biện.", key: "lớp giá trị", color: C.vermilion },
    { r: 230, label: "THIẾT CHẾ", head: "Thiết chế", body: "Được biết · tham gia · đại diện · giám sát · giải trình · kiểm soát quyền lực.", key: "lớp thiết chế", color: C.cobalt },
    { r: 125, label: "CHỦ THỂ", head: "Chủ thể", body: "Quyền quyết định việc chung thuộc về nhân dân, nhất là người chịu tác động.", key: "lớp chủ thể", color: C.charcoal },
  ].map((layer) => ({ ...layer, p: appear(t, cue(layer.key, 1.0)) }));
  return (
    <>
      <Kicker label="Định nghĩa làm việc của Nhóm 14" p={appear(t, 0.1)} />
      <Svg>
        {layers.map(({ r, label, color, p }) => (
          <circle key={label} cx={cx} cy={cy} r={r - 2.5} fill={RING_FILL} stroke={color} strokeWidth={5} opacity={p} />
        ))}
      </Svg>
      {layers.map(({ r, label, color, p }) => (
        <Txt key={label} x={cx} y={cy - r + (r < 200 ? 56 : 46)} size={28} weight="bold" color={color} anchor="c" v="m" p={p}>
          {label}
        </Txt>
      ))}
      <div style={{ position: "absolute", left: 990, top: 214, width: 780, display: "flex", flexDirection: "column", gap: 34 }}>
        {[...layers].reverse().map(({ head, body, key, p }) => (
          <div key={key} style={{ opacity: p, transform: `translateY(${(1 - p) * 12}px)`, fontFamily: FONT }}>
            <div style={{ fontSize: sf(46), fontWeight: W.bold, color: C.charcoal, lineHeight: 1.2 }}>{head}</div>
            <div style={{ marginTop: 10, fontSize: 31, fontWeight: W.medium, color: C.inkSoft, lineHeight: 1.3, textWrap: "pretty" }}>{body}</div>
          </div>
        ))}
      </div>
    </>
  );
};

// ---------------------------------------------------------------- process
const Process: React.FC = () => {
  const { t, cue } = useShot();
  const p = appear(t, 0.3);
  const atProcess = cue("quá trình", 1.5);
  const q = appear(t, atProcess);
  const steps = [
    { label: "được biết", key: "được biết" },
    { label: "tham gia có hiệu lực", key: "tham gia có hiệu lực" },
    { label: "phản biện", key: "phản biện" },
    { label: "yêu cầu giải trình", key: "giải trình" },
    { label: "tác động đến quyết định", key: "tác động đến quyết định" },
  ].map((s, i) => ({ ...s, x: 150 + i * 330, r: appear(t, cue(s.key, 3 + i)) }));
  return (
    <>
      <Kicker label="Dân chủ hóa = một quá trình" p={appear(t, 0.1)} />
      <Txt x={150} y={170} size={sf(64)} weight="bold" color={C.cobalt} p={p} rise={14}>
        Dân chủ
      </Txt>
      <Txt x={150} y={250} size={30} weight="medium" color={C.inkSoft} p={p}>
        giá trị · hình thức tổ chức quyền lực
      </Txt>
      <Txt x={1000} y={170} size={sf(64)} weight="bold" color={C.vermilion} p={q} rise={14}>
        Dân chủ hóa
      </Txt>
      <Txt x={1000} y={250} size={30} weight="medium" color={C.inkSoft} p={q}>
        mở rộng trong một cấu trúc cụ thể
      </Txt>
      <Svg>
        <Arrow a={[150, 360]} b={[1780, 360]} p={draw(t, atProcess, 2.0)} width={6} />
        {steps.map(({ key, x, r }) => (
          <circle key={key} cx={x + 145} cy={360} r={15} fill={C.vermilion} opacity={r} />
        ))}
      </Svg>
      {steps.map(({ label, key, x, r }, i) => (
        <React.Fragment key={key}>
          <Card x0={x} y0={430} x1={x + 300} y1={640} p={r} accent={i === 4 ? C.vermilion : C.cobalt} />
          <Txt x={x + 24} y={452} size={sf(52)} weight="bold" color={C.vermilion} p={r} lh={1.1}>
            {i + 1}
          </Txt>
          <Txt x={x + 24} y={530} size={31} weight="demi" p={r} maxW={252} lh={1.2}>
            {label}
          </Txt>
        </React.Fragment>
      ))}
    </>
  );
};

// ------------------------------------------------------------------ chain
// Philosophy → democracy → public power → design → governance → redesign.
const CHAIN_NODES = [
  { head: "Triết học", sub: "chủ thể · quyền lực\ngiá trị · trách nhiệm", key: "triết học" },
  { head: "Nội hàm\ndân chủ", sub: "quyền · thiết chế\nquy trình", key: "dân chủ biến" },
  { head: "Quyền lực công", sub: "thực hiện qua\nhệ thống kỹ thuật", key: "quyền lực công" },
  { head: "Thiết kế", sub: "dữ liệu · tiêu chí\nphân quyền", key: "thiết kế công nghệ" },
  { head: "Quản trị", sub: "giám sát · giải trình\nkháng nghị", key: "quản trị công nghệ" },
  { head: "Tái thiết kế", sub: "phản hồi làm\nđổi quy tắc", key: "phân biệt then chốt" },
] as const;
const CHAIN_LABELS = ["đặt câu hỏi", "cụ thể hóa", "được thực hiện qua", "kết tinh trong", "kiểm soát bằng", "quay lại"] as const;
const CHAIN_COUNT: Record<number, number> = { 1: 2, 2: 4, 3: 6, 4: 6 };

// Six 256px cards with 30px gutters span x 124–1810, inside the 1920 title-safe area.
const CHAIN_HALF = 128;
const CHAIN_STEP = 286;
const CHAIN_Y = 420;
// 28px keeps the widest head ("Quyền lực công") clear of the accent bar inside a 256px card.
const CHAIN_HEAD_SIZE = 28;
const chainX = (i: number) => 124 + CHAIN_HALF + i * CHAIN_STEP;

const makeChain = (stage: number): React.FC => {
  const Chain: React.FC = () => {
    const { t, D, cue } = useShot();
    const y = CHAIN_Y;
    const nodes = CHAIN_NODES.slice(0, CHAIN_COUNT[stage]).map((node, i) => ({
      ...node,
      at: stage < 4 ? cue(node.key, 0.6 + i * 1.6) : 0.3 + i * 0.5,
      accent: i === 2 || i === 5 ? C.vermilion : C.cobalt,
    }));
    const loop = draw(t, 3.5, 1.4);
    return (
      <>
        <Kicker label="Từ triết học đến công nghệ" p={appear(t, 0.1)} />
        <Svg>
          {nodes.slice(1).map((node, k) => (
            <Arrow
              key={node.key}
              a={[chainX(k) + CHAIN_HALF + 4, y]}
              b={[chainX(k + 1) - CHAIN_HALF - 4, y]}
              p={draw(t, node.at, 0.6)}
              width={4}
              head={13}
            />
          ))}
          {stage === 4 ? (
            <Thread
              pts={[[chainX(5), y + 126], [chainX(5), 640], [chainX(0), 640], [chainX(0), y + 126]]}
              p={loop}
              width={4}
            />
          ) : null}
        </Svg>
        {nodes.map(({ head, sub, key, at, accent }, i) => {
          const p = appear(t, at);
          return (
            <React.Fragment key={key}>
              <Card x0={chainX(i) - CHAIN_HALF} y0={y - 110} x1={chainX(i) + CHAIN_HALF} y1={y + 110} p={p} accent={accent} />
              <Txt x={chainX(i)} y={y - 82} size={CHAIN_HEAD_SIZE} weight="bold" color={accent} anchor="c" p={p} lh={1.1}>
                <span style={{ whiteSpace: "pre" }}>{head}</span>
              </Txt>
              <Txt x={chainX(i)} y={y + 6} size={24} weight="medium" anchor="c" p={p} lh={1.3}>
                <span style={{ whiteSpace: "pre" }}>{sub}</span>
              </Txt>
              {i > 0 ? (
                <Txt x={chainX(i) - CHAIN_STEP / 2} y={y - 140} size={22} weight="demi" color={C.vermilion} anchor="c" v="m" p={draw(t, at, 0.6)}>
                  {CHAIN_LABELS[i - 1]}
                </Txt>
              ) : null}
            </React.Fragment>
          );
        })}
        {stage === 4 ? (
          <>
            <Txt x={960} y={676} size={24} weight="demi" color={C.vermilion} anchor="c" v="m" p={loop}>
              {CHAIN_LABELS[5]}
            </Txt>
            <Txt x={960} y={770} size={sf(48)} weight="bold" anchor="c" v="m" p={appear(t, cue("có thể được định hướng", 4))} rise={12}>
              Công nghệ mang giá trị, nhưng có thể được định hướng.
            </Txt>
          </>
        ) : null}
        {stage === 3 ? (
          <Txt x={960} y={700} size={sf(52)} weight="bold" color={C.vermilion} anchor="c" v="m" p={appear(t, cue("không hề có tiếng nói", D - 3))} rise={12}>
            Sử dụng chưa phải là tham gia thiết kế và quản trị
          </Txt>
        ) : null}
      </>
    );
  };
  return Chain;
};

// ---------------------------------------------------------------- two_way
const TwoWay: React.FC = () => {
  const { t, D, cue } = useShot();
  const ways = [
    {
      label: "Chiều 1",
      head: "Công nghệ phục vụ dân\u00A0chủ trong quản\u00A0trị xã\u00A0hội",
      body: "Người dân được biết, kiến nghị, giám sát, khiếu nại qua nền tảng số.",
      at: cue("chiều thứ nhất", 0.8),
      color: C.cobalt,
    },
    {
      label: "Chiều 2",
      head: "Dân chủ hóa chính công nghệ",
      body: "Người chịu tác động tham gia thiết kế và quản trị hệ thống.",
      at: cue("chiều thứ hai", 3.8),
      color: C.vermilion,
    },
  ];
  const at = cue("gắn với nhau", D - 4);
  const q = draw(t, at, 0.8);
  return (
    <>
      <Kicker label="Dân chủ và công nghệ gặp nhau theo hai chiều" p={appear(t, 0.1)} />
      {ways.map(({ label, head, body, at: wayAt, color }, i) => {
        const p = appear(t, wayAt);
        const x0 = 150 + i * 880;
        return (
          <Card key={label} x0={x0} y0={190} x1={x0 + 740} y1={600} p={p} accent={color} pad="30px 40px">
            <div style={{ fontFamily: FONT, transform: `translateY(${(1 - p) * 12}px)` }}>
              <div style={{ fontSize: 26, fontWeight: W.demi, color, textTransform: "uppercase", letterSpacing: "0.02em", lineHeight: 1.25 }}>{label}</div>
              <div style={{ marginTop: 18, fontSize: 44, fontWeight: W.bold, color: C.charcoal, lineHeight: 1.15, textWrap: "balance" }}>{head}</div>
              <div style={{ marginTop: 20, fontSize: 31, fontWeight: W.medium, color: C.inkSoft, lineHeight: 1.3, textWrap: "pretty" }}>{body}</div>
            </div>
          </Card>
        );
      })}
      <Svg>
        <Arrow a={[902, 360]} b={[1022, 360]} p={q} width={5} />
        <Arrow a={[1022, 430]} b={[902, 430]} p={q} color={C.cobalt} width={5} />
      </Svg>
      <Txt x={960} y={700} size={38} weight="demi" color={C.vermilion} anchor="c" v="m" p={appear(t, at + 0.4)} rise={12}>
        Chiều 1 chỉ có hiệu lực khi chiều 2 được bảo đảm.
      </Txt>
    </>
  );
};

// ----------------------------------------------------------------- thanks
const Thanks: React.FC = () => {
  const { t, cue } = useShot();
  const p = appear(t, 0.3, 0.9);
  const q = appear(t, cue("các bạn", 2.5));
  return (
    <>
      <Txt x={960} y={300} size={sf(54)} weight="medium" color={C.inkSoft} anchor="c" v="m" p={p} rise={12}>
        Xin chân thành cảm ơn
      </Txt>
      <Txt x={960} y={410} size={sf(96)} weight="bold" anchor="c" v="m" p={p} rise={16}>
        TS Nguyễn Hữu Sơn
      </Txt>
      <Svg>
        <Thread pts={[[620, 500], [1300, 500]]} p={draw(t, 0.8, 1.4)} width={4} />
      </Svg>
      <Txt x={960} y={590} size={sf(48)} weight="medium" color={C.cobalt} anchor="c" v="m" p={q} rise={12}>
        và các bạn đã theo dõi
      </Txt>
      <Txt x={960} y={700} size={28} weight="demi" color={C.vermilion} anchor="c" v="m" p={q} track={0.02}>
        NHÓM 14 · PH2001.26.1.CH.02
      </Txt>
    </>
  );
};

export const GFX_BESPOKEA: Record<string, React.FC> = {
  film_title: FilmTitle,
  two_concepts: TwoConcepts,
  data_trace: DataTrace,
  three_questions: ThreeQuestions,
  etymology: Etymology,
  rings: Rings,
  process: Process,
  chain1: makeChain(1),
  chain2: makeChain(2),
  chain3: makeChain(3),
  chain4: makeChain(4),
  two_way: TwoWay,
  thanks: Thanks,
};
