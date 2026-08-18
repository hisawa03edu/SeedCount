-- Seed Morphology Analyzer 2.1.0 新規設置用
-- Bread側テーブルは変更せず、seed_接頭辞のテーブルだけを作成します。
CREATE TABLE IF NOT EXISTS seed_count_records (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, job_id CHAR(36) NOT NULL, access_token CHAR(48) NOT NULL,
 device_name VARCHAR(100) NOT NULL DEFAULT '', memo VARCHAR(255) NOT NULL DEFAULT '', seed_count INT UNSIGNED NOT NULL DEFAULT 0,
 original_path VARCHAR(255) NOT NULL, result_path VARCHAR(255) NOT NULL, threshold_value DECIMAL(8,2) NULL,
 settings_json JSON NULL, analysis_json JSON NULL, processing_ms INT UNSIGNED NULL, engine VARCHAR(100) NOT NULL DEFAULT '',
 algorithm_version VARCHAR(60) NOT NULL DEFAULT '', module_version VARCHAR(30) NOT NULL DEFAULT '2.1.0',
 mean_area_px2 DECIMAL(14,4) NULL, mean_major_axis_px DECIMAL(12,4) NULL, mean_minor_axis_px DECIMAL(12,4) NULL,
 mean_circularity DECIMAL(8,5) NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NULL,
 PRIMARY KEY(id), UNIQUE KEY uq_seed_job(job_id), UNIQUE KEY uq_seed_token(access_token), KEY idx_seed_created(created_at),
 KEY idx_seed_device(device_name), KEY idx_seed_count(seed_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS seed_manual_corrections (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, record_id BIGINT UNSIGNED NOT NULL,
 automatic_count INT UNSIGNED NOT NULL, corrected_count INT UNSIGNED NOT NULL,
 deleted_object_ids JSON NULL, added_points JSON NULL, note VARCHAR(255) NOT NULL DEFAULT '',
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id), KEY idx_seed_correction_record(record_id),
 CONSTRAINT fk_seed_correction_record FOREIGN KEY(record_id) REFERENCES seed_count_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS seed_count_settings (
 id TINYINT UNSIGNED NOT NULL, threshold_value SMALLINT NOT NULL DEFAULT -1,
 threshold_method ENUM('otsu','manual','adaptive') NOT NULL DEFAULT 'otsu', foreground ENUM('dark','light') NOT NULL DEFAULT 'dark',
 min_area DECIMAL(10,2) NOT NULL DEFAULT 100, max_area DECIMAL(10,2) NOT NULL DEFAULT 12000, max_aspect DECIMAL(6,2) NOT NULL DEFAULT 6,
 min_solidity DECIMAL(5,3) NOT NULL DEFAULT .550, min_circularity DECIMAL(6,4) NOT NULL DEFAULT .1500,
 max_circularity DECIMAL(6,4) NOT NULL DEFAULT 1.2000, min_extent DECIMAL(6,4) NOT NULL DEFAULT .2500,
 blur_size SMALLINT UNSIGNED NOT NULL DEFAULT 5, morph_kernel SMALLINT UNSIGNED NOT NULL DEFAULT 3,
 open_iterations SMALLINT UNSIGNED NOT NULL DEFAULT 1, close_iterations SMALLINT UNSIGNED NOT NULL DEFAULT 1,
 watershed_enabled TINYINT(1) NOT NULL DEFAULT 1, distance_ratio DECIMAL(6,4) NOT NULL DEFAULT .3800,
 watershed_bg_iterations SMALLINT UNSIGNED NOT NULL DEFAULT 2, clahe_enabled TINYINT(1) NOT NULL DEFAULT 0,
 clahe_clip DECIMAL(6,3) NOT NULL DEFAULT 2, background_correction TINYINT(1) NOT NULL DEFAULT 1,
 background_kernel SMALLINT UNSIGNED NOT NULL DEFAULT 101, adaptive_block SMALLINT UNSIGNED NOT NULL DEFAULT 51,
 adaptive_c DECIMAL(7,3) NOT NULL DEFAULT 5, peak_kernel SMALLINT UNSIGNED NOT NULL DEFAULT 21,
 border_margin SMALLINT UNSIGNED NOT NULL DEFAULT 2,
 max_side SMALLINT UNSIGNED NOT NULL DEFAULT 2000, pixels_per_mm DECIMAL(12,5) NOT NULL DEFAULT 0,
 allow_student_edit TINYINT(1) NOT NULL DEFAULT 0, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO seed_count_settings(id) VALUES(1) ON DUPLICATE KEY UPDATE id=id;
CREATE TABLE IF NOT EXISTS seed_morphology_objects (
 id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, record_id BIGINT UNSIGNED NOT NULL, object_number INT UNSIGNED NOT NULL,
 centroid_x DECIMAL(12,3) NOT NULL, centroid_y DECIMAL(12,3) NOT NULL, area_px2 DECIMAL(14,3) NOT NULL,
 perimeter_px DECIMAL(14,3) NOT NULL, major_axis_px DECIMAL(12,3) NOT NULL, minor_axis_px DECIMAL(12,3) NOT NULL,
 aspect_ratio DECIMAL(10,4) NOT NULL, circularity DECIMAL(10,4) NOT NULL, solidity DECIMAL(10,4) NOT NULL,
 extent DECIMAL(10,4) NOT NULL, convex_hull_area_px2 DECIMAL(14,3) NOT NULL, equivalent_diameter_px DECIMAL(12,3) NOT NULL,
 orientation_deg DECIMAL(9,3) NOT NULL, area_mm2 DECIMAL(14,5) NULL, perimeter_mm DECIMAL(12,5) NULL,
 major_axis_mm DECIMAL(12,5) NULL, minor_axis_mm DECIMAL(12,5) NULL, quality_class VARCHAR(30) NOT NULL DEFAULT 'normal',
 metrics_json JSON NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id),
 UNIQUE KEY uq_seed_object(record_id,object_number), KEY idx_seed_object_record(record_id),
 CONSTRAINT fk_seed_object_record FOREIGN KEY(record_id) REFERENCES seed_count_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
