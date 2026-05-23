import streamlit as st
import pandas as pd
import os
import re
from pathlib import Path
from PIL import Image
import streamlit.components.v1 as components

##### How to run script
# 1. In terminal, run `py -m pip install streamlit pandas pillow`
# 2. In terminal, navigate to "...ch1_eco_subobj_01/" using run `cd "...full path.../ch1_eco_subobj_01/"`
# 3. In terminal, run `py -m streamlit run scripts/L2/203_label_EPT_images_app.py`
# 4. Navigate to web browser and use web-based application for annotating EPT images


# 0. Helper functions
def make_square_thumb(img):
    """Center crop for thumbnails"""
    width, height = img.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    return img.crop((left, top, left + size, top + size))

def make_square_main(img):
    """Pad with a dark background (letterbox) for main image so no data is cut off"""
    width, height = img.size
    size = max(width, height)
    new_img = Image.new("RGB", (size, size), (25, 25, 25)) # Dark gray padding
    new_img.paste(img, ((size - width) // 2, (size - height) // 2))
    return new_img

# 1. Page Configuration
st.set_page_config(page_title="EPT Annotation Tool", layout="wide")

# Get the absolute path of the directory containing this script (scripts/L2)
SCRIPT_DIR = Path(__file__).resolve().parent
# Step backward two levels to reach the root 'ch1_eco_subobj_01' directory
ROOT_DIR = SCRIPT_DIR.parent.parent

# Build absolute paths by joining the root directory to data folders
BASE_DIR = ROOT_DIR / "data" / "L2" / "EPT_images"
METADATA_CSV = ROOT_DIR / "data" / "L2" / "202b_images_metadata_EUSA_EPT.csv"
OUTPUT_CSV = ROOT_DIR / "data" / "L2" / "203_EPT_image_labels.csv"
LABELS = ["Adult", "Nymph", "Larvae", "Hand", "Can't ID", "Look into Later", "Missing Data", "Other"]

def parse_filename(filepath):
    filename = filepath.name
    match = re.match(r"([EPT])_obs(\d+)_img(\d+)_(\d+)\.jpg", filename, re.IGNORECASE)
    if match:
        spp_initial = match.group(1).upper()
        obs_id = match.group(2)
        img_id = match.group(3) 
        species_map = {"E": "Ephemeroptera", "P": "Plecoptera", "T": "Trichoptera"}
        species = species_map.get(spp_initial, "Unknown EPT")
        return species, obs_id, img_id
    return "Unknown", "Unknown", "Unknown"

# 2. Initialization and Scanning
if os.path.exists(OUTPUT_CSV):
    df_labels = pd.read_csv(OUTPUT_CSV)
    df_labels['notes'] = df_labels['notes'].fillna("")
    # Failsafe: Ensure our new boolean columns don't have blank/NaN values
    for lbl in LABELS:
        snake_lbl = lbl.lower().replace(" ", "_")
        col_name = f"label_{snake_lbl}"
        if col_name in df_labels.columns:
            df_labels[col_name] = df_labels[col_name].fillna(False).astype(bool)
else:
    st.info("Building master list from R metadata...")
    if not os.path.exists(METADATA_CSV):
        st.error(f"Metadata not found at {METADATA_CSV}. Please export it from R.")
        st.stop()
        
    # Read the master list from R
    df_metadata = pd.read_csv(METADATA_CSV)
    
    all_image_data = []
    for _, row in df_metadata.iterrows():
        obs_id = row['id']
        filename = row['img_name']
        
        species, _, img_id = parse_filename(Path(filename))
        
        if species == "Ephemeroptera": subdir = "ephe_imgs"
        elif species == "Plecoptera": subdir = "plec_imgs"
        elif species == "Trichoptera": subdir = "tric_imgs"
        else: subdir = ""
            
        expected_path = os.path.join(BASE_DIR, subdir, filename)
        
        # Base row data
        row_data = {
            "image_path": expected_path,
            "filename": filename,
            "species": species,
            "observation_id": obs_id,
            "image_id": img_id,
            "notes": "",          
            "labeled": False
        }
        
        # Create a boolean column for each possible label, defaulting to False
        for lbl in LABELS:
            snake_lbl = lbl.lower().replace(" ", "_")
            row_data[f"label_{snake_lbl}"] = False
            
        all_image_data.append(row_data)
        
    df_labels = pd.DataFrame(all_image_data)
    df_labels['obs_total'] = df_labels.groupby('observation_id')['image_id'].transform('count')
    df_labels['obs_pos'] = df_labels.groupby('observation_id')['image_id'].rank(method='dense').astype(int)
    df_labels.to_csv(OUTPUT_CSV, index=False)

# 3. Session State Setup (Observation-Centric)
if 'df' not in st.session_state:
    st.session_state.df = df_labels

if 'unique_obs' not in st.session_state:
    # Maintain an ordered list of unique observation IDs
    st.session_state.unique_obs = st.session_state.df['observation_id'].unique()

# Resume Logic: Find the first observation that isn't fully labeled
if 'current_obs_index' not in st.session_state:
    unlabeled = st.session_state.df[st.session_state.df['labeled'] == False]
    if not unlabeled.empty:
        first_unlabeled_obs = unlabeled.iloc[0]['observation_id']
        # Find where this obs_id lives in the unique list
        st.session_state.current_obs_index = list(st.session_state.unique_obs).index(first_unlabeled_obs)
    else:
        st.session_state.current_obs_index = 0

# 4. Handle State Transitions (When moving to a new observation)
# This block pulls existing data if you go backwards to review a previous observation
if 'prev_obs_index' not in st.session_state or st.session_state.prev_obs_index != st.session_state.current_obs_index:
    st.session_state.prev_obs_index = st.session_state.current_obs_index
    st.session_state.current_img_subindex = 0 # Reset to the first image of the observation
    
    # Grab data for the newly loaded observation
    curr_obs_id = st.session_state.unique_obs[st.session_state.current_obs_index]
    obs_df = st.session_state.df[st.session_state.df['observation_id'] == curr_obs_id]
    first_row = obs_df.iloc[0]
    
    # Load existing labels into active state
    st.session_state.active_labels = set()
    if first_row['labeled']:
            for lbl in LABELS:
                snake_lbl = lbl.lower().replace(" ", "_")
                if first_row.get(f"label_{snake_lbl}", False):
                    st.session_state.active_labels.add(lbl)
        
    # Load existing notes securely into the text area's widget key
    st.session_state['notes_input_key'] = str(first_row['notes']) if first_row['notes'] else ""

# Helper to get the subset of images for the current Observation ID
curr_obs_id = st.session_state.unique_obs[st.session_state.current_obs_index]
obs_df = st.session_state.df[st.session_state.df['observation_id'] == curr_obs_id].reset_index()
total_imgs_in_obs = len(obs_df)

# 5. Core Actions
def submit_observation():
    mask = st.session_state.df['observation_id'] == curr_obs_id
    
    # First, reset all label columns to False for this observation
    for lbl in LABELS:
        snake_lbl = lbl.lower().replace(" ", "_")
        st.session_state.df.loc[mask, f"label_{snake_lbl}"] = False
        
    # Then, set the currently active ones to True
    for active_lbl in st.session_state.active_labels:
        snake_lbl = active_lbl.lower().replace(" ", "_")
        st.session_state.df.loc[mask, f"label_{snake_lbl}"] = True
        
    st.session_state.df.loc[mask, 'notes'] = st.session_state.notes_input_key
    
    has_labels = len(st.session_state.active_labels) > 0
    st.session_state.df.loc[mask, 'labeled'] = has_labels 
    
    st.session_state.df.to_csv(OUTPUT_CSV, index=False)
    jump_to_next_unlabeled()

def next_obs():
    if st.session_state.current_obs_index < len(st.session_state.unique_obs) - 1:
        st.session_state.current_obs_index += 1

def prev_obs():
    if st.session_state.current_obs_index > 0:
        st.session_state.current_obs_index -= 1

# ==========================================
# 6. Main Interface Layout
# ==========================================
st.title("EPT Image Annotation Tool")
st.write("Annotation tool for locally saved image observations. After assigning an observation one (or more) labels and an optional note, click the 'Submit' button to proceed to the next unlabelled observation, or click the `tab` key.")

# --- NEW: Dashboard & Search Expander ---
with st.expander("🔍 Search & Species Progress Dashboard", expanded=False):
    
    # 1. Species Progress Metrics
    st.markdown("#### Progress by Species")
    # Group by observation to get accurate batch counts
    obs_status = st.session_state.df.groupby(['species', 'observation_id'])['labeled'].first().reset_index()
    species_stats = obs_status.groupby('species')['labeled'].agg(Finished='sum', Total='count').reset_index()
    
    # Create columns dynamically based on how many species are in the dataset
    stat_cols = st.columns(len(species_stats) if len(species_stats) > 0 else 1)
    for i, row in species_stats.iterrows():
        with stat_cols[i]:
            remaining = row['Total'] - row['Finished']
            # Using Streamlit's built-in metric card
            st.metric(
                label=row['species'], 
                value=f"{row['Finished']} / {row['Total']}", 
                delta=f"{remaining} left", 
                delta_color="inverse"
            )
            
    st.write("---")
    
    # 2. Quick Jump & Search Tools
    st.markdown("#### Quick Jump")
    s_col1, s_col2, s_col3 = st.columns(3)
    
    with s_col1:
        # Jump by Master Index
        jump_idx = st.number_input(
            "Jump to Observation Index:", 
            min_value=1, 
            max_value=len(st.session_state.unique_obs), 
            value=st.session_state.current_obs_index + 1
        )
        if st.button("Go to Index", width="stretch"):
            st.session_state.current_obs_index = jump_idx - 1
            st.session_state.current_img_subindex = 0
            st.rerun()
            
    with s_col2:
        # Jump by Observation ID
        search_obs = st.text_input("Search Observation ID:")
        if st.button("Go to Observation", width="stretch"):
            search_str = str(search_obs).strip()
            # Safely check matching strings to avoid CSV integer inference issues
            matches = st.session_state.df[st.session_state.df['observation_id'].astype(str) == search_str]
            if not matches.empty:
                target_obs = matches.iloc[0]['observation_id']
                st.session_state.current_obs_index = list(st.session_state.unique_obs).index(target_obs)
                st.session_state.current_img_subindex = 0
                st.rerun()
            else:
                st.error(f"Observation ID '{search_str}' not found.")
                
    with s_col3:
        # Jump by Image ID
        search_img = st.text_input("Search Image ID:")
        if st.button("Go to Image", width="stretch"):
            search_str = str(search_img).strip()
            matches = st.session_state.df[st.session_state.df['image_id'].astype(str) == search_str]
            if not matches.empty:
                target_obs = matches.iloc[0]['observation_id']
                st.session_state.current_obs_index = list(st.session_state.unique_obs).index(target_obs)
                # Automatically set the subindex to show the exact searched image
                st.session_state.current_img_subindex = int(matches.iloc[0]['obs_pos']) - 1
                st.rerun()
            else:
                st.error(f"Image ID '{search_str}' not found.")

# --- Overall Progress Bar ---
total_obs = len(st.session_state.unique_obs)
labeled_obs_count = st.session_state.df.groupby('observation_id')['labeled'].first().sum()
st.progress(labeled_obs_count / total_obs if total_obs > 0 else 0)
st.write(f"**Overall Progress:** {labeled_obs_count} / {total_obs} total observations annotated")

# --- Top Navigation ---
def jump_to_next_unlabeled():
    # Filter dataframe for only unlabeled rows
    unlabeled_rows = st.session_state.df[~st.session_state.df['labeled']]
    
    if not unlabeled_rows.empty:
        unlabeled_obs_ids = unlabeled_rows['observation_id'].unique()
        unique_obs_list = list(st.session_state.unique_obs)
        current_idx = st.session_state.current_obs_index
        
        # Look for the first unlabeled observation AFTER your current position
        for obs_id in unlabeled_obs_ids:
            idx = unique_obs_list.index(obs_id)
            if idx > current_idx:
                st.session_state.current_obs_index = idx
                st.session_state.current_img_subindex = 0
                return
                
        # If none exist after your position, wrap around and grab the first available one
        st.session_state.current_obs_index = unique_obs_list.index(unlabeled_obs_ids[0])
        st.session_state.current_img_subindex = 0

# Adjust columns to [1, 1, 1] so they are equal width and can fit the new button
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
with nav_col1:
    if st.button("⬅️ Previous Observation", width="stretch"):
        prev_obs()
        st.rerun()
        
with nav_col2:
    if st.button("⏭️ Find Next Unlabelled Observation", type="secondary", width="stretch"):
        jump_to_next_unlabeled()
        st.rerun()
        
with nav_col3:
    if st.button("Skip to Next Observation ➡️", width="stretch"):
        next_obs()
        st.rerun()

st.write("---")

curate_metadata_col, curate_image_col = st.columns([1, 1]) 

# Get data for the specific image currently being viewed within the observation
current_img_row = obs_df.iloc[st.session_state.current_img_subindex]
is_labeled_str = "✅ Annotated" if current_img_row['labeled'] else "❌ Not annotated"

with curate_metadata_col:
    st.markdown("### Observation Metadata")
# Split the top of this section into two inner columns
    meta_info_col, meta_thumb_col = st.columns([1, 1])
    
    with meta_info_col:
        st.markdown(f"**Observation Index:** {st.session_state.current_obs_index + 1} of {len(st.session_state.unique_obs)}")
        st.markdown(f"**Species:** {current_img_row['species']}")
        st.markdown(f"**Observation ID:** `{current_img_row['observation_id']}`")
        st.markdown(f"**Total Images:** {total_imgs_in_obs}")
        st.markdown(f"**Status:** {is_labeled_str}")
        
    with meta_thumb_col:
        # Generate the thumbnails right beside the text
        thumb_imgs = []
        thumb_caps = []
        for idx, row in obs_df.iterrows():
            try:
                img = Image.open(row['image_path'])
                # NEW: Apply the square crop
                thumb_imgs.append(make_square_thumb(img)) 
                
                cap = f"Img {idx+1}" + (" 📍" if idx == st.session_state.current_img_subindex else "")
                thumb_caps.append(cap)
            except:
                pass
                
        if thumb_imgs:
            st.image(thumb_imgs, width=70, caption=thumb_caps)
    
    st.write("---")
    st.markdown("### Assign Labels")
    st.markdown("Applies to ALL images in observation")
    
    # Dynamic Toggle Buttons for Multi-Select
    button_cols = st.columns(len(LABELS))
    for i, lbl in enumerate(LABELS):
        is_active = lbl in st.session_state.active_labels
        with button_cols[i]:
            # The button type determines its color (primary = blue/active, secondary = gray/inactive)
            if st.button(lbl, type="primary" if is_active else "secondary", width="stretch", key=f"btn_{lbl}"):
                if is_active:
                    st.session_state.active_labels.remove(lbl)
                else:
                    st.session_state.active_labels.add(lbl)
                st.rerun()
    
    st.write(" ")
    
    # Notes Text Area (Tied securely to session state so it survives button clicks)
    st.text_area(
        "Descriptive Note:",
        key="notes_input_key", 
        height=100,
        placeholder="Add details (e.g., multiple specimens, obscured view, hand present...)"
    )
    
    submit_btn_col, _ = st.columns([1, 2])
    with submit_btn_col:
        st.write(" ") 
        if st.button("💾 Submit & Go to the next unlabelled observation", type="primary", width="stretch"):
            submit_observation()
            st.rerun()

with curate_image_col:
    st.markdown(f"### Image {st.session_state.current_img_subindex + 1} of {total_imgs_in_obs}")
    st.markdown(f"**Image ID:** `{current_img_row['image_id']}` | **File:** `{current_img_row['filename']}`")
    
    if os.path.exists(current_img_row['image_path']):
        try:
            img = Image.open(current_img_row['image_path'])
            sq_img = make_square_main(img)
            
            img_container_col, _ = st.columns([2, 2])
            with img_container_col:
                st.image(sq_img, width="stretch")
        except Exception as e:
            st.error(f"Image corrupted or unreadable: {e}")
    else:
        # Failsafe display for missing downloads
        st.warning("⚠️ **Image File Missing**")
        st.info("This image failed to download or is not located in the expected directory. You can leave a note and skip, or apply a specific label for missing data.")
        st.code(f"Expected path: {current_img_row['image_path']}")

    # Image Cycling Controls (Only show if there is more than 1 image)
    if total_imgs_in_obs > 1:
        img_nav_col1, _, img_nav_col2 = st.columns([1, 1, 1])
        with img_nav_col1:
            if st.button("⬅️ Previous Image", width="stretch", disabled=(st.session_state.current_img_subindex == 0)):
                st.session_state.current_img_subindex -= 1
                st.rerun()
        with img_nav_col2:
            if st.button("Next Image ➡️", width="stretch", disabled=(st.session_state.current_img_subindex == total_imgs_in_obs - 1)):
                st.session_state.current_img_subindex += 1
                st.rerun()

# ==========================================
# 7. Keyboard Shortcuts (Single Key: Tab)
# ==========================================
components.html(
    """
    <script>
    // 1. Break out of the Streamlit sandbox to access the main browser window
    const mainDoc = window.parent.document;
    
    // 2. Check if we already injected the listener (so we don't duplicate it on every click)
    if (!mainDoc.getElementById('tab-keybind-script')) {
        
        // 3. Create a new script tag and inject it directly into the main page head
        const script = mainDoc.createElement('script');
        script.id = 'tab-keybind-script';
        script.innerHTML = `
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    
                    // Stop the browser from tabbing into text boxes
                    e.preventDefault(); 
                    e.stopPropagation();
                    
                    // Find all buttons on the screen
                    const buttons = Array.from(document.querySelectorAll('button'));
                    
                    // Find ANY button with the word "Submit" (handles all variations)
                    const submitBtn = buttons.find(el => el.innerText.includes('Submit & Go to the next unlabelled observation'));
                    
                    if (submitBtn) {
                        submitBtn.click();
                    }
                }
            }, true); // The 'true' forces this to fire before Streamlit can intercept it
        `;
        mainDoc.head.appendChild(script);
    }
    </script>
    """,
    height=0,
    width=0
)

