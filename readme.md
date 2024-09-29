Dependencies
openai: GPT model for text generation.
opencv-python: For image handling and capture simulation.
geopy: To fetch location details (simulated in this project).
faiss-cpu: For storing vectorized data and memory retrieval.
numpy: For handling vector calculations and arrays.
Setup Instructions
Clone the repository and navigate to the project directory:
bash
Copy code
git clone https://github.com/your-repo/memory-creator.git
cd memory-creator
Install the dependencies:
bash
Copy code
pip install -r requirements.txt
Set your OpenAI API key:
python
Copy code
openai.api_key = 'your_openai_api_key'
Run the project to start capturing and storing memories:
bash
Copy code
python memory_creator.py
How it Works
The script captures a photo every 15 minutes (you can modify the interval).
It generates a text summary of the photo using OpenAI's GPT model.
The image is compressed to save space (resize to 800x600 and reduce quality to 70%).
Metadata (timestamp, location) is stored alongside the summary in a FAISS database.
You can search for specific memories by timestamp, and the system will return the closest matching memory.
Memory Search Example
To retrieve a memory, search by a timestamp:

python
Copy code
memory_summary, memory_time, memory_location = search_memory_by_time("2024-09-29 10:00:00")
print(f"Memory Summary: {memory_summary}\nTime: {memory_time}\nLocation: {memory_location}")
File Structure
bash
Copy code
memory-creator/
│
├── captured_images/        # Directory where images are stored
├── requirements.txt        # List of dependencies
├── README.md               # Project documentation
└── memory_creator.py       # Main Python script for capturing and storing memories
Future Enhancements
Smart Glasses Integration: Replace the simulated OpenCV image capture with real smart glasses API.
Security Enhancements: Add encryption and authentication to secure memory access.
Memory Summaries: Improve GPT-based summarization and metadata collection (e.g., activity detection from images).
License
This project is licensed under the MIT License - see the LICENSE file for details.