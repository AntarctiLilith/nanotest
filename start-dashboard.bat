@echo off
echo Starting Streaming Dashboard Server...
echo.
echo Project: Streaming Dashboard
echo Port: 8080
echo Directory: D:\LLM Projects\nano
echo.
echo To stop the server, press Ctrl+C in this window.
echo.
echo Server is now running...
echo.

cd "D:\LLM Projects\nano"
python -m http.server 8080 --bind 127.0.0.1

echo.
echo Server stopped.
pause
