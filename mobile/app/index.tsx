/**
 * Faza 0.4 — telefon backendni ko'ryaptimi?
 *
 * Bu ekran demo uchun emas, jamoa uchun. Xakaton davomida tarmoq bir necha marta
 * uziladi va "nega ishlamayapti" degan savolga shu ekran javob beradi: qaysi
 * manzilga urinilyapti, qancha vaqtda javob keldi, qaysi konteyner tushib qolgan.
 *
 * Faza 3.2 da bu ekran o'rnini kirish ekrani egallaydi.
 */

import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { api, API_URL, Health, IS_API_URL_SET, IS_LOCALHOST, NetworkError } from "../lib/api";
import { color, radius, space, touch } from "../theme/tokens";

type State =
  | { kind: "checking" }
  | { kind: "ok"; data: Health; ms: number }
  | { kind: "error"; message: string; hint: string };

/** Xatoni foydalanuvchi bajara oladigan qadamga aylantiradi. */
function hintFor(error: unknown): string {
  if (!IS_API_URL_SET) {
    return "mobile/.env faylida EXPO_PUBLIC_API_URL ni to'ldiring va Expo ni qayta ishga tushiring.";
  }
  if (IS_LOCALHOST) {
    return "Manzilda localhost turibdi. Telefon uchun bu o'zining ichki manzili.\nNoutbukning LAN IP sini yozing: ipconfig getifaddr en0";
  }
  if (error instanceof NetworkError) {
    return "1) docker compose ps — konteynerlar ishlayaptimi\n2) Telefon va noutbuk bitta tarmoqdami\n3) Tarmoq qurilmalar orasini bloklasa — telefondan hotspot tarqating\n4) Eski jarayon 8000-portni band qilmaganmi: lsof -nP -iTCP:8000";
  }
  return "Backend javob berdi, lekin kutilgan shaklda emas.";
}

export default function ConnectionScreen() {
  const [state, setState] = useState<State>({ kind: "checking" });

  const check = useCallback(async () => {
    setState({ kind: "checking" });
    const started = Date.now();
    try {
      const data = await api.health();
      setState({ kind: "ok", data, ms: Date.now() - started });
    } catch (error) {
      setState({
        kind: "error",
        message: error instanceof Error ? error.message : String(error),
        hint: hintFor(error),
      });
    }
  }, []);

  useEffect(() => {
    void check();
  }, [check]);

  return (
    <ScrollView contentContainerStyle={styles.page}>
      <View style={styles.card}>
        <Text style={styles.label}>API MANZILI</Text>
        <Text style={styles.mono} selectable>
          {IS_API_URL_SET ? API_URL : "ko'rsatilmagan"}
        </Text>
        {IS_LOCALHOST ? (
          <View style={styles.warn}>
            <Text style={styles.warnText}>
              Manzilda localhost turibdi — telefon buni o'zining ichki manzili deb
              tushunadi va backendga yetib bormaydi.
            </Text>
          </View>
        ) : null}
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>HOLAT</Text>

        {state.kind === "checking" ? (
          <View style={styles.row}>
            <ActivityIndicator color={color.accent} />
            <Text style={styles.body}>Tekshirilmoqda…</Text>
          </View>
        ) : null}

        {state.kind === "ok" ? (
          <>
            <View style={styles.row}>
              <View style={[styles.dot, { backgroundColor: color.low }]} />
              <Text style={[styles.body, styles.strong]}>Backend javob berdi</Text>
            </View>
            <View style={styles.kvGroup}>
              <KV k="Versiya" v={state.data.version} />
              <KV k="Javob vaqti" v={`${state.ms} ms`} />
              <KV k="Baza" v={state.data.services.db} ok={state.data.services.db === "ok"} />
              <KV k="AI xizmati" v={state.data.services.ai} ok={state.data.services.ai === "ok"} />
            </View>
          </>
        ) : null}

        {state.kind === "error" ? (
          <>
            <View style={styles.row}>
              <View style={[styles.dot, { backgroundColor: color.high }]} />
              <Text style={[styles.body, styles.strong]}>Ulanmadi</Text>
            </View>
            <Text style={styles.errText}>{state.message}</Text>
            <View style={styles.err}>
              <Text style={styles.label}>NIMA QILISH KERAK</Text>
              <Text style={styles.hint}>{state.hint}</Text>
            </View>
          </>
        ) : null}
      </View>

      <Pressable
        onPress={check}
        disabled={state.kind === "checking"}
        style={({ pressed }) => [
          styles.button,
          pressed && styles.pressed,
          state.kind === "checking" && styles.disabled,
        ]}
      >
        <Text style={styles.buttonText}>Qayta tekshirish</Text>
      </Pressable>
    </ScrollView>
  );
}

function KV({ k, v, ok }: { k: string; v: string; ok?: boolean }) {
  return (
    <View style={styles.kv}>
      <Text style={styles.kvKey}>{k}</Text>
      <Text
        style={[styles.kvVal, ok === false && { color: color.high }]}
        numberOfLines={1}
      >
        {v}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { padding: space.base, gap: space.md },
  card: {
    backgroundColor: color.panel,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: color.line,
    padding: space.base,
    gap: space.sm,
  },
  label: { fontSize: 11, fontWeight: "600", letterSpacing: 1.1, color: color.muted },
  mono: { fontFamily: "Menlo", fontSize: 14, color: color.ink },
  body: { fontSize: 16, color: color.ink },
  strong: { fontWeight: "600" },
  row: { flexDirection: "row", alignItems: "center", gap: space.sm },
  dot: { width: 10, height: 10, borderRadius: radius.full },

  kvGroup: { gap: space.xs, marginTop: space.xs },
  kv: { flexDirection: "row", justifyContent: "space-between", gap: space.md },
  kvKey: { fontSize: 13, color: color.muted },
  kvVal: { fontFamily: "Menlo", fontSize: 13, color: color.ink, flexShrink: 1 },

  errText: { fontSize: 14, color: color.high },
  warn: { backgroundColor: color.mediumWash, borderRadius: radius.sm, padding: space.md },
  warnText: { fontSize: 13, color: color.medium, lineHeight: 19 },
  err: { backgroundColor: color.highWash, borderRadius: radius.sm, padding: space.md, gap: space.xs },
  hint: { fontSize: 13, color: color.ink, lineHeight: 20 },

  button: {
    height: touch.primary,
    borderRadius: radius.md,
    backgroundColor: color.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  pressed: { opacity: 0.85 },
  disabled: { opacity: 0.45 },
  buttonText: { color: "#FFFFFF", fontSize: 17, fontWeight: "600" },
});
