import sqlite3


class DatabaseManager:
    def __init__(self, db_path="vgls_snap.db"):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                generated_hash TEXT NOT NULL,
                size INTEGER NOT NULL,
                permissions TEXT NOT NULL,
                owner INTEGER NOT NULL,
                modified_time REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def get_all_metadata(self):
        """Retrieve all file metadata from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files")
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row for row in rows}  # Return a dictionary keyed by file path

    def update_or_insert_metadata(self, metadata_list):
        """Update existing records or insert new ones."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for metadata in metadata_list:
            cursor.execute("SELECT * FROM files WHERE path = ?", (metadata.path,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Update if metadata has changed
                if (existing_entry[1] != metadata.generated_hash or
                        existing_entry[2] != metadata.size or
                        existing_entry[3] != metadata.permissions or
                        existing_entry[4] != metadata.owner or
                        existing_entry[5] != metadata.modified_time):
                    cursor.execute("""
                        UPDATE files
                        SET generated_hash = ?, size = ?, permissions = ?, owner = ?, modified_time = ?
                        WHERE path = ?
                    """, (metadata.generated_hash, metadata.size, metadata.permissions, metadata.owner, metadata.modified_time,
                          metadata.path))
            else:
                # Insert new file
                cursor.execute("""
                    INSERT INTO files (path, generated_hash, size, permissions, owner, modified_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (metadata.path, metadata.generated_hash, metadata.size, metadata.permissions, metadata.owner,
                      metadata.modified_time))

        conn.commit()
        conn.close()

    def delete_removed_files(self, current_files):
        """Delete files from the database that are not in the current scan."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT path FROM files")
        all_stored_files = {row[0] for row in cursor.fetchall()}

        files_to_delete = all_stored_files - current_files
        for file_path in files_to_delete:
            cursor.execute("DELETE FROM files WHERE path = ?", (file_path,))

        conn.commit()
        conn.close()
