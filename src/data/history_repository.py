class HistoryRepository:
    """complaint_status_history: append-only, so no update or delete methods."""

    def __init__(self, conn):
        self.conn = conn

    def get_for_complaint(self, complaint_id):
        """The six history columns, oldest first (the order of the contract's Complaint.history)."""
        return self.conn.execute(
            """SELECT history_id, complaint_id, old_status, new_status, changed_at, changed_by_role
               FROM complaint_status_history
               WHERE complaint_id = %s
               ORDER BY changed_at, history_id""",
            (complaint_id,),
        ).fetchall()

    def next_id(self):
        """'H' + (highest number + 1), five digits, e.g. H00281 after the seed."""
        row = self.conn.execute(
            """SELECT 'H' || LPAD((COALESCE(MAX(CAST(SUBSTRING(history_id FROM 2) AS INTEGER)), 0) + 1)::TEXT,
                                  5, '0') AS next_id
               FROM complaint_status_history"""
        ).fetchone()
        return row["next_id"]

    def add(self, complaint_id, old_status, new_status, changed_at, changed_by_role):
        """Insert one row with next_id() and return its history_id."""
        history_id = self.next_id()
        self.conn.execute(
            """INSERT INTO complaint_status_history
                   (history_id, complaint_id, old_status, new_status, changed_at, changed_by_role)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (history_id, complaint_id, old_status, new_status, changed_at, changed_by_role),
        )
        return history_id