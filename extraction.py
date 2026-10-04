"""
extraction.py - Extração de conteúdo de PDFs e imagens

Suporta: pdfplumber (nativo), Tesseract (OCR fallback), Google Vision, AWS Textract
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

import pdfplumber
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURAÇÃO ===
OCR_PROVIDER = os.getenv("OCR_PROVIDER", "tesseract").lower()
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")


# === OCR STRATEGIES ===
class OCRStrategy(ABC):
    """Interface para diferentes provedores de OCR"""
    
    @abstractmethod
    def extract_from_image(self, image_path: str) -> str:
        """Extrair texto de imagem"""
        pass


class TesseractOCR(OCRStrategy):
    """OCR usando Tesseract (local)"""
    
    def extract_from_image(self, image_path: str) -> str:
        """Extrair com Tesseract"""
        try:
            import pytesseract
            img = Image.open(image_path)
            return pytesseract.image_to_string(img, lang="por+eng")
        except Exception as e:
            print(f"⚠️ Tesseract error: {e}")
            return ""


class GoogleVisionOCR(OCRStrategy):
    """OCR usando Google Cloud Vision"""
    
    def __init__(self):
        try:
            from google.cloud import vision
            self.client = vision.ImageAnnotatorClient()
        except ImportError:
            raise ImportError("google-cloud-vision não instalado")
    
    def extract_from_image(self, image_path: str) -> str:
        """Extrair com Google Vision"""
        try:
            from google.cloud import vision
            with open(image_path, "rb") as f:
                content = f.read()
            image = vision.Image(content=content)
            response = self.client.document_text_detection(image=image)
            return response.full_text_annotation.text
        except Exception as e:
            print(f"⚠️ Google Vision error: {e}")
            return ""


class AWSTextractOCR(OCRStrategy):
    """OCR usando AWS Textract"""
    
    def __init__(self):
        try:
            import boto3
            self.client = boto3.client("textract",
                region_name=os.getenv("AWS_REGION", "us-east-1"))
        except ImportError:
            raise ImportError("boto3 não instalado")
    
    def extract_from_image(self, image_path: str) -> str:
        """Extrair com AWS Textract"""
        try:
            with open(image_path, "rb") as f:
                response = self.client.detect_document_text(Document={"Bytes": f.read()})
            text = ""
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    text += item.get("Text", "") + "\n"
            return text
        except Exception as e:
            print(f"⚠️ AWS Textract error: {e}")
            return ""


def get_ocr_strategy() -> OCRStrategy:
    """Factory para seleção de estratégia OCR"""
    provider = OCR_PROVIDER.lower()
    
    if provider == "tesseract":
        return TesseractOCR()
    elif provider == "google_vision":
        return GoogleVisionOCR()
    elif provider == "aws_textract":
        return AWSTextractOCR()
    else:
        print(f"⚠️ OCR provider '{provider}' não reconhecido, usando Tesseract")
        return TesseractOCR()


# === EXTRACTION CORE ===
class PolicyExtractor:
    """Extrator de conteúdo de apólices (PDF/Imagem)"""
    
    def __init__(self):
        self.ocr = get_ocr_strategy()
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extrair texto de PDF usando pdfplumber"""
        result = {
            "text": "",
            "metadata": {},
            "pages": 0,
            "success": False
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result["pages"] = len(pdf.pages)
                result["metadata"] = pdf.metadata or {}
                
                # Extrair texto de cada página
                texts = []
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        texts.append(f"--- PÁGINA {i} ---\n{text}")
                
                result["text"] = "\n\n".join(texts)
                result["success"] = len(result["text"]) > 50
                
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ PDF extraction error: {e}")
        
        return result
    
    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extrair texto de imagem usando OCR"""
        result = {
            "text": "",
            "metadata": {},
            "success": False
        }
        
        try:
            img = Image.open(image_path)
            result["metadata"] = {
                "size": img.size,
                "format": img.format,
                "mode": img.mode
            }
            
            result["text"] = self.ocr.extract_from_image(image_path)
            result["success"] = len(result["text"]) > 50
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Image extraction error: {e}")
        
        return result
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """Extrair texto de arquivo (PDF ou Imagem)"""
        file_path = str(file_path)
        extension = Path(file_path).suffix.lower()
        
        if extension == ".pdf":
            return self.extract_from_pdf(file_path)
        elif extension in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]:
            return self.extract_from_image(file_path)
        else:
            return {
                "text": "",
                "error": f"Formato não suportado: {extension}",
                "success": False
            }
    
    @staticmethod
    def compute_hash(file_path: str) -> str:
        """Computar hash SHA256 do arquivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


if __name__ == "__main__":
    # Test
    extractor = PolicyExtractor()
    
    # Testar com PDF de exemplo (se existir)
    test_pdf = "data/exemplo_apolice.pdf"
    if Path(test_pdf).exists():
        result = extractor.extract(test_pdf)
        print(f"✓ Extracted {len(result['text'])} chars")
        print(f"  Pages: {result['pages']}")
        print(f"  Hash: {extractor.compute_hash(test_pdf)}")
