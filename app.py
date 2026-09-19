from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse
import vtracer
import os
import uuid

app = FastAPI(title="Robô Vetorizador Estável")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor do robô vetorizador está pronto!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    input_path = f"input_{unique_id}.png"
    output_path = f"output_{unique_id}.svg"
    
    try:
        # Lê e grava a imagem recebida
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Comando leve e otimizado para o processador do plano gratuito
        vtracer.convert_image_to_svg_py(input_path, output_path)
        
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                svg_data = f.read()
            
            # Devolve o arquivo forçando o navegador a abrir o botão de download
            return Response(
                content=svg_data,
                media_type="image/svg+xml",
                headers={
                    "Content-Disposition": "attachment; filename=vetor_corel.svg",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        else:
            return JSONResponse(status_code=500, content={"erro": "O arquivo final não foi encontrado no servidor."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": f"Erro interno: {str(e)}"})
        
    finally:
        # Garante a limpeza dos arquivos para não estourar o limite gratuito
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
