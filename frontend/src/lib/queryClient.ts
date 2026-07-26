import { QueryClient } from "@tanstack/react-query";

/** Cấu hình cache dùng chung cho toàn bộ server state. */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Dữ liệu roster và lịch rảnh đổi không thường xuyên, giữ 1 phút là hợp lý
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
