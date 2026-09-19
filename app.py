from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import vtracer
import os

app = FastAPI(title="Robô Vetorizador Gratuito")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor do seu robô vetorizador está funcionando perfeitamente!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    output_path = "resultado.svg"

    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    # Configurações do VTracer otimizadas para o CorelDRAW
    vtracer.convert_image_to_svg(
        input_path,
        output_path,
        mode='spline',       
        colormode='color',   
        hierarchical='stacked', 
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        filter_speckle=4     
    )

    if os.path.exists(input_path):
        os.remove(input_path)

    return FileResponse(output_path, media_type="image/svg+xml", filename="seu_vetor.svg")
