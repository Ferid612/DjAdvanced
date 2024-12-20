from collections import defaultdict
from datetime import datetime
from sqlalchemy import CheckConstraint, Boolean, DateTime, Float, Column, ForeignKey, Integer, String, DECIMAL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from DjAdvanced.settings.production import engine
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

    name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)
    currency_code = Column(String,  nullable=False)
    currency_symbol = Column(String,  nullable=False)
    phone_code = Column(Integer, nullable=False)

    locations = relationship('Location', back_populates='country')

    def to_json(self):
        return {
                "id": self.id,
                "name": self.name,
                "short_name": self.short_name,
                "currency_code": self.currency_code,
                "currency_symbol": self.currency_symbol,
                "phone_code": self.phone_code,
        }



class Location(Base, TimestampMixin):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)    
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)

    city = Column(EncryptedType(String, 'AES'), nullable=False)
    state = Column(EncryptedType(String, 'AES'), nullable=False)
    address_line_1 = Column(EncryptedType(String, 'AES'), nullable=False)
    district = Column(EncryptedType(String, 'AES'))
    postal_code = Column(EncryptedType(String, 'AES'), nullable=False)
    description = Column(EncryptedType(String, 'AES'))

    persons = relationship('Person', back_populates='location')
    employment_jobs = relationship('EmploymentJobs', back_populates='location')
    supplier = relationship('Supplier', back_populates='location')
    country = relationship('Country', back_populates='locations')

    def to_json(self):
        return {
                "id": self.id,
                "country_id": self.country_id,
                "country_name": self.country.name,
                "city": self.city,
                "state": self.state,
                "address_line_1": self.address_line_1,
                "district": self.district,
                "postal_code": self.postal_code,
                "description": self.description,
        }



class PhoneNumber(Base, TimestampMixin):

    __tablename__ = 'phone_number'
    id = Column(Integer, primary_key=True)
    phone_number = Column(EncryptedType(Integer, 'AES'),
                          nullable=False, unique=True)
    country_phone_code = Column(Integer, nullable=False)
    phone_type_id = Column(Integer)

    person = relationship('Person', back_populates='phone_number')
    supplier = relationship('Supplier', back_populates='phone_number')
    
    def to_json(self):
        return {
                "id": self.id,
                "phone_number": self.phone_number,
                "country_phone_code": self.country_phone_code,
                "phone_type_id": self.phone_type_id,
                
        }



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
        return any(child.has_products() for child in self.children)

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
        profil_image = self.profil_image[0].to_json() if self.profil_image else None

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'profil_image': profil_image,
            'location_id': self.location_id,
            'country_phone_code': str(self.phone_number.country_phone_code),
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
    name = Column(String)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    description = Column(String)

    entries = relationship(
        'ProductEntry', back_populates='product', overlaps="products")
    supplier = relationship('Supplier', back_populates='products')
    category = relationship('Category', back_populates='products')

    colors = relationship("ProductColor", secondary="product_entry",
                          primaryjoin="ProductEntry.product_id == Product.id", secondaryjoin="ProductEntry.color_id == ProductColor.id",
                          viewonly=True)

    materials = relationship("ProductMaterial", secondary="product_entry",
                             primaryjoin="ProductEntry.product_id == Product.id", secondaryjoin="ProductEntry.material_id == ProductMaterial.id",
                             viewonly=True)

    sizes = relationship("ProductMeasure", secondary="product_entry",
                         primaryjoin="ProductEntry.product_id == Product.id", secondaryjoin="ProductEntry.measure_value_id == ProductMeasureValue.id",
                         viewonly=True)

    def get_first_image(self):
        return self.entries[0].images[0].to_json() if self.entries[0].images else None

    
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
            'exist_colors': self.get_exist_colors(),
        }

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.get_first_image(),
            'supplier_data': self.supplier.to_json_for_card(),
            'category_data': self.category.to_json(),
            'exist_colors': self.get_exist_colors(),
            'exist_materials': self.get_exist_materials(),
            'exist_sizes': self.get_exist_sizes(),

        }


class ProductImage(Base, TimestampMixin):
    __tablename__ = 'product_image'
    id = Column(Integer, primary_key=True)
    index = Column(Integer, default=0, nullable=False)
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
    tags = relationship('Tag', secondary='product_tag',
                        back_populates='product_entries')

    rates = relationship('ProductRate', back_populates='product_entry')
    fags = relationship('ProductFag', back_populates='product_entry')
    comments = relationship('ProductComment', back_populates='product_entry')

    product_discounts = relationship(
        'ProductDiscount', back_populates='product_entry')

    images = relationship('ProductImage', back_populates='product_entry',  order_by=(
        ProductImage.index, ProductImage.id,))

    color = relationship("ProductColor", back_populates="product_entries")
    material = relationship(
        "ProductMaterial", back_populates="product_entries")

    size = relationship('ProductMeasureValue', back_populates='product_entry')

    cart_items = relationship('CartItem', back_populates='product_entry')
    order_items = relationship('OrderItem', back_populates='product_entry')

    wishlist_product_entry = relationship(
        'WishListProductEntry', back_populates='product_entry')

    product_entry_card_boxs = relationship(
        'ProductEntryCardBox', back_populates='product_entry')

    def get_raters_data(self):
        count = len(self.rates)
        if count == 0:
            return {'count': count, 'avg_rating': 0}

        avg_rating = sum(product_rate.rate for product_rate in self.rates) / count

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
        image = self.images[0].to_json() if self.images else None
        return {
            'product': self.product.to_json_for_entry(),
            'entry': {
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
        images = [image.to_json() for image in self.images] if self.images else None
        size = self.size.to_json() if self.size else None
        rates = [rate.to_json() for rate in self.rates] if self.rates else None
        tags = [tag.to_json() for tag in self.tags] if self.tags else None
        
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
            "rates": rates,
            "fags": self.get_all_fags()['fags_data'],
            "comments": self.get_entry_comments()['comment_tree'],
            "tags": tags,
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


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    product_entries = relationship(
        'ProductEntry', secondary='product_tag', back_populates='tags')

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class ProductTag(Base):
    __tablename__ = 'product_tag'
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)


class Campaign(Base):
    __tablename__ = 'campaign'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    valid_from = Column(DateTime, nullable=False, server_default='now()')
    valid_to = Column(DateTime, nullable=False)
    # Define the relationship to CampaignProduct
    product_entries = relationship('CampaignProduct', back_populates='campaign')

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
        }

    def get_campaign_products(self):
        """
        Get the products associated with the campaign.

        Returns:
            list: A list of campaign product data.
        """
        campaign_products = []

        for campaign_product in self.product_entries:
            campaign_product_data = campaign_product.to_json()
            campaign_products.append(campaign_product_data)

        return campaign_products


class CampaignProduct(Base):
    __tablename__ = 'campaign_product'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity_required = Column(Integer, nullable=False)
    quantity_discounted = Column(Integer, nullable=False)

    # Define the relationship to Campaign
    campaign = relationship('Campaign', back_populates='product_entries')
    product_entry = relationship('Product')

    def to_json(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "product_id": self.product_id,
            "quantity_required": self.quantity_required,
            "quantity_discounted": self.quantity_discounted,
        }



class ProductMeasureValue(Base):
    __tablename__ = 'product_measure_value'
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
    measure_id = Column(Integer, ForeignKey(
        'product_measure.id', ondelete='CASCADE'), nullable=False, index=True)
    measure = relationship('ProductMeasure', back_populates='values')
    product_entry = relationship('ProductEntry', back_populates='size',
                                 cascade="all, delete", lazy="joined", overlaps="sizes")

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
            'product_id': self.product_entry.product.id,
            'product_name': self.product_entry.product.name,
            'product_description': self.product_entry.product.description,
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



    def to_json(self):
        return {
            'id': self.id,
            'product_entry_id': self.product_entry_id,
            'person_id': self.person_id,
            'parent_comment_id': self.parent_comment_id,
            'comment_text': self.comment_text,
            'status': self.status,
        }


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
    gender = Column(String, CheckConstraint(
        "gender IN ('man', 'woman')"), default='woman')

    email = Column(EncryptedType(String, 'AES'), unique=True,
                   nullable=False)
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
    employee = relationship('Employees', uselist=False, back_populates='person')
    user = relationship('Users', uselist=False, back_populates='person')
    profil_image = relationship('ProfilImage',uselist=False, back_populates='person')
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
            person_profil_image = self.profil_image.to_json()

        user_id = None
        employee_id = None
        if self.person_type == 'user':
            user_id = self.user.id if self.user else None
        else:
            employee_id = self.employee.id if self.employee else None

        location_data = self.location.to_json() if self.location else None
        return {
            'person_id': self.id,
            'user_id': user_id,
            'employee_id': employee_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'location_data': location_data,
            'phone_number': self.phone_number.to_json(),

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
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    job_title = Column(String, nullable=False, unique=True)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)

    location = relationship('Location', back_populates='employment_jobs')
    employees = relationship('Employees', back_populates='employment_job')


class Users(Base, TimestampMixin):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'),
                       unique=True, nullable=False)

    person = relationship('Person', back_populates='user', lazy='joined')
    user_user_group_role = relationship(
        'UserUserGroupRole', back_populates='users')
    credit_cards = relationship('CreditCard', back_populates='user')
    shopping_session = relationship('ShoppingSession', back_populates='user')
    orders = relationship('Order', back_populates='user')
    product_rates = relationship('ProductRate', back_populates='user')
    wishlists = relationship('WishList', back_populates='user')
    discount_coupons = relationship('DiscountCoupon', secondary='discount_coupon_user',
                                    back_populates='users', overlaps="discount_coupon_users")
    discount_coupon_users = relationship(
        'DiscountCouponUser', back_populates='user', overlaps="discount_coupons")

    def get_user_discount_coupons(self):
        return [discount_coupons.to_json() for discount_coupons in self.discount_coupons]

    def get_user_wishlists_list(self, count):
        return [wishlist.to_json(count) for wishlist in self.wishlists]


class CreditCard(Base):
    __tablename__ = 'credit_card'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_number = Column(EncryptedType(String(50), 'AES'), nullable=False)
    expiration_date = Column(String(10), nullable=False)
    cvv = Column(EncryptedType(String(10), 'AES'), nullable=False)

    user = relationship("Users", back_populates='credit_cards')


class DiscountCoupon(Base, TimestampMixin):
    __tablename__ = 'discount_coupon'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False, unique=True)
    discount = Column(Float, nullable=False)
    valid_from = Column(DateTime, nullable=False, server_default='now()')
    valid_to = Column(DateTime, nullable=False)
    users = relationship('Users', secondary='discount_coupon_user',
                         back_populates='discount_coupons', overlaps="discount_coupon_users")
    orders = relationship('Order', back_populates='discount_coupon')

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "discount": self.discount,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
        }


class DiscountCouponUser(Base):
    __tablename__ = 'discount_coupon_user'
    is_active = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, primary_key=True)
    discount_coupon_id = Column(Integer, ForeignKey(
        'discount_coupon.id'), nullable=False, primary_key=True)
    user = relationship(
        'Users', back_populates='discount_coupon_users', overlaps="discount_coupons,users")


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
            wishlist_product_entries = [wishlist_product_entry.to_json(
            ) for wishlist_product_entry in self.wishlist_product_entries[:count]]
        else:
            wishlist_product_entries = [wishlist_product_entry.to_json(
            ) for wishlist_product_entry in self.wishlist_product_entries]

        return {
            'id': self.id,
            'user_id': self.user_id,
            'length':len(self.wishlist_product_entries),
            'title': self.title,
            'product_entries': wishlist_product_entries
        }


    def to_json_light(self):
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'length':len(self.wishlist_product_entries),
            'title': self.title,
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


class ShoppingSession(Base, TimestampMixin):

    __tablename__ = 'shopping_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     unique=True, nullable=False)

    user = relationship('Users', back_populates='shopping_session')
    cart_items = relationship('CartItem', back_populates='shopping_session')

    def total(self):
        return sum(
            item.product_entry.price * item.quantity
            for item in self.cart_items
            if item.status == 'inOrder'
        )

    def get_count_of_cart_items(self):
        return len(self.cart_items)

    def calculate_supplier_prices_and_cargo_discounts(self, amount_to_be_paid, cart_items_in_order):
        """
        Calculates the total price of each supplier's products and applies cargo discounts if applicable.
        Returns a tuple of (supplier_prices, supplier_cargo_discounts, amount_to_be_paid)
        """

        supplier_prices = {}
        for cart_item in cart_items_in_order:
            product_entry = cart_item.product_entry
            if product_entry.cargo_active:
                supplier = product_entry.product.supplier
                price = product_entry.price * cart_item.quantity
                if supplier not in supplier_prices:
                    supplier_prices[supplier] = price
                else:
                    supplier_prices[supplier] += price

        supplier_cargo_discounts = []
        for supplier, price in supplier_prices.items():
            if not supplier.cargo_min_limit:
                supplier.cargo_min_limit = 1.0
                supplier.cargo_percent = 0.0
            if (price > supplier.cargo_min_limit):
                cargo_discount = float(supplier.cargo_percent) * price

                supplier_cargo_discounts.append(
                    {"supplier_name": supplier.name, "cargo_discount": cargo_discount})
                amount_to_be_paid -= cargo_discount

        return supplier_prices, supplier_cargo_discounts, amount_to_be_paid

    def get_user_shopping_session_data(self, session):
        """
        Retrieves all the cart items for the authenticated user and returns them along with the corresponding product data.
        """

        # Eager load related data
        cart_items_in_cart = self.cart_items
        cart_items_in_order = filter(
            lambda x: x.status == 'inOrder', cart_items_in_cart)
        shopping_session_total = self.total()

        # Calculate discounts and cargo fees
        whole_discounts = sum(cart_item.calculate_discounts()
                              for cart_item in cart_items_in_order)
        whole_cargo_fee = sum(cart_item.calculate_cargo_fee()
                              for cart_item in cart_items_in_order)

        # Calculate total amount to be paid
        amount_to_be_paid = shopping_session_total - whole_discounts + whole_cargo_fee

        supplier_prices,\
                supplier_cargo_discounts,\
                amount_to_be_paid = self.calculate_supplier_prices_and_cargo_discounts(
                amount_to_be_paid, cart_items_in_order)

        coupon_discount_data = {}
        # Check Discount coupon is assign or not
        active_coupon = session.query(DiscountCoupon).join(DiscountCouponUser).filter(
            DiscountCouponUser.user_id == self.user_id,
            DiscountCouponUser.is_active == True,
            DiscountCoupon.valid_from <= datetime.now(),
            DiscountCoupon.valid_to >= datetime.now()
        ).first()

        if active_coupon is not None:
            coupon_discount = active_coupon.discount

            amount_to_be_paid = amount_to_be_paid - coupon_discount
            amount_to_be_paid = max(amount_to_be_paid, 0)
            coupon_discount_data = active_coupon.to_json()

        # Process cart items
        # Group cart items by supplier name
        cart_item_data = {}
        for cart_item in cart_items_in_cart:
            supplier_name = cart_item.product_entry.product.supplier.name

            if supplier_name not in cart_item_data:
                cart_item_data[supplier_name] = {
                    "supplier_name": supplier_name, "cart_items": []}

            cart_item_data[supplier_name]["cart_items"].append(
                cart_item.to_json())

        return {
            'amount_to_be_paid': amount_to_be_paid,
            'total': shopping_session_total,
            'coupon_discount_data': coupon_discount_data,
            'whole_discounts': whole_discounts,
            'whole_cargo_fee': whole_cargo_fee,
            'supplier_cargo_discounts': supplier_cargo_discounts,
            "suppliers": list(cart_item_data.values())
        }


class CartItem(Base, TimestampMixin):

    __tablename__ = 'cart_item'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey(
        'shopping_session.id'), nullable=False)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    _quantity = Column(Integer)
    status = Column(String(50), CheckConstraint(
        "status IN ('inCart','inOrder')"), nullable=False, default='inOrder')
    shopping_session = relationship(
        "ShoppingSession", back_populates='cart_items')
    product_entry = relationship(
        "ProductEntry", back_populates='cart_items')

    @hybrid_property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = min(max(quantity, 0), 100000)

    def calculate_cargo_data(self):
        product_entry = self.product_entry
        cargo_data = {}
        
        if (product_entry.cargo_active) and (product_entry.product.supplier.cargo_percent is not None):
            cargo_percent = float(product_entry.product.supplier.cargo_percent)
            item_cargo_fee = self.total() * cargo_percent
            cargo_data['supplier_cargo_percent'] = cargo_percent
            cargo_data['item_cargo_fee'] = item_cargo_fee
        
        else:
            cargo_data = "Not any cargo fee"
        
        return cargo_data

    # Helper functions for calculating discounts and cargo fees

    def calculate_discounts(self):
        discounts = self.product_entry.product_discounts
        active_discounts = [d for d in discounts if d.discount.active]
        return sum(
            self.total() * float(d.discount.discount_percent) / 100
            for d in active_discounts
        )

    def calculate_cargo_fee(self):
        product_entry = self.product_entry
        if product_entry.cargo_active:
            if product_entry.product.supplier.cargo_percent:
                cargo_percent = float(
                    product_entry.product.supplier.cargo_percent)
            else:
                cargo_percent = 0
            return self.total() * cargo_percent
        return 0

    def total(self):
        return (self._quantity)*(self.product_entry.price)

    def to_json(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'status': self.status,
            'cart_item_total': self.total(),
            'cargo_data':   self.calculate_cargo_data(),
            'product_entry': self.product_entry.to_json_for_card(),
        }


class Payment(Base, TimestampMixin):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), CheckConstraint(
        "payment_method IN ('cash', 'credit_card')"), nullable=False, default='credit_card')
    status = Column(String(50), CheckConstraint(
        "status IN ('pending','completed', 'failed')"), nullable=False, default='pending')

    order = relationship('Order', back_populates='payment')
    credit_card_payment = relationship(
        'CreditCardPayment', uselist=False, back_populates='payment')
    cash_payment = relationship(
        'CashPayment', uselist=False, back_populates='payment')

    def to_json(self):
        if self.payment_method == 'cash':
            payment_id = self.cash_payment.id
            credit_card_details = None
        else:
            payment_id = self.credit_card_payment.id
            credit_card_details = self.credit_card_payment.to_json()

        return {
            "id": self.id,
            "payment_id": payment_id,
            "order_id": self.order_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "status": self.status,
            "credit_card_details": credit_card_details,
        }


class CreditCardPayment(Base):
    __tablename__ = 'credit_card_payment'
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=False)
    card_number = Column(EncryptedType(String(50), 'AES'), nullable=False)
    expiration_date = Column(String(10), nullable=False)
    cvv = Column(EncryptedType(String(10), 'AES'), nullable=False)

    payment = relationship('Payment', back_populates='credit_card_payment')

    def to_json(self):
      
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "card_number": self.card_number,
            "expiration_date": self.expiration_date,
        }



class CashPayment(Base):
    __tablename__ = 'cash_payment'
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=False)
    payment = relationship('Payment', back_populates='cash_payment')



class Order(Base, TimestampMixin):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    discount_coupon_id = Column(Integer, ForeignKey('discount_coupon.id'))
    status = Column(String(50), CheckConstraint(
        "status IN ('preparing','placed', 'shipped', 'delivered', 'cancelled')"), nullable=False, default='placed')

    user = relationship('Users', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')
    payment = relationship('Payment', back_populates='order')
    discount_coupon = relationship('DiscountCoupon', back_populates='orders')

    def to_json(self):
        discount_coupon_data = "No discount coupon for this order"
        payment_data = {"total_price": self.total_price}
        if self.discount_coupon_id:
            discount_coupon_data = self.discount_coupon.to_json()

        if self.payment:
            payment_data = self.payment[0].to_json()

        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.person.username,
            "status": self.status,
            "total_price": self.total_price,
            "discount_coupon_data": discount_coupon_data,
            "payment_data": payment_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class OrderItem(Base, TimestampMixin):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    product_entry_id = Column(Integer, ForeignKey(
        'product_entry.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship('Order', back_populates='order_items')
    product_entry = relationship('ProductEntry', back_populates='order_items')
