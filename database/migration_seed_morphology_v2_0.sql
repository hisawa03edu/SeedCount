-- Seed Morphology Analyzer Version 2.0
-- Bread既存テーブルは変更しません。seed_接頭辞の既存テーブル拡張と新規テーブル追加のみです。
-- Version 1.4までのSeedテーブルを作成済みのDBで、1回だけ実行してください。

ALTER TABLE seed_count_settings
  ADD COLUMN min_circularity DECIMAL(6,4) NOT NULL DEFAULT 0.1500 AFTER min_solidity,
  ADD COLUMN max_circularity DECIMAL(6,4) NOT NULL DEFAULT 1.2000 AFTER min_circularity,
  ADD COLUMN min_extent DECIMAL(6,4) NOT NULL DEFAULT 0.2500 AFTER max_circularity,
  ADD COLUMN watershed_enabled TINYINT(1) NOT NULL DEFAULT 1 AFTER close_iterations,
  ADD COLUMN distance_ratio DECIMAL(6,4) NOT NULL DEFAULT 0.3800 AFTER watershed_enabled,
  ADD COLUMN watershed_bg_iterations SMALLINT UNSIGNED NOT NULL DEFAULT 2 AFTER distance_ratio,
  ADD COLUMN clahe_enabled TINYINT(1) NOT NULL DEFAULT 0 AFTER watershed_bg_iterations,
  ADD COLUMN clahe_clip DECIMAL(6,3) NOT NULL DEFAULT 2.000 AFTER clahe_enabled,
  ADD COLUMN pixels_per_mm DECIMAL(12,5) NOT NULL DEFAULT 0 AFTER max_side;

ALTER TABLE seed_count_records
  ADD COLUMN analysis_json JSON NULL AFTER settings_json,
  ADD COLUMN mean_area_px2 DECIMAL(14,4) NULL AFTER module_version,
  ADD COLUMN mean_major_axis_px DECIMAL(12,4) NULL AFTER mean_area_px2,
  ADD COLUMN mean_minor_axis_px DECIMAL(12,4) NULL AFTER mean_major_axis_px,
  ADD COLUMN mean_circularity DECIMAL(8,5) NULL AFTER mean_minor_axis_px;

CREATE TABLE IF NOT EXISTS seed_morphology_objects (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id BIGINT UNSIGNED NOT NULL,
  object_number INT UNSIGNED NOT NULL,
  centroid_x DECIMAL(12,3) NOT NULL,
  centroid_y DECIMAL(12,3) NOT NULL,
  area_px2 DECIMAL(14,3) NOT NULL,
  perimeter_px DECIMAL(14,3) NOT NULL,
  major_axis_px DECIMAL(12,3) NOT NULL,
  minor_axis_px DECIMAL(12,3) NOT NULL,
  aspect_ratio DECIMAL(10,4) NOT NULL,
  circularity DECIMAL(10,4) NOT NULL,
  solidity DECIMAL(10,4) NOT NULL,
  extent DECIMAL(10,4) NOT NULL,
  convex_hull_area_px2 DECIMAL(14,3) NOT NULL,
  equivalent_diameter_px DECIMAL(12,3) NOT NULL,
  orientation_deg DECIMAL(9,3) NOT NULL,
  area_mm2 DECIMAL(14,5) NULL,
  perimeter_mm DECIMAL(12,5) NULL,
  major_axis_mm DECIMAL(12,5) NULL,
  minor_axis_mm DECIMAL(12,5) NULL,
  quality_class VARCHAR(30) NOT NULL DEFAULT 'normal',
  metrics_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_seed_object (record_id, object_number),
  KEY idx_seed_object_record (record_id),
  CONSTRAINT fk_seed_object_record FOREIGN KEY (record_id) REFERENCES seed_count_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
