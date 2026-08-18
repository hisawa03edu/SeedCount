-- Seed Morphology Analyzer 2.0.1 -> 2.1.0
-- Bread側テーブルは変更しません。1回だけ実行してください。
CREATE TABLE IF NOT EXISTS seed_manual_corrections (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id BIGINT UNSIGNED NOT NULL,
  automatic_count INT UNSIGNED NOT NULL,
  corrected_count INT UNSIGNED NOT NULL,
  deleted_object_ids JSON NULL,
  added_points JSON NULL,
  note VARCHAR(255) NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_seed_correction_record (record_id),
  CONSTRAINT fk_seed_correction_record FOREIGN KEY (record_id)
    REFERENCES seed_count_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
