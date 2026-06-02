#!/bin/bash
# Start FastAPI backend in the background on port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend on the port provided dynamically by Railway
streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0