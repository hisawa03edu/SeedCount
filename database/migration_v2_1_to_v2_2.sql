-- Seed Morphology Analyzer 2.1 -> 2.2
-- Seed専用設定テーブルだけを拡張します。1回だけ実行してください。
ALTER TABLE seed_count_settings
  ADD COLUMN threshold_method ENUM('otsu','manual','adaptive') NOT NULL DEFAULT 'otsu' AFTER threshold_value,
  ADD COLUMN background_correction TINYINT(1) NOT NULL DEFAULT 1 AFTER clahe_clip,
  ADD COLUMN background_kernel SMALLINT UNSIGNED NOT NULL DEFAULT 101 AFTER background_correction,
  ADD COLUMN adaptive_block SMALLINT UNSIGNED NOT NULL DEFAULT 51 AFTER background_kernel,
  ADD COLUMN adaptive_c DECIMAL(7,3) NOT NULL DEFAULT 5.000 AFTER adaptive_block,
  ADD COLUMN peak_kernel SMALLINT UNSIGNED NOT NULL DEFAULT 21 AFTER adaptive_c;
