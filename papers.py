import google.generativeai as genai
import os
import glob
from datetime import datetime

current_date = datetime.now().strftime("%Y%m%d")
folder_path = f"papers/{current_date}"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction="You are the single host of a podcast that aims to talk about AI research papers published daily on the website huggingface.co. You're gonna be presenting a certain amount of papers during one episode.")
papers = glob.glob(os.path.join(folder_path, "*.pdf"))
separator = ', '
papersList = separator.join(papers)
response = model.generate_content(["These are the papers that you are gonna present in today's episode", papersList])
print(response.text)