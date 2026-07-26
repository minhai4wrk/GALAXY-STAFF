# Quy tắc React

- File naming: PascalCase cho component (ShiftCard.tsx), camelCase cho hooks (useShifts.ts)
- Mỗi page có Loading skeleton + Error fallback
- Form validation: React Hook Form + Zod
- Toast notification: sonner (đã có trong shadcn/ui)
- Date handling: date-fns (KHÔNG dùng moment.js)
- Icon: lucide-react
- Không inline style — chỉ dùng Tailwind classes
- Tối đa 1 component per file (trừ sub-components nhỏ)