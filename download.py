import requests
import os
from datetime import datetime
import concurrent.futures
import time
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_session():
    """
    Create a requests Session with retry capabilities.
    This allows for automatic retries on failed requests with exponential backoff.
    """
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def download_pdf(session, url, filename):
    """
    Download a PDF from the given URL and save it to the specified filename.
    
    Args:
    session (requests.Session): The session to use for the request
    url (str): The URL of the PDF to download
    filename (str): The path where the PDF should be saved
    
    Returns:
    bool: True if download was successful, False otherwise
    """
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {filename}: {str(e)}")
        return False

def process_item(item, nested_folder, session):
    """
    Process a single item from the API response.
    Extract the paper ID, construct the PDF URL, and attempt to download the PDF.
    
    Args:
    item (dict): A dictionary containing information about a paper
    nested_folder (str): The path to the folder where PDFs should be saved
    session (requests.Session): The session to use for the download
    
    Returns:
    bool: True if download was successful, False otherwise
    """
    paper_id = item['paper'].get('id')
    if not paper_id:
        logging.warning(f"PDF parameter not found for item: {item}")
        return False

    pdf_url = f"https://arxiv.org/pdf/{paper_id}"
    filename = os.path.join(nested_folder, f"{paper_id}.pdf")
    return download_pdf(session, pdf_url, filename)

def main():
    """
    Main function to orchestrate the PDF download process.
    """
    # Create the directory structure for storing PDFs
    current_date = datetime.now().strftime('%Y%m%d')
    parent_directory = 'papers'
    nested_folder = os.path.join(parent_directory, current_date)
    os.makedirs(nested_folder, exist_ok=True)
    logging.info(f"Nested folder created at: {nested_folder}")

    # Create a session for making HTTP requests
    session = create_session()
    url = "https://huggingface.co/api/daily_papers"
    
    # Fetch the list of papers from the API
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in initial API call: {str(e)}")
        return

    # Start the download process
    start_time = time.time()
    success_count = 0
    total_count = len(data)

    # Use ThreadPoolExecutor for concurrent downloads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all download tasks to the executor
        future_to_item = {executor.submit(process_item, item, nested_folder, session): item for item in data}
        # Process completed tasks as they finish
        for future in concurrent.futures.as_completed(future_to_item):
            if future.result():
                success_count += 1

    # Calculate and log performance metrics
    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"Download process completed in {duration:.2f} seconds")
    logging.info(f"Successfully downloaded {success_count} out of {total_count} papers")

if __name__ == "__main__":
    main()