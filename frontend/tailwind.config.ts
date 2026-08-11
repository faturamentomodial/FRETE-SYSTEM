import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0F1115",
        surface: "#171A21",
        surface2: "#1D2129",
        border: "#2A2F38",
        text: {
          primary: "#F5F5F5",
          secondary: "#9CA3AF",
        },
        state: {
          success: "#22C55E",
          warning: "#F59E0B",
          error: "#EF4444",
          info: "#3B82F6",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
