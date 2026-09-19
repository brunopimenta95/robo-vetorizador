from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
import vtracer

app = FastAPI(title="Robô Vetorizador Gratuito")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor do seu robô vetorizador está funcionando perfeitamente!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    try:
        # Lê a imagem enviada diretamente para a memória do servidor
        image_bytes = await file.read()
        
        # Executa a vetorização em memória (sem criar arquivos temporários)
        svg_text = vtracer.convert_raw_image_to_svg(
            image_bytes,
            mode='spline',       # Suaviza as curvas para o CorelDRAW
            colormode='color',   # Mantém as cores originais da imagem complexa
            hierarchical='stacked', 
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            filter_speckle=4     # Remove pequenos ruídos da imagem original
        )
        
        # Retorna o arquivo .SVG pronto para o navegador baixar
        return Response(
            content=svg_text, 
            media_type="image/svg+xml", 
            headers={"Content-Disposition": "attachment; filename=seu_vetor.svg"}
        )
        
    except Exception as e:
        return {"erro": str(e)}
