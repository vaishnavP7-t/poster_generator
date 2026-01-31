# 🎨 AI POSTER GENERATOR
 <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXg1NDZwaW4zcm1vc29sMmptNm94M3dyazNjOHVhZTVzaG5uNDhyYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/12r4pHjvAOv48o/giphy.gif" width="500" align="centre"></h2>

## 📌 Overview

The Simple AI Poster Generator leverages the power of diffusion models to generate high-quality poster backgrounds from descriptive prompts. The tool is ideal for creating event posters, educational flyers, and promotional material in just a few clicks.

Create stunning event posters in seconds using generative AI powered by the [OpenJourney](https://huggingface.co/prompthero/openjourney) model and [Gradio](https://www.gradio.app/) UI.


---

## ✨ Features

- 🧠 **AI-generated backgrounds** based on user-provided prompts
- 📝 **Custom text layout** with subtitle and event details
- 🖼️ **Optional logo upload** (supports auto-resizing and placement)
- ⚙️ **Multiple aspect ratios** like Square, Poster, Widescreen, etc.
- 🚀 Built with `Gradio`, `Diffusers`, and `Stable Diffusion`

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://gitlab.com/your-username/ai-poster-generator.git
cd ai-poster-generator
```

### 2. Install Dependencies

Make sure you are using Python 3.10+ (recommended: 3.10 or 3.11).


```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, manually install:

```bash
pip install gradio diffusers torch pillow
```

### 3. (Optional) Set Hugging Face Token

To use the `prompthero/openjourney` model, set your Hugging Face token:

```bash
export HF_TOKEN=your_huggingface_token_here  # For Linux/macOS
set HF_TOKEN=your_huggingface_token_here     # For Windows CMD
$env:HF_TOKEN="your_huggingface_token_here"  # For PowerShell
```

### 4. Run the App

```bash
version1-2.py
```

It will open a Gradio interface locally. You can also share it with others using the `share=True` flag.

---

## 🖼 Sample Use Case

- Prompt: `Tech conference poster with futuristic cityscape`
- Subtitle: `Tech Summit 2024`
- Details:  
  ```
  December 15-17, 2024  
  Convention Center  
  Register: techsummit.com
  ```

Output: A high-quality AI-generated poster image with your event branding and layout.

---

## 🧱 Tech Stack

- 🧠 [Stable Diffusion (OpenJourney)](https://huggingface.co/prompthero/openjourney)
- 🎨 [Gradio](https://www.gradio.app/) for user interface
- 🐍 Python (3.10+)
- 🔧 `PIL` (Pillow) for image manipulation
- 🖼 `diffusers` and `torch` for AI image generation

---

## 📁 File Structure

```
.
├── e.py                # Main app code
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies (recommended to add)
└── assets/             # Optional: Add example logos or sample outputs
```

---

## 📌 Future Improvements

- Add dark/light theme toggle
- Support downloading posters directly
- Enable text font and color customization
- Add multiple logo positioning options

---

## 🤝 License

MIT License – feel free to use, modify, and share.

---

## 🧠 Acknowledgments

- [PromptHero's OpenJourney](https://huggingface.co/prompthero/openjourney)
- [Gradio UI](https://www.gradio.app/)
- Hugging Face `diffusers` and community
