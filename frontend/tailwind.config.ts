import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#07111D",
        panel: "#0D1B2A",
        panelraised: "#122437",
        panelborder: "#24384C",
        osd: "#39D5C3",
        watch: "#FFB454",
        alert: "#FF6470",
        info: "#6FA8FF",
        muted: "#8FA5B8",
        ink: "#ECF4F8",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
        osd: ["var(--font-osd)"],
      },
    },
  },
  plugins: [],
};
export default config;
