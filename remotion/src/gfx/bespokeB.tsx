import React from "react";
import { Img, staticFile } from "remotion";
import { useShot } from "../kit/shot";
import { C, FONT, W, appear, clamp, draw, ease } from "../kit/theme";
import { Arrow, Card, DrawLine, Kicker, SourceLine, Svg, Thread, Txt } from "../kit/ui";

type Pt = readonly [number, number];

// V12 "serif" display faces were Avenir Next at 92% of the nominal size.
const ds = (size: number) => Math.round(size * 0.92);

const abs = (left: number, top: number, width: number, height: number): React.CSSProperties => ({
  position: "absolute",
  left,
  top,
  width,
  height,
  boxSizing: "border-box",
});

const centred: React.CSSProperties = { display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center" };

// ------------------------------------------------------------- feenberg
const PHOTO = { x: 190, y: 110, w: 480, h: 620, mat: 10 } as const;

const Feenberg: React.FC = () => {
  const { t, D, cue } = useShot();
  const p = appear(t, 0.2, 0.8);
  const zoom = 1 + 0.03 * clamp(t / Math.max(D, 1));
  const q = appear(t, 0.8);
  const r = appear(t, cue("simon fraser", 2.0));
  const s = appear(t, cue("lý thuyết phê phán", 3.0));
  const frameW = PHOTO.w + 2 * PHOTO.mat;
  return (
    <>
      <div style={{ ...abs(PHOTO.x, PHOTO.y, frameW, PHOTO.h + 2 * PHOTO.mat), padding: PHOTO.mat, backgroundColor: C.paper, opacity: p }}>
        <div style={{ width: PHOTO.w, height: PHOTO.h, overflow: "hidden" }}>
          <Img
            src={staticFile("feenberg.jpg")}
            style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 35%", transform: `scale(${zoom})` }}
          />
        </div>
      </div>
      <div style={{ ...abs(PHOTO.x, 768, frameW, 4), backgroundColor: C.vermilion, opacity: p }} />
      <Txt x={PHOTO.x} y={784} size={20} color={C.inkSoft} p={p} lh={1.1}>
        Ảnh: Beatrice Murch · Wikimedia Commons · CC BY-SA 3.0
      </Txt>

      <Txt x={840} y={200} size={26} weight="demi" color={C.cobalt} p={q} rise={10} lh={1.1}>
        CON NGƯỜI VÀ TƯ TƯỞNG
      </Txt>
      <Txt x={840} y={250} size={ds(96)} p={q} rise={14} lh={1.1}>
        Andrew
      </Txt>
      <Txt x={840} y={360} size={ds(120)} weight="bold" color={C.vermilion} p={q} rise={14} lh={1.1}>
        Feenberg
      </Txt>
      <Txt x={840} y={540} size={ds(48)} weight="demi" p={r} rise={10} lh={1.1}>
        Nhà triết học công nghệ
      </Txt>
      <Txt x={840} y={610} size={34} color={C.inkSoft} p={r} rise={10} lh={1.1}>
        Giáo sư danh dự, Đại học Simon Fraser, Canada
      </Txt>
      <Card x0={840} y0={690} x1={1700} y1={780} p={s} accent={C.vermilion} pad="0 40px" style={{ display: "flex", alignItems: "center" }}>
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: W.demi, color: C.charcoal }}>Lý thuyết phê phán về công nghệ</span>
      </Card>
    </>
  );
};

// --------------------------------------------------------------- matrix
// Grid is 320 px per cell (V12: 330) so the bottom axis labels stay well above the subtitle band.
const MX = { x0: 560, y0: 165, s: 320 } as const;

type Cell = { readonly col: number; readonly row: number; readonly label: string; readonly at: (cue: (k: string, f: number) => number) => number; readonly color: string };

const MATRIX_CELLS: readonly Cell[] = [
  { col: 0, row: 0, label: "Thuyết\ntất định", at: (cue) => cue("thuyết tất định", 1.5), color: C.cobalt },
  { col: 1, row: 0, label: "Thuyết\nthực chất", at: (cue) => cue("hai trục", 1.5) + 0.8, color: C.sage },
  { col: 0, row: 1, label: "Thuyết\ncông cụ", at: (cue) => cue("thuyết công cụ", 1.5), color: C.cobalt },
  { col: 1, row: 1, label: "Lý thuyết\nphê phán", at: (cue) => cue("lý thuyết phê phán", 1.5), color: C.vermilion },
];

const Matrix: React.FC = () => {
  const { t, D, cue } = useShot();
  const { x0, y0, s } = MX;
  const axisAt = cue("hai trục", 0.5);
  const p = appear(t, axisAt);
  const r = appear(t, cue("thiết chế phù hợp", D - 5));
  const axisLabel = { size: 26, weight: "demi" as const, color: C.inkSoft, p, lh: 1.2 };
  return (
    <>
      <Kicker label="Feenberg: hai trục, bốn lập trường" p={appear(t, 0.1)} />
      <Svg>
        <DrawLine a={[x0, y0 + s]} b={[x0 + 2 * s, y0 + s]} p={draw(t, axisAt, 0.8)} color={C.charcoal} width={3} />
        <DrawLine a={[x0 + s, y0]} b={[x0 + s, y0 + 2 * s]} p={draw(t, axisAt, 0.8)} color={C.charcoal} width={3} />
      </Svg>
      <Txt x={x0 - 20} y={y0 + s / 2} anchor="r" v="m" {...axisLabel}>
        Tự trị
      </Txt>
      <Txt x={x0 - 20} y={y0 + 1.5 * s} anchor="r" v="m" {...axisLabel}>
        Con người
        <br />
        kiểm soát
      </Txt>
      <Txt x={x0 + s / 2} y={y0 + 2 * s + 30} anchor="c" v="m" {...axisLabel}>
        Trung tính
      </Txt>
      <Txt x={x0 + 1.5 * s} y={y0 + 2 * s + 30} anchor="c" v="m" {...axisLabel}>
        Mang giá trị
      </Txt>

      {MATRIX_CELLS.map(({ col, row, label, at, color }) => {
        const q = appear(t, at(cue));
        const critical = color === C.vermilion;
        return (
          <div
            key={label}
            style={{
              ...abs(x0 + col * s + 12, y0 + row * s + 12, s - 24, s - 24),
              ...centred,
              // Every stance on two lines: the longest names do not fit one line with comfortable side margins.
              whiteSpace: "pre-line",
              opacity: q,
              border: `3px solid ${color}`,
              borderRadius: 12,
              backgroundColor: critical ? C.vermilionWash : C.paper,
              fontFamily: FONT,
              fontSize: ds(36),
              fontWeight: W.bold,
              lineHeight: 1.2,
              color: color === C.sage ? C.inkSoft : color,
            }}
          >
            {label}
          </div>
        );
      })}

      <Txt x={1300} y={300} size={ds(40)} weight="demi" p={r} rise={12} lh={52 / ds(40)}>
        Vấn đề: thiếu thiết chế
        <br />
        phù hợp để kiểm soát
        <br />
        công nghệ.
      </Txt>
      <Txt x={1300} y={480} size={22} color={C.inkSoft} p={r} lh={30 / 22}>
        Feenberg, What Is Philosophy
        <br />
        of Technology? (2003), tr. 5–6, 9
      </Txt>
    </>
  );
};

// -------------------------------------------------------------- options
const OPTIONS = ["Phương án A", "Phương án B", "Phương án C"] as const;

const Options: React.FC = () => {
  const { t, D, cue } = useShot();
  const p = appear(t, 0.4);
  // The verdict line follows the narration's "không phải muốn …" rather than the earlier "tương đối",
  // so it lands after the three options instead of before them in this 4.5 s shot.
  const r = appear(t, cue("không phải muốn", cue("tương đối", D - 3)));
  return (
    <>
      <Kicker label="Ý 1 · Tính bất định tương đối" p={appear(t, 0.1)} />
      <div style={{ ...abs(300, 220, 1320, 480), border: `4px solid ${C.cobalt}`, borderRadius: 24, opacity: p }} />
      <Txt x={330} y={240} size={24} weight="demi" color={C.cobalt} p={p} lh={1.1}>
        RÀNG BUỘC KỸ THUẬT
      </Txt>
      {OPTIONS.map((label, i) => {
        const q = appear(t, cue("nhiều phương án", 0.5) + i * 0.35);
        const x = 420 + i * 380;
        return (
          <Card key={label} x0={x} y0={360} x1={x + 320} y1={560} p={q} accent={i === 1 ? C.vermilion : C.cobalt} style={centred}>
            <span style={{ fontFamily: FONT, fontSize: ds(40), fontWeight: W.bold, color: C.charcoal }}>{label}</span>
          </Card>
        );
      })}
      <Txt x={960} y={640} anchor="c" v="m" size={ds(44)} weight="bold" color={C.vermilion} p={r} rise={10} lh={1.2}>
        Bất định tương đối, không phải muốn sao cũng được
      </Txt>
      <Txt x={960} y={770} anchor="c" v="m" size={28} color={C.inkSoft} p={p} lh={1.2}>
        ngoài khung: không khả thi
      </Txt>
    </>
  );
};

// ---------------------------------------------------------- rationality
const FACTORS = [
  { label: "bối cảnh", sx: -1, sy: 1 },
  { label: "chi phí", sx: 1, sy: 1 },
  { label: "kinh nghiệm", sx: -1, sy: -1 },
  { label: "người chịu tác động", sx: 1, sy: -1 },
] as const;

const Rationality: React.FC = () => {
  const { t, D, cue } = useShot();
  const cx = 960;
  const cy = 430;
  const radius = 140 + 120 * ease((t - cue("mở rộng", 1.0)) / 2.5);
  const q = appear(t, cue("hiệu quả cho ai", D - 3));
  return (
    <>
      <Kicker label="Ý 4 · Hợp lý hóa dân chủ" p={appear(t, 0.1)} />
      <Svg>
        <circle cx={cx} cy={cy} r={radius} fill="#FAF0E8" stroke={C.vermilion} strokeWidth={5} />
        {FACTORS.map(({ label, sx, sy }, i) => (
          <circle key={label} cx={cx + sx * 330} cy={cy + sy * 200} r={14} fill={C.cobalt} opacity={appear(t, cue(label, 1.5 + i * 0.6))} />
        ))}
      </Svg>
      <Txt x={cx} y={cy + 6} anchor="c" v="m" size={ds(44)} weight="bold" lh={52 / ds(44)}>
        Tính hợp lý
        <br />
        kỹ thuật
      </Txt>
      {FACTORS.map(({ label, sx, sy }, i) => (
        <Txt
          key={label}
          x={cx + sx * 358}
          y={cy + sy * 200}
          anchor={sx > 0 ? "l" : "r"}
          v="m"
          size={30}
          weight="demi"
          color={C.cobalt}
          p={appear(t, cue(label, 1.5 + i * 0.6))}
          lh={1.2}
        >
          {label}
        </Txt>
      ))}
      <Txt x={cx} y={770} anchor="c" v="m" size={ds(46)} weight="bold" color={C.vermilion} p={q} rise={10} lh={1.2}>
        Hiệu quả cho ai? Chi phí do ai gánh?
      </Txt>
      <SourceLine y={812} p={appear(t, 0.6)} text="Feenberg (1992) gọi là “subversive rationalization”, Inquiry 35, tr. 320" />
    </>
  );
};

// ------------------------------------------------------------ lifecycle
const STAGES = [
  { name: "Xác định nhu cầu", mech: "bản đồ người chịu tác động", key: "xác định nhu cầu" },
  { name: "Thiết kế", mech: "công khai mục đích, dữ liệu, tiêu chí", key: "thiết kế" },
  { name: "Thử nghiệm", mech: "thử với nhóm dễ bị bỏ sót", key: "thử nghiệm" },
  { name: "Vận hành", mech: "hỗ trợ · chỉnh sửa · khiếu nại", key: "vận hành" },
  { name: "Giám sát", mech: "kiểm tra độc lập", key: "giám sát" },
  { name: "Tái thiết kế", mech: "phản hồi làm đổi quy tắc", key: "tái thiết kế" },
] as const;

const ROLES = [
  { role: "Cơ quan có thẩm quyền", duty: "quyết định cuối cùng", accent: C.cobalt },
  { role: "Kỹ sư", duty: "trách nhiệm chuyên môn", accent: C.cobalt },
  { role: "Người chịu tác động", duty: "tiếng nói có đường đi tới quyết định", accent: C.vermilion },
] as const;

// Hexagon centre/radius: V12 used (620, 500, 250); shifted right and tightened so the left labels clear the
// chapter spine and the bottom label ends well above the subtitle band.
const LC = { cx: 660, cy: 490, R: 240, gap: 30 } as const;

const StageLabel: React.FC<{ readonly x: number; readonly y: number; readonly name: string; readonly mech: string; readonly p: number }> = ({
  x, y, name, mech, p,
}) => {
  const { cx, gap } = LC;
  const nameStyle: React.CSSProperties = { fontFamily: FONT, fontSize: ds(32), fontWeight: W.bold, color: C.charcoal, lineHeight: 1.2 };
  const mechStyle: React.CSSProperties = { fontFamily: FONT, fontSize: 23, fontWeight: W.medium, color: C.inkSoft, lineHeight: "28px" };
  if (Math.abs(x - cx) < 5) {
    const above = y < LC.cy;
    return (
      <div
        style={{
          position: "absolute",
          left: x,
          top: above ? y - gap : y + gap,
          translate: above ? "-50% -100%" : "-50% 0",
          textAlign: "center",
          whiteSpace: "nowrap",
          opacity: p,
        }}
      >
        <div style={nameStyle}>{name}</div>
        <div style={mechStyle}>{mech}</div>
      </div>
    );
  }
  const right = x > cx;
  return (
    <div
      style={{
        position: "absolute",
        left: right ? x + 34 : x - 34,
        top: y - 38,
        translate: right ? "0 0" : "-100% 0",
        width: 300,
        textAlign: right ? "left" : "right",
        opacity: p,
      }}
    >
      <div style={nameStyle}>{name}</div>
      <div style={{ ...mechStyle, marginTop: 4, textWrap: "balance" }}>{mech}</div>
    </div>
  );
};

const Lifecycle: React.FC = () => {
  const { t, D, cue } = useShot();
  const { cx, cy, R } = LC;
  const pts: Pt[] = STAGES.map((_, i) => {
    const ang = -Math.PI / 2 + (i * 2 * Math.PI) / STAGES.length;
    return [cx + R * Math.cos(ang), cy + R * Math.sin(ang)];
  });
  const last = cue("tái thiết kế", 8);
  const roleAt = cue("người quyết định cuối cùng", D * 0.6);
  const stageP = STAGES.map(({ key }, i) => appear(t, cue(key, 0.8 + i * 1.2)));
  return (
    <>
      <Kicker label="Đưa dân chủ vào giai đoạn nào? — mô hình của Nhóm 14" p={appear(t, 0.1)} />
      <Svg>
        <Thread pts={[...pts, pts[0]]} p={ease((t - 0.4) / Math.max(last, 1))} />
        {pts.map(([x, y], i) => (
          <circle key={STAGES[i].key} cx={x} cy={y} r={16} fill={C.paper} stroke={C.cobalt} strokeWidth={5} opacity={stageP[i]} />
        ))}
      </Svg>
      {STAGES.map(({ name, mech }, i) => (
        <StageLabel key={name} x={pts[i][0]} y={pts[i][1]} name={name} mech={mech} p={stageP[i]} />
      ))}
      {ROLES.map(({ role, duty, accent }, i) => {
        const y = 260 + i * 170;
        return (
          <Card key={role} x0={1250} y0={y} x1={1790} y1={y + 130} p={appear(t, roleAt + i * 0.8)} accent={accent} pad="0 30px" style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 8 }}>
            <div style={{ fontFamily: FONT, fontSize: ds(34), fontWeight: W.bold, color: C.charcoal, lineHeight: 1.2 }}>{role}</div>
            <div style={{ fontFamily: FONT, fontSize: 26, fontWeight: W.medium, color: C.inkSoft, lineHeight: 1.2 }}>{duty}</div>
          </Card>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------- ab
const AB_STEPS = [
  { label: "Tiêu chí xử lý công bố", key: "tiêu chí xử lý" },
  { label: "Mã theo dõi, không lộ danh tính", key: "mã theo dõi" },
  { label: "Phản hồi kèm lý do", key: "phản hồi kèm lý do" },
  { label: "Tổng hợp đã khử nhận dạng", key: "khử nhận dạng" },
  { label: "Yêu cầu xem xét lại", key: "xem xét lại" },
  { label: "Nhật ký thay đổi sau góp ý", key: "nhật ký" },
] as const;

const Ab: React.FC = () => {
  const { t, D, cue } = useShot();
  // The narration of this shot starts on B's first feature, so card B must be up before its first dot
  // (V12 let the dots appear on bare paper when "phương án b" was not spoken in the shot).
  const atB = Math.max(0.5, Math.min(cue("phương án b", 4), cue(AB_STEPS[0].key, 5) - 0.6));
  const pa = appear(t, Math.min(cue("phương án a", 0.6), atB));
  const pb = appear(t, atB);
  const decideAt = cue("chạm tới quyết định", D - 2.5);
  const qd = appear(t, decideAt + 0.8);
  return (
    <>
      <Kicker label="Mô hình minh họa của Nhóm 14 — không phải hệ thống có thật" p={appear(t, 0.1)} />

      <Card x0={130} y0={190} x1={640} y1={800} p={pa} accent={C.cobalt} />
      <Txt x={170} y={220} size={ds(90)} weight="bold" color={C.cobalt} p={pa} lh={1}>
        A
      </Txt>
      <div
        style={{
          ...abs(180, 380, 410, 70),
          display: "flex",
          alignItems: "center",
          paddingLeft: 20,
          border: `3px solid ${C.charcoal}`,
          borderRadius: 10,
          opacity: pa,
          fontFamily: FONT,
          fontSize: 28,
          fontWeight: W.medium,
          color: C.inkSoft,
        }}
      >
        Gửi ý kiến…
      </div>
      <div style={{ ...abs(300, 610, 170, 110), ...centred, backgroundColor: C.charcoal, opacity: pa, fontFamily: FONT, fontSize: ds(60), fontWeight: W.bold, color: C.paper }}>
        ?
      </div>

      <Card x0={700} y0={190} x1={1790} y1={800} p={pb} accent={C.vermilion} />
      <Txt x={740} y={220} size={ds(90)} weight="bold" color={C.vermilion} p={pb} lh={1}>
        B
      </Txt>
      <Svg>
        <Arrow a={[385, 470]} b={[385, 600]} p={ease((t - cue("không biết", 2)) / 0.8)} color={C.cobalt} width={4} />
        {AB_STEPS.map(({ key }, i) => {
          const [col, row] = [Math.floor(i / 3), i % 3];
          return <circle key={key} cx={780 + col * 520} cy={360 + row * 120} r={14} fill={C.vermilion} opacity={appear(t, Math.max(atB + 0.3, cue(key, 5 + i)))} />;
        })}
        <Thread pts={[[745, 340], [745, 725], [1088, 725]]} p={ease((t - decideAt) / 1.2)} />
      </Svg>
      {AB_STEPS.map(({ label, key }, i) => {
        const [col, row] = [Math.floor(i / 3), i % 3];
        return (
          <Txt key={key} x={810 + col * 520} y={360 + row * 120} v="m" size={29} weight="demi" p={appear(t, Math.max(atB + 0.3, cue(key, 5 + i)))} lh={1.2}>
            {label}
          </Txt>
        );
      })}
      {/* The pill fades in whole as the thread reaches it — never an empty outline beforehand. */}
      <div
        style={{
          ...abs(1090, 690, 380, 70),
          ...centred,
          borderRadius: 12,
          backgroundColor: C.vermilion,
          opacity: qd,
          fontFamily: FONT,
          fontSize: 32,
          fontWeight: W.bold,
          color: C.paper,
          letterSpacing: "0.02em",
        }}
      >
        QUYẾT ĐỊNH
      </div>
    </>
  );
};

// --------------------------------------------------------------- funnel
const FILTER_REASONS = [
  { label: "thư rác", key: "thư rác" },
  { label: "xâm phạm người khác", key: "xâm phạm" },
  { label: "bảo vệ người góp ý", key: "bảo vệ người góp ý" },
] as const;

const SAFEGUARDS = [
  { label: "Tiêu chí lọc công bố", key: "tiêu chí lọc" },
  { label: "Người bị lọc biết lý do", key: "người bị lọc" },
  { label: "Đề nghị xem xét lại", key: "đề nghị xem xét lại" },
] as const;

const FUNNEL_PATH = "M560,230 L1360,230 L1060,560 L1060,680 L860,680 L860,560 Z";

const Funnel: React.FC = () => {
  const { t, D, cue } = useShot();
  const p = appear(t, 0.4);
  const first = Math.max(0.6, cue(SAFEGUARDS[0].key, D * 0.5));
  // Each safeguard card follows its own phrase (V12 staggered all three from the first one).
  const cardAt = SAFEGUARDS.map(({ key }, i) => (i === 0 ? first : Math.max(first + i * 0.4, cue(key, first + i * 0.7))));
  const s = appear(t, cue("tham gia hình thức", D - 2));
  return (
    <>
      <Kicker label="Kiểm duyệt có điều kiện" p={appear(t, 0.1)} />
      <Svg>
        <path d={FUNNEL_PATH} fill={C.cobaltWash} stroke={C.cobalt} strokeWidth={2} strokeLinejoin="round" opacity={p} />
      </Svg>
      <Txt x={960} y={300} anchor="c" v="m" size={32} weight="demi" color={C.cobalt} p={p} lh={1.2}>
        Ý kiến gửi đến
      </Txt>
      {FILTER_REASONS.map(({ label, key }, i) => (
        <Txt key={key} x={520} y={380 + i * 60} anchor="r" v="m" size={28} color={C.inkSoft} p={appear(t, cue(key, 1 + i))} lh={1.2}>
          {label}
        </Txt>
      ))}
      {SAFEGUARDS.map(({ label, key }, i) => {
        const y = 300 + i * 120;
        return (
          <Card key={key} x0={1420} y0={y} x1={1800} y1={y + 90} p={appear(t, cardAt[i])} accent={C.vermilion} pad="0 25px" style={{ display: "flex", alignItems: "center" }}>
            <span style={{ fontFamily: FONT, fontSize: 28, fontWeight: W.demi, color: C.charcoal }}>{label}</span>
          </Card>
        );
      })}
      <Txt x={960} y={770} anchor="c" v="m" size={ds(44)} weight="bold" color={C.vermilion} p={s} rise={10} lh={1.2}>
        Thiếu giải trình và kháng nghị: chỉ còn tham gia hình thức
      </Txt>
    </>
  );
};

export const GFX_BESPOKEB: Record<string, React.FC> = {
  feenberg: Feenberg,
  matrix: Matrix,
  options: Options,
  rationality: Rationality,
  lifecycle: Lifecycle,
  ab: Ab,
  funnel: Funnel,
};
