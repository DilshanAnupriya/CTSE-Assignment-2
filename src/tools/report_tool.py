"""
Report Tool
===========
Custom tool for the Report Agent in the Sri Lanka Travel Planner MAS.
Provides functionality to save the final generated travel report to a file.

Author: Hirun Athukorala (Report Agent Module)
"""

import os
import logging

logger = logging.getLogger(__name__)


def save_report_to_file(content: str, filename: str) -> str:
    """
    Save the final markdown report to a file.
    
    Args:
        content (str): The markdown content of the travel itinerary.
        filename (str): The name of the file to save it to (e.g., 'Kandy_travel_plan.md').
        
    Returns:
        str: Success or error message.
    """
    logger.info("[ReportTool] Saving report to file: %s", filename)
    
    try:
        # Save to the root directory of the project
        # Using an absolute path or relative to current working directory
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        success_msg = f"Report successfully saved to {filepath}"
        logger.info("[ReportTool] %s", success_msg)
        return success_msg
        
    except Exception as e:
        error_msg = f"Failed to save report: {str(e)}"
        logger.error("[ReportTool] %s", error_msg)
        return error_msg
