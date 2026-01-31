import streamlit as st

# ---------------------------------------------------------------------
# ⚠️  PAGE CONFIG MUST BE FIRST
# ---------------------------------------------------------------------
st.set_page_config(page_title="AI Image Studio (Diagnostic)", page_icon="🔍", layout="wide")

from PIL import Image
import contextlib, io, torch, os, glob
from pathlib import Path

# ---------------------------------------------------------------------
# ⚠️  HARD DEPENDENCY CHECK
# ---------------------------------------------------------------------
try:
    import transformers
    st.success("✅ Transformers library found")
except ModuleNotFoundError:
    st.error("❌ Transformers library missing - run: pip install transformers")
    st.stop()

try:
    from diffusers import StableDiffusionPipeline
    st.success("✅ Diffusers library found")
except ModuleNotFoundError:
    st.error("❌ Diffusers library missing - run: pip install diffusers")
    st.stop()

# ---------------------------------------------------------------------
# 🔍 MODEL FINDER FUNCTIONS
# ---------------------------------------------------------------------
def find_cached_models():
    st.write("🔍 **Searching for cached models...**")

    possible_locations = [
        os.path.expanduser("~/.cache/huggingface/hub"),
        os.path.expanduser("~/.cache/huggingface/transformers"),
        os.path.expanduser("~/.cache/huggingface/diffusers"),
        os.path.expanduser("~/AppData/Local/huggingface/hub"),
        "./models", "./stable-diffusion", "../models", "."
    ]

    found_models = []
    for base_path in possible_locations:
        if os.path.exists(base_path):
            st.write(f"✅ Found directory: `{os.path.normpath(base_path)}`")
            try:
                contents = os.listdir(base_path)
                st.write(f"   📁 Contents: {contents[:10]}{'...' if len(contents) > 10 else ''}")
            except Exception as e:
                st.write(f"   ❌ Can't list contents: {e}")

            patterns = [
                "*stable-diffusion*",
                "*runwayml*",
                "models--*stable-diffusion*",
                "models--runwayml--stable-diffusion*"
            ]

            for pattern in patterns:
                matches = glob.glob(os.path.join(base_path, "**", pattern), recursive=True)
                for match in matches:
                    if os.path.isdir(match):
                        st.write(f"🔍 Checking potential model: `{os.path.normpath(match)}`")
                        try:
                            model_contents = os.listdir(match)
                            st.write(f"   📁 Model contents: {model_contents}")
                        except Exception as e:
                            st.write(f"   ❌ Can't list model contents: {e}")

                        indicators = [
                            'model_index.json', 'unet/config.json', 'vae/config.json',
                            'text_encoder/config.json', 'unet', 'vae', 'text_encoder',
                            'tokenizer', 'scheduler'
                        ]

                        valid = [i for i in indicators if os.path.exists(os.path.join(match, i))]
                        if valid:
                            found_models.append({'path': match, 'indicators': valid})
                            st.write(f"🎯 **Found model at:** `{os.path.normpath(match)}`")
                            st.write(f"   - Has: {', '.join(valid)}")
                        else:
                            st.write("   ⚠️ Directory found but no model indicators")
        else:
            st.write(f"❌ Directory not found: `{os.path.normpath(base_path)}`")
    return found_models


def test_model_loading(model_path):
    st.write(f"🧪 **Testing model loading from:** `{os.path.normpath(model_path)}`")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        st.write("   - Trying direct path loading...")
        pipe = StableDiffusionPipeline.from_pretrained(
            model_path, torch_dtype=dtype, local_files_only=True
        )
        st.success(f"✅ Successfully loaded model from {os.path.normpath(model_path)}")
        return pipe, "direct"
    except Exception as e:
        st.error(f"❌ Failed to load model: {str(e)}")
        try:
            snapshots = glob.glob(os.path.join(model_path, "snapshots", "*"))
            if snapshots:
                latest = max(snapshots, key=os.path.getctime)
                st.write(f"   - Trying snapshot folder: `{os.path.normpath(latest)}`")
                pipe = StableDiffusionPipeline.from_pretrained(
                    latest, torch_dtype=dtype, local_files_only=True
                )
                st.success(f"✅ Loaded from snapshot: {os.path.normpath(latest)}")
                return pipe, "snapshot"
        except Exception as e2:
            st.error(f"❌ Snapshot loading also failed: {str(e2)}")
        return None, None

# ---------------------------------------------------------------------
# 🛆 PIPELINE LOADER
# ---------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_pipeline_smart():
    found = find_cached_models()
    if not found:
        st.warning("⚠️ No cached models found. Will download...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        with st.spinner("Downloading model..."):
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5", torch_dtype=dtype
            )
        return pipe.to(device)

    for info in found:
        pipe, method = test_model_loading(info['path'])
        if pipe is not None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            pipe = pipe.to(device)
            if hasattr(pipe, "safety_checker"):
                pipe.safety_checker = lambda imgs, **kwargs: (imgs, False)
            st.success(f"🎉 Using model loaded via {method} method!")
            return pipe

    st.warning("⚠️ Local models found but couldn't load. Downloading...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    with st.spinner("Downloading model..."):
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", torch_dtype=dtype
        )
    return pipe.to(device)


def generate_image(prompt: str, guidance_scale: float = 7.5, steps: int = 30, seed: int | None = None):
    pipe = load_pipeline_smart()
    device = pipe.device
    gen = torch.Generator(device=device).manual_seed(seed) if seed else None
    with torch.autocast(device.type) if device.type == "cuda" else contextlib.nullcontext():
        out = pipe(prompt, guidance_scale=guidance_scale, num_inference_steps=steps, generator=gen)
    return out.images[0]

# ---------------------------------------------------------------------
# 🎨 STREAMLIT UI
# ---------------------------------------------------------------------
st.title("🔍 AI Image Studio - Diagnostic Mode")
st.write("This version helps find and use your local Stable Diffusion installation.")

st.subheader("💻 System Information")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**CUDA Available:** {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        st.write(f"**GPU:** {torch.cuda.get_device_name(0)}")
with col2:
    st.write(f"**PyTorch Version:** {torch.__version__}")
    st.write(f"**Device:** {'CUDA' if torch.cuda.is_available() else 'CPU'}")

st.divider()

st.subheader("🔍 Model Diagnostics")
if st.button("🔍 Search for Models", type="primary"):
    with st.spinner("Searching for models..."):
        models = find_cached_models()
    if models:
        st.success(f"Found {len(models)} potential model(s)!")
        for i, m in enumerate(models):
            st.write(f"**Model {i+1}:** `{os.path.normpath(m['path'])}`")
    else:
        st.info("No cached models found. The app will download one as needed.")

st.divider()

st.subheader("🎨 Generate Image")
prompt = st.text_area("Enter your prompt:", "a beautiful sunset over mountains", height=100)
col1, col2, col3 = st.columns(3)
with col1:
    steps = st.slider("Steps", 10, 50, 20)
with col2:
    guidance = st.slider("Guidance", 1.0, 20.0, 7.5)
with col3:
    seed = st.number_input("Seed (0 for random)", 0, 1000000, 0)

if st.button("🚀 Generate Image", type="primary"):
    if prompt.strip():
        try:
            with st.spinner("Generating image..."):
                seed_val = None if seed == 0 else seed
                image = generate_image(prompt, guidance, steps, seed_val)
            st.image(image, caption="Generated Image", use_column_width=True)
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button(
                "📅 Download Image",
                data=buf.getvalue(),
                file_name="generated_image.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")
            st.code(str(e))
    else:
        st.error("Please enter a prompt!")

st.divider()
st.caption("🔧 This diagnostic version will help identify and fix any model loading issues.")
