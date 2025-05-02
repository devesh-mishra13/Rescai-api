from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import io
import whisper

app = FastAPI()

# Load Whisper model once on startup
model = whisper.load_model("tiny")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI OCR/Audio/PDF API is running!"}

@app.post("/extract-text/")
async def extract_text_from_image(file: UploadFile = File(...)):
    try:
        img_data = await file.read()
        img = Image.open(io.BytesIO(img_data))
        custom_config = r'--psm 11'
        extracted_text = pytesseract.image_to_string(img, config=custom_config)
        cleaned_text = "\n".join([line.strip() for line in extracted_text.splitlines() if line.strip()])
        return JSONResponse(content={"extracted_text": cleaned_text})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/pdfextract-text/")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")
    try:
        pdf_content = await file.read()
        reader = PdfReader(io.BytesIO(pdf_content))
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()
        return {"extracted_text": extracted_text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/audioextract-text/")
async def extract_text_from_audio(file: UploadFile = File(...)):
    try:
        with open("temp_audio.mp3", "wb") as audio_file:
            audio_file.write(await file.read())
        result = model.transcribe("temp_audio.mp3")
        return JSONResponse(content={"extracted_text": result["text"]})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
