from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse
from PIL import Image
import vtracer
import os
import uuid

app = FastAPI(title="Robô Vetorizador Otimizado P&B")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor P&B de alta estabilidade está pronto!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    raw_path = f"raw_{unique_id}.png"
    input_path = f"input_{unique_id}.png"
    output_path = f"output_{unique_id}.svg"
    
    try:
        # 1. Salva a imagem original enviada
        content = await file.read()
        with open(raw_path, "wb") as f:
            f.write(content)
        
        # 2. Redimensiona e limpa a imagem para não estourar a memória do Render gratuito
        with Image.open(raw_path) as img:
            # Converte para escala de cinza e redimensiona mantendo a proporção
            img.thumbnail((800, 800))
            img.save(input_path, "PNG")
        
        # 3. Executa a vetorização binária leve (Linhas lisas perfeitas)
        vtracer.convert_image_to_svg_py(
            input_path, 
            output_path,
            colormode="binary",       # Preto e Branco puro (estilo silhueta)
            mode="spline",            # Suaviza curvas eliminando o efeito serrilhado
            filter_speckle=8,         # Ignora ruídos e imperfeições isoladas
            corner_threshold=60       # Mantém os cantos das fontes bem definidos
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
            return JSONResponse(status_code=500, content={"erro": "O arquivo final não foi gerado."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
        
    finally:
        # Garante a limpeza absoluta de todos os arquivos temporários
        for path in [raw_path, input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
