"""
Job Monitoring and Download Script

This script provides utility functions for:
1. Monitoring the status of a job submitted via CE API.
2. Downloading the CE output files of a completed job.

Author: Nikolas Cruz Camacho
Email:  cnc6@illinois.edu
"""

import sys
import os
import time
import logging

# Configure logging to output to stdout, with level determined by the LOG_LEVEL environment variable.
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv('LOG_LEVEL', logging.WARNING))

def monitor_job(job_id, api, time_limit=3600, sleep_interval=60):
    """
    Periodically checks the status of a job via the provided API until completion or timeout.

    Parameters:
    -----------
    job_id : str
        Unique identifier of the job to be monitored.
    api : object
        API object with a method `job_list(uuid=...)` to query the job status.
    time_limit : int, optional
        Maximum number of seconds to wait before giving up (default: 3600 seconds).
    sleep_interval : int, optional
        Number of seconds to wait between status checks (default: 60 seconds).

    Returns:
    --------
    dict or None
        The job status dictionary on success or failure, or None if an exception occurred.
    """
    try:
        start_time = time.time()

        while True:
            job_status = api.job_list(uuid=job_id)
            elapsed_time = time.time() - start_time

            if job_status['status'] in ['SUCCESS', 'FAILURE']:
                logging.info(f'Job completed. \nStatus: {job_status["status"]}')
                break
            
            else:
                if elapsed_time > time_limit:
                    logging.error(f"Job {job_id} exceeded the time limit of {time_limit} seconds.")
                    break
                else:
                    time.sleep(sleep_interval)
            
        return job_status
    except Exception as e:
        logging.error(f'An error occurred during job monitoring for job {job_id}: {e}')
        return None

def download_successful_job(job_id, job_status, api, output_dir='./downloads/'):
    """
    Downloads all files associated with a successful job using the provided API.

    Parameters:
    -----------
    job_id : str
        Unique identifier of the job whose files are to be downloaded.
    job_status : dict
        Dictionary containing job status information, including 'status' and 'files'.
    api : object
        API object with a method `download_job_file(job_id, file_path, root_dir)` to fetch files.
    output_dir : str, optional
        Directory path to store downloaded files (default: './downloads/').

    Returns:
    --------
    None
    """
    if job_status['status'] == 'SUCCESS':
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f'Downloading files into {os.path.join(output_dir, job_id)}')

        # Iterate through all files associated with the job and download each
        for file_info in job_status['files']:
            print(f'  "{file_info["path"]}"...')
            if file_info['size'] > 0:
                api.download_job_file(job_id, file_info['path'], root_dir=output_dir)

    elif job_status['status'] == 'FAILURE':
        print(f'Job failed. Error: "{job_status["error_info"]}"')

    else:
        print(f'Job ended with unexpected status: {job_status["status"]}')
        print(f'Error info: {job_status.get("error_info", "No error info available")}')
