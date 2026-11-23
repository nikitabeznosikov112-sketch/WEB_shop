from fastapi import APIRouter, Form, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.user_repositories import ClientRepository, SellerRepository
from dependencies import get_current_user, get_repo
router = APIRouter(prefix="/auth")

templates = Jinja2Templates(directory='templates')


@router.get("/", response_class=HTMLResponse)
def authentication(request: Request):
    return templates.TemplateResponse(request=request, name="auth.html", context={})
@router.post("/login")
def login_web(request: Request, response: Response, login: str = Form(...), password: str = Form(...), user_type: str = Form(...), session = Depends(get_repo)):
    repo = SellerRepository(session) if user_type == 'seller' else ClientRepository(session)
    result = repo.login(login, password)

    if not result:
        return templates.TemplateResponse(request=request, name='auth.html', context={'error': 'Неверный пароль или логин'})
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
        return templates.TemplateResponse(request=request, name="auth.html", context={'error': "Слишком слабый пароль или логин занят"})
    return RedirectResponse(url='/auth/', status_code=303)

@router.post("/logout")
def logout():
    response = RedirectResponse(url='/auth/', status_code=303)
    response.delete_cookie("access_token")
    return response

@router.post("/change_password")
def change_password(request: Request, user_data: dict = Depends(get_current_user), password: str = Form(...), new_password: str = Form(...), session = Depends(get_repo)):
    user_id = user_data['user_id']
    role = user_data['role']
    repo = ClientRepository(session) if role == "client" else SellerRepository(session)
    repo.change_password(user_id, password, new_password)
    return RedirectResponse(url="/profile/settings", status_code=303)

    