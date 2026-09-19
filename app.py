from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse
import vtracer
import os
import uuid

app = FastAPI(title="Robô Vetorizador P&B Definitivo")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor P&B ultra-estável está pronto!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    input_path = f"input_{unique_id}.png"
    output_path = f"output_{unique_id}.svg"
    
    try:
        # Salva a imagem recebida de forma simples
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Executa a vetorização em Preto e Branco (Traço puro e limpo)
        # Usando configurações nativas para preservar o processamento do servidor gratuito
        vtracer.convert_image_to_svg_py(
            input_path, 
            output_path,
            colormode="binary",       # Transforma em Preto e Branco (silhueta/contorno)
            mode="spline",            # Cria curvas suaves e lisas ideais para o CorelDRAW
            filter_speckle=12,         # Ignora pequenas sujeiras e serrilhados da logo
            corner_threshold=60
        )
        
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                svg_data = f.read()
            
            return Response(
                content=svg_data,
                media_type="image/svg+xml",
                headers={"Content-Disposition": "attachment; filename=vetor_final_pb.svg"}
            )
        else:
            return JSONResponse(status_code=500, content={"erro": "Falha ao gerar vetor."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
        
    finally:
        # Limpa os arquivos gerados para liberar espaço
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
