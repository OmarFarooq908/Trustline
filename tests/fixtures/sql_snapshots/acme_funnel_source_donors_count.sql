SELECT COUNT(*) AS actual_count
FROM (
SELECT donor_id, email, gift_amount FROM main.donor_gifts WHERE gift_date >= '2025-01-01'
) AS source_donors
