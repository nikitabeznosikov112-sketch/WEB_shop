from database import Seller, Product, Deal, Client
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import Cookie, HTTPException

load_dotenv
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": int(payload["sub"]), "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Сессия истекла")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")
    
class SellerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int):
        return self.session.query(Seller).filter_by(id=id).first()

    def registrate(self, name: str, surname: str, login: str, password: str):
        if len(password) < 10:
            return None
        if self.session.query(Seller).filter_by(login=login).first():
            return None            
        hashed_password = generate_password_hash(password)
        user = Seller(name=name, surname=surname, login=login, password_hash=hashed_password)
        self.session.add(user)
        try:
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            return None

    def login(self, login: str, password: str):
        user = self.session.query(Seller).filter_by(login=login).first()
        if not user:
            return None
        if not check_password_hash(user.password_hash, password):
            return None

        payload = {
            "sub": str(user.id),
            "role": "seller",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {"user": user, "access_token": token, "token_type": "bearer"}

    def create_product(self, id: int, name: str, description: str, price: int, ):
        product = Product(seller_id=id, name=name, description=description, price=price)
        self.session.add(product)
        try:
            self.session.commit()
            return product
        except Exception as e:
            self.session.rollback()
            return False
        
    def get_active_products(self, id: int):
        products = self.session.query(Product).filter_by(seller_id=id, status=True).all()
        if not products:
            return False
        return products

    def get_deals(self, id: int):
        deals = self.session.query(Deal).filter_by(seller_id=id, active=True).all()
        if not deals:
            return False
        return deals

    def delete_account(self, id: int):
        user = self.session.query(Seller).filter_by(id=id).first()
        self.session.delete(user)
        try:
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_ns(self, id: int, name: str, surname: str):
        user = self.session.query(Seller).filter_by(id=id).first()
        user.name = name
        user.surname = surname
        try:
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            return False
class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_product(self, seller_id: int, name: str, description: str, price: int):
        product = Product(name=name, seller=seller_id, price=price, description=description)
        self.session.add(product)
        try:
            self.session.commit()
            return product
        except Exception as e:
            self.session.rollback()
            return False

    def delete_product(self, id: int):
        product = self.session.query(Product).filter_by(id=id).first()
        self.session.delete(product)
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def get_all_products(self):
        return self.session.query(Product).filter_by(status=True).all()

class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int):
        return self.session.query(Client).filter_by(id=id).first()

    def registrate(self, name: str, surname: str, login: str, password: str):
        if len(password) < 10:
            return None
        if self.session.query(Client).filter_by(login=login).first():
            return None           
        hashed_password = generate_password_hash(password)
        user = Client(name=name, surname=surname, login=login, password_hash=hashed_password)
        self.session.add(user)
        try:
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            return None

    def login(self, login: str, password: str):
        user = self.session.query(Client).filter_by(login=login).first()
        if not user:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        payload = {
            "sub": str(user.id),
            "role": "client",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {"user": user, "access_token": token, "token_type": "bearer"}



    def get_deals(self, id):
        deals = self.session.query(Deal).filter_by(client_id=id, active=True).all()
        if not deals:
            return False
        return deals

    def delete_account(self, id: int):
        user = self.session.query(Client).filter_by(id=id).first()
        self.session.delete(user)
        try:
            self.session.commit()
            return True
        except Exception as e:
            return False

    def change_ns(self, id: int, name: str, surname: str):
        user = self.session.query(Client).filter_by(id=id).first()
        user.name = name
        user.surname = surname
        try:
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            return False

class DealRepositorie:
    def __init__(self, session: Session):
        self.session = session

    def create_deal(self, client_id: int, product_id: int, seller_id: int):
        deal = Deal(seller_id=seller_id, product_id=product_id, client_id=client_id)
        self.session.add(deal)
        try:
            self.session.commit()
            return deal
        except Exception as e:
            return False

    def end_deal(self, id: int):
        deal = self.session.query(Deal).filter_by(id=id).first()
        deal.status=True
        deal.active=False
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def cancel_deal(self, id: int):
        deal = self.session.query(Deal).filter_by(id=id).first()
        deal.active=False
        try:
            self.session.commit()
            return True
        except Exception as e:
            return False



    




    