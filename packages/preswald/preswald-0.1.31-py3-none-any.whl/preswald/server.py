from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
import asyncio
import os
import pkg_resources
import uvicorn
from typing import Dict, Any, Optional, Set, List, Union
from preswald.scriptrunner import ScriptRunner
from preswald.core import (
    get_all_component_states,
    update_component_state,
    get_rendered_components,
    clear_rendered_components,
    connections
)
from preswald.serializer import dumps as json_dumps, loads as json_loads
from preswald.llm import OpenAIService
import json
import signal
import sys
import time
import zlib
import numpy as np
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, inspect
import toml
from preswald.celery_app import parse_connections_task
from celery.result import AsyncResult
from preswald.utils import logger

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCRIPT_PATH: Optional[str] = None

# Store active websocket connections and their states
websocket_connections: Dict[str, WebSocket] = {}
client_states: Dict[str, Dict[str, Any]] = {}
script_runners: Dict[WebSocket, ScriptRunner] = {}

# Store persistent component states
component_states: Dict[str, Any] = {}

# Global variables for connections cache and parsing status
connections_cache: Dict[str, List] = {"connections": []}
connections_parsing_status = {
    "is_parsing": False,
    "last_parsed": None,
    "error": None,
    "task_id": None  # Add task_id tracking
}

# Global flag to track server shutdown state
is_shutting_down = False

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    global is_shutting_down
    logger.info("Received shutdown signal, cleaning up...")
    is_shutting_down = True
    
    # Clean up WebSocket connections
    async def cleanup():
        for client_id, websocket in list(websocket_connections.items()):
            try:
                # Get the script runner for this websocket
                runner = next((r for r in script_runners.values() if r.session_id == client_id), None)
                if runner:
                    await runner.stop()
                    script_runners.pop(next(ws for ws, r in script_runners.items() if r == runner), None)
                
                # Close the websocket
                await websocket.close(code=1000, reason="Server shutting down")
                websocket_connections.pop(client_id, None)
                logger.info(f"Cleaned up connection for client {client_id}")
            except Exception as e:
                logger.error(f"Error cleaning up connection for client {client_id}: {e}")
    
    # Run cleanup in event loop
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(cleanup())
    else:
        loop.run_until_complete(cleanup())
    
    # Exit gracefully
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

try:
    # Get the package's static directory using pkg_resources
    BASE_DIR = pkg_resources.resource_filename('preswald', '')
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    ASSETS_DIR = os.path.join(STATIC_DIR, "assets")

    # Ensure directories exist
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # Mount static files - only mount /assets, not root
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
    logger.info(f"Mounted assets directory: {ASSETS_DIR}")
    
    # Copy default branding files to assets directory
    default_logo = os.path.join(STATIC_DIR, "logo.png")
    default_favicon = os.path.join(STATIC_DIR, "favicon.ico")
    
    if os.path.exists(default_logo):
        import shutil
        # Copy to assets
        shutil.copy2(default_logo, os.path.join(ASSETS_DIR, "logo.png"))
        logger.info("Copied default logo to assets directory")
    else:
        logger.warning(f"Default logo not found at {default_logo}")
    
    if os.path.exists(default_favicon):
        import shutil
        # Copy to assets
        shutil.copy2(default_favicon, os.path.join(ASSETS_DIR, "favicon.ico"))
        logger.info("Copied default favicon to assets directory")
    else:
        logger.warning(f"Default favicon not found at {default_favicon}")

except Exception as e:
    logger.error(f"Error setting up static files: {str(e)}", exc_info=True)
    raise

# Add explicit route for favicon.ico
@app.get("/favicon.ico")
async def get_favicon():
    """Serve favicon.ico from config.toml branding or fallback to assets directory"""
    if SCRIPT_PATH:
        try:
            script_dir = os.path.dirname(SCRIPT_PATH)
            config_path = os.path.join(script_dir, "config.toml")
            import toml
            config = toml.load(config_path)
            
            if "branding" in config and "favicon" in config["branding"]:
                favicon = config["branding"]["favicon"]
                favicon_path = os.path.join(script_dir, favicon)
                logger.info(f"Using favicon from config: {favicon_path}")
                if os.path.exists(favicon_path):
                    return FileResponse(favicon_path)
        except Exception as e:
            logger.warning(f"Error loading favicon from config: {e}")
    
    # Fallback to assets directory
    favicon_path = os.path.join(ASSETS_DIR, "favicon.ico")
    logger.info(f"Using favicon from assets: {favicon_path}")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    
    # Try default favicon as last resort
    default_favicon = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(default_favicon):
        logger.info(f"Using default favicon: {default_favicon}")
        return FileResponse(default_favicon)
        
    raise HTTPException(status_code=404, detail="Favicon not found")

# Add explicit route for static files that aren't in assets
@app.get("/static/{path:path}")
async def get_static(path: str):
    """Serve static files that aren't in assets"""
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def serve_index():
    """Serve the index.html file"""
    try:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            import toml
            script_dir = os.path.dirname(SCRIPT_PATH)
            config_path = os.path.join(script_dir, "config.toml")
            config = toml.load(config_path)
            branding_config = config["branding"]
            # Load config if script path is set
            title = "Preswald"  # Default title
            branding = {
                "name": "Preswald",
                "logo": "/assets/logo.png",
                "favicon": "/assets/favicon.ico",
                "primaryColor": branding_config.get("primaryColor", "#000000")
            }
            
            if SCRIPT_PATH:
                try:
                    script_dir = os.path.dirname(SCRIPT_PATH)
                    config_path = os.path.join(script_dir, "config.toml")
                    logger.info(f"Loading config from {config_path}")
                    import toml
                    config = toml.load(config_path)
                    logger.info(f"Loaded config in server.py: {config}")
                    
                    # Get branding configuration
                    if "branding" in config:
                        branding_config = config["branding"]
                        branding["name"] = branding_config.get("name", branding["name"])
                        # Use branding name as the title
                        title = branding["name"]
                        
                        # Handle logo
                        logo = branding_config.get("logo")
                        if logo:
                            if logo.startswith(("http://", "https://")):
                                branding["logo"] = logo
                                logger.info(f"Using remote logo URL: {logo}")
                            else:
                                # Copy local logo to assets directory
                                logo_path = os.path.join(script_dir, logo)
                                logger.info(f"Looking for logo at: {logo_path}")
                                if os.path.exists(logo_path):
                                    import shutil
                                    # Create a unique filename to avoid conflicts
                                    logo_ext = os.path.splitext(logo_path)[1]
                                    dest_logo_path = os.path.join(ASSETS_DIR, f"logo{logo_ext}")
                                    shutil.copy2(logo_path, dest_logo_path)
                                    branding["logo"] = f"/assets/logo{logo_ext}"
                                    logger.info(f"Copied logo to: {dest_logo_path}")
                                else:
                                    logger.warning(f"Logo file not found at {logo_path}, using default")
                                    # Copy default logo if custom one not found
                                    default_logo = os.path.join(BASE_DIR, "static", "logo.png")
                                    if os.path.exists(default_logo):
                                        shutil.copy2(default_logo, os.path.join(ASSETS_DIR, "logo.png"))
                                        branding["logo"] = "/assets/logo.png"
                                        logger.info("Using default logo")
                        
                        # Handle favicon
                        favicon = branding_config.get("favicon")
                        if favicon:
                            if favicon.startswith(("http://", "https://")):
                                branding["favicon"] = favicon
                                logger.info(f"Using remote favicon URL: {favicon}")
                            else:
                                # Copy local favicon to assets directory
                                favicon_path = os.path.join(script_dir, favicon)
                                logger.info(f"Looking for favicon at: {favicon_path}")
                                if os.path.exists(favicon_path):
                                    import shutil
                                    # Create a unique filename to avoid conflicts
                                    favicon_ext = os.path.splitext(favicon_path)[1]
                                    dest_favicon_path = os.path.join(ASSETS_DIR, f"favicon{favicon_ext}")
                                    shutil.copy2(favicon_path, dest_favicon_path)
                                    branding["favicon"] = f"/assets/favicon{favicon_ext}"
                                    logger.info(f"Copied favicon to: {dest_favicon_path}")
                                else:
                                    logger.warning(f"Favicon file not found at {favicon_path}, using default")
                                    # Copy default favicon if custom one not found
                                    default_favicon = os.path.join(BASE_DIR, "static", "favicon.ico")
                                    if os.path.exists(default_favicon):
                                        shutil.copy2(default_favicon, os.path.join(ASSETS_DIR, "favicon.ico"))
                                        branding["favicon"] = "/assets/favicon.ico"
                                        logger.info("Using default favicon")
                    
                    logger.info(f"Final branding configuration: {branding}")
                    
                except Exception as e:
                    logger.error(f"Error loading config for index: {e}", exc_info=True)
                    # Ensure defaults are used in case of error
                    if not os.path.exists(os.path.join(ASSETS_DIR, "logo.png")):
                        default_logo = os.path.join(BASE_DIR, "static", "logo.png")
                        if os.path.exists(default_logo):
                            shutil.copy2(default_logo, os.path.join(ASSETS_DIR, "logo.png"))
                    
                    if not os.path.exists(os.path.join(ASSETS_DIR, "favicon.ico")):
                        default_favicon = os.path.join(BASE_DIR, "static", "favicon.ico")
                        if os.path.exists(default_favicon):
                            shutil.copy2(default_favicon, os.path.join(ASSETS_DIR, "favicon.ico"))

            # Read and modify the index.html content
            with open(index_path, 'r') as f:
                content = f.read()
                # Replace the title tag content
                content = content.replace('<title>Vite + React</title>', f'<title>{title}</title>')
                
                # Add both ICO and SVG favicon links to ensure compatibility
                favicon_links = f'''    <link rel="icon" type="image/x-icon" href="{branding["favicon"]}" />
    <link rel="shortcut icon" type="image/x-icon" href="{branding["favicon"]}" />'''
                
                # Remove existing favicon link and add new ones
                import re
                content = re.sub(r'<link[^>]*rel="icon"[^>]*>', '', content)
                content = content.replace('<meta charset="UTF-8" />', f'<meta charset="UTF-8" />\n{favicon_links}')
                
                # Add branding data
                branding_script = f'<script>window.PRESWALD_BRANDING = {json.dumps(branding)};</script>'
                content = content.replace('</head>', f'{branding_script}\n</head>')
            
            logger.info(f"Serving index.html with branding: {branding}")
            return HTMLResponse(content)
        else:
            logger.error(f"Index file not found at {index_path}")
            return HTMLResponse("<html><body><h1>Error: Frontend not properly installed</h1></body></html>")
    except Exception as e:
        logger.error(f"Error serving index: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/connections")
async def get_connections():
    """Get all active connections and config-defined connections with metadata"""
    # Try to get latest results before returning
    await update_connections_from_celery()
    
    return {
        "connections": connections_cache["connections"],
        "status": {
            "is_parsing": connections_parsing_status["is_parsing"],
            "last_parsed": connections_parsing_status["last_parsed"],
            "error": connections_parsing_status["error"]
        }
    }

async def update_connections_from_celery():
    """Update connections cache from Celery task result and IPC file"""
    try:
        latest_result = None
        latest_timestamp = 0
        
        task_id = connections_parsing_status.get("task_id")
        if task_id:
            logger.info(f"Checking Celery task result for ID: {task_id}")
            task_result = AsyncResult(task_id)
            logger.info(f"Task status: {task_result.status}")
            
            if task_result and task_result.ready():
                logger.info("Task is ready, getting result")
                result = task_result.get()
                logger.info(f"Raw result from Celery: {result}")
                
                if result and isinstance(result, dict):
                    logger.info(f"Processing Celery result with keys: {result.keys()}")
                    celery_timestamp = result.get("timestamp", 0)
                    if celery_timestamp > latest_timestamp:
                        latest_timestamp = celery_timestamp
                        latest_result = result

        ipc_file = os.environ.get("PRESWALD_IPC_FILE")
        if ipc_file and os.path.exists(ipc_file):
            logger.info(f"Checking IPC file: {ipc_file}")
            try:
                with open(ipc_file, 'r') as f:
                    result = json.load(f)
                    logger.info(f"Read from IPC file: {result}")
                    if result and isinstance(result, dict):
                        logger.info(f"Processing IPC result with keys: {result.keys()}")
                        ipc_timestamp = result.get("timestamp", 0)
                        if ipc_timestamp > latest_timestamp:
                            latest_timestamp = ipc_timestamp
                            latest_result = result
            except Exception as e:
                logger.error(f"Error reading IPC file: {e}", exc_info=True)

        if latest_result:
            logger.info(f"Updating state with result from timestamp: {latest_timestamp}")
            connections_cache["connections"] = latest_result.get("connections", [])
            connections_parsing_status["error"] = latest_result.get("error")
            connections_parsing_status["last_parsed"] = latest_result.get("timestamp")
            connections_parsing_status["is_parsing"] = latest_result.get("is_parsing", False)
            logger.info("Updated connections cache with latest result")

    except Exception as e:
        logger.error(f"Error updating connections from Celery/IPC: {e}", exc_info=True)
        connections_parsing_status["error"] = str(e)
        connections_parsing_status["is_parsing"] = False

async def run_server():
    """Run the FastAPI server with Celery background task"""
    try:
        connections_parsing_status["is_parsing"] = True
        connections_parsing_status["error"] = None
        
        task = parse_connections_task.delay()
        connections_parsing_status["task_id"] = task.id
        logger.info(f"Started background connections parsing task with ID: {task.id}")
        
        async def check_celery_results():
            while True:
                await update_connections_from_celery()
                await asyncio.sleep(5)  # Check every 5 seconds
        
        asyncio.create_task(check_celery_results())
        
        config = uvicorn.Config(app, host="0.0.0.0", port=8501, loop="asyncio")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"Error in server startup: {e}")
        connections_parsing_status["is_parsing"] = False
        connections_parsing_status["error"] = str(e)
        raise

# Add catch-all route for SPA routing
@app.get("/{path:path}")
async def serve_spa(path: str):
    """Serve the SPA for any other routes"""
    return await serve_index()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections"""
    try:
        logger.info(f"[WebSocket] New connection request from client: {client_id}")
        await websocket.accept()
        logger.info(f"[WebSocket] Connection accepted for client: {client_id}")
        
        # Store the connection
        websocket_connections[client_id] = websocket
        
        # Create a script runner for this client
        script_runner = ScriptRunner(
            session_id=client_id,
            send_message_callback=_send_message_callback
        )
        script_runners[websocket] = script_runner
        
        try:
            # Send initial states
            initial_states = get_all_component_states()
            await websocket.send_json({
                "type": "initial_state",
                "states": initial_states
            })
            
            # Run the script initially
            if SCRIPT_PATH:
                await script_runner.start(SCRIPT_PATH)
            
            # Handle incoming messages
            while not is_shutting_down:
                try:
                    message = await websocket.receive_text()
                    await handle_websocket_message(websocket, message)
                except WebSocketDisconnect:
                    logger.info(f"[WebSocket] Client disconnected: {client_id}")
                    break
                except Exception as e:
                    if not is_shutting_down:
                        logger.error(f"[WebSocket] Error handling message: {e}")
                        await send_error(websocket, "Error processing message")
                    break
                    
        except WebSocketDisconnect:
            logger.info(f"[WebSocket] Client disconnected: {client_id}")
        except Exception as e:
            if not is_shutting_down:
                logger.error(f"[WebSocket] Error in connection handler: {e}")
                await send_error(websocket, f"Connection error: {str(e)}")
    finally:
        # Clean up
        if client_id in websocket_connections:
            websocket_connections.pop(client_id)
        if websocket in script_runners:
            runner = script_runners.pop(websocket)
            await runner.stop()

async def handle_websocket_message(websocket: WebSocket, message: str):
    """Handle incoming WebSocket messages"""
    start_time = time.time()
    try:
        data = json_loads(message)
        logger.debug(f"[WebSocket] Received message: {data}")
        
        msg_type = data.get('type')
        if not msg_type:
            logger.error("[WebSocket] Message missing type field")
            await send_error(websocket, "Message missing type field")
            return

        if msg_type == 'component_update':
            states = data.get('states', {})
            if not states:
                logger.warning("[WebSocket] Component update missing states")
                await send_error(websocket, "Component update missing states")
                return
                
            logger.info("[Component Update] Processing updates:")
            update_start = time.time()
            for component_id, value in states.items():
                try:
                    # Update component state
                    update_component_state(component_id, value)
                    logger.info(f"  - Updated {component_id}: {value}")
                    
                    # Broadcast to other clients
                    await broadcast_state_update(component_id, value, exclude_client=websocket)
                    logger.info(f"  - Broadcasted {component_id} update")
                except Exception as e:
                    logger.error(f"Error updating component {component_id}: {e}")
                    await send_error(websocket, f"Failed to update component {component_id}")
                    continue
            logger.info(f"[Component Update] State updates took {time.time() - update_start:.3f}s")

            # Trigger script rerun with all states
            logger.info(f"[Script Rerun] Triggering with states: {states}")
            rerun_start = time.time()
            await rerun_script(websocket, states)
            logger.info(f"[Script Rerun] Script rerun took {time.time() - rerun_start:.3f}s")

    except json.JSONDecodeError as e:
        logger.error(f"[WebSocket] Error decoding message: {e}")
        await send_error(websocket, "Invalid message format")
    except Exception as e:
        logger.error(f"[WebSocket] Error processing message: {e}")
        await send_error(websocket, f"Error processing message: {str(e)}")
    finally:
        logger.info(f"[WebSocket] Total message handling took {time.time() - start_time:.3f}s")

async def send_error(websocket: WebSocket, message: str):
    """Send error message to client"""
    if not is_shutting_down:
        try:
            error_msg = {
                "type": "error",
                "content": {
                    "message": message
                }
            }
            await websocket.send_json(error_msg)
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

def optimize_plotly_data(data: Dict[str, Any], max_points: int = 5000) -> Dict[str, Any]:
    """Optimize Plotly data for large datasets."""
    if not isinstance(data, dict) or 'data' not in data:
        return data
    
    optimized_data = {'data': [], 'layout': data.get('layout', {})}
    
    for trace in data['data']:
        if not isinstance(trace, dict):
            continue
            
        # Handle scatter/scattergeo traces
        if trace.get('type') in ['scatter', 'scattergeo']:
            points = len(trace.get('x', [])) if 'x' in trace else len(trace.get('lat', []))
            if points > max_points:
                # Calculate sampling rate
                sample_rate = max(1, points // max_points)
                
                # Sample the data
                if 'x' in trace and 'y' in trace:
                    trace['x'] = trace['x'][::sample_rate]
                    trace['y'] = trace['y'][::sample_rate]
                elif 'lat' in trace and 'lon' in trace:
                    trace['lat'] = trace['lat'][::sample_rate]
                    trace['lon'] = trace['lon'][::sample_rate]
                
                # Sample other array attributes
                for key in ['text', 'marker.size', 'marker.color']:
                    if key in trace:
                        if isinstance(trace[key], list):
                            trace[key] = trace[key][::sample_rate]
        
        optimized_data['data'].append(trace)
    
    return optimized_data

def compress_data(data: Union[Dict, List, str]) -> bytes:
    """Compress data using zlib."""
    json_str = json_dumps(data)
    return zlib.compress(json_str.encode('utf-8'))

def decompress_data(compressed_data: bytes) -> Union[Dict, List, str]:
    """Decompress zlib compressed data."""
    decompressed = zlib.decompress(compressed_data)
    return json_loads(decompressed.decode('utf-8'))

async def broadcast_state_update(component_id: str, value: Any, exclude_client: WebSocket = None):
    """Broadcast state updates to all connected clients with optimizations."""
    if not websocket_connections:
        return

    # Optimize plotly data if it's a visualization component
    if isinstance(value, dict) and 'data' in value and 'layout' in value:
        value = optimize_plotly_data(value)
    
    # Compress the data
    compressed_value = compress_data(value)
    
    message = {
        'type': 'state_update',
        'component_id': component_id,
        'value': compressed_value,
        'compressed': True
    }
    
    for client_id, websocket in websocket_connections.items():
        if websocket != exclude_client:
            try:
                await websocket.send_bytes(compress_data(message))
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")

async def rerun_script(websocket: WebSocket, states: Dict[str, Any]):
    """Rerun the script with updated states"""
    try:
        runner = script_runners.get(websocket)
        if runner:
            await runner.rerun(states)
        else:
            logger.error("[Script Rerun] No script runner found for websocket")
            await send_error(websocket, "Script runner not found")
    except Exception as e:
        logger.error(f"[Script Rerun] Error: {e}")
        await send_error(websocket, f"Script rerun failed: {str(e)}")

async def broadcast_message(msg: dict):
    """Broadcast a message to all connected clients"""
    try:
        for websocket in websocket_connections.values():
            await websocket.send_json(msg)
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")

def _send_message_callback(msg: dict):
    """Callback for sending messages from ScriptRunner"""
    async def _send():
        try:
            for websocket in websocket_connections.values():
                await websocket.send_json(msg)
        except Exception as e:
            logger.error(f"Error in send message callback: {e}")
    
    # Create and run the task in the event loop
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(_send())
    else:
        loop.run_until_complete(_send())
    return None  # Return None to avoid awaiting this callback

def start_server(script=None, port=8501):
    """
    Start the FastAPI server.

    Args:
        script (str, optional): Path to the script to run. Defaults to None.
        port (int, optional): The port to run the server on. Defaults to 8501.
    """
    print(f"Starting Preswald server at http://localhost:{port}")
    global SCRIPT_PATH

    if script:
        SCRIPT_PATH = os.path.abspath(script)
        script_dir = os.path.dirname(SCRIPT_PATH)
        config_path = os.path.join(script_dir, "config.toml")
        
        # Load config if it exists
        if os.path.exists(config_path):
            try:
                config = toml.load(config_path)
                if "project" in config and "port" in config["project"]:
                    port = config["project"]["port"]
                    print(f"Using port {port} from config.toml")
            except Exception as e:
                logger.error(f"Error loading config.toml: {e}")
        
        print(f"Will run script: {SCRIPT_PATH}")

    asyncio.run(run_server())
