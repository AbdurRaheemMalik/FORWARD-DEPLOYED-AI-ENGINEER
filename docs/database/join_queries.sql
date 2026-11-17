-- J1. Show each complaint with customer name.           (expected: 30 rows)
SELECT c.complaint_id,
       cu.first_name || ' ' || cu.last_name AS customer_name,
       c.category, c.priority, c.status, c.received_at
FROM complaint c
JOIN customer cu ON cu.customer_id = c.customer_id
ORDER BY c.complaint_id;


-- J2. Add optional account type without dropping complaints that have no account.
-- LEFT JOIN keeps all 30; CMP023, CMP029, CMP030 show NULL account_type.
SELECT c.complaint_id,
       cu.first_name || ' ' || cu.last_name AS customer_name,
       c.account_id,
       a.account_type
FROM complaint c
JOIN customer cu    ON cu.customer_id = c.customer_id
LEFT JOIN account a ON a.account_id   = c.account_id
ORDER BY c.complaint_id;


-- J3. Verify distinct complaint count before and after joins.
-- Expected: before 30, after 30, joined rows 30, and 27 with an INNER JOIN.
SELECT
    (SELECT COUNT(DISTINCT complaint_id) FROM complaint)                    AS before_join,
    (SELECT COUNT(DISTINCT c.complaint_id)
       FROM complaint c
       JOIN customer cu    ON cu.customer_id = c.customer_id
       LEFT JOIN account a ON a.account_id   = c.account_id)                AS after_left_join,
    (SELECT COUNT(*)
       FROM complaint c
       JOIN customer cu    ON cu.customer_id = c.customer_id
       LEFT JOIN account a ON a.account_id   = c.account_id)                AS joined_rows,
    (SELECT COUNT(DISTINCT c.complaint_id)
       FROM complaint c
       JOIN account a ON a.account_id = c.account_id)                       AS after_inner_join;


-- J4. Create complaint_analyst_view containing only justified fields.
-- Included: what an analyst needs to investigate a complaint.
-- Excluded: customer email and phone, account number and balance (not needed, sensitive).
DROP VIEW IF EXISTS complaint_analyst_view;

CREATE VIEW complaint_analyst_view AS
SELECT c.complaint_id,
       c.received_at,
       c.channel,
       c.category,
       c.priority,
       c.status,
       c.complaint_text,
       cu.customer_id,
       cu.first_name || ' ' || cu.last_name AS customer_name,
       cu.segment,
       c.account_id,
       a.account_type,
       c.assigned_analyst_id
FROM complaint c
JOIN customer cu    ON cu.customer_id = c.customer_id
LEFT JOIN account a ON a.account_id   = c.account_id;

SELECT COUNT(*) AS view_rows FROM complaint_analyst_view;   -- expected: 30
