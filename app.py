from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse
import vtracer
import os
import uuid

app = FastAPI(title="Robô Vetorizador Otimizado")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor de alta precisão está pronto!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    input_path = f"input_{unique_id}.png"
    output_path = f"output_{unique_id}.svg"
    
    try:
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Sintaxe oficial e atualizada do VTracer para traçados limpos
        vtracer.convert_image_to_svg_py(
            input_path, 
            output_path,
            colormode="color",        # Mantém todas as cores originais da logo
            hierarchical="stacked",    # Empilha as camadas (perfeito para o CorelDRAW)
            mode="spline",            # Suaviza os nós eliminando o efeito serrilhado
            filter_speckle=4,         # Limpa pequenos pontos indesejados
            color_precision=6,        # Melhora a fidelidade das tonalidades
            layer_difference=16,
            corner_threshold=60,      # Deixa cantos de fontes bem acabados
            length_threshold=4.0
        )
        
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                svg_data = f.read()
            
            return Response(
                content=svg_data,
                media_type="image/svg+xml",
                headers={"Content-Disposition": "attachment; filename=vetor_alta_precisao.svg"}
            )
        else:
            return JSONResponse(status_code=500, content={"erro": "Falha ao gerar arquivo final."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
        
    finally:
        # Garante a limpeza do servidor gratuito após cada execução
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
