# Fable — Digital Closet App

A personal wardrobe management app that lets you catalogue your clothing, generate outfit combinations, and save looks to a lookbook.

---

## Features

**Wardrobe**
- Upload clothing items with a photo, name, category, vibe, and gender
- Filter your closet by vibe (Formal, Traditional, Casual, Gym Wear) and gender
- Delete items from your wardrobe

**Outfit Generator**
- Select a gender and vibe to generate a color-balanced outfit from your wardrobe
- Automatically detects the dominant color of each clothing item from its photo
- Applies basic color theory — at most one bold-colored item per outfit
- Bold colors: red, pink, orange, yellow, purple, green, blue
- Neutral colors: white, black, grey, beige, navy, brown
- Supports dress-based and top/bottom/shoes combinations for female outfits
- Save generated outfits directly to your lookbook

**Lookbook**
- View all saved outfits with their clothing items
- Filter saved looks by vibe and gender
- Delete looks you no longer want

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | React 19, CSS Modules             |
| Backend  | FastAPI, SQLAlchemy, SQLite        |
| Server   | Uvicorn                           |

---

## Project Structure

```
closet-app/
├── backend/
│   ├── main.py          # API routes + color detection + outfit logic
│   ├── models.py        # Database models
│   ├── database.py      # DB connection and session
│   ├── uploads/         # Uploaded clothing images (not tracked in git)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/  # React components
    │   └── styles/      # CSS modules
    └── package.json
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000`. Requests to the backend are proxied automatically via the `proxy` field in `package.json`.

---

## API Endpoints

| Method | Endpoint               | Description                        |
|--------|------------------------|------------------------------------|
| GET    | /items                 | Get all clothing items             |
| POST   | /items                 | Upload a new item                  |
| DELETE | /items/{id}            | Delete an item                     |
| GET    | /generate-outfit       | Generate a color-balanced outfit   |
| GET    | /outfits               | Get all saved outfits              |
| POST   | /outfits               | Save an outfit                     |
| DELETE | /outfits/{id}          | Delete a saved outfit              |

---

## Notes

- Uploaded images are stored in `backend/uploads/` and served as static files
- Each uploaded file is renamed with a UUID prefix to prevent filename collisions
- The database is a local SQLite file at `backend/closet.db`
- `backend/uploads/` and `backend/closet.db` are excluded from version control via `.gitignore`
- Color is detected automatically from the uploaded image using `colorthief` — no user input required
- If color detection fails for an image, the item defaults to neutral and will still appear in outfit generation
