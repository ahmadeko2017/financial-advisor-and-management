/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Inter Tight"', "Inter", "system-ui", "sans-serif"],
        sans: ['"Inter Tight"', "Inter", "system-ui", "sans-serif"],
      },
      colors: {
        ink: {
          900: "#0f172a",
          700: "#1e293b",
          500: "#334155",
          300: "#cbd5e1",
          100: "#e2e8f0",
        },
        lime: {
          500: "#a3e635",
          600: "#84cc16",
        },
      },
    },
  },
  plugins: [],
};
