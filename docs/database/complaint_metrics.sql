-- M1. Headline volumes: total, unresolved, closed and urgent complaints.
-- (expected: total 30, unresolved 29, closed 1, urgent_unresolved 12)
SELECT COUNT(*)                                                              AS total_complaints,
       SUM(CASE WHEN status NOT IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END) AS unresolved,
       SUM(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END)     AS closed,
       SUM(CASE WHEN status NOT IN ('RESOLVED', 'CLOSED')
                 AND priority IN ('Critical', 'High') THEN 1 ELSE 0 END)     AS urgent_unresolved
FROM complaint;


-- M2. Closure rate: share of complaints closed, as a percentage.
-- 100.0 (not 100) avoids whole-number division.        (expected: 3.3)
SELECT ROUND(100.0 * SUM(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS closure_rate_pct
FROM complaint;


-- M3. Complaints by status, with share of total.       (expected: 4 rows)
SELECT status,
       COUNT(*)                                              AS complaints,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)    AS pct_of_total
FROM complaint
GROUP BY status
ORDER BY complaints DESC;


-- M4. Complaints by category, with how many are still unresolved.  (expected: 7 rows)
SELECT category,
       COUNT(*)                                                              AS complaints,
       SUM(CASE WHEN status NOT IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END) AS unresolved,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)                    AS pct_of_total
FROM complaint
GROUP BY category
ORDER BY complaints DESC, category;


-- M5. Complaints by priority, in priority order.       (expected: 4 rows)
SELECT priority,
       COUNT(*) AS complaints
FROM complaint
GROUP BY priority
ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
                       WHEN 'Medium'   THEN 3 WHEN 'Low'  THEN 4 ELSE 5 END;


-- M6. Complaints by channel.                           (expected: 4 rows)
SELECT channel,
       COUNT(*)                                           AS complaints,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM complaint
GROUP BY channel
ORDER BY complaints DESC;


-- M7. Complaints received per month.                   (expected: 2025-01: 10, 2025-02: 20)
SELECT strftime('%Y-%m', received_at) AS month,
       COUNT(*)                       AS complaints
FROM complaint
GROUP BY month
ORDER BY month;


-- M8. Ageing of unresolved complaints: average, oldest and newest age in days.
-- (expected: 29 unresolved; oldest 55 days, newest 1 day)
SELECT COUNT(*)                                                                 AS unresolved,
       ROUND(AVG(julianday('2025-02-25') - julianday(date(received_at))), 1)    AS avg_age_days,
       MAX(CAST(julianday('2025-02-25') - julianday(date(received_at)) AS INTEGER)) AS oldest_age_days,
       MIN(CAST(julianday('2025-02-25') - julianday(date(received_at)) AS INTEGER)) AS newest_age_days
FROM complaint
WHERE status NOT IN ('RESOLVED', 'CLOSED');


-- M9. Analyst workload: assigned and unresolved complaints per analyst.
-- (expected: 4 analysts with complaints; John Smith, Sarah Lee, Sophia Martin 8 each)
SELECT e.employee_id,
       e.first_name || ' ' || e.last_name                                         AS analyst,
       COUNT(c.complaint_id)                                                      AS assigned,
       SUM(CASE WHEN c.status NOT IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END)    AS unresolved,
       SUM(CASE WHEN c.priority IN ('Critical', 'High') THEN 1 ELSE 0 END)        AS urgent
FROM employee e
JOIN complaint c ON c.assigned_analyst_id = e.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY assigned DESC, e.employee_id;


-- M10. Repeat complainant rate: customers with more than one complaint.
-- (expected: 10 customers, 10 repeat, 100.0%, 3.0 complaints per customer)
WITH complaints_per_customer AS (
    SELECT customer_id, COUNT(*) AS complaint_count
    FROM complaint
    GROUP BY customer_id
)
SELECT COUNT(*)                                                         AS customers_with_complaints,
       SUM(CASE WHEN complaint_count > 1 THEN 1 ELSE 0 END)             AS repeat_complainants,
       ROUND(100.0 * SUM(CASE WHEN complaint_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                        AS repeat_rate_pct,
       ROUND(AVG(complaint_count), 1)                                   AS avg_complaints_per_customer
FROM complaints_per_customer;


-- M11. Average days from complaint received to first customer response.
-- Only complaints that have a response are counted.     (expected: 10 responded)
SELECT COUNT(*)                                                                   AS responded,
       ROUND(AVG(julianday(r.first_sent) - julianday(date(c.received_at))), 1)    AS avg_days_to_first_response,
       MAX(CAST(julianday(r.first_sent) - julianday(date(c.received_at)) AS INTEGER)) AS max_days_to_first_response
FROM complaint c
JOIN (SELECT complaint_id, MIN(sent_date) AS first_sent
      FROM customer_response
      GROUP BY complaint_id) r ON r.complaint_id = c.complaint_id;


-- M12. Investigation progress: started, completed and average days to complete.
-- (expected: 10 started, 2 completed, 2.0 days on average)
SELECT COUNT(*)                                                         AS investigations,
       SUM(CASE WHEN completed_at IS NOT NULL THEN 1 ELSE 0 END)        AS completed,
       SUM(CASE WHEN completed_at IS NULL THEN 1 ELSE 0 END)            AS in_progress,
       ROUND(AVG(julianday(completed_at) - julianday(started_at)), 1)   AS avg_days_to_complete
FROM investigation;


-- M13. Complaints with no linked account (data-quality metric). (expected: 3)
SELECT COUNT(*)                                     AS complaints_without_account,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaint), 1) AS pct_of_total
FROM complaint
WHERE account_id IS NULL;