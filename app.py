from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse
import vtracer
import os
import uuid

app = FastAPI(title="Robô Vetorizador Preto e Branco")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor P&B de alta precisão está pronto!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    input_path = f"input_{unique_id}.png"
    output_path = f"output_{unique_id}.svg"
    
    try:
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Configuração cirúrgica para transformar a logo em um traço preto e branco perfeito
        vtracer.convert_image_to_svg_py(
            input_path, 
            output_path,
            colormode="binary",       # Transforma em Preto e Branco puro (perfeito para logos)
            mode="spline",            # Suaviza os nós eliminando o efeito serrilhado nas fontes
            filter_speckle=10,         # Remove pequenas sujeiras e pontinhos isolados da imagem
            corner_threshold=45,      # Deixa os cantos das letras mais vivos e definidos
            length_threshold=3.5      # Foca na precisão das curvas longas
        )
        
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                svg_data = f.read()
            
            return Response(
                content=svg_data,
                media_type="image/svg+xml",
                headers={"Content-Disposition": "attachment; filename=vetor_preto_branco.svg"}
            )
        else:
            return JSONResponse(status_code=500, content={"erro": "Falha ao gerar arquivo."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
        
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
