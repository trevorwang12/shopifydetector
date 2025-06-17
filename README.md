# Shopify Theme Detector

## Project Overview
This is a web application for detecting themes used by Shopify websites. Users simply need to input a Shopify website URL, and the system will automatically analyze and identify the theme name and related information used by that website.

## Features
- 🔍 **Theme Detection**: Input Shopify website URL to automatically detect the theme being used
- 🎨 **Theme Information**: Display detailed information including theme name, version, developer, etc.
- 📱 **Responsive Design**: Support for desktop and mobile device access
- ⚡ **Fast Detection**: Complete theme identification within seconds
- 🛡️ **Secure and Reliable**: Does not store user-inputted website information

## Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Theme Detection**: Through analysis of theme identifiers in website source code
- **Styling Framework**: Bootstrap 5

## How to Use
1. Enter the complete URL of a Shopify website in the input box
2. Click the "Detect Theme" button
3. Wait a few seconds for the system to display detection results
4. View theme name, version, and other related information

## Installation and Running

### Requirements
- Python 3.7+
- pip package manager

### Installation Steps
1. Clone or download the project locally
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access `http://localhost:5000` in your browser

## Detection Principle
The system detects Shopify themes through the following methods:
1. Retrieve the HTML source code of the target website
2. Search for characteristic identifiers of Shopify themes
3. Analyze CSS file paths and JavaScript files
4. Match known theme patterns and signatures
5. Return detected theme information

## Supported Themes
The system can detect most popular Shopify themes, including but not limited to:
- Dawn (Official Shopify theme)
- Debut
- Brooklyn
- Minimal
- Supply
- Narrative
- And hundreds of third-party themes

## Important Notes
- Only supports detection of publicly accessible Shopify websites
- Some highly customized themes may not be accurately identified
- Detection results are for reference only; actual theme information should be verified with official sources

## Changelog
- v1.0.0: Initial version with basic theme detection functionality

## Contact
If you have any questions or suggestions, please contact us through:
- Project Repository: [GitHub Repository Link]
- Email: [Contact Email]

---
*This project is for educational and research purposes only. Please comply with the terms of use of relevant websites.*