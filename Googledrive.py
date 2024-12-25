import gdown
import zipfile
import os
from PIL import Image

# Step 1: Download ZIP file from Google Drive
def download_zip_from_drive(file_id, output_path):
    # Google Drive download link: https://drive.google.com/uc?id=FILE_ID
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# Step 2: Extract ZIP file
def extract_zip(zip_path, extract_to_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)
    print(f"ZIP file extracted to {extract_to_folder}")

# Step 3: Loop through the folder and read .jpg images
def read_images_from_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            image_path = os.path.join(folder_path, filename)
            with Image.open(image_path) as img:
                print(f"Processing {filename}: Size: {img.size}, Mode: {img.mode}")
                # You can add your image processing logic here

# Main function
def main():
    # Step 1: Download the ZIP file from Google Drive
    file_id = 'YOUR_GOOGLE_DRIVE_FILE_ID'  # Replace with your Google Drive file ID
    zip_output_path = 'downloaded_file.zip'  # Path to save the ZIP file
    extract_folder = 'extracted_folder'  # Folder to extract the ZIP contents

    download_zip_from_drive(file_id, zip_output_path)
    
    # Step 2: Extract the ZIP file
    extract_zip(zip_output_path, extract_folder)
    
    # Step 3: Read .jpg images in the extracted folder
    read_images_from_folder(extract_folder)

if __name__ == '__main__':
    main()
  
