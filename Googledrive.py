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








import zipfile
import os
from PIL import Image

# Define the path of the zip file
zip_file_path = 'path/to/your/zipfile.zip'
extracted_folder = 'extracted_files/'

# Step 1: Extract the contents of the zip file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    # Extract all contents into a specified folder
    zip_ref.extractall(extracted_folder)

# Step 2: Read .jpg images inside the extracted folder
for root, dirs, files in os.walk(extracted_folder):
    for file in files:
        if file.lower().endswith('.jpg'):  # Check if it's a .jpg file
            image_path = os.path.join(root, file)
            print(f'Reading image: {image_path}')
            
            # Step 3: Open and process the image
            try:
                with Image.open(image_path) as img:
                    img.show()  # This will display the image, or you can save, manipulate, etc.
            except Exception as e:
                print(f"Could not open image {image_path}: {e}")
                
