import gradio as gr
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

class SimplePosterGenerator:
    def __init__(self):
        self.pipe = None
        self.load_model()

    def load_model(self):
        try:
            torch.cuda.empty_cache()
            model_id = "prompthero/openjourney"
            token = os.getenv("HF_TOKEN")
            if token:
                print("🔐 Using Hugging Face token for model loading.")

            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None,
                requires_safety_checker=False,
                use_auth_token=token
            )

            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)

            if torch.cuda.is_available():
                self.pipe = self.pipe.to("cuda")
                print("✅ Model loaded on GPU")
            else:
                self.pipe = self.pipe.to("cpu")
                print("✅ Model loaded on CPU")

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.pipe = None

    def get_font(self, size):
        try:
            system_fonts = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
            for font_file in system_fonts:
                try:
                    return ImageFont.truetype(font_file, size)
                except:
                    continue
            return ImageFont.load_default()
        except Exception as e:
            print(f"Font loading error: {e}")
            return ImageFont.load_default()

    def process_logo(self, logo_image, max_size=200):
        if logo_image is None:
            return None
        try:
            logo = logo_image.copy()
            logo.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            return logo
        except Exception as e:
            print(f"Logo processing error: {e}")
            return None

    def create_background(self, prompt, width=1024, height=1024):
        if not self.pipe:
            return self.create_fallback_background(width, height)

        full_prompt = f"{prompt}, poster design, concept art, trending on artstation, sharp, 4k"
        try:
            image = self.pipe(
                full_prompt,
                negative_prompt="blurry, distorted, bad anatomy, low quality",
                width=width,
                height=height,
                num_inference_steps=35,
                guidance_scale=7.5
            ).images[0]
            return image
        except Exception as e:
            print(f"Background generation error: {e}")
            return self.create_fallback_background(width, height)

    def create_fallback_background(self, width, height):
        colors = [(100, 150, 255), (150, 200, 255)]
        return self.create_gradient_background(width, height, colors[0], colors[1])

    def create_gradient_background(self, width, height, color1, color2):
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        return image

    def apply_text_layout(self, image, subtitle, details, logo=None):
        poster = image.copy().convert('RGBA')
        width, height = poster.size
        overlay = Image.new('RGBA', poster.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        color_overlay = Image.new('RGBA', poster.size, (0, 0, 0, 80))
        poster = Image.alpha_composite(poster, color_overlay)

        base_size = min(width, height) // 15
        subtitle_size = int(base_size * 0.8)
        details_size = int(base_size * 0.5)

        subtitle_font = self.get_font(subtitle_size)
        details_font = self.get_font(details_size)

        y_pos = height // 3
        spacing = 60

        if subtitle:
            self.draw_text_with_outline(draw, subtitle, width//2, y_pos, subtitle_font, 'white', 'black', center=True)
            y_pos += spacing * 2

        if details:
            for line in details.split('\n'):
                if line.strip():
                    self.draw_text_with_outline(draw, line.strip(), width//2, y_pos, details_font, 'lightgray', 'black', center=True)
                    y_pos += spacing // 2

        if logo:
            logo_pos = (width - logo.size[0] - 50, 50)
            poster.paste(logo, logo_pos, logo)

        poster = Image.alpha_composite(poster, overlay)
        return poster.convert('RGB')

    def draw_text_with_outline(self, draw, text, x, y, font, fill_color, outline_color, center=False):
        if center:
            bbox = draw.textbbox((0, 0), text, font=font)
            x = x - (bbox[2] - bbox[0]) // 2
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill_color)

poster_gen = SimplePosterGenerator()

def generate_simple_poster(prompt, subtitle, details, logo_image, aspect_ratio):
    aspect_ratios = {
        "1:1 - Square": (1024, 1024),
        "2:3 - Portrait": (683, 1024),
        "3:2 - Landscape": (1024, 683),
        "3:4 - Poster": (768, 1024),
        "16:9 - Widescreen": (1024, 576)
    }
    width, height = aspect_ratios.get(aspect_ratio, (1024, 1024))
    background = poster_gen.create_background(prompt, width, height)
    processed_logo = poster_gen.process_logo(logo_image)
    final_poster = poster_gen.apply_text_layout(background, subtitle, details, processed_logo)
    return final_poster

def create_simple_interface():
    with gr.Blocks(title="🎨 Simple AI Poster Generator", theme=gr.themes.Glass()) as demo:
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 3em; background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        background-clip: text; margin-bottom: 10px;">
                🎨 Simple AI Poster Generator
            </h1>
            <p style="font-size: 1.2em; color: #666;">
                Create stunning posters with the OpenJourney fine-tuned model!
            </p>
        </div>
        """)
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### 🎯 *Poster Description*")
                    prompt_input = gr.Textbox(
                        label="Describe your poster",
                        value="Tech conference poster with futuristic cityscape",
                        lines=3
                    )

                with gr.Group():
                    gr.Markdown("### 📝 *Text Content*")
                    subtitle_input = gr.Textbox(label="Subtitle", value="Tech Summit 2024")
                    details_input = gr.Textbox(
                        label="Details",
                        value="December 15-17, 2024\nConvention Center\nRegister: techsummit.com",
                        lines=4
                    )

                with gr.Group():
                    gr.Markdown("### 🖼 *Optional Logo*")
                    logo_upload = gr.Image(label="Upload Logo (Optional)", type="pil", height=150)

                with gr.Group():
                    gr.Markdown("### 📐 *Output Settings*")
                    aspect_ratio_radio = gr.Radio(
                        choices=["1:1 - Square", "2:3 - Portrait", "3:2 - Landscape", "3:4 - Poster", "16:9 - Widescreen"],
                        value="3:4 - Poster",
                        label="Aspect Ratio"
                    )
                    generate_btn = gr.Button("🚀 Generate Poster", variant="primary", size="lg")

            with gr.Column(scale=2):
                gr.Markdown("### ✨ *Generated Poster*")
                output_image = gr.Image(label="Your AI-Generated Poster", type="pil", interactive=False)

        generate_btn.click(
            generate_simple_poster,
            inputs=[prompt_input, subtitle_input, details_input, logo_upload, aspect_ratio_radio],
            outputs=[output_image]
        )

    return demo

if __name__ == "__main__":
    demo = create_simple_interface()
    demo.launch(share=True, debug=True)
