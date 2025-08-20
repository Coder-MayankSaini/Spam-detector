# OCR Setup Guide

This guide helps you set up Tesseract OCR for image-based spam detection functionality.

## Windows Installation

### Method 1: Using Windows Installer (Recommended)

1. **Download Tesseract for Windows:**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer as Administrator
   - **Important:** During installation, make sure to check "Add to PATH"
   - Choose installation directory (default: `C:\Program Files\Tesseract-OCR`)

3. **Verify Installation:**
   ```powershell
   tesseract --version
   ```
   You should see version information if installed correctly.

### Method 2: Using Chocolatey

```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Tesseract
choco install tesseract
```

### Method 3: Using Scoop

```powershell
# Install Scoop if not already installed
iwr -useb get.scoop.sh | iex

# Install Tesseract
scoop install tesseract
```

## Configuration

### Environment Variables

If Tesseract is not automatically detected, you may need to set the path manually:

```python
# Add this to your app.py if needed
import os
os.environ['TESSERACT_CMD'] = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Language Packs

For better OCR accuracy, you can install additional language packs:

1. Download language files from: https://github.com/tesseract-ocr/tessdata
2. Place them in: `C:\Program Files\Tesseract-OCR\tessdata`
3. Common files:
   - `eng.traineddata` (English - usually included)
   - `spa.traineddata` (Spanish)
   - `fra.traineddata` (French)

## Testing OCR Installation

Create a test script to verify OCR is working:

```python
import pytesseract
from PIL import Image
import requests
from io import BytesIO

# Test with a simple image
try:
    # Create a simple test image with text
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (300, 100), color='white')
    d = ImageDraw.Draw(img)
    d.text((10, 40), "URGENT: Win $1000!", fill='black')
    
    # Extract text
    text = pytesseract.image_to_string(img)
    print(f"Extracted text: '{text.strip()}'")
    
    if text.strip():
        print("✅ OCR is working correctly!")
    else:
        print("❌ OCR extracted no text")
        
except Exception as e:
    print(f"❌ OCR Error: {e}")
```

## Troubleshooting

### Common Issues

#### 1. "TesseractNotFoundError"
**Solution:** Tesseract is not installed or not in PATH
- Reinstall Tesseract with "Add to PATH" option
- Or manually add to PATH: `C:\Program Files\Tesseract-OCR`

#### 2. "Permission Denied"
**Solution:** Run as Administrator or check file permissions

#### 3. Poor OCR Accuracy
**Solutions:**
- Ensure images are high resolution (300+ DPI)
- Use high contrast images (black text on white background)
- Avoid skewed or rotated text
- Use clear, sans-serif fonts when possible

#### 4. "Failed to load library"
**Solution:** 
- Check if Visual C++ Redistributables are installed
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Testing with Sample Images

You can test the OCR functionality with sample spam email screenshots:

1. Create a screenshot of a spam email
2. Use the web interface to upload and analyze
3. Check the OCR extraction quality in the result

### Performance Optimization

For better OCR performance:

```python
# Add these settings to improve OCR accuracy
pytesseract_config = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*(),.?":{}|<> '
```

## Advanced Configuration

### Custom OCR Models

For specialized email formats, you can train custom Tesseract models:

1. Collect training images
2. Create ground truth text files
3. Use `tesstrain` to create custom models
4. Place in tessdata directory

### Docker Alternative

If you prefer Docker:

```dockerfile
FROM python:3.9
RUN apt-get update && apt-get install -y tesseract-ocr
COPY requirements.txt .
RUN pip install -r requirements.txt
# ... rest of your Dockerfile
```

## Verification Checklist

- [ ] Tesseract installed and in PATH
- [ ] Python packages installed (`pytesseract`, `pillow`, `opencv-python`)
- [ ] Test script runs successfully
- [ ] Web interface shows "Image Analysis" tab
- [ ] Can upload and analyze sample images
- [ ] OCR extracts text correctly from test images

## Getting Help

If you encounter issues:

1. Check the error logs in the Flask application
2. Verify Tesseract installation: `tesseract --version`
3. Test with simple black-and-white text images first
4. Check GitHub issues for tesseract-ocr and pytesseract projects

---

*Note: OCR accuracy depends on image quality. For best results, use clear, high-contrast images with readable text.*
