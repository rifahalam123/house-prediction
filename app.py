from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS - Allow all origins for public API
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "max_age": 3600,
        "supports_credentials": False
    }
})

# Security: Disable debug mode
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Production settings
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 16 KB max request size

# Load model and scaler
model = None
scaler = None
model_loaded_at = None

def load_model():
    """Load ML model and scaler with proper error handling"""
    global model, scaler, model_loaded_at
    try:
        model_path = os.environ.get('MODEL_PATH', 'house_price_model.joblib')
        scaler_path = os.environ.get('SCALER_PATH', 'scaler.joblib')

        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")

        if not os.path.exists(scaler_path):
            logger.error(f"Scaler file not found: {scaler_path}")
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        model_loaded_at = datetime.utcnow().isoformat()

        logger.info("Model and scaler loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}", exc_info=True)
        return False

# Load model on startup
if not load_model():
    logger.critical("Failed to load model on startup!")

@app.route('/', methods=['GET'])
def home():
    """Root endpoint - serve HTML interface directly"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>House Price Predictor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 520px;
            width: 100%;
        }
        h1 { color: #1a1a1a; text-align: center; margin-bottom: 5px; font-size: 32px; }
        .subtitle { color: #666; text-align: center; margin-bottom: 25px; font-size: 14px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 6px; color: #333; font-weight: 600; font-size: 13px; }
        input { 
            width: 100%;
            padding: 11px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.2s;
        }
        input:focus { outline: none; border-color: #667eea; background-color: #f9f9ff; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 5px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        button:active { transform: translateY(0); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .api-section { background: #f5f5f5; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .api-section label { margin-bottom: 6px; }
        .api-section input { font-size: 12px; margin-bottom: 5px; }
        .api-section small { color: #999; font-size: 11px; display: block; margin-top: 5px; }
        .result { 
            background: #f0fef5;
            border: 2px solid #10b981;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            display: none;
            margin-top: 20px;
        }
        .result.show { display: block; animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .result-label { color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
        .result-price { font-size: 42px; font-weight: 700; color: #10b981; margin-bottom: 8px; }
        .result-details { color: #666; font-size: 12px; }
        .error { 
            background: #fee;
            border: 1px solid #fcc;
            color: #c33;
            padding: 12px;
            border-radius: 6px;
            margin-top: 15px;
            display: none;
            font-size: 13px;
        }
        .error.show { display: block; }
        @media (max-width: 480px) { .form-row { grid-template-columns: 1fr; } .container { padding: 25px; } h1 { font-size: 26px; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 House Price Predictor</h1>
        <p class="subtitle">Get an accurate estimate in seconds</p>

        <div class="api-section">
            <label>API Endpoint</label>
            <input type="text" id="apiUrl" value="http://127.0.0.1:5000" placeholder="http://127.0.0.1:5000">
            <small>Update if running on different server</small>
        </div>

        <form id="predictionForm">
            <div class="form-row">
                <div class="form-group">
                    <label>Bedrooms</label>
                    <input type="number" id="bedrooms" min="1" max="10" value="3" required>
                </div>
                <div class="form-group">
                    <label>Bathrooms</label>
                    <input type="number" id="bathrooms" min="1" max="10" step="0.5" value="2" required>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Square Feet</label>
                    <input type="number" id="sqft" min="100" max="50000" value="2000" required>
                </div>
                <div class="form-group">
                    <label>Age (years)</label>
                    <input type="number" id="age" min="0" max="100" value="10" required>
                </div>
            </div>

            <button type="submit">Predict Price</button>
        </form>

        <div id="result" class="result">
            <div class="result-label">Estimated Value</div>
            <div class="result-price" id="predictedPrice"></div>
            <div class="result-details" id="resultDetails"></div>
        </div>

        <div id="error" class="error"></div>
    </div>

    <script>
        const form = document.getElementById('predictionForm');
        const resultDiv = document.getElementById('result');
        const errorDiv = document.getElementById('error');
        const priceElement = document.getElementById('predictedPrice');
        const resultDetails = document.getElementById('resultDetails');
        const apiUrlInput = document.getElementById('apiUrl');
        const submitButton = form.querySelector('button');

        const savedApiUrl = localStorage.getItem('hppApiUrl');
        if (savedApiUrl) apiUrlInput.value = savedApiUrl;

        apiUrlInput.addEventListener('change', () => {
            const apiUrl = apiUrlInput.value.trim();
            if (apiUrl) localStorage.setItem('hppApiUrl', apiUrl);
        });
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const apiUrl = apiUrlInput.value.trim();
            if (!apiUrl) { showError('Please enter the API endpoint'); return; }
            const formData = {
                bedrooms: parseFloat(document.getElementById('bedrooms').value),
                bathrooms: parseFloat(document.getElementById('bathrooms').value),
                sqft: parseFloat(document.getElementById('sqft').value),
                age: parseFloat(document.getElementById('age').value)
            };
            if (Object.values(formData).some(v => isNaN(v) || v < 0)) {
                showError('Please enter valid values');
                return;
            }
            resultDiv.classList.remove('show');
            errorDiv.classList.remove('show');
            submitButton.textContent = 'Predicting...';
            submitButton.disabled = true;
            try {
                const predictUrl = apiUrl.endsWith('/') ? apiUrl + 'predict' : apiUrl + '/predict';
                const response = await fetch(predictUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const data = await response.json();
                if (response.ok && data.success) {
                    const price = data.prediction;
                    const formattedPrice = new Intl.NumberFormat('en-US', {
                        style: 'currency', currency: 'USD',
                        minimumFractionDigits: 0, maximumFractionDigits: 0
                    }).format(price);
                    priceElement.textContent = formattedPrice;
                    resultDetails.innerHTML = '<div>' + formData.bedrooms + ' bed • ' + formData.bathrooms + ' bath • ' + formData.sqft.toLocaleString() + ' sqft • ' + formData.age + ' yrs</div>';
                    resultDiv.classList.add('show');
                } else {
                    showError(data.message || 'Failed to get prediction');
                }
            } catch (error) {
                showError('Connection error. Check the API URL');
            } finally {
                submitButton.textContent = 'Predict Price';
                submitButton.disabled = false;
            }
        });
        function showError(message) {
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
            resultDiv.classList.remove('show');
        }
    </script>
</body>
</html>"""
    response = app.make_response(html)
    response.headers['Cache-Control'] = 'max-age=0, no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    return response

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with detailed diagnostics"""
    try:
        model_loaded = model is not None and scaler is not None
        status_code = 200 if model_loaded else 503

        return jsonify({
            'status': 'healthy' if model_loaded else 'unhealthy',
            'model_loaded': model_loaded,
            'model_loaded_at': model_loaded_at,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'production')
        }), status_code
    except Exception as e:
        logger.error(f"Error in health endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed'
        }), 503

def validate_input(data):
    """Validate input data with proper bounds checking"""
    required_fields = ['bedrooms', 'bathrooms', 'sqft', 'age']

    # Check for missing fields
    for field in required_fields:
        if field not in data:
            return False, f'Missing required field: {field}'

    # Validate data types and ranges
    try:
        bedrooms = float(data['bedrooms'])
        bathrooms = float(data['bathrooms'])
        sqft = float(data['sqft'])
        age = float(data['age'])

        # Reasonable bounds checking
        if not (0 <= bedrooms <= 20):
            return False, 'Bedrooms must be between 0 and 20'

        if not (0 <= bathrooms <= 15):
            return False, 'Bathrooms must be between 0 and 15'

        if not (100 <= sqft <= 50000):
            return False, 'Square footage must be between 100 and 50,000'

        if not (0 <= age <= 200):
            return False, 'Age must be between 0 and 200 years'

        return True, {
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sqft': sqft,
            'age': age
        }

    except (ValueError, TypeError) as e:
        return False, f'Invalid data type: {str(e)}'

@app.route('/predict', methods=['POST'])
def predict():
    """Predict house price with comprehensive error handling"""
    request_id = datetime.utcnow().isoformat()

    try:
        # Check if model is loaded
        if model is None or scaler is None:
            logger.error(f"[{request_id}] Model not loaded")
            return jsonify({
                'error': 'Model not available',
                'message': 'The prediction model is not loaded. Please contact support.'
            }), 503

        # Get JSON data
        if not request.is_json:
            logger.warning(f"[{request_id}] Request is not JSON")
            return jsonify({
                'error': 'Invalid request format',
                'message': 'Request must be JSON'
            }), 400

        data = request.get_json()

        if not data:
            logger.warning(f"[{request_id}] Empty request body")
            return jsonify({
                'error': 'Empty request',
                'message': 'Request body cannot be empty'
            }), 400

        # Validate input
        is_valid, result = validate_input(data)
        if not is_valid:
            logger.warning(f"[{request_id}] Validation failed: {result}")
            return jsonify({
                'error': 'Validation error',
                'message': result
            }), 400

        validated_data = result

        # Extract and prepare features
        features = np.array([[
            validated_data['bedrooms'],
            validated_data['bathrooms'],
            validated_data['sqft'],
            validated_data['age']
        ]])

        # Scale features
        features_scaled = scaler.transform(features)

        # Make prediction
        prediction = model.predict(features_scaled)[0]

        logger.info(f"[{request_id}] Prediction successful: {prediction}")

        return jsonify({
            'success': True,
            'prediction': round(float(prediction), 2),
            'currency': 'USD',
            'input': {
                'bedrooms': validated_data['bedrooms'],
                'bathrooms': validated_data['bathrooms'],
                'sqft': validated_data['sqft'],
                'age': validated_data['age']
            },
            'request_id': request_id
        }), 200

    except ValueError as e:
        logger.error(f"[{request_id}] Value error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Invalid input values',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.',
            'request_id': request_id
        }), 500

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Only set CSP if not already set by the route
    if 'Content-Security-Policy' not in response.headers:
        response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    logger.warning(f"405 error: {request.method} on {request.url}")
    return jsonify({
        'error': 'Method not allowed',
        'message': f'The {request.method} method is not allowed for this endpoint'
    }), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 errors"""
    logger.warning(f"413 error: Request too large from {request.remote_addr}")
    return jsonify({
        'error': 'Request too large',
        'message': 'Request payload exceeds maximum allowed size'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # For production, use a WSGI server like Gunicorn
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
