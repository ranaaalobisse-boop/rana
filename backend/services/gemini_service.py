import os
import base64
import google.generativeai as genai
from PIL import Image
import io
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiService:
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
        else:
            self.model = None
    
    def generate_jewelry_design(
        self,
        jewelry_type: str,
        color: str,
        shape: str,
        material: str,
        karat: str,
        gemstone_type: str,
        gemstone_color: str
    ) -> Optional[bytes]:
        """
        Generate a jewelry design using Google Gemini API
        Returns the image bytes or None if generation fails
        """
        if not self.model:
            raise ValueError("Gemini API key not configured")
        
        prompt = self._construct_prompt(
            jewelry_type, color, shape, material, 
            karat, gemstone_type, gemstone_color
        )
        
        try:
            response = self.model.generate_content(prompt)
            
            # Try to get image from response
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = part.inline_data.data
                            return base64.b64decode(image_data)
                        elif hasattr(part, 'text') and part.text:
                            # If text response, we might need to extract image URL or handle differently
                            print(f"Text response: {part.text}")
            
            # Alternative: Check if response has image bytes directly
            if hasattr(response, 'image_bytes') and response.image_bytes:
                return response.image_bytes
            
            return None
            
        except Exception as e:
            print(f"Error generating image with Gemini: {e}")
            return None
    
    def _construct_prompt(
        self,
        jewelry_type: str,
        color: str,
        shape: str,
        material: str,
        karat: str,
        gemstone_type: str,
        gemstone_color: str
    ) -> str:
        """
        Construct a detailed prompt for the AI image generator
        """
        gemstone_desc = ""
        if gemstone_type and gemstone_type.lower() != "none":
            gemstone_desc = f" featuring a stunning {gemstone_color} {gemstone_type} gemstone"
        
        prompt = f"""Create a professional, high-quality product photograph of a luxury {jewelry_type} jewelry piece.

Specifications:
- Material: {material} ({karat})
- Color Tone: {color}
- Shape: {shape}{gemstone_desc}

Style Requirements:
- Elegant, luxurious, and high-end jewelry photography style
- Clean white or soft gradient background
- Professional studio lighting with soft reflections
- Photorealistic, 4K quality, highly detailed
- Focus on the craftsmanship and shine of the metal
- The piece should be centered and shown from the best angle
- Macro photography style with shallow depth of field
- Product photography suitable for luxury e-commerce website

The image should look like a professional jewelry catalog photo that would be displayed on a high-end luxury jewelry website like Tiffany's or Cartier.
"""
        return prompt
    
    def save_image(self, image_bytes: bytes, filename: str, output_dir: str = "static/generated_designs") -> str:
        """
        Save the generated image to the filesystem
        Returns the relative path to the saved image
        """
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return filepath

# Singleton instance
gemini_service = GeminiService()
