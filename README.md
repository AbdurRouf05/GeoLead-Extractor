# GeoLead Extractor

A professional Python and Streamlit-based tool designed to automatically extract high-quality business leads from Google Maps. It provides a user-friendly web interface that requires no programming knowledge to operate.

This tool is optimized for B2B Lead Generation, digital marketing agencies, comprehensive business research, and cold outreach campaigns.

## Key Features
- **Global & Local Scraping**: Search and extract business data across specific cities or globally based on target niches.
- **Dual Engine Architecture**: 
  - **Manual Engine (Selenium)**: Operates locally using headless browser automation.
  - **API Engine (RapidAPI)**: Connects directly to `maps-data` endpoint for high-speed, stable, and large-scale data retrieval.
- **Automated Email Extraction**: Integrates website crawling to scan and capture official business email addresses directly from their websites.
- **Smart Data Filtering**: Built-in blacklist system to automatically filter out generic emails (e.g., info@, support@) and major corporate franchises (e.g., Starbucks, McDonald's) to ensure the relevance of your leads.
- **Data Export**: Seamlessly export extracted leads into a neatly formatted `.xlsx` (Excel) file.

## System Requirements
- Python 3.8 or newer
- Google Chrome browser (Required for the Manual/Selenium engine)

## Installation Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbdurRouf05/GeoLead-Extractor.git
   cd GeoLead-Extractor
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   For Windows users, simply double-click the executable batch script:
   **`run.bat`**

   Alternatively, start the application manually via the terminal:
   ```bash
   cd GoogleMaps-Lead-Scraper
   streamlit run app.py
   ```

## Usage Instructions
1. Open your browser and navigate to `http://localhost:8501`.
2. Enter your target niches/keywords in the input panel (e.g., `software agency`, `digital marketing`).
3. Select your preferred Scraping Engine (API or Manual). Note: The API engine requires a valid RapidAPI Key.
4. Specify the target Location (City/Country).
5. Enable the "Extract Email from Website" feature if you need contact emails (only available on the Manual engine).
6. Click the "Start Scraping" button and wait for the completion progress bar.
7. Click "Download Excel" to save the final dataset.

## Important Notes
- **Performance**: The speed of the Manual Engine heavily depends on your internet connection and system RAM. For large-scale scraping, the API engine is highly recommended.
- **Maintenance**: Web structures change frequently. Ensure you keep the application updated to maintain compatibility with the latest search layouts.

---
### License
This project is open-source. Please use this tool responsibly, ethically, and in compliance with the target websites' terms of service and privacy policies.
