from fastapi import APIRouter, Form, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import Session
from repositories.user_repositories import ClientRepository, SellerRepository

router = APIRouter(prefix="/logreg")

templates = Jinja2Templates(directory='templates')
def get_repo():
    session = Session()
    try:
        yield session
    finally:
        session.close()

@router.get("/")
def authentication(request: Request, response: HTMLResponse):
    return templates.TemplateResponse(request=request, name="logreg.html", context={})
@router.post("/login")
def login_web(request: Request, response: Response, login: str = Form(...), password: str = Form(...), user_type: str = Form(...), session = Depends(get_repo)):
    repo = SellerRepository(session) if user_type == 'seller' else ClientRepository(session)
    result = repo.login(login, password)

    if not result:
        return templates.TemplateResponse(request=request, name='logreg.html', context={'error': 'Неверный пароль или логин'})
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(
        key="access_token",
        value=result['access_token'],
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    return response

@router.post("/registration")
def registrate_web(request: Request, response: Response, login: str = Form(...), user_type: str = Form(...), password: str = Form(...),name: str = Form(...), surname: str = Form(...) ,session = Depends(get_repo)):
    repo = SellerRepository(session) if user_type == "seller" else ClientRepository(session)
    result = repo.registrate(name, surname, login, password)
    if not result:
        return templates.TemplateResponse(request=request, name="logreg.html", context={'error': "Слишком слабый пароль или логин занят"})
    return RedirectResponse(url='/logreg/', status_code=303)

@router.post("/logout")
def logout():
    response = RedirectResponse(url='/logreg', status_code=303)
    response.delete_cookie("access_token")
    return response