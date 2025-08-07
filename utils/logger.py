"""
Logging utility for the gaming performance monitor.
Provides structured logging with file rotation and different log levels.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str, log_level: str = 'INFO', log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup a logger with console and file handlers.
    
    Args:
        name: Logger name (usually module name)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Set logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "performance_monitor.log"
    
    try:
        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets more detailed logs
        
        # File formatter includes more details
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        # If file logging fails, just use console
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

def setup_performance_logger() -> logging.Logger:
    """Setup specialized logger for performance metrics."""
    logger = logging.getLogger('performance_metrics')
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    try:
        # Performance metrics log file
        perf_file = logs_dir / "performance_metrics.log"
        
        # Daily rotating file handler for performance metrics
        file_handler = logging.handlers.TimedRotatingFileHandler(
            perf_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days of performance logs
            encoding='utf-8'
        )
        
        # Performance metrics use CSV-like format for easier analysis
        perf_formatter = logging.Formatter('%(asctime)s,%(message)s')
        file_handler.setFormatter(perf_formatter)
        logger.addHandler(file_handler)
        
        # Add header to performance log
        logger.info("timestamp,metric_type,metric_name,value,unit,status")
        
    except Exception as e:
        print(f"Could not setup performance logging: {e}")
    
    return logger

def log_performance_metric(metric_type: str, metric_name: str, value: float, 
                         unit: str = "", status: str = "normal"):
    """
    Log a performance metric in structured format.
    
    Args:
        metric_type: Type of metric (system, game, network)
        metric_name: Name of the metric (cpu_usage, fps, ping)
        value: Metric value
        unit: Unit of measurement (%, ms, fps)
        status: Status (normal, warning, critical)
    """
    perf_logger = logging.getLogger('performance_metrics')
    perf_logger.info(f"{metric_type},{metric_name},{value},{unit},{status}")

def log_optimization_event(optimization_type: str, action: str, success: bool, 
                         details: str = ""):
    """
    Log optimization events.
    
    Args:
        optimization_type: Type of optimization (windows, hardware, network)
        action: Action taken (apply, rollback, test)
        success: Whether the action was successful
        details: Additional details about the optimization
    """
    opt_logger = logging.getLogger('optimization_events')
    
    if not opt_logger.handlers:
        # Setup optimization event logger
        opt_logger.setLevel(logging.INFO)
        
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        try:
            opt_file = logs_dir / "optimization_events.log"
            
            file_handler = logging.handlers.RotatingFileHandler(
                opt_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            
            opt_formatter = logging.Formatter(
                '%(asctime)s,%(message)s'
            )
            file_handler.setFormatter(opt_formatter)
            opt_logger.addHandler(file_handler)
            
            # Add header
            opt_logger.info("timestamp,optimization_type,action,success,details")
            
        except Exception as e:
            print(f"Could not setup optimization event logging: {e}")
    
    status = "SUCCESS" if success else "FAILED"
    opt_logger.info(f"{optimization_type},{action},{status},{details}")

def log_system_event(event_type: str, description: str, severity: str = "info"):
    """
    Log system events with appropriate severity.
    
    Args:
        event_type: Type of event (startup, shutdown, error, game_detected)
        description: Event description
        severity: Event severity (debug, info, warning, error, critical)
    """
    system_logger = logging.getLogger('system_events')
    
    if not system_logger.handlers:
        # Setup system event logger
        system_logger.setLevel(logging.INFO)
        
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        try:
            sys_file = logs_dir / "system_events.log"
            
            file_handler = logging.handlers.RotatingFileHandler(
                sys_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5,
                encoding='utf-8'
            )
            
            sys_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(sys_formatter)
            system_logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Could not setup system event logging: {e}")
    
    # Log with appropriate severity
    log_method = getattr(system_logger, severity.lower(), system_logger.info)
    log_method(f"{event_type}: {description}")

class PerformanceTimer:
    """Context manager for timing performance operations."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger('performance_timer')
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"{self.operation_name} completed in {duration:.3f} seconds")
            log_performance_metric("timing", self.operation_name, duration, "seconds")
        else:
            self.logger.error(f"{self.operation_name} failed after {duration:.3f} seconds: {exc_val}")
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the timed operation."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

def create_debug_dump(error_info: dict, dump_dir: str = "debug_dumps"):
    """
    Create a debug dump file with error information and system state.
    
    Args:
        error_info: Dictionary containing error information
        dump_dir: Directory to store debug dumps
    """
    try:
        dump_path = Path(dump_dir)
        dump_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_file = dump_path / f"debug_dump_{timestamp}.log"
        
        with open(dump_file, 'w', encoding='utf-8') as f:
            f.write(f"Debug Dump Created: {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            # Error information
            f.write("ERROR INFORMATION:\n")
            f.write("-" * 20 + "\n")
            for key, value in error_info.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # System information
            f.write("SYSTEM INFORMATION:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"Working Directory: {os.getcwd()}\n")
            f.write(f"Python Path: {sys.path}\n")
            
            # Environment variables
            f.write("\nENVIRONMENT VARIABLES:\n")
            f.write("-" * 20 + "\n")
            for key, value in os.environ.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'key', 'token', 'secret']):
                    f.write(f"{key}: [REDACTED]\n")
                else:
                    f.write(f"{key}: {value}\n")
        
        print(f"Debug dump created: {dump_file}")
        return str(dump_file)
        
    except Exception as e:
        print(f"Failed to create debug dump: {e}")
        return None

def setup_exception_logging():
    """Setup global exception logging."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        logger = logging.getLogger('uncaught_exceptions')
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Create debug dump
        error_info = {
            'exception_type': str(exc_type.__name__),
            'exception_message': str(exc_value),
            'exception_traceback': str(exc_traceback)
        }
        create_debug_dump(error_info)
    
    # Set the global exception handler
    sys.excepthook = handle_exception

def get_log_summary(log_file: str, lines: int = 100) -> list:
    """
    Get a summary of recent log entries.
    
    Args:
        log_file: Path to log file
        lines: Number of recent lines to return
    
    Returns:
        List of recent log lines
    """
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return []
        
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
            
    except Exception as e:
        print(f"Error reading log file {log_file}: {e}")
        return []

def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 30):
    """
    Clean up old log files to save disk space.
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days of logs to keep
    """
    try:
        log_path = Path(log_dir)
        if not log_path.exists():
            return
        
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for log_file in log_path.glob("*.log*"):
            try:
                # Get file modification time
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    
            except Exception as e:
                print(f"Error deleting log file {log_file}: {e}")
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old log files")
            
    except Exception as e:
        print(f"Error during log cleanup: {e}")

# Initialize global exception logging
setup_exception_logging()