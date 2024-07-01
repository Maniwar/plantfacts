from openai import OpenAI
from gtts import gTTS
from io import BytesIO
import streamlit as st
from streamlit_searchbox import st_searchbox
import base64
import requests
import json
import redis
import re

# Set page config to wide mode
st.set_page_config(layout="wide")

# Initialize OpenAI client
client = OpenAI()

# Connect to Redis instance
r = redis.Redis(host=st.secrets["REDIS_HOST"], port=st.secrets["REDIS_PORT"], password=st.secrets["REDIS_PASSWORD"], decode_responses=True)

# Instruction paragraph with FontAwesome CSS included
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
    <div style="display:flex;align-items:center">
        <i class="fas fa-seedling" style="font-size:48px; margin-right: 10px;"></i>
        <div>
            <h3>Discover Your Plant's Facts</h3>
            <p>This app uses AI to provide detailed information and facts about your plants.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# UI for selecting input method
input_method = st.radio("Select Input Method", ("Search Box", "File Upload", "Camera Capture"))

# Define the function for getting search suggestions with extra flexibility
def get_search_suggestions(query, **kwargs):
    try:
        # Add '/complete/' and 'client' parameter to the search URL
        url = f"http://google.com/complete/search?client=chrome&q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        response = requests.get(url, headers=headers)
        results = json.loads(response.text)[1]

        # Insert the user input as the first option
        results.insert(0, query)

        return results
    except Exception as e:
        print(e)
        return []

# Function to retrieve plant analysis from OpenAI
def get_analysis(plant_name):
    key = f'plant:{plant_name}'
    result = r.get(key)
    if result is not None:
        return result
    else:
        prompt = f"""Write a comprehensive and detailed report on the plant {plant_name}. Include the following information:
1. **General Information**:
   - Common name
   - Scientific name
   - Origin and habitat
   - Description and physical characteristics

2. **Care Instructions**:
   - Light requirements
   - Watering needs
   - Soil preferences
   - Temperature and humidity requirements
   - Fertilization tips
   - Pruning and maintenance

3. **Toxicity**:
   - Is the plant toxic to humans or pets?
   - Symptoms of poisoning
   - What you should do

4. **Propagation**:
   - Methods of propagation
   - Best time to propagate

5. **Common Issues**:
   - Pests and diseases
   - Common problems and solutions

6. **Interesting Facts**:
   - Any unique features or historical significance

Make sure the report is detailed and easy to understand for both novice and experienced plant enthusiasts."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a plant expert providing detailed information about various plants."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
        )
        analysis = response.choices[0].message.content.strip()
        r.set(key, analysis)
        return analysis

def clean_text_for_tts(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold markdown
    text = re.sub(r'\#\#(.*?)\n', r'\1. ', text)  # Translate headers to plain text
    text = re.sub(r'\#(.*?)\n', r'\1. ', text)  # Ensure single hashes are also replaced
    text = re.sub(r'\* (.*?)\n', r'\1. ', text)  # Translate markdown list items
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove markdown links, keeping link text
    text = text.replace('|', ', ').replace('-', ' ').replace('`', '')  # Remove or replace other special characters
    return text

def display_analysis(analysis, mute_audio=True):
    st.subheader("AI Analysis:")
    st.write(analysis)

    if not mute_audio:
        clean_analysis = clean_text_for_tts(analysis)
        audio_stream = BytesIO()
        tts = gTTS(text=clean_analysis, lang='en')
        tts.write_to_fp(audio_stream)
        st.audio(audio_stream, format="audio/mpeg", start_time=0)

# Search Box/Input Method
if input_method == "Search Box":
    st.title("Search Plants")
    st.markdown("""
    Instructions for Search Box:
    - Enter the plant's common name or scientific name in the search box.
    - Select it from the drop down menu.
    - Click "Search" to start the analysis.
    """)
    plant_name = st_searchbox(
        search_function=get_search_suggestions,
        placeholder="e.g., Monstera Deliciosa",
        label=None,
        clear_on_submit=False,
        clearable=True,
        key="plant_search",
    )
    search_button = st.button("Search")
    mute_audio = st.checkbox("Reset & Don't Load Audio", value=True)
    if search_button:
        with st.spinner("Analyzing..."):
            analysis = get_analysis(plant_name)
        display_analysis(analysis)

# File Upload/Input Method
elif input_method == "File Upload":
    st.title("Upload Plant Image")
    st.markdown("""
    Instructions for File Upload:
    - Click 'Upload an Image' to select an image file from your device.
    - Supported formats are JPG and PNG.
    - The app will analyze the image and extract the plant information.
    """)
    uploaded_image = st.file_uploader("Upload an image", type=['jpg', 'png'])
    
    if uploaded_image:
        with st.spinner("Processing..."):
            image_bytes = uploaded_image.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            st.image(image_bytes, caption='Uploaded Image', width=300)
            
            user_message_content = {
                "type": "text",
                "text": "Identify the plant in the image and provide its common name or scientific name."
            }
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [user_message_content,
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_b64}",
                                        },
                                    },
                                   ],
                    }
                ],
                max_tokens=50,
            )
            plant_name = response.choices[0].message.content
            st.write("Plant:")
            st.write(plant_name)
            
            analysis = get_analysis(plant_name)
            display_analysis(analysis)

# Camera Capture/Input Method
elif input_method == "Camera Capture":
    st.title("Capture Image with Camera")
    st.markdown("""
    Instructions for Camera Capture:
    - Snap a photo of the plant.
    - Ensure the picture is clear and legible.
    - The app will process the captured image to identify the plant.
    """)
    captured_image = st.camera_input("Capture an image")
    
    if captured_image:
        with st.spinner("Processing..."):
            image_bytes = captured_image.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            user_message_content = {
                "type": "text",
                "text": "Identify the plant in the image and provide its common name or scientific name."
            }
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [user_message_content,
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_b64}",
                                        },
                                    },
                                   ],
                    }
                ],
                max_tokens=50,
            )
            
            plant_name = response.choices[0].message.content
            st.write("Plant:")
            st.write(plant_name)

            analysis = get_analysis(plant_name)
            display_analysis(analysis)


st.divider()
expander = st.expander("Legal and Data Privacy Statement", expanded=False)
with expander:
    st.markdown(
    """
<p style="font-size:14px;">Legal Statement</p>
<p style="font-size:14px;">
This application ("App") is provided "as is" without any warranties, express or implied. The information provided by the App is intended to be used for informational purposes only and not as a substitute for professional advice, diagnosis, or treatment. Always seek the advice of your qualified info provider with any questions you may have regarding a plant. Never disregard professional advice or delay in seeking it because of something you have read on the App.
</p>
<p style="font-size:14px;">
The App uses the OpenAI Application Protocol Interface (API) to analyze plants and provide an assessment. This information is not intended to be exhaustive and does not cover all possible uses, directions, precautions, or adverse effects that may occur. While we strive to provide accurate information, we make no representation and assume no responsibility for the accuracy of information on or available through the App.
</p>
<p style="font-size:14px;">
The App does not endorse any specific product, service, or treatment. The use of any information provided by the App is solely at your own risk. The App and its owners or operators are not liable for any direct, indirect, punitive, incidental, special or consequential damages that result from the use of, or inability to use, this site.
</p>
<p style="font-size:14px;">
Certain state laws do not allow limitations on implied warranties or the exclusion or limitation of certain damages. If these laws apply to you, some or all of the above disclaimers, exclusions, or limitations may not apply to you, and you might have additional rights.
</p>
<p style="font-size:14px;">
By using this App, you agree to abide by the terms of this legal statement.
</p>
<p style="font-size:14px;">
* This information is based on provided references sourced by AI. It should not be taken as medical advice.
</p>
<p style="font-size:14px;">Data Privacy Statement</p>
<p style="font-size:14px;">
This application ("App") respects your privacy. This statement outlines our practices regarding your data.
</p>
<p style="font-size:14px;">
<b>Information Collection:</b> The only data the App collects is the plant name queries you enter when you use the App. We do not collect any personal data, including contact information.
</p>
<p style="font-size:14px;">
<b>Information Usage:</b> Your plant name queries are used solely to provide the App's services, specifically to analyze plant information and offer care-related insights. We now cache the results of previously searched items to speed up the performance of the App. All data is processed in real time and is not stored on our servers or databases beyond this purpose.
</p>
<p style="font-size:14px;">
<b>Information Sharing:</b> We do not share your data with any third parties, except as necessary to provide the App's services, such as interacting with the OpenAI API.
</p>
<p style="font-size:14px;">
<b>User Rights:</b> As we do not store your data beyond the current session, we cannot facilitate requests for data access, correction, or deletion.
</p>
<p style="font-size:14px;">
<b>Security Measures:</b> We implement security measures to protect your data during transmission, but no system is completely secure. We cannot fully eliminate the risks associated with data transmission.
</p>
<p style="font-size:14px;">
<b>Changes to this Policy:</b> Any changes to this data privacy statement will be updated on the App.
</p>
<p style="font-size:14px;">
<b>Ownership of Data:</b> All output data generated by the App, including but not limited to the analysis of plant information, belongs to the owner of the App. The owner retains the right to use, reproduce, distribute, display, and perform the data in any manner and for any purpose. The user acknowledges and agrees that any information input into the App may be used in this way, subject to the limitations set out in the Data Privacy Statement.
</p>

    """,
    unsafe_allow_html=True,
)
