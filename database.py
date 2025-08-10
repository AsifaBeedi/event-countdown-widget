import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_FILE = "countdown_events.db"

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                event_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                notification_enabled INTEGER DEFAULT 1,
                notification_days_before INTEGER DEFAULT 1,
                theme_color TEXT DEFAULT '#013220',
                priority INTEGER DEFAULT 1
            )
        ''')
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                notification_type TEXT,
                notification_time TIMESTAMP,
                is_sent INTEGER DEFAULT 0,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_event(self, name: str, event_date: str, description: str = "", 
                  notification_enabled: bool = True, notification_days_before: int = 1,
                  theme_color: str = "#013220", priority: int = 1) -> int:
        """Add a new event to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (name, description, event_date, notification_enabled, 
                              notification_days_before, theme_color, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, event_date, notification_enabled, 
              notification_days_before, theme_color, priority))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_all_events(self, active_only: bool = True) -> List[Dict]:
        """Get all events from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, name, description, event_date, created_at, updated_at,
                   is_active, notification_enabled, notification_days_before,
                   theme_color, priority
            FROM events
        '''
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY event_date ASC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            events.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'event_date': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'is_active': row[6],
                'notification_enabled': row[7],
                'notification_days_before': row[8],
                'theme_color': row[9],
                'priority': row[10]
            })
        
        conn.close()
        return events
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict]:
        """Get a specific event by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, event_date, created_at, updated_at,
                   is_active, notification_enabled, notification_days_before,
                   theme_color, priority
            FROM events WHERE id = ?
        ''', (event_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'event_date': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'is_active': row[6],
                'notification_enabled': row[7],
                'notification_days_before': row[8],
                'theme_color': row[9],
                'priority': row[10]
            }
        return None
    
    def update_event(self, event_id: int, **kwargs) -> bool:
        """Update an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['name', 'description', 'event_date', 'notification_enabled',
                        'notification_days_before', 'theme_color', 'priority', 'is_active']:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            conn.close()
            return False
        
        # Add updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(event_id)
        
        query = f"UPDATE events SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event (soft delete by setting is_active to 0)"""
        return self.update_event(event_id, is_active=0)
    
    def hard_delete_event(self, event_id: int) -> bool:
        """Permanently delete an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete associated notifications first
        cursor.execute("DELETE FROM notifications WHERE event_id = ?", (event_id,))
        
        # Delete the event
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def get_setting(self, key: str, default_value: str = None) -> str:
        """Get a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        return default_value
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        
        conn.commit()
        conn.close()
        return True
