"""
Logging configuration for the GroundCite library.

This module provides centralized logging functionality for the GroundCite library,
including structured logging with custom dimensions, file-based logging, and
integration with the dependency injection system.
"""

import os
import logging
from ..core.di.core_di import coredi_injectable
from .settings import AppSettings


@coredi_injectable()
class AppLogger:
    """
    Centralized logger for the GroundCite library.
    
    This class provides a structured logging interface for the entire GroundCite library,
    with support for custom dimensions, different log levels, and file-based output.
    The logger is automatically configured with proper formatting and handlers.
    
    Attributes:
        logger (logging.Logger): The underlying Python logger instance
    """

    def __init__(self, settings: AppSettings):
        """
        Initialize AppLogger with application settings.
        
        Sets up the logger with file handler, formatter, and appropriate log level.
        Creates the logs directory if it doesn't exist and configures structured
        logging with custom dimensions support.
        
        Args:
            settings (AppSettings): Application settings containing base directory path
        """
        # Create the main logger instance
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers by checking if handlers already exist
        if not self.logger.handlers:
                # Set up logs directory path
                LOGS_DIR = os.path.join(settings.BASE_DIR, "logs")
                # Create logs directory if it doesn't exist
                os.makedirs(LOGS_DIR, exist_ok=True)
                
                # Configure file handler for persistent logging
                log_file = os.path.join(LOGS_DIR, "app.log")
                file_handler = logging.FileHandler(log_file)
                
                # Set up structured logging format with timestamp, level, message, and custom dimensions
                formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s %(custom_dimensions)s')
                file_handler.setFormatter(formatter)
                
                # Add the configured handler to the logger
                self.logger.addHandler(file_handler)
        

    def log_debug(self, message: str, custom_dimensions: dict = None):
        """
        Log a debug message with optional custom dimensions.
        
        Debug messages are used for detailed diagnostic information that is typically
        only of interest when diagnosing problems or development debugging.
        
        Args:
            message (str): The debug message to log
            custom_dimensions (dict, optional): Additional context data to include in the log
        """
        self.logger.debug(message, extra={"custom_dimensions": custom_dimensions or {}})

    def log_info(self, message: str, custom_dimensions: dict = None):
        """
        Log an informational message with optional custom dimensions.
        
        Info messages are used for general information about the application's
        operation and major workflow steps.
        
        Args:
            message (str): The informational message to log
            custom_dimensions (dict, optional): Additional context data to include in the log
        """
        self.logger.info(message, extra={"custom_dimensions": custom_dimensions or {}})

    def log_warning(self, message: str, custom_dimensions: dict = None):
        """
        Log a warning message with optional custom dimensions.
        
        Warning messages indicate potential issues that don't prevent the application
        from continuing but may cause problems or unexpected behavior.
        
        Args:
            message (str): The warning message to log
            custom_dimensions (dict, optional): Additional context data to include in the log
        """
        self.logger.warning(message, extra={"custom_dimensions": custom_dimensions or {}})

    def log_error(self, message: str, exception: Exception = None, custom_dimensions: dict = None):
        """
        Log an error message with optional exception details and custom dimensions.
        
        Error messages indicate serious problems that prevented the application from
        performing a specific operation or function.
        
        Args:
            message (str): The error message to log
            exception (Exception, optional): The exception object to include for detailed traceback
            custom_dimensions (dict, optional): Additional context data to include in the log
        """
        self.logger.error(message, exc_info=exception, extra={"custom_dimensions": custom_dimensions or {}})
