/**
 * Kiểu dữ liệu API — ánh xạ 1-1 với components.schemas trong docs/api/openapi.yaml.
 * Giữ nguyên tên trường; lệch tên là dấu hiệu code đã đi chệch thiết kế.
 */

// ---------- Bao ngoài thống nhất (.claude/rules/api.md) ----------
export interface ApiResponse<T> {
  data: T;
}

export interface ApiListResponse<T> {
  data: T[];
  total: number;
}

export interface ApiError {
  detail: string;
}

// ---------- ENUM (khớp docs/erd.md mục 4) ----------
export type UserRole = "manager" | "staff";

/** Chỉ có 2 giá trị. Open-shift là `assigned_user === null`, khóa trao đổi là `is_locked`. */
export type ShiftStatus = "draft" | "published";

export type AssignSource = "manual" | "auto" | "application" | "exchange";

export type ApplyStatus = "pending" | "approved" | "rejected" | "cancelled";

export type ExchangeStatus =
  | "available_for_exchange"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "cancelled";

export type NotificationType =
  | "roster_published"
  | "shift_updated"
  | "shift_deleted"
  | "shift_applied"
  | "shift_apply_approved"
  | "shift_apply_rejected"
  | "exchange_request"
  | "exchange_approved"
  | "exchange_rejected"
  | "news_posted";

// ---------- Auth & Users ----------
export interface Location {
  id: number;
  name: string;
  address: string | null;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  location: Location;
  is_active: boolean;
  /** true = đang dùng mật khẩu mặc định, phải ép đổi trước khi vào Dashboard */
  must_change_password: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface UserBrief {
  id: number;
  full_name: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ---------- Availability ----------
export interface AvailabilitySlot {
  /** 0 = Thứ 6, 1 = Thứ 7, ..., 6 = Thứ 5 (tuần rạp chạy T6 -> T5) */
  day_of_week: number;
  /** HH:mm. CÓ THỂ nhỏ hơn start_time khi khung giờ vắt qua nửa đêm (18:00 -> 02:00) */
  start_time: string;
  end_time: string;
}

export interface AvailabilitySubmission {
  id: number;
  user_id: number;
  user_name?: string;
  week_start: string;
  total_days: number;
  reason: string | null;
  slots: AvailabilitySlot[];
  /** Tính ở server tại thời điểm gọi API, không lưu trong database */
  is_locked: boolean;
  deadline_at?: string;
  submitted_at: string;
  updated_at: string | null;
}

export interface OverlapCell {
  day_of_week: number;
  /** 0 = 08:00–08:30 ... 35 = 01:30–02:00 */
  slot_index: number;
  count: number;
  user_ids: number[];
}

export interface OverlapView {
  week_start: string;
  total_staff: number;
  /** Chỉ chứa ô có ít nhất một người rảnh — ô vắng mặt nghĩa là không ai rảnh */
  cells: OverlapCell[];
}

// ---------- Shifts ----------
export interface Shift {
  id: number;
  location_id: number;
  /** Ngày vận hành — ca kết thúc 02:00 vẫn thuộc ngày làm việc hôm trước */
  work_date: string;
  week_start: string;
  /** UTC. 18:00 giờ rạp (UTC+7) tương ứng 11:00Z */
  start_at: string;
  end_at: string;
  duration_hours: number;
  /** null nghĩa là Open-shift — đây là cách duy nhất nhận biết ca trống */
  assigned_user: UserBrief | null;
  assignment_source: AssignSource | null;
  assigned_at: string | null;
  status: ShiftStatus;
  /** true khi ca đang có yêu cầu trao đổi hoặc đơn xin ca chờ duyệt */
  is_locked: boolean;
  unassigned_reason: string | null;
  override_reason: string | null;
  published_at: string | null;
  created_at: string;
}

export type ShiftConflictCode =
  | "not_available"
  | "overlapping_shift"
  | "exceeds_weekly_hours"
  | "insufficient_rest"
  | "too_many_consecutive_days";

export interface ShiftConflict {
  code: ShiftConflictCode;
  message: string;
  related_shift_id: number | null;
}

// ---------- Exchange ----------
export interface Exchange {
  id: number;
  shift: Shift;
  from_user: UserBrief;
  to_user: UserBrief | null;
  message: string | null;
  status: ExchangeStatus;
  has_conflict: boolean;
  conflict_note: string | null;
  created_at: string;
  taken_at: string | null;
  reviewed_at: string | null;
}

// ---------- News & Notification ----------
export interface NewsImage {
  id: number;
  image_url: string;
  sort_order: number;
}

export interface NewsPost {
  id: number;
  title: string;
  content: string;
  author: UserBrief;
  images: NewsImage[];
  /** Trạng thái đọc của người đang đăng nhập */
  is_read: boolean;
  read_count?: number;
  created_at: string;
  /** Khác null -> hiện nhãn "Đã chỉnh sửa" */
  updated_at: string | null;
}

export interface Notification {
  id: number;
  type: NotificationType;
  message: string;
  reference_id: number | null;
  /** Chỉ dùng cho roster_published — chứa week_start để mở đúng tuần trên Roster */
  reference_date: string | null;
  is_read: boolean;
  created_at: string;
}
