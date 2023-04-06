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
        

class ImageGallery(Base, TimestampMixin):
    __tablename__ = 'image_gallery'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    slide_photos = relationship('SlidePhotos', back_populates='image_gallery')  
    def to_json(self):
        return {
        'id': self.id,
        'url': self.name,
        'title': self.description,
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
        if self.image_gallery:
            image_gallery_id = self.image_gallery.id 
            image_gallery_name = self.image_gallery.name 
        else:
            image_gallery_id= -1
            image_gallery_name = "Not" 
       
        return {
        'id': self.id,
        'url': self.url,
        'title': self.title,
        'relavant_url': self.relavant_url,
        'gallery_id': self.gallery_id,
        }
        
Base.metadata.create_all(engine)
  