from sqlalchemy import Boolean, DateTime, Float, Column, ForeignKey, Integer, String,DECIMAL
from sqlalchemy.orm import relationship
from DjAdvanced.settings import engine
from sqlalchemy_utils import EncryptedType
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from passlib.context import CryptContext

Base = declarative_base()


"""
This function creates the tables for the categories, subcategories, and products in the database.
"""
class Category(Base):
    """
    This class creates the table for the categories in the database.
    """
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String)


class Subcategory(Base):
    """
    This class creates the table for the subcategories in the database.
    """
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'subcategory'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('subcategory.id'))
    category_id = Column(Integer, ForeignKey('category.id'))


class Product(Base):
    """
    A table representing the products.
    """
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    SKU = Column(String)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    creadet_at = Column(DateTime)    
    modified_at = Column(DateTime)    
    deleted_at = Column(DateTime)    
    
    
class Discount(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'discount'
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    description = Column(String)
    discount_percent= Column(DECIMAL)
    active = Column(Boolean)
    creadet_at = Column(DateTime)    
    modified_at = Column(DateTime)    
    deleted_at = Column(DateTime)    


pwd_context = CryptContext(
        schemes=["bcrypt"],
        default="bcrypt",
        bcrypt__min_rounds=12
    )

class Users(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime,default=datetime.utcnow)
    modified_at = Column(DateTime)
    active = Column(Boolean,default=False)
    phone_verify = Column(Boolean,default=False)
    _password =Column(String, unique=True, nullable=False)
    usermail = Column(EncryptedType(String, 'AES'), unique=True, nullable=False)
    telephone = Column(EncryptedType(Integer, 'AES'), unique=True, nullable=False)
    token  = Column(String)
    
    def hash_password(self, password):
        password = password.encode('utf-8')
        new_pwd = pwd_context.hash(password)
        self._password = new_pwd

    def verify_password(self, password):
        password = password.encode('utf-8')
        return pwd_context.verify(password, self._password)


class UserGroup(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'user_group'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


class UserAddress(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'user_address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    addres_line_1 = Column(EncryptedType(String, 'AES'))
    addres_line_2 = Column(EncryptedType(String, 'AES'))
    city = Column(String)
    postal_code = Column(EncryptedType(Integer, 'AES'))
    country = Column(DateTime)
    telephone = Column(EncryptedType(Integer, 'AES'))
    creadet_at = Column(DateTime)
    modified_at = Column(DateTime)


class UserPayment(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'user_payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    patment_type = Column(String)
    provider = Column(String)
    account_no = Column(Integer)
    expiry = Column(DateTime)
    
class ShoppingSession(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'shopping_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total = Column(DECIMAL)
    creadet_at = Column(DateTime)
    modified_at = Column(DateTime)
  
class CardItem(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'card_item'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('shopping_session.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    creadet_at = Column(DateTime)
    modified_at = Column(DateTime)

class PaymentDetails(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'payment_details'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    amount = Column(Integer)
    provider = Column(String)
    status = Column(String)
    creadet_at = Column(DateTime)
    modified_at = Column(DateTime)


class OrderDetails(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'order_details'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    payment_id = Column(Integer, ForeignKey('payment_details.id'))
    total = Column(DECIMAL)
    creadet_at = Column(DateTime)
    modified_at = Column(DateTime)


class OrderItems(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order_details.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity= Column(Integer)
    creadet_at = Column(DateTime)
    modified_at = Column(DateTime)


class Role(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)


class Permission(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)


class RolePermission(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'role_permission'
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id))
    role = relationship("Role")
    permission_id = Column(Integer, ForeignKey(Permission.id))
    permission = relationship("Permission")


class UserUserGroupRole(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'user_user_group_role'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users")
    user_group_id = Column(Integer, ForeignKey('user_group.id'))
    user_group = relationship("UserGroup")
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role")


Base.metadata.create_all(engine)
 