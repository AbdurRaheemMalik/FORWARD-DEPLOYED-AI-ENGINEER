class ServiceRequestRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_for_complaint(self, complaint_id):
        """Only request_id, request_type, status, created_date; ordered by created_date, request_id."""
        return self.conn.execute(
            """SELECT request_id, request_type, status, created_date
               FROM service_request
               WHERE complaint_id = %s
               ORDER BY created_date, request_id""",
            (complaint_id,),
        ).fetchall()