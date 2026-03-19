import os
import random
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import ClothingItem, SavedOutfit

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS - allows React to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images as static files
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ─── CLOTHING ITEMS ───────────────────────────────────────────

@app.get("/items")
def get_items(vibe: str = None, gender: str = None, db: Session = Depends(get_db)):
    query = db.query(ClothingItem)
    if vibe:
        query = query.filter(ClothingItem.vibe == vibe)
    if gender:
        query = query.filter(ClothingItem.gender.in_([gender, "Unisex"]))
    return query.all()


@app.post("/items")
async def create_item(
    name: str = Form(...),
    category: str = Form(...),
    vibe: str = Form(...),
    gender: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    img_url = f"/uploads/{file.filename}"
    item = ClothingItem(name=name, category=category, vibe=vibe, gender=gender, img_url=img_url)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Delete image file from disk
    file_path = f".{item.img_url}"
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}


# ─── OUTFIT GENERATOR ─────────────────────────────────────────

@app.get("/generate-outfit")
def generate_outfit(vibe: str, gender: str, db: Session = Depends(get_db)):
    def pick(category):
        items = db.query(ClothingItem).filter(
            ClothingItem.vibe == vibe,
            ClothingItem.category == category,
            ClothingItem.gender.in_([gender, "Unisex"])
        ).all()
        return random.choice(items) if items else None

    outfit = {
        "top": pick("Top"),
        "bottom": pick("Bottom"),
        "shoes": pick("Shoes"),
        "outerwear": pick("Outerwear"),
    }

    if not any(outfit.values()):
        raise HTTPException(status_code=404, detail="No items found for this vibe and gender")

    return outfit

# ─── LOOKBOOK / SAVED OUTFITS ─────────────────────────────────

@app.get("/outfits")
def get_outfits(db: Session = Depends(get_db)):
    return db.query(SavedOutfit).all()


@app.post("/outfits")
def save_outfit(
    name: str = Form(...),
    vibe: str = Form(...),
    item_ids: str = Form(...),
    db: Session = Depends(get_db),
):
    ids = [int(i) for i in item_ids.split(",") if i]
    items = db.query(ClothingItem).filter(ClothingItem.id.in_(ids)).all()

    outfit = SavedOutfit(name=name, vibe=vibe, items=items)
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit


@app.delete("/outfits/{outfit_id}")
def delete_outfit(outfit_id: int, db: Session = Depends(get_db)):
    outfit = db.query(SavedOutfit).filter(SavedOutfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    db.delete(outfit)
    db.commit()
    return {"message": "Outfit deleted"}