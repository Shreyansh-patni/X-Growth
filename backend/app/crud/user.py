from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

from app.core.security import verify_password, get_password_hash

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_x_user_id(self, db: Session, *, x_user_id: str) -> Optional[User]:
        return db.query(User).filter(User.x_user_id == x_user_id).first()

    def get_by_x_username(self, db: Session, *, x_username: str) -> Optional[User]:
        return db.query(User).filter(User.x_username == x_username).first()

    def authenticate(self, db: Session, *, x_username: str, password: str) -> Optional[User]:
        user = self.get_by_x_username(db, x_username=x_username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            x_username=obj_in.x_username,
            x_user_id=obj_in.x_user_id,
            access_token=obj_in.access_token,
            access_token_secret=obj_in.access_token_secret,
            hashed_password=get_password_hash(obj_in.password),
            ai_rules=obj_in.ai_rules,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser(User)
