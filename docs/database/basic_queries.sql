-- B1. List all open complaints.                         (expected: 19 rows)
SELECT complaint_id, customer_id, category, priority, status, received_at
FROM complaint
WHERE status = 'OPEN'
ORDER BY received_at;


-- B2. List high-priority unresolved complaints.         (expected: 12 rows)
-- 'Critical' is included because it ranks above 'High'.
SELECT complaint_id, customer_id, category, priority, status, received_at
FROM complaint
WHERE priority IN ('Critical', 'High')
  AND status NOT IN ('RESOLVED', 'CLOSED')
ORDER BY CASE priority WHEN 'Critical' THEN 1 ELSE 2 END, received_at;


-- B3. Count complaints by status.                       (expected: 4 rows)
SELECT status, COUNT(*) AS complaint_count
FROM complaint
GROUP BY status
ORDER BY complaint_count DESC;


-- B4. Count complaints by category.                     (expected: 7 rows)
SELECT category, COUNT(*) AS complaint_count
FROM complaint
GROUP BY category
ORDER BY complaint_count DESC, category;


-- B5. Show complaints for a supplied customer ID.       (CUS001: 4 rows)
SELECT complaint_id, category, priority, status, received_at
FROM complaint
WHERE customer_id = :customer_id
ORDER BY received_at;


-- B6. Show complaints opened within a supplied date range.
-- '< end date + 1 day' keeps complaints received later on the end date.
-- (2025-02-01 to 2025-02-05: 3 rows)
SELECT complaint_id, customer_id, category, status, received_at
FROM complaint
WHERE received_at >= :start_date
  AND received_at <  date(:end_date, '+1 day')
ORDER BY received_at;


-- B7. List closed complaints where date_closed is missing (expected zero).
-- The complaint table has NO date_closed column, so the literal query fails:
--   SELECT complaint_id FROM complaint
--   WHERE status = 'CLOSED' AND date_closed IS NULL;   -- error: no such column
-- Closest check with the current schema: CLOSED complaints that have no
-- CLOSED event in the status history.                   (expected: 0 rows)
SELECT c.complaint_id, c.status
FROM complaint c
LEFT JOIN complaint_status_history h
       ON h.complaint_id = c.complaint_id
      AND h.new_status   = 'CLOSED'
WHERE c.status = 'CLOSED'
  AND h.history_id IS NULL;


-- B8. Show the ten most recently opened complaints.     (expected: 10 rows, CMP030 first)
SELECT complaint_id, customer_id, category, status, received_at
FROM complaint
ORDER BY received_at DESC, complaint_id DESC
LIMIT 10;
