# Shopify Theme Detector

## Project Overview
This is a comprehensive multilingual web application for detecting themes used by Shopify websites and sharing related insights through our blog platform. Users can input a Shopify website URL to automatically analyze and identify the theme information, while also accessing valuable content about Shopify themes and e-commerce development in multiple languages.

## Features
- 🔍 **Theme Detection**: Input Shopify website URL to automatically detect the theme being used
- 🎨 **Theme Information**: Display detailed information including theme name, version, developer, etc.
- 📝 **Blog Platform**: Share insights, tutorials, and updates about Shopify themes and e-commerce
- 🌍 **Multilingual Support**: Full interface translation in 7 languages (English, Chinese, French, Portuguese, Spanish, German, Japanese)
- 🔄 **Language Switching**: Easy language switching with dropdown menu
- 📱 **Responsive Design**: Support for desktop and mobile device access
- ⚡ **Fast Detection**: Complete theme identification within seconds
- 🛡️ **Secure and Reliable**: Does not store user-inputted website information
- 🏷️ **Content Management**: Git-based blog workflow for secure content publishing
- 🔗 **SEO Optimized**: Dynamic sitemap generation and RSS feed support

## Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Blog Engine**: Markdown + YAML Front Matter
- **Internationalization**: JSON-based translation system with Flask session management
- **Theme Detection**: Through analysis of theme identifiers in website source code
- **Content Management**: Git-based workflow with file system storage
- **Styling Framework**: Custom CSS with Shopify-inspired design
- **Dependencies**: 
  - `markdown` - Markdown processing
  - `python-frontmatter` - YAML front matter parsing
  - `python-dateutil` - Date parsing utilities

## How to Use

### Language Selection
1. Use the language dropdown in the top-right corner of the navigation
2. Choose from 7 supported languages: English, Chinese, French, Portuguese, Spanish, German, Japanese
3. The interface will immediately switch to your selected language
4. Language preference is saved in your browser session

### Theme Detection
1. Enter the complete URL of a Shopify website in the input box
2. Click the "Detect Theme" button
3. Wait a few seconds for the system to display detection results
4. View theme name, version, and other related information

### Blog Platform
1. Visit `/blog` to browse all articles
2. Use tags to filter articles by topic
3. Subscribe to RSS feed at `/blog/feed` for updates

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

## Blog Content Management

### Publishing Workflow (Git-based)
1. **Create Article**: Write markdown files in `blog/posts/` directory
2. **File Naming**: Use format `YYYY-MM-DD-article-slug.md`
3. **Front Matter**: Include YAML metadata (title, date, tags, description)
4. **Git Commit**: Commit new articles to repository
5. **Auto Deploy**: Server automatically updates and displays new content

### Article Format
```markdown
---
title: "Your Article Title"
date: "2024-08-14"
author: "Author Name"
tags: ["shopify", "themes", "tutorial"]
description: "Brief description for SEO"
featured: false
slug: "article-url-slug"
---

# Article Content

Your article content in Markdown format...
```

### Security Features
- ✅ Admin-only publishing (no public file uploads)
- ✅ Git-based version control and rollback capability
- ✅ File system storage (no database vulnerabilities)
- ✅ Markdown sanitization and safe rendering
- ✅ Static file serving for optimal performance

## API Endpoints

### Theme Detection
- `POST /api/detect` - Detect Shopify theme from URL

### Blog
- `GET /blog` - Blog homepage with pagination
- `GET /blog/<slug>` - Individual blog post
- `GET /blog/tag/<tag>` - Posts filtered by tag
- `GET /blog/feed` - RSS feed

### Internationalization
- `GET /set_language/<language_code>` - Switch interface language (en, zh, fr, pt, es, de, ja)

### SEO & Utilities
- `GET /sitemap.xml` - Dynamic sitemap including all blog posts
- `GET /robots.txt` - Search engine crawler instructions

## Multilingual Implementation

### Supported Languages
- **English** (en) - Default language
- **中文** (zh) - Chinese Simplified
- **Français** (fr) - French  
- **Português** (pt) - Portuguese
- **Español** (es) - Spanish
- **Deutsch** (de) - German
- **日本語** (ja) - Japanese

### Translation System
- **JSON Configuration**: Each language has its own JSON file in `/i18n/` directory
- **Single-File Approach**: All translations for a language are contained in one file
- **Dot Notation**: Access nested translations using keys like `hero.title` or `features.fast.description`
- **Fallback Support**: Automatically falls back to English if translation is missing
- **Session Management**: Language preference stored in user session

### Translation Files Structure
```json
{
  "site": {
    "title": "Shopify Theme Detector",
    "description": "Free tool description"
  },
  "nav": {
    "home": "Home",
    "blog": "Blog",
    ...
  },
  "hero": {
    "title": "Main headline",
    "subtitle": "Subtitle text"
  }
}
```

## Changelog
- v3.0.0: Added comprehensive multilingual support with 7 languages
- v2.0.0: Added comprehensive blog platform with Git-based content management
- v1.0.0: Initial version with basic theme detection functionality

## Contact
If you have any questions or suggestions, please contact us through:
- Project Repository: [GitHub Repository Link]
- Email: [Contact Email]

---
*This project is for educational and research purposes only. Please comply with the terms of use of relevant websites.*