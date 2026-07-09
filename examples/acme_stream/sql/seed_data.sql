-- ACME Stream synthetic demo data for Trustline v0.1.
-- Views keep demo.duckdb small while preserving seeded audit outcomes.

CREATE SCHEMA IF NOT EXISTS main;

CREATE OR REPLACE VIEW main.donor_gifts AS
SELECT
    i AS donor_id,
    'donor' || i || '@acme-stream.example' AS email,
    25.0 + (i % 50) AS gift_amount,
    DATE '2025-01-01' + CAST((i % 90) AS INTEGER) AS gift_date
FROM generate_series(1, 2000) AS gs(i);

CREATE OR REPLACE VIEW main.app_users AS
SELECT
    i AS user_id,
    'donor' || i || '@acme-stream.example' AS email
FROM generate_series(1, 800) AS gs(i);

CREATE OR REPLACE VIEW main.watch_events AS
SELECT
    user_id,
    DATE '2025-02-01' + CAST((user_id % 28) AS INTEGER) AS watch_date
FROM generate_series(1, 180) AS gs(user_id);

CREATE OR REPLACE VIEW main.crm_push_queue AS
SELECT i AS contact_id
FROM generate_series(1, 300) AS gs(i);

CREATE OR REPLACE VIEW main.crm_contacts_mirror AS
SELECT i AS contact_id
FROM generate_series(1, 80) AS gs(i);

CREATE OR REPLACE VIEW main.user_events_silver AS
SELECT
    'LegacyPlayer' AS event_source,
    DATE '2025-01-01' + CAST((i % 60) AS INTEGER) AS event_date
FROM generate_series(1, 1000) AS gs(i)
UNION ALL
SELECT
    'NewPlayer' AS event_source,
    DATE '2025-03-15' + CAST((i % 60) AS INTEGER) AS event_date
FROM generate_series(1, 1110) AS gs(i);

CREATE OR REPLACE VIEW main.propensity_scores_staging AS
SELECT
    i AS score_id,
    CURRENT_TIMESTAMP - INTERVAL 1 DAY AS scored_at
FROM generate_series(1, 100) AS gs(i);

CREATE OR REPLACE VIEW main.features_training AS
SELECT
    i AS user_id,
    CASE
        WHEN i <= 12 THEN DATE '2025-04-15'
        ELSE NULL
    END AS subscription_date
FROM generate_series(1, 100) AS gs(i);

CREATE OR REPLACE VIEW main.features_scoring AS
SELECT i AS user_id
FROM generate_series(1, 100) AS gs(i);
