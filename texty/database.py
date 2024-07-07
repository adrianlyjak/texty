###############################
## data persistence (sqlite) ##
###############################

from contextlib import contextmanager
import datetime
from queue import Queue
import sqlite3 as sql
from typing import List, Optional

from texty.gametypes import TimeNode

import threading
from functools import wraps


def init_db():
    """
    Initialize the database
    """
    with db_pool.connection() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS time_nodes (
    id TEXT PRIMARY KEY,
    scenario_id TEXT,
    summary TEXT,
    data TEXT)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS active_node (
    scenario_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL REFERENCES time_nodes(id),
    last_updated TEXT
)"""
        )
        conn.commit()


def get_active_node(scenario_id: str) -> Optional[TimeNode]:
    """
    Get the active node
    """
    with db_pool.connection() as conn:
        result = conn.execute(
            "SELECT data FROM time_nodes WHERE id = (SELECT node_id FROM active_node WHERE scenario_id = ?)",
            (scenario_id,),
        ).fetchone()

    return TimeNode.model_validate_json(result[0]) if result else None


def list_games() -> List[tuple[datetime.datetime, TimeNode]]:
    with db_pool.connection() as conn:
        rows = conn.execute(
            "SELECT an.last_updated, tn.data, tn.id, tn.scenario_id FROM active_node as an INNER JOIN time_nodes as tn ON tn.id = an.node_id ORDER BY an.last_updated DESC"
        ).fetchall()
        response = []
        for row in rows:
            data = row[1]
            parsed = TimeNode.model_validate_json(data)
            time = datetime.datetime.fromisoformat(row[0])
            response.append((time, parsed))
        return response


def delete_game(scenario_id: str):
    with db_pool.connection() as conn:
        conn.execute("DELETE FROM active_node WHERE scenario_id = ?", (scenario_id,))
        conn.execute("DELETE FROM time_nodes WHERE scenario_id = ?", (scenario_id,))
        conn.commit()


def get_node(id: str) -> Optional[TimeNode]:
    """
    Get a time node by id
    """
    with db_pool.connection() as conn:
        result = conn.execute(
            "SELECT data FROM time_nodes WHERE id = ?", (id,)
        ).fetchone()
    return TimeNode.model_validate_json(result[0]) if result else None


def insert_time_node(
    time_node: TimeNode,
    now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
):
    """
    Insert a time node into the database
    """
    with db_pool.connection() as conn:

        conn.execute(
            "INSERT INTO time_nodes (id, summary, data) VALUES (?, ?, ?)",
            (time_node.id, time_node.summary, time_node.model_dump_json()),
        )
        conn.execute(
            "INSERT OR REPLACE INTO active_node (scenario_id, node_id, last_updated) VALUES (?, ?, ?)",
            (time_node.scenario_id(), time_node.id, now.isoformat(timespec="seconds")),
        )
        conn.commit()


def set_active_node(
    scenario_id: str,
    node_id: str,
    now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
):
    """
    Set the active node
    """
    with db_pool.connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO active_node (scenario_id, node_id, last_updated) VALUES (?, ?, ?)",
            (scenario_id, node_id, now.isoformat(timespec="seconds")),
        )
        conn.commit()


def list_all_time_nodes(scenario_id: str) -> List[TimeNode]:
    """
    List all time nodes in the database
    """
    with db_pool.connection() as conn:

        return [
            TimeNode.model_validate_json(row[0])
            for row in conn.execute(
                "SELECT data FROM time_nodes WHERE scenario_id = ?", (scenario_id,)
            )
        ]


class SQLiteConnectionPool:
    def __init__(self, database, max_connections=5):
        self.database = database
        self.max_connections = max_connections
        self.connections = Queue(maxsize=max_connections)
        self.connection_count = 0
        self.lock = threading.Lock()

    def get_connection(self):
        if self.connections.qsize() > 0:
            return self.connections.get()

        with self.lock:
            if self.connection_count < self.max_connections:
                self.connection_count += 1
                return sql.connect(self.database, check_same_thread=False)

        return self.connections.get()

    def return_connection(self, connection):
        if self.connections.qsize() < self.max_connections:
            self.connections.put(connection)
        else:
            connection.close()

    @contextmanager
    def connection(self):
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)


# Create a global instance of the connection pool
db_pool = SQLiteConnectionPool("texty.db")
