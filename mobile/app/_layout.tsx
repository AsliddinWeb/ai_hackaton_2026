import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { color } from "../theme/tokens";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: color.ground },
          headerShadowVisible: false,
          headerTintColor: color.ink,
          headerTitleStyle: { fontWeight: "600" },
          contentStyle: { backgroundColor: color.ground },
        }}
      >
        <Stack.Screen name="index" options={{ title: "Ulanish" }} />
      </Stack>
    </SafeAreaProvider>
  );
}
