export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        drone: "0 0 35px rgba(34, 197, 94, 0.18)",
      },
      colors: {
        midnight: "#08101c",
        ocean: "#0b1734",
      },
    },
  },
  plugins: [],
};
