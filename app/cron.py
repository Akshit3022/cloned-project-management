
import logging

def job():
    try:
        # Your cron job logic here
        logging.info('Cron job executed successfully')
    except Exception as e:
        logging.error(f'An error occurred in cron job: {e}')