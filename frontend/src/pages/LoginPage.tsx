import { Clapperboard } from "lucide-react";

/**
 * Trang đăng nhập — hiện mới là khung giao diện.
 * Sprint 2 sẽ nối API POST /api/auth/login và thêm React Hook Form + Zod.
 */
export function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted px-4">
      <div className="w-full max-w-sm rounded-lg border bg-card p-8 shadow-sm">
        <div className="mb-6 flex flex-col items-center gap-2">
          <Clapperboard className="size-10 text-primary" />
          <h1 className="text-xl font-semibold">Galaxy Staff</h1>
          <p className="text-sm text-muted-foreground">Hệ thống quản lý nhân sự rạp chiếu phim</p>
        </div>

        <form className="space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="manager@galaxy.vn"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="text-sm font-medium">
              Mật khẩu
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          <button
            type="submit"
            disabled
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          >
            Đăng nhập (Sprint 2)
          </button>
        </form>
      </div>
    </div>
  );
}
