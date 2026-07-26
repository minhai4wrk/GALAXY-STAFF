/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Thang màu cho Overlap View: càng nhiều người rảnh càng đậm (FR-AVAIL-01)
        overlap: {
          0: "hsl(0 0% 100%)",
          1: "hsl(152 60% 92%)",
          2: "hsl(152 60% 82%)",
          3: "hsl(152 58% 70%)",
          4: "hsl(152 56% 56%)",
          5: "hsl(152 60% 42%)",
        },
        // Màu trạng thái ca trên Roster và Exchange Board
        shift: {
          assigned: "hsl(211 90% 55%)",
          open: "hsl(215 16% 65%)",
          conflict: "hsl(0 72% 55%)",
          exchange: "hsl(32 95% 55%)",
          pending: "hsl(262 70% 60%)",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};
