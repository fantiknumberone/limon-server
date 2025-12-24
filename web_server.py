from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uvicorn
from database import get_points, get_stats

app = FastAPI(title="Карта сигнала dBm")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def api_data(limit: int = 1000):
    points = await get_points(limit)
    return {"points": points}

@app.get("/api/stats")
async def api_stats():
    return await get_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)