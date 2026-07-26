import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuthStore } from "@/stores/authStore";

interface ProtectedRouteProps {
  children: ReactNode;
  /** Đặt true cho các trang chỉ Manager mới được vào (FR-AUTH-13) */
  managerOnly?: boolean;
}

/** Chặn truy cập trang nội bộ khi chưa đăng nhập hoặc sai vai trò. */
export function ProtectedRoute({ children, managerOnly = false }: ProtectedRouteProps) {
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const accessToken = useAuthStore((state) => state.accessToken);

  if (!user || !accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Còn dùng mật khẩu mặc định thì phải đổi trước khi vào bất kỳ trang nào khác
  if (user.must_change_password && location.pathname !== "/doi-mat-khau") {
    return <Navigate to="/doi-mat-khau" replace />;
  }

  if (managerOnly && user.role !== "manager") {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
