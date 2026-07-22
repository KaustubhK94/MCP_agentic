import json
import sqlite3
from datetime import datetime, UTC

DB_NAME = "knowledge.db"


class KnowledgeStore:

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_invocations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                trip_id TEXT,

                tool_name TEXT,

                arguments TEXT,

                timestamp TEXT,

                payload TEXT
            )
            """
        )

        self.conn.commit()

    def store_tool_result(
        self,
        trip_id,
        tool_name,
        arguments,
        payload,
    ):

        self.conn.execute(
            """
            INSERT INTO tool_invocations
            (
                trip_id,
                tool_name,
                arguments,
                timestamp,
                payload
            )

            VALUES
            (?, ?, ?, ?, ?)
            """,
            (
                trip_id,
                tool_name,
                json.dumps(arguments),
                datetime.now(UTC).isoformat(),
                json.dumps(payload),
            ),
        )

        self.conn.commit()

    def find_previous_call(
        self,
        trip_id,
        tool_name,
        arguments,
    ):

        rows = self.conn.execute(
            """
            SELECT *

            FROM tool_invocations

            WHERE
                trip_id=?
                AND tool_name=?
            ORDER BY id DESC
            """,
            (
                trip_id,
                tool_name,
            ),
        ).fetchall()

        for row in rows:

            old_args = json.loads(row["arguments"])

            match = True

            for key, value in arguments.items():

                if old_args.get(key) != value:
                    match = False
                    break

            if match:
                return dict(row)

        return None

    def get_payload(self, invocation):

        return json.loads(invocation["payload"])


knowledge_store = KnowledgeStore()