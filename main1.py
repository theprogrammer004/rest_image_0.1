from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Maximum allowed size of uploaded file (50KB = 50 * 1024 bytes)
MAX_IMAGE_SIZE = 50 * 1024  # 50KB
IMAGE_FOLDER = 'images'
LATEST_IMAGE_PATH = os.path.join(IMAGE_FOLDER, 'latest_image.jpg')

# Ensure the images directory exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Endpoint to upload an image to the API
@app.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    # Read image content
    image_data = await image.read()

    # Check image size (limit to 50KB)
    if len(image_data) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image too large, must be 50KB or less")

    # Save the image as the latest image
    with open(LATEST_IMAGE_PATH, "wb") as f:
        f.write(image_data)

    return {"message": "Image uploaded successfully"}

# Endpoint for ESP32 to get the latest image
@app.get("/get_latest_image")
async def get_latest_image():
    if os.path.exists(LATEST_IMAGE_PATH):
        return FileResponse(LATEST_IMAGE_PATH, media_type='image/jpeg')
    else:
        raise HTTPException(status_code=404, detail="No image available")

# FastAPI includes automatic interactive API documentation at /docs
