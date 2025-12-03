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

- `GET /` - Main application page
- `GET /api/metadata` - Get list of available fruits
- `POST /api/weather` - Get temperature for given coordinates
- `POST /api/juice/recommend` - Calculate optimal juice amount
- `POST /api/suggest/auto` - Generate auto blend
- `POST /api/suggest/manual` - Calculate manual blend

## 🚀 Deployment

### Heroku

```bash
heroku create your-app-name
git push heroku master
heroku open
```

### Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Procfile
3. Deploy with one click

### Render

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app`

## 🔧 Environment Variables

Optional environment variables:
- `PORT`: Port number (default: 5000)
- `FLASK_DEBUG`: Set to "true" for debug mode (development only)

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

## 💡 Future Enhancements

- Save and load recipes
- Export recipes as PDF
- Batch scaling calculator
- Shopping list generation
- Fermentation timer with notifications
- Multi-language support
- PWA (Progressive Web App) capabilities

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ for probiotic drink enthusiasts
