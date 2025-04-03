"""
PDF Processor utility for extracting, chunking, summarizing, and generating PDFs.
This module provides standalone utilities for PDF processing operations.
"""

import os
import logging
import tempfile
from typing import List, Dict, Any, Union, Optional, Tuple
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Utility class for PDF processing operations.
    
    Provides functionality for:
    - Text extraction from PDFs
    - Text chunking with configurable size and overlap
    - Content summarization
    - PDF generation
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        logger.info("PDF Processor initialized")
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            from PyPDF2 import PdfReader
            
            with open(pdf_file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                total_pages = len(reader.pages)
                logger.info(f"Extracting text from PDF with {total_pages} pages")
                
                for i, page in enumerate(reader.pages):
                    # Log progress for large PDFs
                    if i % 10 == 0 and total_pages > 20:
                        logger.info(f"Extracting page {i+1}/{total_pages}")
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            logger.info(f"Extracted {len(text)} characters from PDF: {pdf_file_path}")
            return text
            
        except Exception as e:
            error_msg = f"Error extracting text from PDF: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks with optional overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        logger.info(f"Chunking text of length {text_length} with chunk_size={chunk_size}, overlap={overlap}")
        
        while start < text_length:
            # Calculate end of chunk (respecting chunk_size)
            end = min(start + chunk_size, text_length)
            
            # If not at the end of text and not at a sentence boundary, try to find a good break point
            if end < text_length:
                # Try to find sentence boundary (period followed by space or newline)
                sentence_end = text.rfind('. ', start, end)
                if sentence_end > start:
                    end = sentence_end + 1  # Include the period
                else:
                    # Try to find paragraph boundary
                    para_end = text.rfind('\n\n', start, end)
                    if para_end > start:
                        end = para_end + 2  # Include the newlines
                    else:
                        # Try to find line break
                        line_end = text.rfind('\n', start, end)
                        if line_end > start:
                            end = line_end + 1  # Include the newline
            
            # Add the chunk to our list
            chunks.append(text[start:end])
            
            # Calculate next start position (with overlap)
            start = end - overlap if end < text_length else text_length
            
            # Ensure we don't get stuck in an infinite loop
            if start >= end:
                break
        
        logger.info(f"Created {len(chunks)} chunks from text of length {text_length}")
        return chunks
    
    def generate_pdf(self, text: str, output_path: str, title: Optional[str] = None) -> str:
        """
        Generate a PDF from text.
        
        Args:
            text: Text content for the PDF
            output_path: Path where to save the generated PDF
            title: Optional title for the PDF
            
        Returns:
            Path to the generated PDF
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib import colors
            
            # Create custom styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=24
            )
            normal_style = styles["Normal"]
            heading_style = styles["Heading2"]
            
            # Create document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Add title if provided
            if title:
                story.append(Paragraph(title, title_style))
                story.append(Spacer(1, 12))
            
            # Split text into paragraphs
            paragraphs = text.split('\n\n')
            
            # Add each paragraph to the document
            for para in paragraphs:
                if para.strip():
                    # Check if it might be a heading (short, ends with no period)
                    if len(para.strip()) < 100 and not para.strip().endswith('.'):
                        story.append(Paragraph(para, heading_style))
                    else:
                        story.append(Paragraph(para, normal_style))
                    story.append(Spacer(1, 12))
            
            # Build the document
            doc.build(story)
            
            logger.info(f"Generated PDF at: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Error generating PDF: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_unique_output_path(self, output_dir: str, prefix: str = "output", extension: str = "pdf") -> str:
        """
        Generate a unique file path for output files.
        
        Args:
            output_dir: Directory for output files
            prefix: Prefix for the filename
            extension: File extension
            
        Returns:
            Unique file path
        """
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{prefix}_{uuid.uuid4().hex}.{extension}"
        return os.path.join(output_dir, filename)
