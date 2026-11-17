-- A1. CASE for unresolved age buckets 0-7, 8-30 and 31+ days.
-- (expected: 29 rows; 7 in 0-7, 13 in 8-30, 9 in 31+)
SELECT complaint_id, status, received_at,
       CAST(julianday('2025-02-25') - julianday(date(received_at)) AS INTEGER) AS age_days,
       CASE
           WHEN julianday('2025-02-25') - julianday(date(received_at)) <= 7  THEN '0-7 days'
           WHEN julianday('2025-02-25') - julianday(date(received_at)) <= 30 THEN '8-30 days'
           ELSE '31+ days'
       END AS age_bucket
FROM complaint
WHERE status NOT IN ('RESOLVED', 'CLOSED')
ORDER BY age_days DESC, complaint_id;


-- A2. CTE to identify repeat complainants.             (expected: 10 rows)
WITH complaint_counts AS (
    SELECT customer_id, COUNT(*) AS complaint_count
    FROM complaint
    GROUP BY customer_id
),
repeat_complainants AS (
    SELECT customer_id, complaint_count
    FROM complaint_counts
    WHERE complaint_count > 1
)
SELECT r.customer_id,
       cu.first_name || ' ' || cu.last_name AS customer_name,
       r.complaint_count
FROM repeat_complainants r
JOIN customer cu ON cu.customer_id = r.customer_id
ORDER BY r.complaint_count DESC, r.customer_id;


-- A3. ROW_NUMBER to select latest status per complaint. (expected: 30 rows)
-- history_id breaks ties: every changed_at is the time the seed script ran.
WITH ranked_status AS (
    SELECT complaint_id, new_status, changed_at,
           ROW_NUMBER() OVER (PARTITION BY complaint_id
                              ORDER BY changed_at DESC, history_id DESC) AS rn
    FROM complaint_status_history
)
SELECT complaint_id, new_status AS latest_status, changed_at
FROM ranked_status
WHERE rn = 1
ORDER BY complaint_id;


-- A4. Rank customers by complaint count.               (ranks 1,1,1,4,4,4,4,8,8,8)
SELECT customer_id, COUNT(*) AS complaint_count,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS customer_rank
FROM complaint
GROUP BY customer_id
ORDER BY customer_rank, customer_id;


-- A5. Determine complaint priority classification.
-- (expected: 12 Urgent, 9 Standard, 8 Routine, 1 Closed)
SELECT complaint_id, priority, status,
       CASE
           WHEN status IN ('RESOLVED', 'CLOSED') THEN 'Closed'
           WHEN priority IN ('Critical', 'High') THEN 'Urgent'
           WHEN priority = 'Medium'              THEN 'Standard'
           WHEN priority = 'Low'                 THEN 'Routine'
           ELSE 'Unclassified'
       END AS priority_classification
FROM complaint
ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
                       WHEN 'Medium'   THEN 3 WHEN 'Low'  THEN 4 ELSE 5 END,
         received_at;


-- A6. Find customers who submitted more than one complaint. (expected: 10 rows)
SELECT customer_id, COUNT(*) AS complaint_count
FROM complaint
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY complaint_count DESC, customer_id;


-- A7. Rank customers by number of complaints (dense rank and unique position).
-- (dense_rnk 1,1,1,2,2,2,2,3,3,3; position 1-10)
SELECT customer_id, COUNT(*) AS complaint_count,
       DENSE_RANK() OVER (ORDER BY COUNT(*) DESC)              AS dense_rnk,
       ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, customer_id) AS position
FROM complaint
GROUP BY customer_id
ORDER BY position;


-- A8. Rank complaints by receive date within each category. (expected: 30 rows)
SELECT complaint_id, category, received_at,
       ROW_NUMBER() OVER (PARTITION BY category
                          ORDER BY received_at, complaint_id) AS rank_in_category
FROM complaint
ORDER BY category, rank_in_category;
