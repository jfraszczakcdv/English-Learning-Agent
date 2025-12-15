import io
from contextlib import asynccontextmanager
import asyncio
import time
import logging
from typing import Annotated

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from kokoro import KPipeline
import whisper

from .tts import generate_speech
from .transcription import transcribe
from .agent import run_streaming_english_learning_agent, run_english_learning_agent
from .config import EnvConfig


kokoro_pipeline: KPipeline | None = None
whisper_model: whisper.Whisper | None = None

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global kokoro_pipeline, whisper_model
    kokoro_pipeline = KPipeline(repo_id="hexgrad/Kokoro-82M", lang_code="a")
    whisper_model = whisper.load_model("base")
    yield


def get_env_config() -> EnvConfig:
    return EnvConfig()


EnvConfigDependency = Annotated[EnvConfig, Depends(get_env_config)]


app: FastAPI = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def measure_time(request: Request, call_next):
    start_time: float = time.perf_counter()
    response = await call_next(request)
    process_time: float = time.perf_counter() - start_time
    logger.info(f"Endpoint {request.url.path} was executed in {process_time:.4f}s")
    return response


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("src/static/index.html", "r", encoding="utf-8") as file:
        html_content: str = file.read()
    return HTMLResponse(content=html_content)


async def run_tts(text: str, websocket: WebSocket) -> None:
    buffer: io.BytesIO = await asyncio.to_thread(
        generate_speech,
        text=text,
        kokoro_pipeline=kokoro_pipeline,
        voice="af_heart"
    )
    await websocket.send_bytes(buffer.getvalue())


@app.get("/tts")
def tts_endpoint(text: str):
    buffer: io.BytesIO = generate_speech(
        text=text,
        kokoro_pipeline=kokoro_pipeline,
        voice="af_heart"
    )

    return StreamingResponse(buffer, media_type="audio/wav", headers={
        "Content-Disposition": f'inline; filename="tts.wav"'
    })


@app.get("/agent")
async def agent_endpoint(text: str, env_config: EnvConfigDependency) -> str:
    output: str = await run_english_learning_agent(
        text=text,
        env_config=env_config
    )
    return output


@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket, env_config: EnvConfigDependency):
    await websocket.accept()
    while True:
        try:
            audio_bytes: bytes = await websocket.receive_bytes()
            await websocket.send_text("Audio received. Processing transcription...")

            transcription: str = await asyncio.to_thread(
                transcribe,
                audio=audio_bytes,
                whisper_model=whisper_model
            )
            logger.info(f"Transcription: {transcription}")
            await websocket.send_text(f"Transcription done: {transcription}")

            await run_streaming_english_learning_agent(
                text=transcription,
                chunk_size=10,
                callback=run_tts,
                env_config=env_config,
                websocket=websocket
            )
        except WebSocketDisconnect:
            logger.info("Client disconnected")
            return
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            await websocket.send_text(f"Error: {str(e)}")
