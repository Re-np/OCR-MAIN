from fasthtml.common import *
from google import genai
from google.genai import types
import os
import base64
import io
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import tempfile

# Create FastHTML app and route decorator
app, rt = fast_app()

# Create Gemini client
client = genai.Client(api_key="AIzaSyB-ssyREcxmGX8KnV9JbxfEZLh6xhXC7-k")

def extract_text_from_image(image_data):
    """Extract text from image using Gemini Vision API"""
    try:
        # Convert image data to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Create the prompt for OCR
        prompt = "Extract all text from this image. Return only the text content, maintaining the original formatting and structure."
        
        # Generate content using Gemini Vision with the client
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, image]
        )
        
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def extract_text_from_pdf(pdf_data):
    """Extract text from PDF using PyMuPDF and Gemini Vision for images"""
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        extracted_text = ""
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # First try to extract text directly
            text = page.get_text()
            if text.strip():
                extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            else:
                # If no text found, convert page to image and use OCR
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                ocr_text = extract_text_from_image(img_data)
                extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}\n"
        
        pdf_document.close()
        return extracted_text
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def process_uploaded_file(file_data, filename):
    """Process uploaded file and extract text"""
    file_extension = filename.lower().split('.')[-1]
    
    if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
        return extract_text_from_image(file_data)
    elif file_extension == 'pdf':
        return extract_text_from_pdf(file_data)
    else:
        return f"Unsupported file type: {file_extension}"

# FastHTML routes
@rt("/")
def index():
    return Titled("OCR Text Extractor",
        Div(
            H1("🔍 OCR Text Extractor"),
            P("Upload images or PDF files to extract text using Google Gemini AI", 
              style="text-align: center; color: #666; margin-bottom: 30px;"),
            
            Form(
                Div(
                    P("📁 Drag and drop files here or click to browse"),
                    Input(type="file", id="fileInput", name="file", 
                          accept=".png,.jpg,.jpeg,.gif,.bmp,.webp,.pdf", required=True,
                          style="margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; width: 100%;"),
                    P("Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP, PDF",
                      style="color: #666; font-size: 14px; margin-top: 10px;"),
                    id="uploadArea",
                    style="border: 2px dashed #ddd; border-radius: 10px; padding: 40px; text-align: center; margin-bottom: 20px; transition: border-color 0.3s;"
                ),
                Button("Extract Text", type="submit", id="submitBtn",
                       style="background-color: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px;"),
                id="uploadForm",
                enctype="multipart/form-data"
            ),
            
            Div(id="result", style="display: none; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff;"),
            
            style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;"
        ),
        
        Style("""
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .upload-area:hover { border-color: #007bff; }
            .upload-area.dragover { border-color: #007bff; background-color: #f8f9fa; }
            button:hover { background-color: #0056b3; }
            button:disabled { background-color: #6c757d; cursor: not-allowed; }
            .loading { text-align: center; color: #007bff; font-style: italic; }
            .error { color: #dc3545; background-color: #f8d7da; border-color: #f5c6cb; }
            .success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
            .text-output { white-space: pre-wrap; font-family: 'Courier New', monospace; background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; max-height: 400px; overflow-y: auto; }
        """),
        
        Script("""
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const form = document.getElementById('uploadForm');
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');

            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                }
            });

            uploadArea.addEventListener('click', (e) => {
                // Only trigger if clicking on the upload area itself, not on child elements
                if (e.target === uploadArea) {
                    fileInput.click();
                }
            });

            // Form submission
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const file = fileInput.files[0];
                if (!file) {
                    showResult('Please select a file to upload.', 'error');
                    return;
                }

                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                showResult('Processing file, please wait...', 'loading');

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.text();
                    
                    if (response.ok) {
                        showResult(result, 'success');
                    } else {
                        showResult(`Error: ${result}`, 'error');
                    }
                } catch (error) {
                    showResult(`Error: ${error.message}`, 'error');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Extract Text';
                }
            });

            function showResult(text, type) {
                resultDiv.style.display = 'block';
                resultDiv.className = `result ${type}`;
                
                if (type === 'success') {
                    resultDiv.innerHTML = `
                        <h3>✅ Text Extracted Successfully</h3>
                        <div class="text-output">${text}</div>
                        <button onclick="copyToClipboard()" style="margin-top: 10px; width: auto; padding: 8px 16px;">Copy Text</button>
                    `;
                } else {
                    resultDiv.innerHTML = `<p>${text}</p>`;
                }
            }

            function copyToClipboard() {
                const textOutput = document.querySelector('.text-output');
                navigator.clipboard.writeText(textOutput.textContent).then(() => {
                    alert('Text copied to clipboard!');
                });
            }
        """)
    )

@rt("/upload", methods=["POST"])
async def upload_file(req):
    try:
        # Get uploaded file from request using Starlette's form handling
        form = await req.form()
        file = form.get('file')
        
        if not file or not hasattr(file, 'filename'):
            return "No file uploaded", 400
        
        # Read file data
        file_data = await file.read()
        filename = file.filename
        
        # Process the file
        extracted_text = process_uploaded_file(file_data, filename)
        
        return extracted_text
        
    except Exception as e:
        return f"Error processing file: {str(e)}", 500

if __name__ == "__main__":
    serve()
