-- Chạy đúng 1 lần khi volume postgres_data còn trống.
-- Tạo database riêng cho pytest (quy tắc testing.md: không mock DB).
CREATE DATABASE galaxy_staff_test;

-- btree_gist cần cho EXCLUDE constraint chống chồng giờ (erd.md mục 5.4)
CREATE EXTENSION IF NOT EXISTS btree_gist;
\connect galaxy_staff_test
CREATE EXTENSION IF NOT EXISTS btree_gist;
