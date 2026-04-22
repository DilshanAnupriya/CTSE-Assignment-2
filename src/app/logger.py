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


def get_logger(name: str) -> logging.Logger:
    """
    Create or retrieve a named logger for a specific module/agent.

    Args:
        name (str): Name of the logger (e.g., ResearchAgent, HotelAgent)

    Returns:
        logging.Logger
    """
    return logging.getLogger(name)


def log(message: str) -> None:
    """
    Generic system-level log.
    """
    logging.getLogger("MAS").info(message)