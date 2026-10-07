import type React from "react";
import { GFX_BESPOKEA } from "./bespokeA";
import { GFX_BESPOKEB } from "./bespokeB";
import { GFX_CORE } from "./core";

/** Graphic name (as used in scripts/v13_film.py PLAN) → component. Components read time via useShot(). */
export const GRAPHICS: Record<string, React.FC> = { ...GFX_CORE, ...GFX_BESPOKEA, ...GFX_BESPOKEB };
