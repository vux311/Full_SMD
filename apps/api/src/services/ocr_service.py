import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """
    Service for digitizing legacy syllabus documents (PDF/Images) using Tesseract OCR.
    """
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
    def extract_text_from_image(self, image_path):
        """Extract text from a single image file."""
        try:
            # Preprocess image for better OCR
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Apply thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Convert back to PIL for pytesseract
            pil_img = Image.fromarray(thresh)
            text = pytesseract.image_to_string(pil_img, lang='vie+eng')
            return text
        except Exception as e:
            logger.error(f"OCR selection error: {e}")
            return f"Error: {str(e)}"

    def extract_text_from_pdf(self, pdf_path):
        """Convert PDF pages to images and extract text from each."""
        try:
            pages = convert_from_path(pdf_path, 300) # 300 DPI
            full_text = ""
            for i, page in enumerate(pages):
                logger.info(f"Processing page {i+1}...")
                text = pytesseract.image_to_string(page, lang='vie+eng')
                full_text += f"\n--- Page {i+1} ---\n" + text
            return full_text
        except Exception as e:
            logger.error(f"PDF OCR error: {e}")
            return f"Error: {str(e)}"

    def process_file(self, file_path):
        """Main entry point to process different file types."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return self.extract_text_from_image(file_path)
        else:
            return f"Unsupported file extension: {ext}"
