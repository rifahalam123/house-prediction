# House Price Prediction API

A simple Flask-based REST API for predicting house prices using a Linear Regression model.

## Features

- Predict house prices based on:
  - Number of bedrooms
  - Number of bathrooms
  - Square footage (sqft)
  - Age of the house
- RESTful API with JSON responses
- CORS enabled for cross-origin requests
- Health check endpoint

## Local Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Model

```bash
python train_model.py
```

This will create `house_price_model.joblib` and `scaler.joblib` files.

### 3. Run the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### GET /
Returns API information and available endpoints.

### GET /health
Check if the API and model are loaded correctly.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST /predict
Predict house price based on input features.

**Request Body:**
```json
{
  "bedrooms": 3,
  "bathrooms": 2,
  "sqft": 2000,
  "age": 10
}
```

**Response:**
```json
{
  "prediction": 385420.50,
  "currency": "USD",
  "input": {
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft": 2000,
    "age": 10
  }
}
```

## Testing the API

### Using curl:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"bedrooms": 3, "bathrooms": 2, "sqft": 2000, "age": 10}'
```

### Using Python:

```python
import requests

url = "http://localhost:5000/predict"
data = {
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft": 2000,
    "age": 10
}

response = requests.post(url, json=data)
print(response.json())
```

## Deployment Options

### Option 1: Render (Free Tier)

1. Create a [Render](https://render.com/) account
2. Create a new Web Service
3. Connect your GitHub repository
4. Render will automatically detect the app using `Procfile`
5. Click "Deploy"

### Option 2: Railway (Free Tier)

1. Create a [Railway](https://railway.app/) account
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect and deploy
5. Get your public URL

### Option 3: Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create a new app
heroku create your-app-name

# Deploy
git push heroku main
```

### Option 4: PythonAnywhere (Free Tier)

1. Create a [PythonAnywhere](https://www.pythonanywhere.com/) account
2. Upload your files
3. Create a web app with Flask
4. Configure WSGI file to point to your app
5. Reload the web app

### Option 5: Vercel (with Serverless)

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in project directory
3. Follow prompts to deploy

## Project Structure

```
.
├── app.py                      # Flask API application
├── train_model.py              # Model training script
├── house_price_model.joblib    # Trained model (generated)
├── scaler.joblib               # Feature scaler (generated)
├── requirements.txt            # Python dependencies
├── Procfile                    # For Heroku/Render deployment
├── runtime.txt                 # Python version specification
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Environment Variables

- `PORT`: Server port (default: 5000)

## Production Considerations

For production deployments:

1. Use a production WSGI server (Gunicorn is already configured)
2. Set `debug=False` in app.py (already done)
3. Add authentication if needed
4. Implement rate limiting
5. Add input validation and sanitization
6. Use HTTPS
7. Monitor logs and errors

## License

MIT
