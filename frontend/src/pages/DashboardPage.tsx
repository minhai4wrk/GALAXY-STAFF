import { CalendarDays, Clapperboard, Megaphone, Repeat, Users } from "lucide-react";

import { useAuthStore } from "@/stores/authStore";

// Các module sẽ được nối vào theo từng sprint
const MODULES = [
  { icon: CalendarDays, title: "Lịch rảnh", description: "Đăng ký và tổng hợp lịch rảnh", sprint: "Sprint 3" },
  { icon: Users, title: "Lịch làm việc", description: "Xếp ca và xếp ca tự động", sprint: "Sprint 4" },
  { icon: Repeat, title: "Trao đổi ca", description: "Pass ca, nhận ca, duyệt", sprint: "Sprint 5" },
  { icon: Megaphone, title: "Bảng tin", description: "Thông báo nội bộ", sprint: "Sprint 2" },
];

/** Khung Dashboard — các module được nối vào dần theo tiến độ sprint. */
export function DashboardPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="min-h-screen bg-muted">
      <header className="border-b bg-card">
        <div className="container flex h-14 items-center gap-3">
          <Clapperboard className="size-6 text-primary" />
          <span className="font-semibold">Galaxy Staff</span>
          <span className="ml-auto text-sm text-muted-foreground">
            {user?.full_name ?? "Chưa đăng nhập"}
          </span>
        </div>
      </header>

      <main className="container py-8">
        <h1 className="mb-1 text-2xl font-semibold">Bảng điều khiển</h1>
        <p className="mb-6 text-sm text-muted-foreground">
          Khung ứng dụng đã sẵn sàng. Các module sẽ được bổ sung theo từng sprint.
        </p>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {MODULES.map((item) => (
            <div key={item.title} className="rounded-lg border bg-card p-5">
              <item.icon className="mb-3 size-6 text-primary" />
              <h2 className="font-medium">{item.title}</h2>
              <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
              <span className="mt-3 inline-block rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                {item.sprint}
              </span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
