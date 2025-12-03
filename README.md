# Probiotic Drink Designer 🧪

A modern web application for designing low-ABV, naturally carbonated probiotic drink blends using fruit juice combinations. Features intelligent auto-calculations, temperature-aware fermentation timing, and a beautiful, responsive UI.

## ✨ Features

### Core Functionality
- **Auto Mode**: Automatically suggest fruit blends based on desired sweetness, tartness, and flavor style
- **Manual Mode**: Manually select fruits and percentages to create custom blends
- **Intelligent Calculations**: Calculate sugar content, CO2 volumes, ABV, and safety parameters

### Smart Features
- **🌡️ Temperature Auto-Detection**: Automatically detect your location's temperature using GPS and weather API (30-second timeout)
- **🧮 Juice Amount Auto-Calculation**: Calculate optimal juice amounts based on selected fruits or intensity preference
- **✅ Percentage Auto-Correction**: Automatically normalizes fruit percentages to 100% with visual feedback
- **🧪 Complete Formulation**: Detailed ingredient breakdown including water, fruit juices, lemon juice, and ginger bug
- **⏱️ Optimal Fermentation Time**: Temperature-aware fermentation time calculation with quality indicators and phase breakdowns

### Modern UI/UX
- **Beautiful Light Theme**: Clean, modern design with cream/beige color palette
- **Floating Bubbles Animation**: Smooth animated bubbles in the background
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Interactive Sliders**: Real-time value updates for sweetness and tartness
- **Metric Cards**: Beautiful cards with icons for all fermentation metrics
- **Quality Indicators**: Color-coded badges for fermentation quality (Optimal, Good, Caution, etc.)

### Results Display
- Large, centered fermentation time display
- Metric cards with emoji icons (💧 Sugar, 🫧 CO₂, 🍷 ABV, 🛡️ Safety)
- Info cards for cost estimation and safety details
- Two-phase fermentation breakdown
- Complete recipe summary

## 🚀 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser with JavaScript enabled
- Location services enabled (optional, for temperature auto-detection)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/Akshit7103/Probiotic-App-DP.git
cd Probiotic-App-DP
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏃 Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

## 📁 Project Structure

```
Probiotic-App-DP/
├── app.py                          # Main Flask application with API endpoints
├── excel_backend.py                # Core business logic and calculations
├── requirements.txt                # Python dependencies
├── Procfile                        # For Heroku/Railway deployment
├── .gitignore                      # Git ignore rules
├── WWY_ProbioticDrink_Model_v1_DASHBOARD.xlsx  # Fruit database
├── templates/
│   └── index.html                  # Main HTML template
└── static/
    ├── styles.css                  # Modern UI styling
    └── app.js                      # Frontend JavaScript logic
```

## 📊 Excel Data Format

The application reads from `WWY_ProbioticDrink_Model_v1_DASHBOARD.xlsx` with the following sheets:

- **FruitMaster**: Contains fruit names, sugar content, sweetness/tartness scores, flavor categories, and notes
- **Costing**: Ingredient costs per unit for cost estimation
- **CO2Safety**: Safety parameters for different sugar levels and temperatures

## 🎯 Usage

### Auto Mode
1. Click "Auto Mode" in the top right
2. Adjust sweetness (1-10) and tartness (1-10) sliders
3. Select flavor style (Tropical, Berry, Citrus, Neutral, or Any)
4. Choose juice intensity (Light, Medium, Strong) or click "Auto-Calculate"
5. Set batch size in liters
6. Optionally click "Auto-Detect" for temperature or enter manually
7. Click "Generate Auto Blend"

### Manual Mode
1. Click "Manual Mode" in the top right
2. Select up to 4 fruits from dropdowns
3. Set percentage for each fruit (auto-corrects to 100%)
4. Click "Auto-Calculate" for optimal juice amount or enter manually
5. Set batch size and temperature
6. Click "Calculate Manual Blend"

### Reading Results
- **Fruit Blend Table**: Shows each fruit's percentage, ml/L, and total ml
- **Complete Formulation**: Exact amounts of water, fruit juices, lemon juice, and ginger bug
- **Fermentation Time**: Large display showing optimal hours with quality indicator
- **Metrics**: Sugar content, CO₂ volumes, ABV percentage, and safety status
- **Cost & Safety**: Estimated cost and detailed safety guidance
- **Recipe Summary**: Complete instructions in one paragraph

## 🌐 API Endpoints

### Main Application
- `GET /` - Main application page
- `GET /health` - Health check endpoint (returns status, timestamp, version)

### Data Endpoints
- `GET /api/metadata` - Get list of available fruits

### Weather & Calculation
- `POST /api/weather` - Get temperature for given coordinates
  - Request: `{"lat": 40.7128, "lon": -74.0060}`
  - Response: `{"success": true, "temp_c": 25, "humidity": 60, "weather": "Clear", "location": "New York, USA"}`

- `POST /api/juice/recommend` - Calculate optimal juice amount
  - Request: `{"fruits": ["Apple", "Orange"], "target_sugar_g_L": 7.0}`
  - Response: `{"success": true, "recommended_ml_per_L": 80, "reasoning": "...", "sugar_estimate_g_L": 7.1}`

### Recipe Generation
- `POST /api/suggest/auto` - Generate auto blend
  - Request: `{"sweetness": 7, "tartness": 5, "style": "tropical", "batch_l": 3, "juice_ml_per_L": 80, "temp_C": 28}`
  - Validation: All parameters have min/max ranges enforced

- `POST /api/suggest/manual` - Calculate manual blend
  - Request: `{"fruit1": "Apple", "fruit2": "Orange", "pct1": 50, "pct2": 50, "batch_l": 3, "juice_ml_per_L": 80, "temp_C": 28}`
  - Auto-corrects percentages if they don't sum to 100%

### Error Handling

All endpoints return proper HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `413` - Request Too Large
- `500` - Internal Server Error
- `503` - Service Unavailable (health check failed)

## 🚀 Deployment

### Production Checklist

Before deploying to production:

- [ ] Set a strong `SECRET_KEY` environment variable
- [ ] Set `FLASK_DEBUG=False`
- [ ] Ensure the Excel file `WWY_ProbioticDrink_Model_v1_DASHBOARD.xlsx` is included
- [ ] Configure monitoring for the `/health` endpoint
- [ ] Set up error tracking (optional: Sentry)
- [ ] Configure HTTPS/SSL for your domain
- [ ] Set appropriate CORS headers if needed

### Heroku

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_DEBUG=False

# Deploy
git push heroku master

# Open app
heroku open

# View logs
heroku logs --tail
```

### Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Procfile
3. Add environment variables in Railway dashboard:
   - `SECRET_KEY`: Generate a secure key
   - `FLASK_DEBUG`: Set to `False`
4. Deploy with one click
5. Railway will automatically use `runtime.txt` for Python version

### Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment Variables**:
     - `SECRET_KEY`: Generate a secure key
     - `FLASK_DEBUG`: `False`
     - `PYTHON_VERSION`: `3.11.9`
4. Deploy

### Other Platforms (AWS, GCP, Azure, DigitalOcean, etc.)

Use the Dockerfile approach:

```bash
# Build image
docker build -t probiotic-app .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e FLASK_DEBUG=False \
  probiotic-app
```

### Health Check Endpoint

After deployment, verify the app is running:
```bash
curl https://your-app-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000000",
  "version": "1.0.0",
  "fruits_loaded": 17
}
```

## 🔧 Environment Variables

Create a `.env` file based on `.env.example`:

**Required:**
- `SECRET_KEY`: Flask secret key for sessions (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

**Optional:**
- `PORT`: Port number (default: 8000)
- `FLASK_DEBUG`: Set to "true" for debug mode (development only, never in production!)
- `WEATHER_API_TIMEOUT`: Timeout for weather API requests (default: 10 seconds)
- `MAX_BATCH_SIZE`: Maximum batch size in liters (default: 50)
- `LOG_LEVEL`: Logging level (default: INFO)

## 🎨 Color Palette

- **Background**: Warm beige (#f5f1e8)
- **Cards**: Clean white (#ffffff)
- **Primary (Green)**: #2d6760
- **Secondary (Amber)**: #d4963c
- **Text**: Dark gray (#2c2c2c)

## 🧪 Technologies Used

- **Backend**: Flask (Python web framework)
- **Data**: OpenPyXL (Excel file processing)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Weather API**: wttr.in (free, no API key required)
- **Deployment**: Gunicorn WSGI server
- **Logging**: Python logging with rotating file handler
- **Validation**: Input validation and error handling

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Temperature auto-detection requires browser location permission
- Works best on modern browsers (Chrome, Firefox, Safari, Edge)

## 🔥 Production Features (New!)

This version includes production-ready enhancements:

- ✅ **Comprehensive Logging**: Rotating log files for monitoring and debugging
- ✅ **Input Validation**: All user inputs validated with proper error messages
- ✅ **Error Handlers**: Custom error pages for 404, 500, 413 errors
- ✅ **Health Check Endpoint**: `/health` for monitoring and load balancers
- ✅ **Environment Configuration**: Proper environment variable management
- ✅ **Security Headers**: Request size limits and secure configuration
- ✅ **Production Logging**: Structured logs with timestamps and severity levels

## 💡 Future Enhancements

- User authentication and recipe storage
- Save and load recipes to database
- Export recipes as PDF
- Batch scaling calculator
- Shopping list generation
- Fermentation timer with notifications
- Multi-language support
- PWA (Progressive Web App) capabilities
- Database migration (PostgreSQL/SQLite)
- Rate limiting and CORS configuration
- Automated testing suite

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ for probiotic drink enthusiasts
