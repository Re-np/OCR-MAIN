# OCR Text Extractor

A FastHTML web application that uses Google's Gemini AI to extract text from uploaded images and PDF files.

## Features

- **Image OCR**: Extract text from PNG, JPG, JPEG, GIF, BMP, and WEBP images
- **PDF Processing**: Extract text from PDF files using both direct text extraction and OCR for scanned pages
- **Modern UI**: Clean, responsive web interface with drag-and-drop file upload
- **Real-time Processing**: Instant text extraction with loading indicators
- **Copy to Clipboard**: Easy text copying functionality

## Prerequisites

- Python 3.11+
- Google Gemini API key (already configured in the application)

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5001`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t ocr-app .
```

2. Run the container:
```bash
docker run -p 5001:5001 ocr-app
```

3. Open your browser and navigate to `http://localhost:5001`

## Usage

1. **Upload Files**: Drag and drop files onto the upload area or click to browse
2. **Supported Formats**: 
   - Images: PNG, JPG, JPEG, GIF, BMP, WEBP
   - Documents: PDF
3. **Extract Text**: Click "Extract Text" to process the file
4. **Copy Results**: Use the "Copy Text" button to copy extracted text to clipboard

## API Endpoints

- `GET /`: Main application interface
- `POST /upload`: File upload endpoint for OCR processing

## Technical Details

- **Framework**: FastHTML for lightweight web serving
- **OCR Engine**: Google Gemini 1.5 Flash Vision API
- **PDF Processing**: PyMuPDF for PDF text extraction and image conversion
- **Image Processing**: Pillow for image manipulation
- **Containerization**: Docker with Python 3.11 slim base image

## File Structure

```
ocr/
├── app.py              # Main FastHTML application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md          # This file
```

## Error Handling

The application includes comprehensive error handling for:
- Unsupported file formats
- API rate limits
- Network connectivity issues
- File processing errors

## Security Notes

- The Gemini API key is hardcoded for demonstration purposes
- In production, use environment variables for API keys
- Consider implementing file size limits and validation
