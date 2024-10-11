import backoff
import glob
import google.generativeai as genai
import json
import logging
import os
import random
import time

from datetime import datetime
from google.api_core import exceptions as google_exceptions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize the model
model = genai.GenerativeModel(
    model_name=config['model_name'],
    system_instruction=config['system_instruction']
)

# Backoff decorator for handling API errors
@backoff.on_exception(backoff.expo, 
                      exception=(google_exceptions.GoogleAPIError, 
                                 google_exceptions.RetryError),
                      max_tries=5)
def generate_content_with_backoff(prompt):
    return model.generate_content(prompt)

def process_paper(paper_path, output_dir):
    """Process a single paper and generate content."""
    paper_id = os.path.basename(paper_path).replace('.pdf', '')
    prompt = f"Present the paper with ID {paper_id}. Focus on the main points and keep it concise, aiming for about 150-200 words. Do not welcome the listeners. Directly introduce the topic of the paper. The introduction must feel like a transition between each paper presented. Do not format the text."
    
    try:
        response = generate_content_with_backoff(prompt)
        content = response.text
        
        # Save individual paper content
        output_file = os.path.join(output_dir, f"{paper_id}_content.txt")
        with open(output_file, 'w') as f:
            f.write(content)
        
        logging.info(f"Generated content for paper {paper_id}")
        return paper_id, content
    except google_exceptions.GoogleAPIError as e:
        logging.error(f"API error processing paper {paper_id}: {str(e)}")
        return paper_id, None
    except Exception as e:
        logging.error(f"Unexpected error processing paper {paper_id}: {str(e)}")
        return paper_id, None

def generate_podcast_script(papers_content):
    """Generate a full podcast script from individual paper contents."""
    script = f"Welcome to today's {config['podcast_title']}! Let's dive into the latest publications.\n\n"
    
    for paper_id, content in papers_content:
        if content:
            script += content
    
    script += f"That concludes our {config['podcast_title']} for today. Thank you for listening!"
    return script

def main():
    current_date = datetime.now().strftime("%Y%m%d")
    papers_folder = f"papers/{current_date}"
    papers = glob.glob(os.path.join(papers_folder, "*.pdf"))
    
    if not papers:
        logging.warning(f"No papers found for date: {current_date}")
        return
    
    # Create nested output directory
    output_dir = os.path.join("scripts", current_date)
    os.makedirs(output_dir, exist_ok=True)
    
    start_time = time.time()
    papers_content = []
    
    # Process papers with rate limiting
    for paper in papers:
        paper_id, content = process_paper(paper, output_dir)
        if content:
            papers_content.append((paper_id, content))
        time.sleep(random.uniform(1, 3))  # Random delay between requests
    
    # Generate full podcast script
    full_script = generate_podcast_script(papers_content)
    
    # Save full podcast script
    script_file = os.path.join(output_dir, f"podcast_script_{current_date}.txt")
    with open(script_file, 'w') as f:
        f.write(full_script)
    
    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"Podcast script generation completed in {duration:.2f} seconds")
    logging.info(f"Processed {len(papers_content)} out of {len(papers)} papers successfully")
    logging.info(f"Output files saved in: {output_dir}")

if __name__ == "__main__":
    main()