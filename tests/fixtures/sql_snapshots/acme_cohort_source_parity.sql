SELECT
  CASE
    WHEN 'main.features_training' = 'main.features_scoring' THEN 1
    ELSE 0
  END AS source_parity
