from collections import defaultdict
from sqlalchemy import CheckConstraint, Boolean, DateTime, Float, Column, ForeignKey, Integer, String, DECIMAL, Table, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from DjAdvanced.settings import engine
from sqlalchemy_utils import EncryptedType
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False,
                        server_default='now()', onupdate='now()')
    deleted_at = Column(DateTime, nullable=True)


class Country(Base, TimestampMixin):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    country_code = Column(Integer, unique=True, nullable=False)
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
    postal_code = Column(EncryptedType(Integer, 'AES'), nullable=False)
    description = Column(EncryptedType(String, 'AES'))

    persons = relationship('Person', back_populates='location')
    supplier = relationship('Supplier', back_populates='location')
    country = relationship('Country', back_populates='locations')


class PhoneNumber(Base, TimestampMixin):

    __tablename__ = 'phone_number'
    id = Column(Integer, primary_key=True)
    phone_number = Column(EncryptedType(Integer, 'AES'),
                          nullable=False, unique=True, cache_ok=True)
    country_code = Column(Integer, nullable=False)
    phone_type_id = Column(Integer)

    person = relationship('Person', back_populates='phone_number')
    supplier = relationship('Supplier', back_populates='phone_number')


class Category(Base, TimestampMixin):
    """
    This class creates the table for the categories in the database.
    """

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    name = Column(String, unique=True, nullable=False, index=True)
    icon = Column(String, unique=True)
    products = relationship('Product', back_populates='category')
    children = relationship('Category', cascade='all, delete-orphan')

    @property
    def has_children(self):
        return bool(self.children)

    @classmethod
    def get_root_categories(cls, session):
        return session.query(cls).filter_by(parent_id=None).all()

    def get_child_categories(self):
        return self.children


    def has_products(self):
        """
        Returns True if there are any products that belong to this category or any of its children,
        and False otherwise.
        """
        if self.products:
            return True
        for child in self.children:
            if child.has_products():
                return True
        return False


    def get_all_products(self):
        """
        Recursively retrieves all products that belong to this category or any of its children.
        """
        products = []
        if self.products:
            products.extend([product.to_json() for product in self.products])
        for child in self.children:
            products.extend(child.get_all_products())
        return products
    
    
    def get_self_products(self):
        """
        Recursively retrieves all products that belong to this category or any of its children.
        """
        products = []
        if self.products:
            products.extend([product.to_json() for product in self.products])
        return products
    
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'icon': self.icon,
            'has_children': self.has_children,
        }


class Supplier(Base, TimestampMixin):
    """
    A table representing the products.
    """
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), unique=True)
    phone_number_id = Column(Integer, ForeignKey(
        'phone_number.id'), unique=True)
    description = Column(String)
    cargo_min_limit = Column(Float)
    cargo_percent = Column(DECIMAL)

    products = relationship('Product', back_populates='supplier')
    phone_number = relationship('PhoneNumber', back_populates='supplier')
    location = relationship('Location', back_populates='supplier')
    profil_image = relationship('ProfilImage', back_populates='supplier')

    def to_json(self):
        profil_image = None
        if self.profil_image:
            profil_image = self.profil_image[0].to_json()

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'profil_image':profil_image, 
            'location_id': self.location_id,
            'country_code': str(self.phone_number.country_code),
            'phone_number': str(self.phone_number.phone_number),
        }


    def to_json_for_card(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


class Product(Base, TimestampMixin):
    """
    A table representing the products.
    """

    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    description = Column(String)

    entries = relationship('ProductEntry', back_populates='product', overlaps="products")
    supplier = relationship('Supplier', back_populates='products')
    category = relationship('Category', back_populates='products')


    colors = relationship("ProductColor", secondary="product_entry",
                        primaryjoin="ProductEntry.product_id == Product.id", secondaryjoin="ProductEntry.color_id == ProductColor.id",
                        viewonly=True)
    
    
    materials = relationship("ProductMaterial", secondary="product_entry",
                        primaryjoin="ProductEntry.product_id == Product.id", secondaryjoin="ProductEntry.material_id == ProductMaterial.id",
                        viewonly=True)


    sizes = relationship("ProductMeasure", secondary="product_entry",
                        primaryjoin="ProductEntry.product_id == Product.id", secondaryjoin="ProductEntry.measure_value_id == ProductMeasure.id",
                        viewonly=True)


    def get_exist_colors(self):
        """
        Returns a list of all colors that are already assigned to at least one product entry
        along with the corresponding product entry IDs.
        """
        return [color.to_json() for color in self.colors]

      
    def get_exist_materials(self):
        """
        Returns a list of all marerials that are already assigned to at least one product entry
        along with the corresponding product entry IDs.
        """
        return [material.to_json() for material in self.materials]


    def get_exist_sizes(self):
        """
        Returns a list of all sizess that are already assigned to at least one product entry
        along with the corresponding product entry IDs.
        """
        return [size.to_json() for size in self.sizes]


    def get_exist_entries(self):
        """
        Returns a list of all entries that are already assigned to at least one product entry
        along with the corresponding product entry IDs.
        """
        return [entry.to_json() for entry in self.entries]

    
    
    def to_json_for_entry(self):
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'supplier_data': self.supplier.to_json_for_card(),
            'category_data': self.category.to_json(),
            'exist_colors' : self.get_exist_colors(),        
            'exist_materials' : self.get_exist_materials(),
            'exist_sizes':self.get_exist_sizes(),
    
        }
        

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'supplier_data': self.supplier.to_json_for_card(),
            'category_data': self.category.to_json(),
            'exist_colors' : self.get_exist_colors(),        
            'exist_materials' : self.get_exist_materials(),
            'exist_sizes':self.get_exist_sizes(),
    
        }


class ProductImage(Base, TimestampMixin):
    __tablename__ = 'product_image'
    id = Column(Integer, primary_key=True)
    index = Column(Integer,default=0,nullable=False)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    image_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    product_entry = relationship("ProductEntry", back_populates='images')

    def to_json(self):
        return {
            'id': self.id,
            'url': self.image_url,
            'title': self.title,
            'product_entry_id': self.product_entry_id,
            'index': self.index,
            }


class ProductEntry(Base):
    __tablename__ = 'product_entry'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey(
        'product.id', ondelete='CASCADE'), nullable=False, index=True)
    
    color_id = Column(Integer, ForeignKey('product_color.id',
                      ondelete='CASCADE'), nullable=False, index=True)
   
    material_id = Column(Integer, ForeignKey(
        'product_material.id', ondelete='CASCADE'), nullable=False, index=True)
   
    measure_value_id = Column(Integer, ForeignKey(
        'product_measure_value.id', ondelete='CASCADE'), index=True)
   
    quantity = Column(Integer, nullable=False, index=True)
    SKU = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    cargo_active = Column(Boolean, default=True)

    product = relationship('Product',  back_populates='entries')
    color = relationship("ProductColor", back_populates="product_entries")
    rates = relationship('ProductRate', back_populates='product_entry')
    fags = relationship('ProductFag', back_populates='product_entry')
    comments = relationship('ProductComment', back_populates='product_entry')

    product_discounts = relationship(
        'ProductDiscount', back_populates='product_entry')
   
    images = relationship('ProductImage', back_populates='product_entry',  order_by=( ProductImage.index, ProductImage.id,))
   
    material = relationship(
        "ProductMaterial", back_populates="product_entries")
   
    size = relationship('ProductMeasureValue',
                        back_populates='product_entry', cascade="all, delete")

    cart_items = relationship('CartItem', back_populates='product_entry')
    order_item = relationship('OrderItem', back_populates='product_entry')
   
    wishlist_product_entry = relationship(
        'WishListProductEntry', back_populates='product_entry')
   
    product_entry_card_boxs = relationship(
        'ProductEntryCardBox', back_populates='product_entry')

    def get_raters_data(self):
        count = len(self.rates)
        if count == 0:
            return {'count': count, 'avg_rating': 0}

        avg_rating = sum(
            [product_rate.rate for product_rate in self.rates])/count
   
        return {'count': count, 'avg_rating': avg_rating}


    @hybrid_property
    def discount_data(self):
        active_discounts = [
            d.discount for d in self.product_discounts if d.discount.active]
        discount_total = sum(
            active_discount.discount_percent for active_discount in active_discounts)

        discounted_price = self.price
        for active_discount in active_discounts:
            discount_percent = active_discount.discount_percent
            discounted_price *= (1 - discount_percent/100)

        return {'discounted_price': discounted_price, 'discount_total': discount_total}


    def to_json_for_card(self):
        # Get the product category chain
        image = None
        if self.images:
            image = self.images[0].to_json() 
            

        return {
            'product': self.product.to_json(),            
            'entry':{
            'id': self.id,
            'price_prev': self.price,
            'price_current': self.discount_data.get('discounted_price'),
            'total_discount_percent': self.discount_data.get('discount_total'),
            'quantity': self.quantity,
            'color': self.color.to_json(),
            'image': image,
            'rates_data': self.get_raters_data(),
        }
            }


    def to_json(self):
        size = None
        images = None

        if self.images:
            images = [image.to_json() for image in self.images]

        if self.size:
            size = self.size.to_json()

        rates = None
        if self.rates:
            rates = [rate.to_json() for rate in self.rates]

        return {
            "id": self.id,
            "price_prev": self.price,
            "price_current": self.discount_data.get('discounted_price'),
            "total_discount_percent": self.discount_data.get('discount_total'),
            "SKU": self.SKU,
            "quantity": self.quantity,
            "color": self.color.to_json(),
            "size": size,
            "material": self.material.to_json(),
            "images": images,   
            'cargo_active': self.cargo_active,
            "rates_data": self.get_raters_data(),
            "rates":rates,
            "fags": self.get_all_fags()['fags_data'],
            "comments": self.get_entry_comments()['comment_tree']
        }


    def get_active_discounts(self):
        """
        Returns all active discounts associated with this product entry.
        """
        active_discounts = [product_discount.discount.to_json(
        ) for product_discount in self.product_discounts if product_discount.discount.active]

        return {"active_discounts": active_discounts}

    def get_all_fags(self):
        """
        Returns all the fags associated with this product entry.
        """
        fags = [fag.to_json() for fag in self.fags]

        return {"fags_data": fags}

    def get_entry_comments(self):
        """
        Returns all the comments associated with this product entry in a nested dictionary format.
        """
        comments_dict = defaultdict(list)

        # group comments by their parent_comment_id, if any
        for comment in self.comments:
            comments_dict[comment.parent_comment_id].append(comment)

        # recursively build comment tree
        def build_comment_tree(comment):
            comment_data = {
                "comment_id": comment.id,
                "person_id": comment.person_id,
                "person_username": comment.person.username,
                "comment_text": comment.comment_text,
                "children": []
            }

            for child_comment in comments_dict[comment.id]:
                comment_data["children"].append(
                    build_comment_tree(child_comment))

            return comment_data

        # build the comment tree starting with the top-level comments
        top_level_comments = comments_dict[None]
        comment_tree = []
        for comment in top_level_comments:
            comment_tree.append(build_comment_tree(comment))

        return {"comment_tree": comment_tree}


class ProductMeasureValue(Base):
    __tablename__ = 'product_measure_value'
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
    measure_id = Column(Integer, ForeignKey(
        'product_measure.id', ondelete='CASCADE'), nullable=False, index=True)
    measure = relationship('ProductMeasure', back_populates='values')
    product_entry = relationship('ProductEntry', back_populates='size')

    def to_json(self):
        return {
            'id': self.id,
            'value': self.value,
            'measure': self.measure.name,
        }


class ProductMeasure(Base):
    __tablename__ = 'product_measure'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    values = relationship(
        'ProductMeasureValue', back_populates='measure', cascade="all, delete", lazy="joined")

    def append_value(self, session, value):
        measure_value = ProductMeasureValue(value=value, measure=self)
        session.add(measure_value)
        session.commit()

    @classmethod
    def add_measure(cls, session, name):
        """P
        Appends a new measure type to the ProductMeasure table with the given name.
        """
        new_measure = cls(name=name)
        session.add(new_measure)
        session.commit()
        return new_measure

    def to_json(self):
        measure_dict = {
            'id': self.id,
            'name': self.name,
            'values': []
        }

        for value in self.values:
            measure_dict['values'].append(value.to_json())

        return measure_dict


class ProductColor(Base):
    __tablename__ = 'product_color'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    color_code = Column(String, nullable=False)

    product_entries = relationship(
        "ProductEntry", back_populates="color", cascade="all, delete", lazy="joined", overlaps="colors")

    @classmethod
    def add_color(cls, session, name, color_code):
        """
        Adds a new color to the ProductColor table with the given name and color code.
        """
        new_color = cls(name=name, color_code=color_code)
        session.add(new_color)
        session.commit()
        return new_color

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'color_code': self.color_code,
        }


class ProductMaterial(Base):
    __tablename__ = 'product_material'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    product_entries = relationship(
        "ProductEntry", back_populates="material", cascade="all, delete", lazy="joined")

    @classmethod
    def add_material(cls, session, name):
        """
        Adds a new color to the ProductColor table with the given name and color code.
        """
        new_material = cls(name=name)
        session.add(new_material)
        session.commit()
        return new_material

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class ProductRate(Base, TimestampMixin):
    """
    A table representing the comments of product.
    """
    __tablename__ = 'product_rate'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    ip = Column(String, nullable=False)
    rate_comment = Column(String, nullable=False)
    _rate = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    product_entry = relationship('ProductEntry', back_populates='rates')
    user = relationship('Users', back_populates='product_rates')

    @hybrid_property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, rate):
        self._rate = min(max(rate, 0), 5)

    def to_json(self):
        return {
            'id': self.id,
            'product_entry_id': self.product_entry_id,
            "user_id": self.user_id,
            "username": self.user.person.username,
            "rate_comment": self.rate_comment,
            "rate": self.rate,
            "status": self.status,
            'ip': self.ip

        }


class ProductFag(Base, TimestampMixin):
    """
    A table representing the fag section of product.
    """
    __tablename__ = 'product_fag'
    id = Column(Integer, primary_key=True)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    status = Column(String, nullable=False)

    product_entry = relationship('ProductEntry', back_populates='fags')

    def to_json(self):
        return {
            'id': self.id,
            'product_entry_id': self.product_entry_id,
            'question': self.question,
            'answer': self.answer,
        }


class ProductComment(Base, TimestampMixin):
    """
    A table representing the comment and answer section of product.
    """
    __tablename__ = 'product_comment'
    id = Column(Integer, primary_key=True)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey(
        'product_comment.id', ondelete='CASCADE'))
    comment_text = Column(String, nullable=False)
    status = Column(String, nullable=False)

    product_entry = relationship('ProductEntry', back_populates='comments')
    child_comments = relationship('ProductComment')
    person = relationship('Person', back_populates='comments')




class Discount(Base, TimestampMixin):
    __tablename__ = 'discount'
    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    discount_percent = Column(Float, nullable=False)
    active = Column(Boolean, default=False)
    product_discounts = relationship(
        "ProductDiscount", back_populates='discount')

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
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    discount_id = Column(Integer, ForeignKey('discount.id'), nullable=False)
    discount = relationship("Discount", back_populates='product_discounts')
    product_entry = relationship(
        "ProductEntry", back_populates='product_discounts')


class Person(Base, TimestampMixin):

    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(EncryptedType(String, 'AES'), unique=True,
                   nullable=False, cache_ok=True)
    _password = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), unique=True)
    phone_number_id = Column(Integer, ForeignKey(
        'phone_number.id'), unique=True)
    person_type = Column(String, CheckConstraint(
        "person_type IN ('user', 'employee')"), nullable=False, default='user')
    phone_verify = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
    refresh_token_id = Column(String, unique=True)

    location = relationship('Location', back_populates='persons')
    phone_number = relationship('PhoneNumber', back_populates='person')
    employee = relationship('Employees', back_populates='person')
    user = relationship('Users', back_populates='person')
    profil_image = relationship('ProfilImage', back_populates='person')
    comments = relationship('ProductComment', back_populates='person')

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
        person_profil_image = None
        if self.profil_image:
            person_profil_image = self.profil_image[0].to_json()
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

            'profil_image': person_profil_image,
            'access_token': '',
            'refresh_token': '',
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
            'url': self.image_url,
            'title': self.title,
            'person_id': self.person_id,
            'supplier_id': self.supplier_id,
        }


class EmploymentJobs(Base, TimestampMixin):

    __tablename__ = 'employment_jobs'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    job_title = Column(String, nullable=False, unique=True)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)

    country = relationship('Country', back_populates='employment_jobs')
    employees = relationship('Employees', back_populates='employment_job')


class Users(Base, TimestampMixin):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'),
                       unique=True, nullable=False)

    person = relationship('Person', back_populates='user', lazy='joined')
    user_user_group_role = relationship(
        'UserUserGroupRole', back_populates='users')
    payments = relationship('UserPayment', back_populates='user')
    shopping_session = relationship('ShoppingSession', back_populates='user')
    orders = relationship('OrderDetails', back_populates='user')
    product_rates = relationship('ProductRate', back_populates='user')
    wishlists = relationship('WishList', back_populates='user')

    def get_user_wishlists_list(self, count):
        return [wishlist.to_json(count) for wishlist in self.wishlists]


class WishList(Base, TimestampMixin):
    __tablename__ = 'wishlist'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String)

    user = relationship('Users', back_populates='wishlists')
    wishlist_product_entries = relationship(
        'WishListProductEntry', back_populates='wishlist', cascade='all, delete-orphan')

    def to_json(self, count=None):
        if count is not None:
            wishlist_product_entries = [wishlist_product_entry.to_json() for wishlist_product_entry in self.wishlist_product_entries[:count]]
        else:
            wishlist_product_entries = [wishlist_product_entry.to_json() for wishlist_product_entry in self.wishlist_product_entries]

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'product_entries': wishlist_product_entries
        }


class WishListProductEntry(Base, TimestampMixin):
    __tablename__ = 'wishlist_product_entry'
    id = Column(Integer, primary_key=True)
    wishlist_id = Column(Integer, ForeignKey('wishlist.id'))
    product_entry_id = Column(Integer, ForeignKey('product_entry.id'))

    wishlist = relationship(
        'WishList', back_populates='wishlist_product_entries')
    product_entry = relationship(
        'ProductEntry', back_populates='wishlist_product_entry')

    def to_json(self):
        product_entry = self.product_entry.to_json_for_card()

        return {
            'id': self.id,
            'wishlist_id': self.wishlist_id,
            'product_entry_id': self.product_entry_id,
            'product_entry': product_entry
        }


class Employees(Base, TimestampMixin):

    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'),
                       unique=True, nullable=False)
    hr_job_id = Column(Integer, ForeignKey('employment_jobs.id'))

    person = relationship('Person', back_populates='employee')
    employment_job = relationship('EmploymentJobs', back_populates='employees')
    employee_employee_group_role = relationship(
        'EmployeeEmployeeGroupRole', back_populates='employees')


class UserGroup(Base, TimestampMixin):

    __tablename__ = 'user_group'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    user_user_group_role = relationship(
        'UserUserGroupRole', back_populates='user_group')


class EmployeeGroup(Base, TimestampMixin):

    __tablename__ = 'employee_group'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    employee_employee_group_role = relationship(
        'EmployeeEmployeeGroupRole', back_populates='employee_group')


class UserRole(Base, TimestampMixin):

    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    roles = relationship("RolePermission", back_populates='user_roles')
    user_user_group_role = relationship(
        'UserUserGroupRole', back_populates='user_roles')


class EmployeeRole(Base, TimestampMixin):

    __tablename__ = 'employee_roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    roles = relationship("RolePermission", back_populates='employee_roles')

    employee_employee_group_role = relationship(
        'EmployeeEmployeeGroupRole', back_populates='employee_roles')


class UserUserGroupRole(Base, TimestampMixin):

    __tablename__ = 'user_user_group_role'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_group_id = Column(Integer, ForeignKey('user_group.id'))
    user_role_id = Column(Integer, ForeignKey('user_roles.id'))

    users = relationship('Users', back_populates='user_user_group_role')
    user_group = relationship(
        'UserGroup', back_populates='user_user_group_role')
    user_roles = relationship(
        'UserRole', back_populates='user_user_group_role')


class EmployeeEmployeeGroupRole(Base, TimestampMixin):

    __tablename__ = 'employee_employee_group_role'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee_group_id = Column(Integer, ForeignKey('employee_group.id'))
    employee_role_id = Column(Integer, ForeignKey('employee_roles.id'))

    employees = relationship(
        "Employees", back_populates='employee_employee_group_role')
    employee_group = relationship(
        "EmployeeGroup", back_populates='employee_employee_group_role')
    employee_roles = relationship(
        "EmployeeRole", back_populates='employee_employee_group_role')


class Permission(Base, TimestampMixin):

    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    roles = relationship("RolePermission", back_populates='permissions')


class RolePermission(Base, TimestampMixin):

    __tablename__ = 'role_permission'
    id = Column(Integer, primary_key=True)
    user_role_id = Column(Integer, ForeignKey(UserRole.id))
    employee_role_id = Column(Integer, ForeignKey(EmployeeRole.id))
    permission_id = Column(Integer, ForeignKey(Permission.id), nullable=False)

    user_roles = relationship("UserRole", back_populates='roles')
    employee_roles = relationship("EmployeeRole", back_populates='roles')
    permissions = relationship("Permission", back_populates='roles')


class UserPayment(Base, TimestampMixin):

    __tablename__ = 'user_payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_type = Column(String)
    provider = Column(String)
    account_no = Column(Integer)
    expiry = Column(DateTime)

    user = relationship('Users', back_populates='payments')


class ShoppingSession(Base, TimestampMixin):

    __tablename__ = 'shopping_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     unique=True, nullable=False)

    user = relationship('Users', back_populates='shopping_session')
    cart_items = relationship('CartItem', back_populates='shopping_session')

    def total(self):
        return sum([item.product_entry.price * item.quantity for item in self.cart_items])


class CartItem(Base, TimestampMixin):

    __tablename__ = 'cart_item'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey(
        'shopping_session.id'), nullable=False)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    _quantity = Column(Integer)

    shopping_session = relationship(
        "ShoppingSession", back_populates='cart_items')
    product_entry = relationship("ProductEntry", back_populates='cart_items')

    @hybrid_property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = min(max(quantity, 0), 10000)

    def total(self):
        return (self._quantity)*(self.product_entry.price)


class PaymentDetails(Base, TimestampMixin):

    __tablename__ = 'payment_details'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    provider = Column(String)
    status = Column(String)

    order_details = relationship(
        "OrderDetails", back_populates='payment_details')


class OrderDetails(Base, TimestampMixin):

    __tablename__ = 'order_details'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_id = Column(Integer, ForeignKey(
        'payment_details.id'), nullable=False)
    total = Column(DECIMAL, nullable=False)

    user = relationship("Users", back_populates='orders')
    payment_details = relationship(
        "PaymentDetails", back_populates='order_details')
    order_items = relationship("OrderItem", back_populates='order_details')


class OrderItem(Base, TimestampMixin):

    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order_details.id'), nullable=False)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    quantity = Column(Integer, default=0)

    order_details = relationship("OrderDetails", back_populates='order_items')
    product_entry = relationship("ProductEntry", back_populates='order_item')
