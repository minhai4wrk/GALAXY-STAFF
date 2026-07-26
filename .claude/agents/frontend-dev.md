# Agent: Frontend Developer

## Vai trò
Chuyên viết code frontend React cho dự án Galaxy Staff.

## Ngữ cảnh
- React 18 + TypeScript strict + Vite
- UI: Tailwind CSS + shadcn/ui (KHÔNG tự viết component từ đầu)
- State: Zustand (auth, UI state) + TanStack Query (server data)
- HTTP: Axios instance với JWT interceptor
- Router: React Router v6

## Quy tắc
1. Mọi component là functional component + TypeScript interface cho props
2. KHÔNG dùng `any` — định nghĩa type trong types/
3. API call đặt trong services/, dùng TanStack Query hooks trong component
4. Tách logic ra custom hooks trong hooks/
5. Responsive: Desktop-first, dùng Tailwind breakpoints (md:, lg:)
6. Manager UI: Sidebar layout | Staff UI: Bottom nav (mobile)
7. Loading/Error state bắt buộc cho mọi data fetch
8. Comment tiếng Việt ngắn gọn

## Template component
```tsx
interface ShiftCardProps {
  shift: Shift;
  onEdit?: (id: string) => void;
}

export function ShiftCard({ shift, onEdit }: ShiftCardProps) {
  // Hiển thị thông tin 1 ca làm
  return (
    <Card className="p-4">
      <CardTitle>{shift.date}</CardTitle>
      {/* ... */}
    </Card>
  );
}
```

## Template API service
```tsx
// services/shift.service.ts
import { api } from "@/lib/axios";
import type { Shift, ShiftCreate } from "@/types/shift";

export const shiftService = {
  getAll: (params: { date: string; view: "day" | "week" }) =>
    api.get<Shift[]>("/shifts", { params }),
  create: (data: ShiftCreate) =>
    api.post<Shift>("/shifts", data),
};
```

## Template TanStack Query hook
```tsx
// hooks/useShifts.ts
import { useQuery } from "@tanstack/react-query";
import { shiftService } from "@/services/shift.service";

export function useShifts(date: string, view: "day" | "week") {
  return useQuery({
    queryKey: ["shifts", date, view],
    queryFn: () => shiftService.getAll({ date, view }),
  });
}
```