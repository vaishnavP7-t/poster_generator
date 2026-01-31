import streamlit as st
import PIL.Image as Image
import PIL.ImageFilter as ImageFilter
import PIL.ImageEnhance as ImageEnhance
import PIL.ImageOps as ImageOps
import io
import base64
import time
import random

# Configure page
st.set_page_config(
    page_title="AI Poster Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .upload-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 2px dashed #e0e0e0;
    }
    
    .prompt-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .result-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .processing-animation {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        border-radius: 15px;
        color: #333;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
    }
    
    .image-container {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def apply_mock_transformation(image, prompt):
    """Apply mock transformations based on prompt keywords"""
    img = image.copy()
    prompt_lower = prompt.lower()
    
    # Apply different filters based on prompt content
    if any(word in prompt_lower for word in ['blur', 'soft', 'dream']):
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    elif any(word in prompt_lower for word in ['sharp', 'enhance', 'crisp']):
        img = img.filter(ImageFilter.SHARPEN)
    
    elif any(word in prompt_lower for word in ['bright', 'light', 'sunny']):
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.3)
    
    elif any(word in prompt_lower for word in ['dark', 'moody', 'shadow']):
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)
    
    elif any(word in prompt_lower for word in ['colorful', 'vibrant', 'saturated']):
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.5)
    
    elif any(word in prompt_lower for word in ['vintage', 'old', 'sepia']):
        img = ImageOps.colorize(ImageOps.grayscale(img), '#704214', '#C0A882')
    
    elif any(word in prompt_lower for word in ['black', 'white', 'mono']):
        img = ImageOps.grayscale(img)
    
    elif any(word in prompt_lower for word in ['contrast', 'dramatic']):
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
    
    else:
        # Default enhancement
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
    
    return img

def create_processing_animation():
    """Create a processing animation"""
    processing_container = st.empty()
    
    messages = [
        "🔍 Analyzing your image...",
        "🧠 Understanding your prompt...",
        "✨ Applying AI magic...",
        "🎨 Generating modifications...",
        "🚀 Almost ready..."
    ]
    
    for i, message in enumerate(messages):
        processing_container.markdown(f"""
        <div class="processing-animation">
            <h3>{message}</h3>
            <div style="width: {(i+1)*20}%; height: 4px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                 border-radius: 2px; margin: 1rem auto;"></div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.8)
    
    processing_container.empty()

# Main app header
st.markdown("""
<div class="main-header">
    <h1>🎨 AI Image Editor</h1>
    <p>Transform your images with the power of AI - completely free!</p>
</div>
""", unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    # Upload section
    st.markdown("""
    <div class="upload-section">
        <h3 style="text-align: center; color: #333; margin-bottom: 1rem;">📸 Upload Your Image</h3>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image to get started"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(image, caption="Original Image", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Prompt section
    st.markdown("""
    <div class="prompt-section">
        <h3 style="margin-bottom: 1rem;">✍️ Describe Your Vision</h3>
        <p style="opacity: 0.9; margin-bottom: 1rem;">Tell the AI how you want to transform your image</p>
    </div>
    """, unsafe_allow_html=True)
    
    prompt = st.text_area(
        "",
        placeholder="e.g., Make it more colorful and vibrant, Add a dreamy blur effect, Convert to black and white, Make it brighter and more cheerful...",
        height=100,
        help="Be creative! Describe colors, moods, styles, or effects you want."
    )
    
    # Example prompts
    st.markdown("**💡 Try these examples:**")
    example_prompts = [
        "Make it bright and sunny",
        "Add a vintage sepia tone",
        "Create a dreamy, soft look",
        "Enhance colors and contrast",
        "Convert to artistic black and white"
    ]
    
    for example in example_prompts:
        if st.button(f"📝 {example}", key=example):
            prompt = example
            st.rerun()

# Process button and results
if uploaded_file is not None and prompt:
    st.markdown("---")
    
    col3, col4, col5 = st.columns([1, 2, 1])
    with col4:
        if st.button("🚀 Transform Image", key="transform"):
            # Create processing animation
            create_processing_animation()
            
            # Apply transformation
            image = Image.open(uploaded_file)
            transformed_image = apply_mock_transformation(image, prompt)
            
            # Store in session state
            st.session_state.transformed_image = transformed_image
            st.session_state.original_image = image
            st.session_state.used_prompt = prompt

# Display results
if 'transformed_image' in st.session_state:
    st.markdown("""
    <div class="result-section">
        <h3 style="text-align: center; color: #333; margin-bottom: 2rem;">✨ Your Transformed Image</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Before and After comparison
    result_col1, result_col2 = st.columns(2)
    
    with result_col1:
        st.markdown("**🔸 Original**")
        st.image(st.session_state.original_image, use_column_width=True)
    
    with result_col2:
        st.markdown("**✨ Transformed**")
        st.image(st.session_state.transformed_image, use_column_width=True)
    
    # Download button
    buf = io.BytesIO()
    st.session_state.transformed_image.save(buf, format='PNG')
    byte_data = buf.getvalue()
    
    st.download_button(
        label="📥 Download Transformed Image",
        data=byte_data,
        file_name="ai_transformed_image.png",
        mime="image/png"
    )
    
    st.success(f"✅ Successfully applied: '{st.session_state.used_prompt}'")

# Features section
st.markdown("---")
st.markdown("### 🌟 Features")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🎨 Creative Transformations</h4>
        <p>Apply artistic effects, color adjustments, and style changes with simple text prompts</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div class="feature-card">
        <h4>⚡ Instant Results</h4>
        <p>See your transformations in seconds with our optimized processing pipeline</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col3:
    st.markdown("""
    <div class="feature-card">
        <h4>💰 Completely Free</h4>
        <p>No subscriptions, no limits. Transform as many images as you want!</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>Made with ❤️ using Streamlit | Transform your creativity into reality</p>
</div>
""", unsafe_allow_html=True)