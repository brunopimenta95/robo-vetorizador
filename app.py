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
        
        # Calibragem avançada para letras nítidas e curvas perfeitas no CorelDRAW
        vtracer.convert_image_to_svg_py(
            input_path, 
            output_path,
            mode='spline',          # Usa curvas suaves (splines) em vez de linhas retas serrilhadas
            colormode='color',      # Mantém o mapeamento de cores idêntico ao original
            hierarchical='stacked', # Empilha as camadas de cores (evita frestas brancas no Corel)
            corner_threshold=30,    # Menor valor = cantos mais vivos e letras mais nítidas (padrão era 60)
            length_threshold=2.0,   # Detalha formas bem menores, ideal para textos pequenos (padrão era 4.0)
            splice_threshold=25,    # Une melhor os caminhos das curvas cortadas
            filter_speckle=2        # Ignora apenas ruídos minúsculos para não perder detalhes da logo
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
            return JSONResponse(status_code=500, content={"erro": "Falha ao gerar vetor."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
        
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
