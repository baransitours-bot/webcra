@echo off
REM Launch Immigration Platform Web UI
REM For Windows

echo.
echo 🌍 Starting Immigration Platform Web UI...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️  Streamlit not installed. Installing...
    pip install streamlit
)

echo ✅ Launching UI on http://localhost:8501
echo 📱 Access from other devices on your network
echo.
echo Press Ctrl+C to stop
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    echo Network URL: http://%%a:8501
)

echo.

REM Launch with network access
streamlit run app.py --server.address=0.0.0.0 --server.port=8501

pause
