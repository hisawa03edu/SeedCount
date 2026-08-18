-- Seed Count Analyzer Version 1.1 追加用マイグレーション
--
-- Bread Research Analyzerが現在使用している「同じデータベース」を選択して実行します。
-- Bread既存テーブルへの DROP / ALTER / UPDATE / DELETE は一切行いません。
-- 追加するのは seed_ 接頭辞の専用テーブルだけです。

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
    module_version VARCHAR(30) NOT NULL DEFAULT '1.1.0',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_seed_job (job_id),
    UNIQUE KEY uq_seed_token (access_token),
    KEY idx_seed_created (created_at),
    KEY idx_seed_device (device_name),
    KEY idx_seed_count (seed_count)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
