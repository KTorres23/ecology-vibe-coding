import streamlit as st
import os
import glob
from PIL import Image, ImageOps
from streamlit_cropper import st_cropper

# Initialize session state to keep track of our position in the image list
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0

st.set_page_config(layout="wide", page_title="iNaturalist Cropper")
st.title("🌿 iNaturalist Image Prep")

# --- DIRECTORY SETUP ---
st.sidebar.header("1. Directory Settings")
directory = st.sidebar.text_input("Folder Path", value=".")

# --- BATCH RENAMING ---
st.sidebar.header("2. Rename Files")
st.sidebar.write("Finds files with ' - Copy' and renames them to end with '_cropped'.")

if st.sidebar.button("Rename ' - Copy' Files"):
    if os.path.isdir(directory):
        renamed_count = 0
        # Check all files in the directory
        for filename in os.listdir(directory):
            if " - Copy" in filename:
                old_path = os.path.join(directory, filename)
                # Replace ' - Copy' with '_cropped'
                new_filename = filename.replace(" - Copy", "_cropped")
                new_path = os.path.join(directory, new_filename)
                
                os.rename(old_path, new_path)
                renamed_count += 1
        st.sidebar.success(f"Successfully renamed {renamed_count} files!")
    else:
        st.sidebar.error("Invalid directory path.")

# --- IMAGE PROCESSING PIPELINE ---
st.header("3. Crop Images")

if os.path.isdir(directory):
    # Find all images containing '_cropped'
    valid_extensions = ('*.png', '*.jpg', '*.jpeg', '*.JPG', '*.JPEG')
    cropped_files = []
    for ext in valid_extensions:
        # Search for files with _cropped in the name
        search_pattern = os.path.join(directory, f"*_cropped{ext[1:]}")
        cropped_files.extend(glob.glob(search_pattern))
    
    # Sort files alphabetically so they process in a predictable order
    cropped_files.sort()

    if not cropped_files:
        st.info("No files containing '_cropped' found in the current directory.")
    else:
        total_images = len(cropped_files)
        
        # Check if we've finished the batch
        if st.session_state.current_image_index >= total_images:
            st.success("🎉 All images in this folder have been processed!")
            if st.button("Start Over"):
                st.session_state.current_image_index = 0
                st.rerun()
        else:
            # Get the current file based on our session state index
            current_path = cropped_files[st.session_state.current_image_index]
            filename = os.path.basename(current_path)
            
            # Progress tracker
            st.write(f"**Processing Image {st.session_state.current_image_index + 1} of {total_images}:** `{filename}`")
            st.progress((st.session_state.current_image_index) / total_images)

            # Load the image
            img = Image.open(current_path)
            # Fix orientation metadata (prevents vertical phone/camera photos from displaying sideways)
            img = ImageOps.exif_transpose(img)
            
            # Ensure image is in RGB mode (necessary for saving as JPEG if it was RGBA)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Render the cropper interface
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # The cropper component
                cropped_img = st_cropper(
                    img, 
                    realtime_update=True, 
                    box_color='#00FF00',
                    aspect_ratio=(1, 1) # Locks the box to a perfect square for iNat thumbnails
                )
            
            with col2:
                st.write("**Preview:**")
                # Show the resulting crop
                _ = cropped_img.thumbnail((300, 300)) # Resize for preview purposes only
                st.image(cropped_img)
                
                st.write("---")
                # Action button to save and advance
                if st.button("💾 Save Crop & Next", use_container_width=True):
                    # Save the cropped image, overwriting the existing '_cropped' file
                    cropped_img.save(current_path)
                    
                    # Advance the index and refresh the app
                    st.session_state.current_image_index += 1
                    st.rerun()
                    
            # Allow skipping an image if it doesn't need to be cropped
            if st.button("Skip (Don't modify)", type="secondary"):
                st.session_state.current_image_index += 1
                st.rerun()