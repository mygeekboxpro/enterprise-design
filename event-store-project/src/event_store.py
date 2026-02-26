"""
Event Store implementation.

Manages persistence of events to PostgreSQL database.
"""

import psycopg2
import json
from typing import List
from events import Event


class EventStore:
    """
    Event Store: manages event persistence.

    Responsibilities:
    - Append events to database
    - Load events by aggregate
    - Ensure version consistency

    Usage:
        store = EventStore(connection_params)
        store.append(event)
        events = store.load_events("Order", "123")
        store.close()
    """

    def __init__(self, connection_params: dict):
        """
        Initialize Event Store.

        Args:
            connection_params: Dictionary with:
                - host: Database host
                - port: Database port
                - database: Database name
                - user: Database user
                - password: Database password
        """
        self.conn_params = connection_params
        self.conn = None

    def connect(self):
        """Open database connection if not already open."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.conn_params)

    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def append(self, event: Event) -> bool:
        """
        Append event to Event Store.

        This is the ONLY way to add events.
        Events are immutable - never updated or deleted.
        Uses UNIQUE constraint on (aggregate_type, aggregate_id,
        version) to prevent duplicate versions.

        Args:
            event: Event to store

        Returns:
            True if successful

        Raises:
            Exception: If version conflict occurs

        Example:
            event = order_created("order-123", "customer-456", 1)
            store.append(event)
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            # Insert event into database
            cursor.execute("""
                INSERT INTO events 
                (event_id, aggregate_type, aggregate_id, 
                 event_type, version, data, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                event.event_id,
                event.aggregate_type,
                event.aggregate_id,
                event.event_type,
                event.version,
                json.dumps(event.data),  # Convert dict to JSON string
                event.timestamp
            ))

            # Commit transaction
            self.conn.commit()
            cursor.close()
            return True

        except psycopg2.IntegrityError as e:
            # Version conflict: another process already used
            # this version
            self.conn.rollback()
            cursor.close()
            raise Exception(
                f"Version conflict for {event.aggregate_id} "
                f"version {event.version}. "
                f"Another event already exists with this version."
            ) from e

    def load_events(self, aggregate_type: str,
                    aggregate_id: str) -> List[Event]:
        """
        Load all events for an aggregate.

        Events are returned in version order (oldest first).
        This is used to rebuild aggregate state by replaying
        events.

        Args:
            aggregate_type: Type of entity (e.g., "Order")
            aggregate_id: Specific entity ID (e.g., "123")

        Returns:
            List of events, ordered by version ascending

        Example:
            events = store.load_events("Order", "order-123")
            for event in events:
                order.apply(event)
        """
        self.connect()
        cursor = self.conn.cursor()

        # Query all events for this aggregate
        cursor.execute("""
            SELECT event_id, aggregate_type, aggregate_id,
                   event_type, version, data, timestamp
            FROM events
            WHERE aggregate_type = %s AND aggregate_id = %s
            ORDER BY version ASC
        """, (aggregate_type, aggregate_id))

        # Build Event objects from database rows
        events = []
        for row in cursor.fetchall():
            event = Event(
                event_id=row[0],
                aggregate_type=row[1],
                aggregate_id=row[2],
                event_type=row[3],
                version=row[4],
                data=row[5],  # json.loads(row[5]),  # Parse JSON to dict
                timestamp=row[6]
            )
            events.append(event)

        cursor.close()
        return events

    def get_latest_version(self, aggregate_type: str,
                           aggregate_id: str) -> int:
        """
        Get the latest version number for an aggregate.

        Use this before appending new events to ensure you're
        using the correct next version number.

        Args:
            aggregate_type: Type of entity
            aggregate_id: Specific entity ID

        Returns:
            Latest version number, or 0 if aggregate doesn't exist

        Example:
            current_version = store.get_latest_version(
                "Order", "order-123"
            )
            next_version = current_version + 1
            event = item_added(..., version=next_version)
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT MAX(version)
            FROM events
            WHERE aggregate_type = %s AND aggregate_id = %s
        """, (aggregate_type, aggregate_id))

        result = cursor.fetchone()[0]
        cursor.close()

        # Return 0 if no events exist
        return result if result is not None else 0

    def event_exists(self, aggregate_type: str,
                     aggregate_id: str) -> bool:
        """
        Check if aggregate has any events.

        Args:
            aggregate_type: Type of entity
            aggregate_id: Specific entity ID

        Returns:
            True if aggregate exists, False otherwise

        Example:
            if store.event_exists("Order", "order-123"):
                print("Order exists")
        """
        return self.get_latest_version(
            aggregate_type, aggregate_id
        ) > 0

    def get_all_aggregate_ids(self, aggregate_type: str) -> List[str]:
        """
        Get all aggregate IDs of a specific type.

        Args:
            aggregate_type: Type of entity

        Returns:
            List of aggregate IDs

        Example:
            order_ids = store.get_all_aggregate_ids("Order")
            print(f"Found {len(order_ids)} orders")
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT DISTINCT aggregate_id
            FROM events
            WHERE aggregate_type = %s
            ORDER BY aggregate_id
        """, (aggregate_type,))

        ids = [row[0] for row in cursor.fetchall()]
        cursor.close()

        return ids
