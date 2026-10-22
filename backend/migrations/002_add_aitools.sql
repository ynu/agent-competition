-- AI 工具（快捷入口）结构迁移脚本
-- 为 contents 表添加快捷入口字段
-- 注意：后端启动时 init_db() 会通过 _ensure_columns() 自动补齐这些列，
-- 本脚本仅供手动迁移其他环境时参考。

-- SQLite
ALTER TABLE contents ADD COLUMN category VARCHAR(100);
ALTER TABLE contents ADD COLUMN tags VARCHAR(500);
ALTER TABLE contents ADD COLUMN external_url VARCHAR(500);
ALTER TABLE contents ADD COLUMN icon VARCHAR(500);

-- MySQL / PostgreSQL
-- ALTER TABLE contents ADD COLUMN category VARCHAR(100);
-- ALTER TABLE contents ADD COLUMN tags VARCHAR(500);
-- ALTER TABLE contents ADD COLUMN external_url VARCHAR(500);
-- ALTER TABLE contents ADD COLUMN icon VARCHAR(500);
