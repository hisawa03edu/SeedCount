-- Seed Count Analyzer Version 1.2 追加用マイグレーション
-- Bread既存テーブルは変更しません。seed_ 接頭辞のテーブルだけを追加します。

CREATE TABLE IF NOT EXISTS seed_count_records (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    job_id CHAR(36) NOT NULL,
    access_token CHAR(48) NOT NULL,
    device_name VARCHAR(100) NOT NULL DEFAULT '',
    memo VARCHAR(255) NOT NULL DEFAULT '',
    seed_count INT UNSIGNED NOT NULL DEFAULT 0,
    original_path VARCHAR(255) NOT NULL,
    result_path VARCHAR(255) NOT NULL,
    threshold_value DECIMAL(8,2) NULL,
    settings_json JSON NULL,
    processing_ms INT UNSIGNED NULL,
    engine VARCHAR(100) NOT NULL DEFAULT '',
    algorithm_version VARCHAR(60) NOT NULL DEFAULT '',
    module_version VARCHAR(30) NOT NULL DEFAULT '1.2.0',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_seed_job (job_id),
    UNIQUE KEY uq_seed_token (access_token),
    KEY idx_seed_created (created_at),
    KEY idx_seed_device (device_name),
    KEY idx_seed_count (seed_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS seed_count_settings (
    id TINYINT UNSIGNED NOT NULL,
    threshold_value SMALLINT NOT NULL DEFAULT -1,
    foreground ENUM('dark','light') NOT NULL DEFAULT 'dark',
    min_area DECIMAL(10,2) NOT NULL DEFAULT 100,
    max_area DECIMAL(10,2) NOT NULL DEFAULT 12000,
    max_aspect DECIMAL(6,2) NOT NULL DEFAULT 6.00,
    min_solidity DECIMAL(5,3) NOT NULL DEFAULT 0.550,
    blur_size SMALLINT UNSIGNED NOT NULL DEFAULT 5,
    morph_kernel SMALLINT UNSIGNED NOT NULL DEFAULT 3,
    open_iterations SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    close_iterations SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    border_margin SMALLINT UNSIGNED NOT NULL DEFAULT 2,
    max_side SMALLINT UNSIGNED NOT NULL DEFAULT 2000,
    allow_student_edit TINYINT(1) NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO seed_count_settings (id) VALUES (1)
ON DUPLICATE KEY UPDATE id = id;
