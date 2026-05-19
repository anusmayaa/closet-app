import os
import random
import shutil
import uuid
import math
from colorthief import ColorThief
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
    color = detect_color(file_path)
    item = ClothingItem(name=name, category=category, vibe=vibe, gender=gender, color=color, img_url=img_url)
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


# ─── COLOR DETECTION ─────────────────────────────────────────

COLOR_REFERENCES = {
    "red":    (160, 35,  45),
    "pink":   (220, 120, 140),
    "orange": (190, 100, 35),
    "yellow": (200, 170, 80),
    "purple": (100, 50,  110),
    "green":  (10,  60,  50),
    "blue":   (50,  90,  160),
    "white":  (210, 210, 210),
    "black":  (38,  33,  31),
    "grey":   (120, 120, 120),
    "beige":  (195, 175, 145),
    "navy":   (20,  30,  80),
    "brown":  (130, 80,  45),
}

BOLD_COLORS = {"red", "pink", "orange", "yellow", "purple", "green", "blue"}

def rgb_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def detect_color(image_path: str) -> str:
    try:
        palette = ColorThief(image_path).get_palette(color_count=8, quality=1)
        # exclude near-black shadows and near-white backgrounds
        def is_shadow(rgb): return max(rgb) < 50 and (max(rgb) - min(rgb)) < 15
        def is_background(rgb): return min(rgb) > 220
        filtered = [c for c in palette if not is_shadow(c) and not is_background(c)]
        candidates = filtered if filtered else palette
        best_color, best_dist = "neutral", float("inf")
        for rgb in candidates:
            match = min(COLOR_REFERENCES, key=lambda n: rgb_distance(rgb, COLOR_REFERENCES[n]))
            dist = rgb_distance(rgb, COLOR_REFERENCES[match])
            if dist < best_dist:
                best_dist = dist
                best_color = match
        return best_color
    except Exception:
        return "neutral"

def is_bold(item) -> bool:
    return item.color in BOLD_COLORS

def boldness_score(item) -> float:
    """Lower = closer to neutral. Used as fallback when no neutrals exist."""
    ref = COLOR_REFERENCES.get(item.color, (128, 128, 128))
    neutral_center = (128, 128, 128)
    return rgb_distance(ref, neutral_center)

def build_outfit(pools):
    categories = list(pools.keys())
    outfit = []
    chosen = []

    for cat in categories:
        pool = pools[cat]
        bold_chosen = any(is_bold(i) for i in chosen)
        if bold_chosen:
            neutrals = [i for i in pool if not is_bold(i)]
            pick = random.choice(neutrals) if neutrals else min(pool, key=boldness_score)
        else:
            pick = random.choice(pool)
        outfit.append((cat, pick))
        chosen.append(pick)

    return {cat.lower(): item for cat, item in outfit}

# ─── OUTFIT GENERATOR ─────────────────────────────────────────

@app.get("/generate-outfit")
def generate_outfit(vibe: str, gender: str, db: Session = Depends(get_db)):
    def pool(category):
        return db.query(ClothingItem).filter(
            ClothingItem.vibe.contains(vibe),
            ClothingItem.category == category,
            ClothingItem.gender.in_([gender, "Unisex"])
        ).all()

    def has(category):
        return len(pool(category)) > 0

    def get_pools(categories):
        return {cat: pool(cat) for cat in categories}

    if gender == "Female":
        option_a = has("Top") and has("Bottom") and has("Shoes")
        option_b = has("Dress") and has("Shoes")
        if not option_a and not option_b:
            raise HTTPException(status_code=404, detail="Add more clothes to generate this look")
        if option_a and option_b:
            use_dress = random.choice([True, False])
        else:
            use_dress = option_b
        return build_outfit(get_pools(["Dress", "Shoes"])) if use_dress else build_outfit(get_pools(["Top", "Bottom", "Shoes"]))
    else:
        if not (has("Top") and has("Bottom") and has("Shoes")):
            raise HTTPException(status_code=404, detail="Add more clothes to generate this look")
        return build_outfit(get_pools(["Top", "Bottom", "Shoes"]))

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
