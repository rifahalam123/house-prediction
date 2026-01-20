@echo off
echo ========================================
echo House Price Prediction API
echo ========================================
echo.

echo Checking if model files exist...
if not exist "house_price_model.joblib" (
    echo Model not found. Training model...
    python train_model.py
    echo.
)

echo Starting Flask API server...
echo API will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
