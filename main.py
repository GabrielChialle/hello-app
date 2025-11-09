from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Hello-app</title>
        <style>
            body {
                background-color: #0b3d91; /* Azul escuro */
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
            }
            h1 {
                color: #ffffff;
                font-size: 72px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>Olá Gabriel!</h1>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
