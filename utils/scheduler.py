import time
import schedule
import logging
import sys
import os

# Add the project root to the python path so it can properly import the agents module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner import PlannerAgent
from agents.memory import MemoryAgent
from utils.emailer import send_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_news_pipeline():
    """
    The scheduled job that executes the end-to-end news workflow via the PlannerAgent
    and automatically emails the results.
    """
    logger.info("Scheduler Triggered: Starting autonomous news workflow...")
    try:
        memory = MemoryAgent()
        prefs = memory.load_user_preferences()
        email_addr = prefs.get("email", "")
        
        planner = PlannerAgent()
        report = planner.execute_news_workflow()
        
        if report["status"] in ["success", "partial_success"]:
            logger.info("Workflow completed successfully.")
            
            # Save to memory
            summary_text = report.get("summary", "")
            memory.save_summary(summary_text, report.get("insights", ""))
            
            # Forward to email if set
            if email_addr:
                logger.info(f"Automated config found. Sending email to {email_addr}...")
                send_email(summary_text, email_addr)
                
        else:
            logger.error(f"Scheduled workflow failed: {report.get('error_message')}")
            
    except Exception as e:
        logger.error(f"Critical error during scheduled job execution: {e}")

def get_job_frequency() -> int:
    try:
        memory = MemoryAgent()
        prefs = memory.load_user_preferences()
        return prefs.get("frequency", 24)
    except:
        return 24

current_freq = 0

def update_schedule_if_needed():
    global current_freq
    freq = get_job_frequency()
    
    # Reload schedule only if user changed the frequency or on first boot
    if freq != current_freq:
        logger.info(f"Updating schedule frequency to run every {freq} hours.")
        schedule.clear()
        
        # Mapping to the exact criteria
        if freq == 2:
            schedule.every(2).hours.do(run_news_pipeline)
        elif freq == 12:
            schedule.every(12).hours.do(run_news_pipeline)
        else:
            schedule.every(24).hours.do(run_news_pipeline)
            
        current_freq = freq

def main():
    """
    Initializes the schedule configuration and runs the continuous background loop smoothly.
    Designed to run seamlessly inside a background thread.
    """
    logger.info("Antigravity Autonomous News Scheduler starting up...")
    update_schedule_if_needed()
    logger.info("Waiting in background loop... Automations are actively checking.")
    
    try:
        while True:
            update_schedule_if_needed()
            schedule.run_pending()
            time.sleep(10)  # Check every 10 seconds to not block UI/CPU heavily
    except KeyboardInterrupt:
        logger.info("Scheduler manually stopped. Exiting cleanly.")

if __name__ == "__main__":
    main()
