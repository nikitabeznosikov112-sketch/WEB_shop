from fastapi import FastAPI, Request
from routers import auth, deals, products
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates=Jinja2Templates(directory="templates")

app = FastAPI()
app.include_router(auth.router)

@app.get("/")
def main_page(request: Request, response: HTMLResponse):
    return templates.TemplateResponse(request=request, name="main.html", context={})