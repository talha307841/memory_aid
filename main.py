import cv2
import openai
import time
import os
from datetime import datetime
from geopy.geocoders import Nominatim
import faiss
import numpy as np

# Set OpenAI API key
openai.api_key = 'enter API keys'

# Initialize the geolocator for location tracking
geolocator = Nominatim(user_agent="geoapiExercises")

# Initialize FAISS for vectorized search
index = faiss.IndexFlatL2(512)  # Example with 512 dimension vectors

# Directory to store images
IMAGE_DIR = './captured_images'

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Image compression function
def compress_image(image_path, output_path, max_width=800, max_height=600, quality=70):
    """
    Compresses the image by resizing and reducing quality.
    :param image_path: Path to the original image.
    :param output_path: Path where the compressed image will be saved.
    :param max_width: The maximum width of the resized image.
    :param max_height: The maximum height of the resized image.
    :param quality: JPEG quality (0 to 100, where 100 is the best quality).
    :return: Path to the compressed image.
    """
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    scale = min(max_width / width, max_height / height)

    if scale < 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    cv2.imwrite(output_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

    return output_path

# Simulate taking a photo every 15 minutes using a camera (OpenCV or placeholder)
def capture_image(image_id):
    original_image_path = f"{IMAGE_DIR}/memory_{image_id}_original.jpg"
    compressed_image_path = f"{IMAGE_DIR}/memory_{image_id}.jpg"
    
    # Simulate capturing an image
    img = cv2.imread('sample_image.jpg')  # Simulated image capture
    cv2.imwrite(original_image_path, img)  # Save original image

    # Compress the image
    compress_image(original_image_path, compressed_image_path, max_width=800, max_height=600, quality=70)

    return compressed_image_path  # Return the path of the compressed image

# Function to get location
def get_location():
    location = geolocator.geocode("Your Location Name")  # Simulating location
    return location.address if location else "Unknown Location"

# Function to generate a summary using OpenAI GPT
def generate_summary(image_path, location, timestamp):
    with open(image_path, "rb") as image_file:
        prompt = f"This is a picture taken at {location} on {timestamp}. Describe it."
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
    return response.choices[0].text.strip()

# Function to store the memory in FAISS
def store_memory_in_faiss(memory_data, memory_vector):
    index.add(memory_vector)
    memory_db.append(memory_data)  # Store the details alongside the vector

# Simulated vector embedding function (using random data for now)
def vectorize_memory(summary):
    return np.random.random(512).astype('float32')  # Simulated vector

# Memory database (simulated)
memory_db = []

# Main memory capture loop (run for a limited number of iterations)
def capture_and_store_memory():
    for i in range(4):  # Simulate running for an hour (4 x 15 minutes)
        image_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        image_path = capture_image(image_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location = get_location()
        summary = generate_summary(image_path, location, timestamp)
        
        # Vectorize the summary for FAISS storage
        memory_vector = vectorize_memory(summary)
        
        # Store the memory in FAISS
        memory_data = {
            'image_path': image_path,
            'timestamp': timestamp,
            'location': location,
            'summary': summary
        }
        store_memory_in_faiss(memory_data, memory_vector)
        
        # Simulate a 15-minute wait
        time.sleep(15 * 60)  # 15 minutes

# Function to search for memories by approximate timestamp
def search_memory_by_time(target_timestamp):
    target_vector = vectorize_memory(f"Memory at {target_timestamp}")  # Simulating vector
    D, I = index.search(np.array([target_vector]), 1)  # Find closest memory

    if I[0][0] != -1:  # If a result is found
        memory = memory_db[I[0][0]]
        return memory['summary'], memory['timestamp'], memory['location']
    else:
        return "No memory found for the given time."

# Start memory capture
capture_and_store_memory()

# Example search
memory_summary, memory_time, memory_location = search_memory_by_time("2024-09-29 10:00:00")
print(f"Memory Summary: {memory_summary}\nTime: {memory_time}\nLocation: {memory_location}")
