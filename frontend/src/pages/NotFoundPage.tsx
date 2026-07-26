import { Link } from "react-router-dom";

/** Trang 404 dùng chung cho mọi đường dẫn không khớp route nào. */
export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-muted px-4 text-center">
      <p className="text-5xl font-semibold text-primary">404</p>
      <p className="text-muted-foreground">Không tìm thấy trang bạn yêu cầu</p>
      <Link to="/dashboard" className="text-sm font-medium text-primary underline">
        Quay lại Bảng điều khiển
      </Link>
    </div>
  );
}
