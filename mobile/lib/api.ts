/**
 * Backend bilan ishlash qatlami.
 *
 * MUHIM: telefon `localhost` ni ko'rmaydi — u noutbukning o'zi emas.
 * `.env` da noutbukning LAN IP si turishi shart:
 *
 *   ipconfig getifaddr en0        // masalan 192.168.1.42
 *   EXPO_PUBLIC_API_URL=http://192.168.1.42:8000
 *
 * `.env` o'zgarsa Expo ni qayta ishga tushiring — EXPO_PUBLIC_* bundle
 * paytida kodga yoziladi, ish paytida o'qilmaydi.
 */

const raw = process.env.EXPO_PUBLIC_API_URL?.trim() ?? "";

export const API_URL = raw.replace(/\/+$/, "");
export const IS_API_URL_SET = API_URL.length > 0;
export const IS_LOCALHOST = /(^https?:\/\/)?(localhost|127\.0\.0\.1)/i.test(API_URL);

const TIMEOUT_MS = 8000;

/** Tarmoq umuman yetib bormaganda — noto'g'ri IP, o'chiq server, bloklangan Wi-Fi. */
export class NetworkError extends Error {
  constructor(message: string, readonly cause?: unknown) {
    super(message);
    this.name = "NetworkError";
  }
}

async function request<T>(path: string): Promise<T> {
  if (!IS_API_URL_SET) {
    throw new NetworkError(
      "API manzili ko'rsatilmagan. mobile/.env faylida EXPO_PUBLIC_API_URL ni to'ldiring.",
    );
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(`${API_URL}${path}`, {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    const text = await res.text();
    if (!res.ok) throw new NetworkError(`Server ${res.status} qaytardi`);
    return JSON.parse(text) as T;
  } catch (cause) {
    if (cause instanceof NetworkError) throw cause;
    const aborted = cause instanceof Error && cause.name === "AbortError";
    throw new NetworkError(
      aborted
        ? `Server ${TIMEOUT_MS / 1000} soniyada javob bermadi.`
        : "Serverga ulanib bo'lmadi. Telefon va noutbuk bitta tarmoqdami?",
      cause,
    );
  } finally {
    clearTimeout(timer);
  }
}

/** docs/api.md — GET /health */
export type Health = {
  status: string;
  version: string;
  time: string;
  services: { db: string; ai: string };
};

export const api = {
  health: () => request<Health>("/health"),
};
