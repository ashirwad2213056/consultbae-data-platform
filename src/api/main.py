import os
import subprocess
import json
import shutil
import re
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Initialize ffmpeg binaries in path
import static_ffmpeg
static_ffmpeg.add_paths()

from src.database.connection import get_connection
from src.ingestion.resolve_identities import normalize_phone

app = FastAPI(title="ConsultBae Audio Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount the static directory so the frontend can retrieve the files natively via URL
app.mount("/media", StaticFiles(directory=UPLOAD_DIR), name="media")


def extract_metadata(file_path):
    # Use ffprobe to extract duration, sample_rate, bitrate
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0, 0, 0
    
    data = json.loads(result.stdout)
    
    duration = 0.0
    sample_rate = 0
    bitrate = 0
    
    if "format" in data:
        duration = float(data["format"].get("duration", 0.0))
        bitrate = int(data["format"].get("bit_rate", 0) or 0)
    
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            sample_rate = int(stream.get("sample_rate", 0) or 0)
            if not duration and "duration" in stream:
                duration = float(stream["duration"])
            if not bitrate and "bit_rate" in stream:
                bitrate = int(stream["bit_rate"])
            break
            
    return duration, sample_rate, int(bitrate / 1000) if bitrate else 0  # converted to kbps

def extract_loudness(file_path):
    # Use ffmpeg with volumedetect
    cmd = [
        "ffmpeg", "-i", file_path, "-af", "volumedetect", "-vn", "-sn", "-dn", "-f", "null", "NUL"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # The output of ffmpeg is on stderr
    output = result.stderr
    
    # regex to find max_volume or mean_volume
    match = re.search(r"mean_volume:\s*([-0-9.]+)\s*dB", output)
    if match:
        return float(match.group(1))
    return 0.0


@app.post("/api/submissions")
async def create_submission(
    name: str = Form(...),
    phone: str = Form(...),
    audio: UploadFile = File(...)
):
    normalized_phone = normalize_phone(phone)
    if not normalized_phone:
        raise HTTPException(status_code=400, detail="Invalid phone number format.")
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT worker_id FROM core.workers WHERE phone_10 = %s LIMIT 1", 
                (normalized_phone,)
            )
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="No matching worker found in Core database.")
            
            worker_id = result[0]
            
            file_name_safe = os.path.basename(audio.filename.replace(" ", "_"))
            file_path = os.path.join(UPLOAD_DIR, f"{worker_id}_{file_name_safe}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)
                
            duration, sample_rate, bitrate = extract_metadata(file_path)
            loudness = extract_loudness(file_path)
            
            # The URL path for the frontend
            db_file_path = f"/media/{worker_id}_{file_name_safe}"
            
            cur.execute(
                """
                INSERT INTO core.audio_submissions 
                (worker_id, file_path, duration_seconds, sample_rate_hz, bitrate_kbps, loudness_db)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING submission_id
                """,
                (worker_id, db_file_path, duration, sample_rate, bitrate, loudness)
            )
            submission_id = cur.fetchone()[0]
            conn.commit()
            
            return {"success": True, "submission_id": submission_id}
            
    finally:
        conn.close()


@app.get("/api/submissions")
async def get_submissions():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.submission_id, a.worker_id, w.canonical_name, w.phone_10, a.file_path,
                       CAST(a.duration_seconds AS FLOAT) as duration_seconds, 
                       a.sample_rate_hz, a.bitrate_kbps, 
                       CAST(a.loudness_db AS FLOAT) as loudness_db, a.submitted_at
                FROM core.audio_submissions a
                JOIN core.workers w ON a.worker_id = w.worker_id
                ORDER BY a.submitted_at DESC
                """
            )
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()
