# Probiotic Drink Designer

A web application for designing low-ABV, naturally carbonated probiotic drink blends using fruit juice combinations.

## Features

- **Auto Mode**: Automatically suggest fruit blends based on desired sweetness, tartness, and flavor style
- **Manual Mode**: Manually select fruits and percentages to create custom blends
- **Fermentation Metrics**: Calculate sugar content, CO2 volumes, ABV, and safety parameters
- **Cost Estimation**: Estimate ingredient costs for batches
- **Safety Guidance**: Provides fermentation safety recommendations based on temperature and sugar levels

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

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

## Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
gunicorn app:app
```

## Project Structure

```
Probiotic-App-DP/
├── app.py                          # Main Flask application
├── data.py                         # Fruit data and blend calculation logic
├── excel_backend.py                # Excel file processing for fruit master data
├── requirements.txt                # Python dependencies
├── WWY_ProbioticDrink_Model_v1_DASHBOARD.xlsx  # Fruit database
├── templates/
│   └── index.html                  # Main HTML template
└── static/
    ├── styles.css                  # CSS styling
    └── app.js                      # Frontend JavaScript
```

## Excel Data Format

The application reads from `WWY_ProbioticDrink_Model_v1_DASHBOARD.xlsx` with the following sheets:

- **FruitMaster**: Contains fruit names, sugar content, sweetness/tartness scores, and notes
- **Costing**: Ingredient costs per unit
- **CO2Safety**: Safety parameters for different sugar levels and temperatures

## Usage

1. Choose between Auto Mode or Manual Mode
2. **Auto Mode**: Set your desired sweetness (1-10), tartness (1-10), flavor style, batch size, and juice amount
3. **Manual Mode**: Select specific fruits, set percentages, batch size, juice amount, and temperature
4. Click generate/calculate to see your blend recipe with:
   - Fruit proportions and volumes
   - Sugar content per liter
   - Expected CO2 carbonation volumes
   - Maximum ABV percentage
   - Safety recommendations
   - Cost estimates

## Deployment

The application can be deployed to platforms like Heroku, Railway, or any platform that supports Python web applications.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
