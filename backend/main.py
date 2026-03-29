import os
import random
import shutil
import uuid
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
        query = query.filter(ClothingItem.vibe.contains(vibe))
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
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{UPLOAD_DIR}/{unique_name}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    img_url = f"/uploads/{unique_name}"
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
    def get(category):
        items = db.query(ClothingItem).filter(
            ClothingItem.vibe.contains(vibe),
            ClothingItem.category == category,
            ClothingItem.gender.in_([gender, "Unisex"])
        ).all()
        return random.choice(items) if items else None

    def has(category):
        return db.query(ClothingItem).filter(
            ClothingItem.vibe.contains(vibe),
            ClothingItem.category == category,
            ClothingItem.gender.in_([gender, "Unisex"])
        ).count() > 0

    if gender == "Female":
        option_a = has("Top") and has("Bottom") and has("Shoes")
        option_b = has("Dress") and has("Shoes")
        if not option_a and not option_b:
            raise HTTPException(status_code=404, detail="Add more clothes to generate this look")
        if option_a and option_b:
            use_dress = random.choice([True, False])
        else:
            use_dress = option_b
        if use_dress:
            return { "dress": get("Dress"), "shoes": get("Shoes") }
        else:
            return { "top": get("Top"), "bottom": get("Bottom"), "shoes": get("Shoes") }
    else:
        if not (has("Top") and has("Bottom") and has("Shoes")):
            raise HTTPException(status_code=404, detail="Add more clothes to generate this look")
        return { "top": get("Top"), "bottom": get("Bottom"), "shoes": get("Shoes") }

# ─── LOOKBOOK / SAVED OUTFITS ─────────────────────────────────

@app.get("/outfits")
def get_outfits(db: Session = Depends(get_db)):
    outfits = db.query(SavedOutfit).all()
    return [
        {
            "id": o.id,
            "name": o.name,
            "vibe": o.vibe,
            "gender": o.gender,
            "items": [
                {"id": i.id, "name": i.name, "category": i.category,
                 "vibe": i.vibe, "gender": i.gender, "img_url": i.img_url}
                for i in o.items
            ],
        }
        for o in outfits
    ]


@app.post("/outfits")
def save_outfit(
    name: str = Form(...),
    vibe: str = Form(...),
    item_ids: str = Form(...),
    gender: str = Form(...),
    db: Session = Depends(get_db),
):
    ids = [int(i) for i in item_ids.split(",") if i]
    items = db.query(ClothingItem).filter(ClothingItem.id.in_(ids)).all()

    outfit = SavedOutfit(name=name, vibe=vibe, gender=gender, items=items)
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