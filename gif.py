from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Global variable to store WebSocket connections
connected_clients = []

# Maximum allowed size of uploaded file (200KB for GIFs)
MAX_IMAGE_SIZE = 200 * 1024  # 200KB
IMAGE_FOLDER = 'images'
LATEST_IMAGE_PATH = os.path.join(IMAGE_FOLDER, 'latest_image.gif')  # Now handling GIF files

# Ensure the images directory exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Endpoint to upload an image to the API
@app.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    # Read image content
    image_data = await image.read()

    # Check image size (limit to 200KB for GIFs)
    if len(image_data) > MAX_IMAGE_SIZE:
        return {"error": f"Image too large, must be {MAX_IMAGE_SIZE / 1024}KB or less"}

    # Save the image as the latest image (GIF)
    with open(LATEST_IMAGE_PATH, "wb") as f:
        f.write(image_data)

    # Notify all connected WebSocket clients about the new image
    for client in connected_clients:
        try:
            await client.send_text("new_image_uploaded")
        except Exception as e:
            print(f"Failed to notify client: {e}")

    return {"message": "GIF uploaded successfully"}

# Endpoint for ESP32 to get the latest GIF
@app.get("/get_latest_image")
async def get_latest_image():
    if os.path.exists(LATEST_IMAGE_PATH):
        return FileResponse(LATEST_IMAGE_PATH, media_type='image/gif')  # Change to 'image/gif'
    else:
        return {"error": "No image available"}

# WebSocket endpoint for real-time notifications
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection open to maintain connection state
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        connected_clients.remove(websocket)  # Remove client from the connected clients list
    except Exception as e:
        print(f"WebSocket error: {e}")
        connected_clients.remove(websocket)  # Clean up the client on any other error
