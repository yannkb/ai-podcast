import requests
import os
from datetime import datetime

def download_pdf(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {filename}: Status code {response.status_code}")

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime('%Y%m%d')

# Define the parent directory path
parent_directory = 'papers'

# Create the full path for the nested folder
nested_folder = os.path.join(parent_directory, current_date)

# Create the directories (both parent and nested if they don't exist)
os.makedirs(nested_folder, exist_ok=True)

print(f"Nested folder created at: {nested_folder}")

# Make the initial API call
url = "https://huggingface.co/api/daily_papers"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # Assuming the response is a list of items
    for item in data:
        # Extract the parameter needed for the PDF URL
        paper_id = item['paper']['id']
        
        if paper_id:
            # Construct the PDF URL
            pdf_url = f"https://arxiv.org/pdf/{paper_id}"
            
            # Generate a filename for the PDF
            filename = f"{nested_folder}/{paper_id}.pdf"
            
            # Download the PDF
            download_pdf(pdf_url, filename)
        else:
            print(f"PDF parameter not found for item: {item}")
else:
    print(f"Error in initial API call: {response.status_code}")