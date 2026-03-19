from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

saved_outfit_items = Table(
    "saved_outfit_items",
    Base.metadata,
    Column("outfit_id", Integer, ForeignKey("saved_outfits.id"), primary_key=True),
    Column("item_id", Integer, ForeignKey("clothing_items.id"), primary_key=True),
)

class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    vibe = Column(String, nullable=False)
    gender = Column(String, nullable=False, default="Unisex")
    img_url = Column(String, nullable=False)

    outfits = relationship("SavedOutfit", secondary=saved_outfit_items, back_populates="items")


class SavedOutfit(Base):
    __tablename__ = "saved_outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="My Outfit")
    vibe = Column(String, nullable=False)
    gender = Column(String, nullable=False, default="Unisex")

    items = relationship("ClothingItem", secondary=saved_outfit_items, back_populates="outfits")