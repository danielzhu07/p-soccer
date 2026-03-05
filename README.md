# p-soccer

Computer vision software that analyzes soccer game footage. Upload a video on the webpage; the backend runs a fine-tuned YOLOv8 model and returns an annotated video plus statistics.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the system diagram and flow.

## Run the app

1. **Create a virtual environment and install dependencies** (from project root):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   pip install -r backend/requirements.txt
   ```

2. **Start the server** (from project root):

   ```bash
   uvicorn backend.app.main:app --reload
   ```

3. **Open the webpage**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

4. Upload a video file. When processing finishes, you can view statistics and download the annotated video.

## Model

- By default the app uses the pretrained **YOLOv8n** model (downloaded automatically on first run).
- To use your own **fine-tuned soccer model**, place weights at `models/soccer_yolov8/best.pt` (or set the `MODEL_PATH` environment variable).

## Data

- Uploaded videos and results are stored under `data/jobs/` (or `JOBS_DIR`). You can delete this folder to free space.
