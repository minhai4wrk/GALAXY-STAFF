import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { TokenPair, User } from "@/types/api";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (tokens: TokenPair) => void;
  setAccessToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  isManager: () => boolean;
}

/**
 * Phiên đăng nhập, lưu vào localStorage để giữ trạng thái khi tải lại trang.
 * Đăng xuất chỉ xóa token phía client — JWT là stateless, V1 không có blacklist.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setSession: (tokens) =>
        set({
          user: tokens.user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        }),

      setAccessToken: (token) => set({ accessToken: token }),

      setUser: (user) => set({ user }),

      logout: () => set({ user: null, accessToken: null, refreshToken: null }),

      isManager: () => get().user?.role === "manager",
    }),
    { name: "galaxy-auth" },
  ),
);
