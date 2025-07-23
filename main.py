from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from analysis import get_top_players_by_year

app = FastAPI()

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "VCT Top Players API"}

@app.get("/top-players")
def top_players(year: int):
    if year < 2021 or year > 2025:
        raise HTTPException(status_code=400, detail="Year must be between 2021 and 2025")
    
    try:
        top_players_dict = get_top_players_by_year(year, data_folder="data")
        
        # Convert DataFrames to JSON-serializable format
        result = {
            tournament: df.to_dict(orient="records")
            for tournament, df in top_players_dict.items()
        }
        return {"year": year, "top_players": result}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data found for year {year}")

