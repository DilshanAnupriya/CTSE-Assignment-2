"""
System Logger
=============
Centralised logging configuration for the Travel Planner MAS.
Sets up both file logging (logs/system.log) and console output.
"""
import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/system.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def log(message: str) -> None:
    """
    Write an INFO-level log entry to the system log.

    Args:
        message (str): The log message to record.
    """
    logging.getLogger("MAS").info(message)