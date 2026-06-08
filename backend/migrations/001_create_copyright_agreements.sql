-- 版权协议签署表迁移脚本
-- 运行此脚本将创建 copyright_agreements 表

-- SQLite
CREATE TABLE IF NOT EXISTS copyright_agreements (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    work_id INTEGER,
    signature_data TEXT NOT NULL,
    signature_name VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    agreement_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (work_id) REFERENCES works (id) ON DELETE CASCADE
);

-- PostgreSQL (如果使用 PostgreSQL)
-- CREATE TABLE IF NOT EXISTS copyright_agreements (
--     id SERIAL NOT NULL PRIMARY KEY,
--     user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     work_id INTEGER REFERENCES works(id) ON DELETE CASCADE,
--     signature_data TEXT NOT NULL,
--     signature_name VARCHAR(100),
--     ip_address VARCHAR(50),
--     user_agent VARCHAR(500),
--     agreement_content TEXT NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_copyright_agreements_user_id ON copyright_agreements(user_id);
CREATE INDEX IF NOT EXISTS idx_copyright_agreements_work_id ON copyright_agreements(work_id);