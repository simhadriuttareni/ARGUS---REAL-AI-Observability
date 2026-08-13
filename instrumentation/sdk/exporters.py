"""
ARGUS Custom Exporters
Exporters for AgentObs and other observability tools
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import csv
import sqlite3


class ConsoleExporter:
    """Export events to console"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
    
    def export(self, event: Dict[str, Any]):
        """Export event to console"""
        if not self.enabled:
            return
        
        print(f"[ARGUS EVENT] {datetime.now().isoformat()}")
        print(json.dumps(event, indent=2, default=str))
        print("-" * 50)


class FileExporter:
    """Export events to a file"""
    
    def __init__(self, file_path: str = "argus_events.log", enabled: bool = True):
        self.file_path = file_path
        self.enabled = enabled
        
        # Create directory if needed
        if enabled:
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
    
    def export(self, event: Dict[str, Any]):
        """Export event to file"""
        if not self.enabled:
            return
        
        try:
            with open(self.file_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}]\n")
                f.write(json.dumps(event, default=str) + "\n")
                f.write("-\n")
        except Exception as e:
            print(f"⚠️ File exporter error: {e}")


class DatabaseExporter:
    """Export events to SQLite database"""
    
    def __init__(self, db_path: str = "argus_events.db", enabled: bool = True):
        self.db_path = db_path
        self.enabled = enabled
        self._init_db()
    
    def _init_db(self):
        """Initialize the database"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    event_type TEXT,
                    source TEXT,
                    payload TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Database exporter init error: {e}")
    
    def export(self, event: Dict[str, Any]):
        """Export event to database"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (timestamp, event_type, source, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event.get("timestamp", datetime.now().isoformat()),
                event.get("event_type", "unknown"),
                event.get("source", "unknown"),
                json.dumps(event.get("payload", {})),
                datetime.now().isoformat(),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Database exporter error: {e}")


class CombinedExporter:
    """Export events to multiple destinations"""
    
    def __init__(self, exporters: List):
        self.exporters = exporters
    
    def export(self, event: Dict[str, Any]):
        """Export event to all configured exporters"""
        for exporter in self.exporters:
            try:
                exporter.export(event)
            except Exception as e:
                print(f"⚠️ Exporter error: {e}")


def get_exporters(settings):
    """
    Get configured exporters based on settings
    """
    exporters = []
    
    # Console exporter (always enabled)
    exporters.append(ConsoleExporter())
    
    # File exporter if configured
    if hasattr(settings, 'LOG_FILE') and settings.LOG_FILE:
        exporters.append(FileExporter(settings.LOG_FILE))
    
    # Database exporter
    if hasattr(settings, 'DB_PATH') and settings.DB_PATH:
        exporters.append(DatabaseExporter(settings.DB_PATH))
    
    return exporters