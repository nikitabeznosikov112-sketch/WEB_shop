from fastapi import APIRouter, Form, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import Session
from repositories.user_repositories import ClientRepository, SellerRepository, get_current_user

templates = Jinja2Templates(directory='templates')

router = APIRouter(prefix='/profile')
def get_repo():
    session = Session()
    try:
        yield session
    finally:
        session.close()

@router.get('/', response_class=HTMLResponse)
def show_profile(request: Request, session = Depends(get_repo), user_data: dict = Depends(get_current_user)):
    role = user_data['role']
    user_id = user_data['user_id']

    repo = SellerRepository(session) if role == 'seller' else ClientRepository(session)
    user = repo.get_by_id(user_id)
    if role == "seller":
        products = repo.get_active_products(user_id)
    deals = repo.get_deals(user_id)

    if role == 'seller':
        return templates.TemplateResponse(request=request, name='seller_profile.html', context={'user': user, 'products': products, 'deals': deals})
    else:
        return templates.TemplateResponse(request=request, name='client_profile.html', context={'user': user, 'deals': deals})

@router.post("/create_product", response_class=HTMLResponse)
def create_poduct(request: Request, session = Depends(get_repo), user_data: dict = Depends(get_current_user)): 
    return templates.TemplateResponse(request=request, name='create_product.html', context={})

@router.post("/create_product/confirm_create_product")
def confirm_create_product(request: Request, session = Depends(get_repo), user_data: dict = Depends(get_current_user), name: str = Form(...), price: int = Form(...), description: str = Form(...)):
    user_id = user_data['user_id']
    repo = SellerRepository(session)
    product = repo.create_product(user_id, name, description, price)

    if product == False:
        return templates.TemplateResponse(name='seller_profile.html', request=request, context={'error': 'Не удалось создать товар'})
    return RedirectResponse(url='/profile/', status_code=303)

    
@router.get('/settings', response_class=HTMLResponse)
def show_settings(request: Request, session = Depends(get_repo), user_data: dict = Depends(get_current_user)):
    role = user_data['role']
    user_id = user_data['user_id']

    repo = SellerRepository(session) if role == 'seller' else ClientRepository(session)
    user = repo.get_by_id(user_id)

    return templates.TemplateResponse(request=request, name='settings.html', context={'user': user})

@router.post('/settings/change_ns', response_class=HTMLResponse)
def change_ns(request: Request, session = Depends(get_repo), user_data: dict = Depends(get_current_user)):
    user_id = user_data['user_id']
    role = user_data['role']

    repo = SellerRepository(session) if role == 'seller' else ClientRepository(session)
    user = repo.get_by_id(user_id)

    return templates.TemplateResponse(request=request, name='change_ns.html', context={'user': user})

@router.post("/settings/change_ns/confirm_change")
def change_ns(session = Depends(get_repo), user_data: dict = Depends(get_current_user), name: str = Form(...), surname: str = Form(...)):
    user_id = user_data['user_id']
    role = user_data['role']

    repo = SellerRepository(session) if role == "seller" else ClientRepository(session)
    repo.change_ns(user_id, name, surname)

    return RedirectResponse(url='/profile/', status_code=303)



