from fastapi import FastAPI, File, UploadFile
from typing import List
import json

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    # Пример: обработка содержимого файла (здесь только чтение имени и расширения)
    result = {
        "files": [{
            "name": file.filename.rsplit('.', 1)[0],
            "extension": file.filename.rsplit('.', 1)[-1],
            "content": content.decode('latin1')  # Пример кодировки
        }]
    }
    return result
