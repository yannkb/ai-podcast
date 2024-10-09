import google.generativeai as genai
import os
import glob
from datetime import datetime
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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

def process_paper(paper_path, output_dir):
    """Process a single paper and generate content."""
    paper_id = os.path.basename(paper_path).replace('.pdf', '')
    prompt = f"Present the paper with ID {paper_id} for today's podcast episode. Remember to cover all the requested sections in detail."
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # Save individual paper content
        output_file = os.path.join(output_dir, f"{paper_id}_content.md")
        with open(output_file, 'w') as f:
            f.write(content)
        
        logging.info(f"Generated content for paper {paper_id}")
        return paper_id, content
    except Exception as e:
        logging.error(f"Error processing paper {paper_id}: {str(e)}")
        return paper_id, None

def generate_podcast_script(papers_content):
    """Generate a full podcast script from individual paper contents."""
    script = "Welcome to today's AI Research Paper Podcast! Let's dive into the latest publications.\n\n"
    
    for paper_id, content in papers_content:
        if content:
            script += f"--- Paper ID: {paper_id} ---\n\n"
            script += content
            script += "\n\n--- End of paper presentation ---\n\n"
    
    script += "That concludes our AI Research Paper Podcast for today. Thank you for listening!"
    return script

def main():
    current_date = datetime.now().strftime("%Y%m%d")
    papers_folder = f"papers/{current_date}"
    papers = glob.glob(os.path.join(papers_folder, "*.pdf"))
    
    if not papers:
        logging.warning(f"No papers found for date: {current_date}")
        return
    
    # Create nested output directory
    output_dir = os.path.join("output", current_date)
    os.makedirs(output_dir, exist_ok=True)
    
    start_time = time.time()
    papers_content = []
    
    # Process papers concurrently
    with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        future_to_paper = {executor.submit(process_paper, paper, output_dir): paper for paper in papers}
        for future in as_completed(future_to_paper):
            paper_id, content = future.result()
            if content:
                papers_content.append((paper_id, content))
    
    # Generate full podcast script
    full_script = generate_podcast_script(papers_content)
    
    # Save full podcast script
    script_file = os.path.join(output_dir, f"podcast_script_{current_date}.md")
    with open(script_file, 'w') as f:
        f.write(full_script)
    
    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"Podcast script generation completed in {duration:.2f} seconds")
    logging.info(f"Processed {len(papers_content)} out of {len(papers)} papers successfully")
    logging.info(f"Output files saved in: {output_dir}")

if __name__ == "__main__":
    main()