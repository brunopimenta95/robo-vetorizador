from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse
import vtracer
import os
import uuid

app = FastAPI(title="Robô Vetorizador Gratuito")

@app.get("/")
def home():
    return {"status": "Online", "mensagem": "O motor do seu robô vetorizador está funcionando perfeitamente!"}

@app.post("/vetorizar")
async def vetorizar_imagem(file: UploadFile = File(...)):
    # Cria nomes de arquivos únicos para evitar conflitos no servidor gratuito
    unique_id = str(uuid.uuid4())
    input_path = f"input_{unique_id}.png"
    output_path = f"output_{unique_id}.svg"
    
    try:
        # Lê e salva temporariamente a imagem enviada
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Executa a vetorização em cores usando a sintaxe padrão e atualizada
        vtracer.convert_image_to_svg_py(input_path, output_path)
        
        # Se o vetor foi gerado com sucesso, lê os dados e prepara para o download
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                svg_data = f.read()
            
            return Response(
                content=svg_data,
                media_type="image/svg+xml",
                headers={"Content-Disposition": "attachment; filename=seu_vetor.svg"}
            )
        else:
            return JSONResponse(status_code=500, content={"erro": "O motor não conseguiu gerar o arquivo vetorial."})
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": f"Erro interno no processamento: {str(e)}"})
        
    finally:
        # Garante que os arquivos temporários sejam apagados para poupar espaço de graça
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
