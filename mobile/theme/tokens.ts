/**
 * Vaqtinchalik tokenlar — Faza 0/1 uchun.
 * To'liq dizayn tizimi Faza 3.1 da `design/screens.html` asosida quriladi.
 * Qoida: vidjet ichida rang qattiq yozilmaydi, hammasi shu fayldan olinadi.
 */

export const color = {
  ground: "#F4F7F8",
  panel: "#FFFFFF",
  panelAlt: "#EDF2F4",
  ink: "#0D1519",
  muted: "#5C6B74",
  line: "#DCE4E7",
  accent: "#175E75",

  // Xavf semantikasi — Faza 3 dan boshlab
  high: "#B32B22",
  highWash: "#FBEBEA",
  medium: "#8A5200",
  mediumWash: "#FBF1E2",
  low: "#14663F",
  lowWash: "#E7F2EC",
} as const;

export const space = { xs: 4, sm: 8, md: 12, base: 16, lg: 20, xl: 24 } as const;
export const radius = { sm: 6, md: 10, lg: 16, full: 999 } as const;
export const touch = { min: 48, primary: 56 } as const;
