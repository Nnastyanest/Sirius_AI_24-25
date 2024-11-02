import os
os.environ["CUDA_VISIBLE_DEVICES"]="1"

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import PlainTextResponse
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

import shutil
from func import generate_latex_document
import torch


app = FastAPI()
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
whisper_model = AutoModelForSpeechSeq2Seq.from_pretrained(
    "openai/whisper-large-v3", torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
whisper_model.to(device)
processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")
pipe = pipeline(
    "automatic-speech-recognition",
    model=whisper_model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    device=device,
)

@app.post("/process/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploaded_files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    text = ""

    if file.filename.endswith('.txt'):
        with open(file_location, 'r', encoding='utf-8') as f:
            text = f.read()

    elif file.filename.endswith('.mp3'):
        pipe("/home/nastya/sites/server/" + file_location)
        print(text)

    elif file.filename.endswith('.mp4'):
        text = pipe(file_location)

    else:
        return PlainTextResponse("Unsupported file format.", status_code=400)

    latex_document = generate_latex_document(text, "gigachat")
    latex_file_path = f"{file.filename}.tex"
    with open(latex_file_path, "w", encoding="utf-8") as f:
        f.write(latex_document)

    return FileResponse(latex_file_path, media_type='text/x-tex', filename="document.tex")
