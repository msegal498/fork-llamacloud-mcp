"""
Shared LlamaCloud client implementation for PDF chunking system.
This module handles core LlamaCloud API interaction and PDF processing methods.
"""

import os
import logging
import tempfile
from typing import List, Dict, Any, Union, Optional, Tuple
from dotenv import load_dotenv
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.llms.openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SharedLlamaClient:
    """
    Shared client for interacting with LlamaCloud and processing PDFs.
    
    This client provides core functionality for:
    - LlamaCloud interaction
    - PDF text extraction
    - Text chunking
    - Summarization
    """
    
    def __init__(self, load_env_path: Optional[str] = None):
        """
        Initialize the shared client.
        
        Args:
            load_env_path: Optional path to .env file for configuration
        """
        # Load environment variables
        if load_env_path:
            load_dotenv(dotenv_path=load_env_path)
        else:
            load_dotenv()
            
        # Get LlamaCloud config from environment variables
        self.index_name = os.getenv("LLAMA_CLOUD_INDEX_NAME")
        self.project_name = os.getenv("LLAMA_CLOUD_PROJECT_NAME")
        self.org_id = os.getenv("LLAMA_CLOUD_ORG_ID")
        self.api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate required environment variables
        if not all([self.index_name, self.project_name, self.org_id, self.api_key]):
            logger.warning("Missing required LlamaCloud configuration. Some functions may not work.")
            
        if not self.openai_api_key:
            logger.warning("Missing OpenAI API key. Summarization may not work.")
        
        # Initialize LLM and Index as None, will be lazily loaded when needed
        self._llm = None
        self._index = None
        
        logger.info("Shared LlamaClient initialized")
    
    @property
    def llm(self):
        """Lazy-load the LLM when needed"""
        if self._llm is None and self.openai_api_key:
            try:
                self._llm = OpenAI(api_key=self.openai_api_key)
                logger.info("LLM initialized")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
        return self._llm
    
    @property
    def index(self):
        """Lazy-load the LlamaCloud index when needed"""
        if self._index is None and all([self.index_name, self.project_name, self.org_id, self.api_key]):
            try:
                self._index = LlamaCloudIndex(
                    name=self.index_name,
                    project_name=self.project_name,
                    organization_id=self.org_id,
                    api_key=self.api_key,
                )
                logger.info(f"LlamaCloud index initialized: {self.index_name}")
            except Exception as e:
                logger.error(f"Failed to initialize LlamaCloud index: {str(e)}")
        return self._index
    
    def query_documentation(self, query: str) -> str:
        """
        Query the LlamaCloud documentation index.
        
        Args:
            query: The query string
            
        Returns:
            Response as a string
        """
        try:
            if not self.index:
                return "Error: LlamaCloud index not initialized"
            
            logger.info(f"Querying LlamaCloud index: {self.index_name}")
            response = self.index.as_query_engine().query(query)
            
            return str(response)
            
        except Exception as e:
            error_msg = f"Error querying LlamaCloud: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
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
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            
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
            
            # Add the chunk to our list
            chunks.append(text[start:end])
            
            # Calculate next start position (with overlap)
            start = end - overlap if end < text_length else text_length
            
            # Ensure we don't get stuck in an infinite loop
            if start >= end:
                break
        
        logger.info(f"Created {len(chunks)} chunks from text of length {text_length}")
        return chunks
    
    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """
        Summarize text using LLM.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        try:
            if not self.llm:
                # Fallback to basic summarization if no LLM is available
                logger.warning("LLM not initialized, using fallback summarization")
                # Simple fallback: extract first few sentences
                sentences = text.split('.')
                summary_sentences = [s.strip() for s in sentences[:5] if s.strip()]
                summary = '. '.join(summary_sentences)
                if len(summary) > max_length:
                    summary = summary[:max_length-3] + '...'
                return summary
            
            prompt = f"""
            Please summarize the following text in a concise way, highlighting the key points.
            Keep the summary under {max_length} characters.
            
            TEXT:
            {text}
            
            SUMMARY:
            """
            
            response = self.llm.complete(prompt)
            summary = response.text.strip()
            
            logger.info(f"Summarized text of length {len(text)} to {len(summary)} characters")
            return summary
            
        except Exception as e:
            error_msg = f"Error summarizing text: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def generate_pdf(self, text: str, output_path: str) -> str:
        """
        Generate a PDF from text.
        
        Args:
            text: Text content for the PDF
            output_path: Path where to save the generated PDF
            
        Returns:
            Path to the generated PDF
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Split text into paragraphs
            paragraphs = text.split('\n\n')
            
            # Add each paragraph to the document
            for para in paragraphs:
                if para.strip():
                    p = Paragraph(para, styles["Normal"])
                    story.append(p)
                    story.append(Spacer(1, 12))
            
            # Build the document
            doc.build(story)
            
            logger.info(f"Generated PDF at: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Error generating PDF: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def process_pdf(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a PDF file: extract text, chunk it, summarize, and generate a new PDF.
        
        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory for output files (optional)
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Create temporary directory if output_dir not provided
            temp_dir = None
            if not output_dir:
                temp_dir = tempfile.TemporaryDirectory()
                output_dir = temp_dir.name
            
            # Extract text from PDF
            extracted_text = self.extract_text_from_pdf(pdf_path)
            
            # Chunk the text
            chunks = self.chunk_text(extracted_text)
            
            # Summarize each chunk
            summaries = []
            for i, chunk in enumerate(chunks):
                summary = self.summarize_text(chunk)
                summaries.append(summary)
            
            # Create a combined summary
            combined_summary = "\n\n".join(summaries)
            
            # Generate summary PDF
            summary_pdf_path = os.path.join(output_dir, "summary.pdf")
            self.generate_pdf(combined_summary, summary_pdf_path)
            
            # Clean up temp directory if we created one
            if temp_dir:
                temp_dir.cleanup()
            
            return {
                "input_pdf": pdf_path,
                "extracted_text_length": len(extracted_text),
                "num_chunks": len(chunks),
                "summary_length": len(combined_summary),
                "output_pdf": summary_pdf_path
            }
            
        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)