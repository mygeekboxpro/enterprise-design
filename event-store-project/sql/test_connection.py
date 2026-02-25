"""
Test database connection.

Run this to verify PostgreSQL is accessible.
"""

import psycopg2

# Connection parameters
conn_params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'eventstore',
    'user': 'eventstore',
    'password': 'eventstore123'
}


def test_connection():
    """Test database connection and setup."""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Test query
        print("Testing query...")
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()

        print("\n" + "=" * 60)
        print("✓ Database connection successful!")
        print("=" * 60)
        print(f"PostgreSQL version:")
        print(f"  {db_version[0]}")

        # Check if events table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'events'
            )
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("\n✓ Events table exists")

            # Count events
            cursor.execute("SELECT COUNT(*) FROM events")
            event_count = cursor.fetchone()[0]
            print(f"✓ Events in database: {event_count}")
        else:
            print("\n✗ Events table not found")
            print("  Run: docker exec -i event-store-db psql "
                  "-U eventstore -d eventstore < schema.sql")

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("Setup verification complete!")
        print("=" * 60)

    except psycopg2.OperationalError as e:
        print("\n" + "=" * 60)
        print("✗ Connection failed!")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if PostgreSQL is running:")
        print("     docker-compose ps")
        print("  2. Start PostgreSQL:")
        print("     docker-compose up -d")
        print("  3. Check logs:")
        print("     docker-compose logs postgres")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    test_connection()