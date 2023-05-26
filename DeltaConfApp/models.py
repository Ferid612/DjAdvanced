from sqlalchemy import DateTime, Float, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from DjAdvanced.settings.production import engine
from DjApp.models import Base

class TimestampMixin:
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()', onupdate='now()')
    deleted_at = Column(DateTime, nullable=True)
        


class ImageGallery(Base, TimestampMixin):
    __tablename__ = 'image_gallery'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    slide_photos = relationship('SlidePhotos', back_populates='image_gallery')  
    new_arrival_photos = relationship('NewArrival', back_populates='image_gallery')  
    def to_json(self):
        return {
        'id': self.id,
        'name': self.name,
        'title': self.description,
  }
    


class NewArrival(Base, TimestampMixin):
    __tablename__ = 'new_arrival_photos'
    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False, default=1)
    url = Column(String, nullable = False)
    title = Column(String, unique=True, nullable=False)
    relavant_url = Column(String, nullable=False)
    description = Column(String, nullable=False)
    gallery_id = Column(Integer, ForeignKey('image_gallery.id'), nullable=False) 
    image_gallery = relationship('ImageGallery', back_populates='new_arrival_photos')  


    def to_json(self):
       
        return {
        'id': self.id,
        'index': self.index,
        'url': self.url,
        'relavant_url': self.relavant_url,
        'title': self.title,
        'description': self.description,
        'gallery_id': self.gallery_id,
        }
    
    
class SlidePhotos(Base, TimestampMixin):
    __tablename__ = 'slide_photos'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable = False)
    title = Column(String, unique=True, nullable=False)
    relavant_url = Column(String, nullable=False)
    
    gallery_id = Column(Integer, ForeignKey('image_gallery.id'), nullable=False) 
    image_gallery = relationship('ImageGallery', back_populates='slide_photos')  


    def to_json(self):
       
        return {
        'id': self.id,
        'url': self.url,
        'title': self.title,
        'relavant_url': self.relavant_url,
        'gallery_id': self.gallery_id,
        }
        
        
class CardBox(Base, TimestampMixin):
    __tablename__ = 'card_box'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    product_entry_card_boxs = relationship('ProductEntryCardBox', back_populates='card_box')
    
    def to_json(self):
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        }

    def to_json_with_entries(self):
        entries = [product_entry_card_box.product_entry.to_json_for_card() for product_entry_card_box in self.product_entry_card_boxs]
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'product_entries': entries,
        }


class ProductEntryCardBox(Base, TimestampMixin):
    __tablename__ = 'product_entry_card_box'
    id = Column(Integer,primary_key=True)
    card_box_id = Column(Integer, ForeignKey('card_box.id'), nullable=False)
    product_entry_id = Column(Integer, ForeignKey('product_entry.id'),nullable=False)

    card_box = relationship('CardBox', back_populates='product_entry_card_boxs')
    product_entry = relationship('ProductEntry', back_populates='product_entry_card_boxs')
    
    
    def to_json(self):
        return {
        'id': self.id,
        'card_box_id': self.card_box_id,
        'product_entry_id': self.product_entry_id,
        }   


        
Base.metadata.create_all(engine)
  