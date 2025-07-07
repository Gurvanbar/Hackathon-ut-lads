@echo off
echo Starting Genie OpenAI-Compatible API Server...
echo.
echo Installing dependencies if needed...
pip install -r requirements.txt
echo.
echo Starting server on http://127.0.0.1:8000
echo API Documentation will be available at: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
python genie_openai_server.py
pause
