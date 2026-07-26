import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

import { useAuthStore } from "@/stores/authStore";
import type { ApiError } from "@/types/api";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
});

/** Gắn access token vào mọi request đã đăng nhập. */
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Gom các request bị 401 trong lúc đang refresh, tránh gọi /auth/refresh nhiều lần song song
let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setAccessToken, logout } = useAuthStore.getState();
  if (!refreshToken) {
    logout();
    return null;
  }
  try {
    const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    const newToken: string = response.data.data.access_token;
    setAccessToken(newToken);
    return newToken;
  } catch {
    logout();
    return null;
  }
}

/** Access token hết hạn thì tự làm mới một lần rồi gửi lại request (FR-AUTH-03). */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const original = error.config as InternalAxiosRequestConfig & { _retried?: boolean };

    const shouldRefresh =
      error.response?.status === 401 &&
      original &&
      !original._retried &&
      !original.url?.includes("/auth/login") &&
      !original.url?.includes("/auth/refresh");

    if (shouldRefresh) {
      original._retried = true;
      refreshing ??= refreshAccessToken().finally(() => {
        refreshing = null;
      });
      const token = await refreshing;
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
    }

    return Promise.reject(error);
  },
);

/** Lấy câu lỗi tiếng Việt do backend trả về, có câu dự phòng nếu mất mạng. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiError>(error)) {
    return error.response?.data?.detail ?? "Không kết nối được máy chủ, vui lòng thử lại";
  }
  return "Đã có lỗi xảy ra";
}

export default api;
