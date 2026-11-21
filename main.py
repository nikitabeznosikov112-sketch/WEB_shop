from fastapi import FastAPI, Request, Depends
from routers import auth, deals, products, profile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from repositories.user_repositories import get_current_user, ProductRepository
from database import Session
templates=Jinja2Templates(directory="templates")

app = FastAPI()

app.include_router(auth.router)
app.include_router(profile.router)

def get_repo():
    session = Session()
    try:
        yield session
    finally:
        session.close()

@app.get("/", response_class=HTMLResponse)
def main_page(request: Request, session = Depends(get_repo), data_user: dict = Depends(get_current_user)):
    role = data_user['role']
    repo = ProductRepository(session)
    products = repo.get_all_products()

    return templates.TemplateResponse(request=request, name="main.html", context={'products': products, 'role': role})