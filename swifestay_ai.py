  from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, ImageEnhance
import io, base64

app = FastAPI(title="SwiftStayAI Backend")

# CORS: allow all while developing (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Preloaded hotels in Southeastern Nigeria (Anambra, Enugu, Imo, Abia, Ebonyi)
HOTELS_SE = [
    {"name": "Nike Lake Resort", "city": "Enugu", "state": "Enugu", "rating": 4.6, "price": 25000, "amenities": ["Pool","Wi-Fi","Restaurant"]},
    {"name": "Golden Tulip", "city": "Onitsha", "state": "Anambra", "rating": 4.4, "price": 22000, "amenities": ["Wi-Fi","Gym","Bar"]},
    {"name": "Rockview Owerri", "city": "Owerri", "state": "Imo", "rating": 4.5, "price": 20000, "amenities": ["Wi-Fi","Restaurant","Parking"]},
    {"name": "Hotel Royal Damgrete", "city": "Umuahia", "state": "Abia", "rating": 4.4, "price": 21000, "amenities": ["Wi-Fi","Gym","Breakfast"]},
    {"name": "Salt Spring Resort", "city": "Abakaliki", "state": "Ebonyi", "rating": 4.3, "price": 18000, "amenities": ["Wi-Fi","Pool","Spa"]},
]

@app.get("/recommendations")
def recommendations(limit: int = 8, sort_by: str = "rating"):
    # sort by rating (desc) or price (asc)
    if sort_by == "price":
        hotels = sorted(HOTELS_SE, key=lambda h: h["price"])
    else:
        hotels = sorted(HOTELS_SE, key=lambda h: h["rating"], reverse=True)
    return {"hotels": hotels[:limit]}

def _enhance_image_pil(img: Image.Image) -> Image.Image:
    # Mild, pleasing enhancements (safe defaults)
    img = ImageEnhance.Brightness(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    return img

@app.post("/enhance-photo")
async def enhance_photo(file: UploadFile = File(...)):
    # Load uploaded image
    original = Image.open(file.file).convert("RGB")
    enhanced = _enhance_image_pil(original)

    # Return as base64 (so frontend can preview without saving)
    out = io.BytesIO()
    enhanced.save(out, format="JPEG", quality=88)
    out.seek(0)
    b64 = base64.b64encode(out.read()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{b64}"
    return {"message": "Photo enhanced successfully", "enhanced_data_url": data_url}

@app.post("/onboard-hotel")
async def onboard_hotel(
    name: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    amenities: str = Form(""),
    photo: UploadFile = File(None)
):
    # Simple amenity auto-suggest if none provided
    if not amenities.strip():
        base = ["Free Wi-Fi","Parking","24/7 Front Desk","Air Conditioning"]
        # lightweight tailoring
        suggested = base + (["Breakfast"] if state.lower() in ["enugu","imo","anambra","abia","ebonyi"] else [])
        amenities = ", ".join(suggested)

    enhanced_url = None
    if photo is not None:
        # enhance uploaded photo and return preview url
        original = Image.open(photo.file).convert("RGB")
        enhanced = _enhance_image_pil(original)
        out = io.BytesIO()
        enhanced.save(out, format="JPEG", quality=88)
        out.seek(0)
        b64 = base64.b64encode(out.read()).decode("utf-8")
        enhanced_url = f"data:image/jpeg;base64,{b64}"

    payload = {
        "message": f"Hotel '{name}' onboarded for {city}, {state}.",
        "amenities": amenities,
        "enhanced_photo": enhanced_url
    }
    return JSONResponse(payload)