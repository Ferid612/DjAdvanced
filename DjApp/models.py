from sqlalchemy import event
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Boolean, DateTime, Float, Column, ForeignKey, Integer, String,DECIMAL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from DjAdvanced.settings import engine
from sqlalchemy_utils import EncryptedType
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()', onupdate='now()')
    deleted_at = Column(DateTime, nullable=True)


class Country(Base, TimestampMixin):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    country_code = Column(Integer,unique=True, nullable = False)
    country_name = Column(String, unique=True, nullable=False)
    currency_code = Column(String,  nullable=False)
    
    locations = relationship('Location', back_populates='country')
    employment_jobs = relationship('EmploymentJobs', back_populates='country')


class Location(Base, TimestampMixin):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    addres_line_1 = Column(EncryptedType(String, 'AES'), nullable=False)
    addres_line_2 = Column(EncryptedType(String, 'AES'))
    city = Column(EncryptedType(String, 'AES'), nullable=False)
    state = Column(EncryptedType(String, 'AES'), nullable=False)
    district = Column(EncryptedType(String, 'AES'))
    location_type_code = Column(String)
    postal_code = Column(EncryptedType(Integer, 'AES'),nullable=False)
    description = Column(EncryptedType(String, 'AES'))
    
    persons = relationship('Person', back_populates='location')
    supplier = relationship('Supplier', back_populates='location')
    country = relationship('Country', back_populates='locations')


class PhoneNumber(Base, TimestampMixin):
    
    __tablename__ = 'phone_number'
    id = Column(Integer, primary_key=True)
    phone_number = Column(EncryptedType(Integer, 'AES'),nullable=False, unique=True, cache_ok=True)
    country_code = Column(Integer, nullable=False)
    phone_type_id = Column(Integer)

    person = relationship('Person', back_populates='phone_number')
    supplier = relationship('Supplier', back_populates='phone_number')


"""
This function creates the tables for the categories, subcategories, and products in the database.
"""
class Category(Base, TimestampMixin):
    """
    This class creates the table for the categories in the database.
    """
    
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String, unique=True, nullable=False)
    sub_categories = relationship('Subcategory', back_populates='category')



class Subcategory(Base, TimestampMixin):
    """
    This class creates the table for the subcategories in the database.
    """
    
    __tablename__ = 'subcategory'
    id = Column(Integer, primary_key=True)
    name = Column(String,unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('subcategory.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    sub_categories = relationship('Subcategory', back_populates='parent', cascade='all, delete')
    parent = relationship('Subcategory', back_populates='sub_categories', remote_side=[id])
    category = relationship('Category', back_populates='sub_categories')
    product = relationship('Product', back_populates='subcategory')


class Supplier(Base, TimestampMixin):
    """
    A table representing the products.
    """
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String,unique=True,nullable=False)
    location_id =  Column(Integer, ForeignKey('location.id'), unique=True)
    phone_number_id = Column(Integer, ForeignKey('phone_number.id'), unique=True)
    description = Column(String)
    cargo_min_limit = Column(Float)
    cargo_percent = Column(DECIMAL)
    
    products = relationship('Product', back_populates='supplier')  
    phone_number = relationship('PhoneNumber', back_populates='supplier')
    location = relationship('Location', back_populates='supplier')  
    profil_image = relationship('ProfilImage', back_populates='supplier')  
  
    def to_json(self):
        if self.profil_image:
            profil_image_url = self.profil_image[0].image_url 
            profil_image_title = self.profil_image[0].title 
        else:
            profil_image_url= "Not"
            profil_image_title = "Not" 
       
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'profil_image': profil_image_url,
        'profil_image_title': profil_image_title,
        'location_id': self.location_id,
        'phone_number_id': self.phone_number_id,
        }
        
  

class Product(Base, TimestampMixin):
    """
    A table representing the products.
    """
    
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False) 
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'),nullable=False)
    price = Column(Float,nullable=False)
    SKU = Column(String,unique=True,nullable=False)
    description = Column(String)
    
    cargo_active = Column(Boolean,default=True)
    
    
    
    image = relationship('ProductImage', back_populates='product')
    supplier = relationship('Supplier', back_populates='products')
    subcategory = relationship('Subcategory', back_populates='product')
    comments = relationship('ProductRate', back_populates='product')
    fags = relationship('ProductFag', back_populates='product')
    questions = relationship('ProductQuestion', back_populates='product')
    discount = relationship('ProductDiscount', back_populates='products')
    cart_items = relationship('CartItem', back_populates='product')
    order_item = relationship('OrderItem', back_populates='product')
       
    def to_json(self):
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'supplier_id': self.supplier_id,
        'subcategory_id': self.subcategory_id,
        'price': self.price,
        'SKU': self.SKU,
        'cargo_active': self.cargo_active,
    }
              
              
              
class ProductRate(Base, TimestampMixin):
    """
    A table representing the comments of product.
    """ 
    __tablename__ = 'product_rate'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    ip = Column(String, nullable=False)
    rate_comment = Column(String, nullable=False)
    _rate = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    product = relationship('Product', back_populates='comments')
    user = relationship('Users', back_populates='comments')

    @hybrid_property
    def rate(self):
        return self._rate
    
    @rate.setter
    def rate(self, rate):
        self._rate = min(max(rate, 0), 5);

            

class ProductFag(Base, TimestampMixin):
    """
    A table representing the fag section of product.
    """
    __tablename__ = 'product_fag'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    status = Column(String, nullable=False)
    
    product = relationship('Product', back_populates='fags')
    


class ProductQuestion(Base, TimestampMixin):
    """
    A table representing the question and answer section of product.
    """
    __tablename__ = 'product_question'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_text = Column(String, nullable=False)
    status = Column(String, nullable=False)

    product = relationship('Product', back_populates='questions')
    answers = relationship('AnswersToQuestions', back_populates='question')
    user = relationship('Users', back_populates='questions')



class AnswersToQuestions(Base, TimestampMixin):
    """
    A table representing the answer to question section of product.
    """
    __tablename__ = 'answers_to_questions'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('product_question.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    answer_text = Column(String, nullable=False)
    status = Column(String, nullable=False)
    
    user = relationship('Users', back_populates='answers')
    question = relationship('ProductQuestion', back_populates='answers')




class ProductImage(Base, TimestampMixin):
    __tablename__ = 'product_image'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    image_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    
    product = relationship("Product", back_populates='image')

    
class Discount(Base, TimestampMixin):
    __tablename__ = 'discount'
    id = Column(Integer, primary_key=True)
    
    name = Column(String,unique=True,nullable=False)
    description = Column(String)
    discount_percent= Column(DECIMAL,nullable=False)
    active = Column(Boolean,default=False)
    product_discount = relationship("ProductDiscount", back_populates='discount')



    def to_json(self):
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'discount_percent': self.discount_percent,
        'active': self.active
    }
    

class ProductDiscount(Base, TimestampMixin):
    
    __tablename__ = 'product_discount'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'),nullable=False)
    discount_id = Column(Integer, ForeignKey('discount.id'),nullable=False)
    discount = relationship("Discount", back_populates='product_discount')
    products = relationship("Product", back_populates='discount')



class Person(Base, TimestampMixin):
    
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True,nullable=False)
    first_name = Column(String,nullable=False)
    last_name = Column(String,nullable=False)
    email = Column(EncryptedType(String, 'AES'), unique=True, nullable=False, cache_ok=True)
    _password =Column(String, nullable=False)
    location_id =  Column(Integer, ForeignKey('location.id'),unique=True)
    phone_number_id = Column(Integer, ForeignKey('phone_number.id'),unique=True)
    person_type = Column(String, CheckConstraint("person_type IN ('user', 'employee')"), nullable=False, default='user')
    phone_verify = Column(Boolean,default=False)
    active = Column(Boolean,default=False)
    refresh_token_id = Column(String, unique=True)

    location = relationship('Location', back_populates='persons')  
    phone_number = relationship('PhoneNumber', back_populates='person')
    employee = relationship('Employees', back_populates='person')
    user = relationship('Users', back_populates='person')
    profil_image = relationship('ProfilImage', back_populates='person')
    
    
    def hash_password(self, password):
        password = password.encode('utf-8')
        new_pwd = pwd_context.hash(password)
        self._password = new_pwd

    def verify_password(self, password):
        password = password.encode('utf-8')
        return pwd_context.verify(password, self._password)


    def __str__(self):
        return f"username:{self.username} {self.first_name} {self.last_name}"
    
    
    def to_json(self):
        try:
            profil_image_url = self.profil_image[0].image_url 
            profil_image_title = self.profil_image[0].title 
        except:
            profil_image_url= "Not"
            profil_image_title = "Not" 
        return {
        'id': self.id,
        'username': self.username,
        'first_name': self.first_name,
        'last_name': self.last_name,
        'email': self.email,
        'location_id': self.location_id,
        'phone_number_id': self.phone_number_id,
        'person_type': self.person_type,
        'phone_verify': self.phone_verify,
        'active': self.active,

        'profil_image': profil_image_url,
        'profil_image_title': profil_image_title,
        'access_token':'',
        'refresh_token':'',
        'created_at': self.created_at.isoformat(),
        'updated_at': self.updated_at.isoformat(),
    }
    
  

pwd_context = CryptContext(
        schemes=["bcrypt"],
        default="bcrypt",
        bcrypt__min_rounds=12
    )



class ProfilImage(Base, TimestampMixin):
    __tablename__ = 'profil_image'
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    title = Column(String, nullable=False)  
    
    person_id = Column(Integer, ForeignKey('persons.id'), unique=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), unique=True) 
    
    supplier = relationship('Supplier', back_populates='profil_image')
    person = relationship('Person', back_populates='profil_image')


    def to_json(self):
        return {
        'id': self.id,
        'image_url': self.image_url,
        'title': self.title,
        'person_id': self.person_id,
        'supplier_id': self.supplier_id,
        'created_at': self.created_at.isoformat(),
        'updated_at': self.updated_at.isoformat(),
    }
        
        
class EmploymentJobs(Base, TimestampMixin):
    
    __tablename__ = 'employment_jobs'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('country.id'),nullable=False)
    job_title = Column(String, nullable=False,unique=True)
    min_salary = Column(Integer,nullable=False)
    max_salary = Column(Integer,nullable=False)    
   
    country = relationship('Country', back_populates='employment_jobs')
    employees = relationship('Employees', back_populates='employment_job')
         


class Users(Base, TimestampMixin):
    
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'),unique=True,nullable=False)
    
    
    person = relationship('Person', back_populates='user')
    user_user_group_role = relationship('UserUserGroupRole', back_populates='users')
    payments =  relationship('UserPayment', back_populates='user')
    shopping_session = relationship('ShoppingSession', back_populates='user')
    orders =  relationship('OrderDetails', back_populates='user')
    comments = relationship('ProductRate', back_populates='user')
    questions = relationship('ProductQuestion', back_populates='user')
    answers = relationship('AnswersToQuestions', back_populates='user')


class Employees(Base, TimestampMixin):
    
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'),unique=True,nullable=False)
    hr_job_id = Column(Integer, ForeignKey('employment_jobs.id'))
    
    person = relationship('Person', back_populates='employee')
    employment_job = relationship('EmploymentJobs', back_populates='employees')
    employee_employee_group_role = relationship('EmployeeEmployeeGroupRole', back_populates='employees')



class UserGroup(Base, TimestampMixin):
    
    __tablename__ = 'user_group'
    id = Column(Integer, primary_key=True)
    name = Column(String,unique=True,nullable=False)
    description = Column(String)
    user_user_group_role = relationship('UserUserGroupRole', back_populates='user_group')
    
    
    
class EmployeeGroup(Base, TimestampMixin):
    
    __tablename__ = 'employee_group'
    id = Column(Integer, primary_key=True)
    name = Column(String,unique=True,nullable=False)
    description = Column(String)
    employee_employee_group_role = relationship('EmployeeEmployeeGroupRole', back_populates='employee_group')


class UserRole(Base, TimestampMixin):
    
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    roles = relationship("RolePermission", back_populates='user_roles')
    user_user_group_role = relationship('UserUserGroupRole', back_populates='user_roles')


    
class EmployeeRole(Base, TimestampMixin):
    
    __tablename__ = 'employee_roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    roles = relationship("RolePermission", back_populates='employee_roles')
   
    employee_employee_group_role = relationship('EmployeeEmployeeGroupRole', back_populates='employee_roles')



class UserUserGroupRole(Base, TimestampMixin):
    
    __tablename__ = 'user_user_group_role'
    id = Column(Integer, primary_key=True)
    
    user_id = Column(Integer, ForeignKey('users.id'),nullable=False)
    user_group_id = Column(Integer, ForeignKey('user_group.id'))
    user_role_id = Column(Integer, ForeignKey('user_roles.id'))
    
    users = relationship('Users', back_populates='user_user_group_role') 
    user_group = relationship('UserGroup', back_populates='user_user_group_role')
    user_roles = relationship('UserRole', back_populates='user_user_group_role')
    

class EmployeeEmployeeGroupRole(Base, TimestampMixin):
    
    __tablename__ = 'employee_employee_group_role'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'),nullable=False)
    employee_group_id = Column(Integer, ForeignKey('employee_group.id'))
    employee_role_id = Column(Integer, ForeignKey('employee_roles.id'))
  
    employees = relationship("Employees", back_populates='employee_employee_group_role')
    employee_group = relationship("EmployeeGroup", back_populates='employee_employee_group_role')
    employee_roles = relationship("EmployeeRole", back_populates='employee_employee_group_role')
    
    

class Permission(Base, TimestampMixin):
    
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True,nullable=False)
    description = Column(String)
    
    roles = relationship("RolePermission", back_populates='permissions')


class RolePermission(Base, TimestampMixin):
    
    __tablename__ = 'role_permission'
    id = Column(Integer, primary_key=True)
    user_role_id = Column(Integer, ForeignKey(UserRole.id))
    employee_role_id = Column(Integer, ForeignKey(EmployeeRole.id))
    permission_id = Column(Integer, ForeignKey(Permission.id),nullable=False)
    
    user_roles = relationship("UserRole", back_populates='roles')
    employee_roles = relationship("EmployeeRole", back_populates='roles')
    permissions = relationship("Permission", back_populates='roles')



class UserPayment(Base, TimestampMixin):
    
    __tablename__ = 'user_payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'),nullable=False)
    payment_type = Column(String)
    provider = Column(String)
    account_no = Column(Integer)    
    expiry = Column(DateTime)
    
    user = relationship('Users', back_populates='payments')
    
    
class ShoppingSession(Base, TimestampMixin):
    
    __tablename__ = 'shopping_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    user = relationship('Users', back_populates='shopping_session')
    cart_items = relationship('CartItem', back_populates='shopping_session')
  
    def total(self):
        return sum([item.product.price * item.quantity for item in self.cart_items])
      
  
  
  
class CartItem(Base, TimestampMixin):
    
    __tablename__ = 'cart_item'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('shopping_session.id'),nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'),nullable=False)
    _quantity= Column(Integer)
    
    shopping_session = relationship("ShoppingSession", back_populates='cart_items')
    product = relationship("Product", back_populates='cart_items')


    @hybrid_property
    def quantity(self):
        return self._quantity
    
    @quantity.setter
    def quantity(self, quantity):
        self._quantity = min(max(quantity, 0), 10000);
     
     
    
    def total(self):
        return (self._quantity)*(self.product.price)
    
        
      
        

class PaymentDetails(Base, TimestampMixin):
    
    __tablename__ = 'payment_details'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    provider = Column(String)
    status = Column(String)
    
    order_details = relationship("OrderDetails", back_populates='payment_details')


class OrderDetails(Base, TimestampMixin):
    
    __tablename__ = 'order_details'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'),nullable=False)
    payment_id = Column(Integer, ForeignKey('payment_details.id'),nullable=False)
    total = Column(DECIMAL,nullable=False)

    user = relationship("Users", back_populates='orders')
    payment_details = relationship("PaymentDetails", back_populates='order_details')
    order_items = relationship("OrderItem", back_populates='order_details')


class OrderItem(Base, TimestampMixin):
    
    __tablename__ = 'order_item'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order_details.id'),nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'),nullable=False)
    quantity= Column(Integer,default=0)

    order_details = relationship("OrderDetails", back_populates='order_items')
    product = relationship("Product", back_populates='order_item')







Base.metadata.create_all(engine)
 
 