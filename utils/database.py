"""
Database management for the gaming performance monitor.
Handles SQLite database operations for storing performance metrics and optimization history.
"""

import sqlite3
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import threading

class DatabaseManager:
    """Manages SQLite database for performance monitoring data."""
    
    def __init__(self, db_path: str = "performance_data.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.lock = threading.Lock()
        
        # Initialize database
        self.initialize_database()
        
        self.logger.info(f"DatabaseManager initialized with database: {self.db_path}")
    
    def initialize_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            self.create_tables()
            
            # Enable WAL mode for better concurrency
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary database tables."""
        try:
            cursor = self.connection.cursor()
            
            # System metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    cpu_usage REAL,
                    gpu_usage REAL,
                    memory_usage REAL,
                    cpu_temperature REAL,
                    gpu_temperature REAL,
                    cpu_frequency REAL,
                    gpu_frequency REAL,
                    memory_available INTEGER,
                    disk_usage REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Game performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    game_name TEXT,
                    fps REAL,
                    frame_time REAL,
                    frame_time_variance REAL,
                    one_percent_low_fps REAL,
                    zero_one_percent_low_fps REAL,
                    input_latency REAL,
                    game_cpu_usage REAL,
                    game_memory_usage INTEGER,
                    stutter_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Network metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    ping_avg REAL,
                    ping_min REAL,
                    ping_max REAL,
                    ping_jitter REAL,
                    packet_loss REAL,
                    download_speed REAL,
                    upload_speed REAL,
                    network_health_score REAL,
                    connection_errors INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Optimization events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    optimization_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    details TEXT,
                    metrics_before TEXT,  -- JSON
                    metrics_after TEXT,   -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Performance issues table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    issue_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    affected_metrics TEXT,  -- JSON
                    resolution_status TEXT DEFAULT 'open',
                    resolved_at REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT,
                    config_type TEXT DEFAULT 'string',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Gaming sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gaming_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    duration INTEGER,
                    avg_fps REAL,
                    min_fps REAL,
                    max_fps REAL,
                    avg_cpu_usage REAL,
                    avg_gpu_usage REAL,
                    avg_memory_usage REAL,
                    avg_ping REAL,
                    issues_encountered TEXT,  -- JSON
                    optimizations_applied TEXT,  -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            self.create_indexes(cursor)
            
            self.connection.commit()
            self.logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            self.logger.error(f"Table creation failed: {e}")
            raise
    
    def create_indexes(self, cursor):
        """Create database indexes for better query performance."""
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_game_metrics_timestamp ON game_metrics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_game_metrics_game_name ON game_metrics(game_name)",
                "CREATE INDEX IF NOT EXISTS idx_network_metrics_timestamp ON network_metrics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_optimization_events_timestamp ON optimization_events(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_optimization_events_type ON optimization_events(optimization_type)",
                "CREATE INDEX IF NOT EXISTS idx_performance_issues_timestamp ON performance_issues(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_performance_issues_type ON performance_issues(issue_type)",
                "CREATE INDEX IF NOT EXISTS idx_gaming_sessions_game_name ON gaming_sessions(game_name)",
                "CREATE INDEX IF NOT EXISTS idx_gaming_sessions_start_time ON gaming_sessions(start_time)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
        except Exception as e:
            self.logger.error(f"Index creation failed: {e}")
    
    def store_system_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Store system performance metrics."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT INTO system_metrics (
                        timestamp, cpu_usage, gpu_usage, memory_usage,
                        cpu_temperature, gpu_temperature, cpu_frequency, gpu_frequency,
                        memory_available, disk_usage
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    metrics.get('cpu_usage_total', 0),
                    metrics.get('gpu_usage', 0),
                    metrics.get('memory_percent', 0),
                    metrics.get('cpu_temperature', 0) or metrics.get('temp_cpu_package', 0),
                    metrics.get('gpu_temperature', 0),
                    metrics.get('cpu_frequency_current', 0),
                    metrics.get('gpu_clock_graphics', 0),
                    metrics.get('memory_available', 0),
                    metrics.get('disk_percent', 0)
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store system metrics: {e}")
            return False
    
    def store_game_metrics(self, metrics: Dict[str, Any], game_name: str = None) -> bool:
        """Store game performance metrics."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT INTO game_metrics (
                        timestamp, game_name, fps, frame_time, frame_time_variance,
                        one_percent_low_fps, zero_one_percent_low_fps, input_latency,
                        game_cpu_usage, game_memory_usage, stutter_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    game_name or metrics.get('game_name', 'Unknown'),
                    metrics.get('fps', 0) or metrics.get('avg_fps_calculated', 0),
                    metrics.get('frame_time', 0),
                    metrics.get('frame_time_variance', 0),
                    metrics.get('1_percent_low_fps', 0),
                    metrics.get('0_1_percent_low_fps', 0),
                    metrics.get('estimated_input_latency', 0),
                    metrics.get('game_cpu_usage', 0),
                    metrics.get('game_memory_rss', 0),
                    metrics.get('stutter_count', 0)
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store game metrics: {e}")
            return False
    
    def store_network_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Store network performance metrics."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT INTO network_metrics (
                        timestamp, ping_avg, ping_min, ping_max, ping_jitter,
                        packet_loss, download_speed, upload_speed, network_health_score,
                        connection_errors
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    metrics.get('ping_avg', 0),
                    metrics.get('ping_min', 0),
                    metrics.get('ping_max', 0),
                    metrics.get('ping_jitter', 0),
                    metrics.get('packet_loss_estimated', 0),
                    metrics.get('download_speed_mbps', 0),
                    metrics.get('upload_speed_mbps', 0),
                    metrics.get('network_health_score', 100),
                    metrics.get('total_network_errors', 0)
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store network metrics: {e}")
            return False
    
    def log_optimization_event(self, issues: List[str], timestamp: float, 
                             optimization_type: str = "auto", 
                             success: bool = True) -> bool:
        """Log an optimization event."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT INTO optimization_events (
                        timestamp, optimization_type, action, success, details
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    optimization_type,
                    "auto_optimization",
                    success,
                    json.dumps(issues)
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to log optimization event: {e}")
            return False
    
    def log_performance_issue(self, issue_type: str, severity: str, 
                            description: str, affected_metrics: Dict[str, Any]) -> bool:
        """Log a performance issue."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT INTO performance_issues (
                        timestamp, issue_type, severity, description, affected_metrics
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    issue_type,
                    severity,
                    description,
                    json.dumps(affected_metrics)
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to log performance issue: {e}")
            return False
    
    def start_gaming_session(self, game_name: str) -> int:
        """Start a new gaming session."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT INTO gaming_sessions (game_name, start_time)
                    VALUES (?, ?)
                """, (game_name, time.time()))
                
                session_id = cursor.lastrowid
                self.connection.commit()
                
                self.logger.info(f"Started gaming session for {game_name} (ID: {session_id})")
                return session_id
                
        except Exception as e:
            self.logger.error(f"Failed to start gaming session: {e}")
            return -1
    
    def end_gaming_session(self, session_id: int, session_stats: Dict[str, Any]) -> bool:
        """End a gaming session with statistics."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                end_time = time.time()
                
                # Get session start time
                cursor.execute("SELECT start_time FROM gaming_sessions WHERE id = ?", (session_id,))
                row = cursor.fetchone()
                
                if not row:
                    self.logger.warning(f"Gaming session {session_id} not found")
                    return False
                
                start_time = row['start_time']
                duration = int(end_time - start_time)
                
                cursor.execute("""
                    UPDATE gaming_sessions SET
                        end_time = ?, duration = ?, avg_fps = ?, min_fps = ?, max_fps = ?,
                        avg_cpu_usage = ?, avg_gpu_usage = ?, avg_memory_usage = ?,
                        avg_ping = ?, issues_encountered = ?, optimizations_applied = ?
                    WHERE id = ?
                """, (
                    end_time,
                    duration,
                    session_stats.get('avg_fps', 0),
                    session_stats.get('min_fps', 0),
                    session_stats.get('max_fps', 0),
                    session_stats.get('avg_cpu_usage', 0),
                    session_stats.get('avg_gpu_usage', 0),
                    session_stats.get('avg_memory_usage', 0),
                    session_stats.get('avg_ping', 0),
                    json.dumps(session_stats.get('issues', [])),
                    json.dumps(session_stats.get('optimizations', [])),
                    session_id
                ))
                
                self.connection.commit()
                
                self.logger.info(f"Ended gaming session {session_id} (duration: {duration}s)")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to end gaming session: {e}")
            return False
    
    def get_recent_metrics(self, metric_type: str, hours: int = 1) -> List[Dict]:
        """Get recent metrics of specified type."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cutoff_time = time.time() - (hours * 3600)
                
                table_map = {
                    'system': 'system_metrics',
                    'game': 'game_metrics',
                    'network': 'network_metrics'
                }
                
                table = table_map.get(metric_type)
                if not table:
                    return []
                
                cursor.execute(f"""
                    SELECT * FROM {table}
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get recent {metric_type} metrics: {e}")
            return []
    
    def get_performance_summary(self, game_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for specified period."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cutoff_time = time.time() - (days * 24 * 3600)
                summary = {}
                
                # System metrics summary
                cursor.execute("""
                    SELECT 
                        AVG(cpu_usage) as avg_cpu,
                        MAX(cpu_usage) as max_cpu,
                        AVG(gpu_usage) as avg_gpu,
                        MAX(gpu_usage) as max_gpu,
                        AVG(memory_usage) as avg_memory,
                        MAX(cpu_temperature) as max_cpu_temp,
                        MAX(gpu_temperature) as max_gpu_temp,
                        COUNT(*) as sample_count
                    FROM system_metrics
                    WHERE timestamp >= ?
                """, (cutoff_time,))
                
                row = cursor.fetchone()
                if row:
                    summary['system'] = dict(row)
                
                # Game metrics summary
                game_filter = ""
                params = [cutoff_time]
                if game_name:
                    game_filter = "AND game_name = ?"
                    params.append(game_name)
                
                cursor.execute(f"""
                    SELECT 
                        AVG(fps) as avg_fps,
                        MIN(fps) as min_fps,
                        MAX(fps) as max_fps,
                        AVG(frame_time) as avg_frame_time,
                        AVG(frame_time_variance) as avg_variance,
                        AVG(input_latency) as avg_latency,
                        COUNT(*) as sample_count
                    FROM game_metrics
                    WHERE timestamp >= ? {game_filter}
                """, params)
                
                row = cursor.fetchone()
                if row:
                    summary['game'] = dict(row)
                
                # Network metrics summary
                cursor.execute("""
                    SELECT 
                        AVG(ping_avg) as avg_ping,
                        MIN(ping_avg) as min_ping,
                        MAX(ping_avg) as max_ping,
                        AVG(ping_jitter) as avg_jitter,
                        AVG(packet_loss) as avg_packet_loss,
                        AVG(network_health_score) as avg_health,
                        COUNT(*) as sample_count
                    FROM network_metrics
                    WHERE timestamp >= ?
                """, (cutoff_time,))
                
                row = cursor.fetchone()
                if row:
                    summary['network'] = dict(row)
                
                # Gaming sessions
                cursor.execute(f"""
                    SELECT COUNT(*) as session_count, AVG(duration) as avg_duration
                    FROM gaming_sessions
                    WHERE start_time >= ? {game_filter and "AND game_name = ?" or ""}
                """, params)
                
                row = cursor.fetchone()
                if row:
                    summary['sessions'] = dict(row)
                
                return summary
                
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    def get_optimization_history(self, days: int = 7) -> List[Dict]:
        """Get optimization history."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cutoff_time = time.time() - (days * 24 * 3600)
                
                cursor.execute("""
                    SELECT * FROM optimization_events
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get optimization history: {e}")
            return []
    
    def get_top_games(self, limit: int = 10) -> List[Dict]:
        """Get top games by play time."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    SELECT 
                        game_name,
                        COUNT(*) as session_count,
                        SUM(duration) as total_duration,
                        AVG(avg_fps) as avg_fps,
                        AVG(avg_cpu_usage) as avg_cpu,
                        AVG(avg_gpu_usage) as avg_gpu
                    FROM gaming_sessions
                    WHERE end_time IS NOT NULL
                    GROUP BY game_name
                    ORDER BY total_duration DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get top games: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old data to save space."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cutoff_time = time.time() - (days_to_keep * 24 * 3600)
                
                # Tables to clean up
                tables = [
                    'system_metrics',
                    'game_metrics', 
                    'network_metrics',
                    'optimization_events',
                    'performance_issues'
                ]
                
                total_deleted = 0
                
                for table in tables:
                    cursor.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff_time,))
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    self.logger.debug(f"Deleted {deleted} old records from {table}")
                
                # Keep gaming sessions for longer (90 days)
                session_cutoff = time.time() - (90 * 24 * 3600)
                cursor.execute("DELETE FROM gaming_sessions WHERE start_time < ?", (session_cutoff,))
                session_deleted = cursor.rowcount
                total_deleted += session_deleted
                
                self.connection.commit()
                
                if total_deleted > 0:
                    self.logger.info(f"Cleaned up {total_deleted} old records from database")
                
                # Vacuum database to reclaim space
                cursor.execute("VACUUM")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                stats = {}
                
                # Table row counts
                tables = [
                    'system_metrics', 'game_metrics', 'network_metrics',
                    'optimization_events', 'performance_issues', 'gaming_sessions'
                ]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    row = cursor.fetchone()
                    stats[f'{table}_count'] = row['count'] if row else 0
                
                # Database size
                stats['database_size'] = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                # Date range
                cursor.execute("SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time FROM system_metrics")
                row = cursor.fetchone()
                if row and row['min_time']:
                    stats['data_start'] = datetime.fromtimestamp(row['min_time']).isoformat()
                    stats['data_end'] = datetime.fromtimestamp(row['max_time']).isoformat()
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Create a backup of the database."""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"performance_data_backup_{timestamp}.db"
            
            with self.lock:
                # Create backup using SQLite backup API
                backup_conn = sqlite3.connect(backup_path)
                self.connection.backup(backup_conn)
                backup_conn.close()
                
                self.logger.info(f"Database backed up to {backup_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.logger.info("Database connection closed")
                
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.close()
        except:
            pass