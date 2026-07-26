import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // Đọc .env ở thư mục gốc dự án để backend và frontend dùng chung một file cấu hình
  envDir: path.resolve(__dirname, ".."),
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    // Cần cho hot-reload khi chạy trong Docker trên Windows
    watch: { usePolling: true },
  },
});
