#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shopify Theme Detector
This application can detect themes used by Shopify websites
"""

import re
import json
import os
import requests
from urllib.parse import urlparse, urljoin
import html.parser
from flask import Flask, render_template, request, jsonify, abort, session, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import frontmatter
import markdown
from datetime import datetime
from dateutil.parser import parse as date_parse
import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Performance optimizations
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Response compression and caching headers
@app.after_request
def after_request(response):
    """Add performance and security headers"""
    # Performance headers
    if response.status_code == 200:
        # Cache static assets
        if request.endpoint in ['static', 'robots_txt']:
            response.headers['Cache-Control'] = 'public, max-age=86400'  # 24 hours
        # Cache blog posts and pages
        elif request.endpoint in ['blog_post', 'about', 'contact', 'disclaimer']:
            response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
        # Cache homepage for shorter time
        elif request.endpoint == 'index':
            response.headers['Cache-Control'] = 'public, max-age=1800'  # 30 minutes
        # Don't cache API responses
        elif request.endpoint == 'detect_theme_api':
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    
    return response

class MultilingualManager:
    """Multilingual Content Manager"""
    
    def __init__(self):
        self.translations = {}
        self.supported_languages = ['en', 'zh', 'fr', 'pt', 'es', 'de', 'ja']
        self.default_language = 'en'
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        for lang in self.supported_languages:
            try:
                with open(f'i18n/{lang}.json', 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                logger.warning(f"Translation file for {lang} not found")
                if lang == self.default_language:
                    self.translations[lang] = {}
    
    def get_language(self):
        """Get current language from session or default"""
        return session.get('language', self.default_language)
    
    def set_language(self, language_code):
        """Set current language in session"""
        if language_code in self.supported_languages:
            session['language'] = language_code
            return True
        return False
    
    def get_text(self, key_path, language=None):
        """Get translated text using dot notation (e.g., 'hero.title')"""
        if language is None:
            language = self.get_language()
        
        if language not in self.translations:
            language = self.default_language
        
        keys = key_path.split('.')
        text = self.translations.get(language, {})
        
        for key in keys:
            if isinstance(text, dict) and key in text:
                text = text[key]
            else:
                # Fallback to English if key not found
                text = self.translations.get(self.default_language, {})
                for fallback_key in keys:
                    if isinstance(text, dict) and fallback_key in text:
                        text = text[fallback_key]
                    else:
                        return key_path  # Return key path if not found
                break
        
        return text if isinstance(text, str) else key_path
    
    def get_language_name(self, lang_code):
        """Get language display name"""
        language_names = {
            'en': 'English',
            'zh': '中文',
            'fr': 'Français',
            'pt': 'Português',
            'es': 'Español',
            'de': 'Deutsch',
            'ja': '日本語'
        }
        return language_names.get(lang_code, lang_code)

class ShopifyThemeDetector:
    """Shopify Theme Detector Class"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set user agent to simulate real browser access
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Known Shopify theme characteristics
        self.theme_patterns = {
            'dawn': {
                'patterns': [r'dawn[_-]?theme', r'shopify[_-]?dawn', r'assets/dawn'],
                'css_patterns': [r'dawn.*\.css', r'theme.*dawn.*\.css'],
                'js_patterns': [r'dawn.*\.js', r'theme.*dawn.*\.js']
            },
            'debut': {
                'patterns': [r'debut[_-]?theme', r'shopify[_-]?debut', r'assets/debut'],
                'css_patterns': [r'debut.*\.css', r'theme.*debut.*\.css'],
                'js_patterns': [r'debut.*\.js', r'theme.*debut.*\.js']
            },
            'brooklyn': {
                'patterns': [r'brooklyn[_-]?theme', r'shopify[_-]?brooklyn', r'assets/brooklyn'],
                'css_patterns': [r'brooklyn.*\.css', r'theme.*brooklyn.*\.css'],
                'js_patterns': [r'brooklyn.*\.js', r'theme.*brooklyn.*\.js']
            },
            'minimal': {
                'patterns': [r'minimal[_-]?theme', r'shopify[_-]?minimal', r'assets/minimal'],
                'css_patterns': [r'minimal.*\.css', r'theme.*minimal.*\.css'],
                'js_patterns': [r'minimal.*\.js', r'theme.*minimal.*\.js']
            },
            'supply': {
                'patterns': [r'supply[_-]?theme', r'shopify[_-]?supply', r'assets/supply'],
                'css_patterns': [r'supply.*\.css', r'theme.*supply.*\.css'],
                'js_patterns': [r'supply.*\.js', r'theme.*supply.*\.js']
            },
            'narrative': {
                'patterns': [r'narrative[_-]?theme', r'shopify[_-]?narrative', r'assets/narrative'],
                'css_patterns': [r'narrative.*\.css', r'theme.*narrative.*\.css'],
                'js_patterns': [r'narrative.*\.js', r'theme.*narrative.*\.js']
            }
        }
    
    def is_shopify_site(self, url):
        """Check if the website is a Shopify site"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check common Shopify indicators
            shopify_indicators = [
                'Shopify.shop',
                'shopify-section',
                'shopify-block',
                'cdn.shopify.com',
                'myshopify.com',
                'Shopify.theme',
                'shopify_pay'
            ]
            
            content = response.text.lower()
            for indicator in shopify_indicators:
                if indicator.lower() in content:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking Shopify site: {e}")
            return False
    
    def extract_theme_info(self, html_content, url):
        """Extract theme information from HTML content"""
        theme_info = {
            'name': 'Unknown',
            'confidence': 0,
            'detected_patterns': []
        }
        
        # Multiple methods to find theme name
        methods = [
            self._check_meta_tags,
            self._check_css_files,
            self._check_js_files,
            self._check_html_comments,
            self._check_asset_paths,
            self._check_theme_patterns
        ]
        
        for method in methods:
            try:
                result = method(html_content, url)
                if result and result.get('confidence', 0) > theme_info['confidence']:
                    theme_info.update(result)
            except Exception as e:
                logger.error(f"Theme detection method error: {e}")
        
        return theme_info
    
    def _check_meta_tags(self, html_content, url):
        """Check theme information in meta tags"""
        # Use regex to find meta tags
        meta_pattern = r'<meta[^>]*name=["\']([^"\'>]*)["\'][^>]*content=["\']([^"\'>]*)["\'][^>]*>'
        meta_matches = re.findall(meta_pattern, html_content, re.IGNORECASE)
        
        for name, content in meta_matches:
            name = name.lower()
            content = content.lower()
            
            if 'theme' in name or 'template' in name:
                for theme_name, patterns in self.theme_patterns.items():
                    for pattern in patterns['patterns']:
                        if re.search(pattern, content, re.IGNORECASE):
                            return {
                                'name': theme_name.title(),
                                'confidence': 90,
                                'detected_patterns': [f'meta tag: {pattern}']
                            }
        return None
    
    def _check_css_files(self, html_content, url):
        """Check theme information in CSS files"""
        # Use regex to find CSS links
        css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\'>]*)["\'][^>]*>'
        css_matches = re.findall(css_pattern, html_content, re.IGNORECASE)
        
        for href in css_matches:
            if href:
                for theme_name, patterns in self.theme_patterns.items():
                    for pattern in patterns.get('css_patterns', []):
                        if re.search(pattern, href, re.IGNORECASE):
                            return {
                                'name': theme_name.title(),
                                'confidence': 85,
                                'detected_patterns': [f'CSS file: {pattern}']
                            }
        return None
    
    def _check_js_files(self, html_content, url):
        """Check JavaScript files for theme information"""
        # Use regex to find JavaScript files
        js_pattern = r'<script[^>]*src=["\']([^"\'>]*)["\'][^>]*>'
        js_matches = re.findall(js_pattern, html_content, re.IGNORECASE)
        
        for src in js_matches:
            if src:
                for theme_name, patterns in self.theme_patterns.items():
                    for pattern in patterns.get('js_patterns', []):
                        if re.search(pattern, src, re.IGNORECASE):
                            return {
                                'name': theme_name.title(),
                                'confidence': 80,
                                'detected_patterns': [f'JS file: {pattern}']
                            }
        return None
    
    def _check_html_comments(self, html_content, url):
        """Check HTML comments for theme information"""
        # Use regex to find HTML comments
        comment_pattern = r'<!--([^>]*)-->'
        comments = re.findall(comment_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        for comment in comments:
            comment_text = comment.lower()
            for theme_name, patterns in self.theme_patterns.items():
                for pattern in patterns['patterns']:
                    if re.search(pattern, comment_text, re.IGNORECASE):
                        return {
                            'name': theme_name.title(),
                            'confidence': 75,
                            'detected_patterns': [f'HTML comment: {pattern}']
                        }
        return None
    
    def _check_asset_paths(self, html_content, url):
        """Check asset paths for theme information"""
        # Find all links containing assets
        asset_patterns = [r'/assets/[^"\s]*', r'cdn\.shopify\.com/[^"\s]*']
        
        for pattern in asset_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                for theme_name, theme_patterns in self.theme_patterns.items():
                    for theme_pattern in theme_patterns['patterns']:
                        if re.search(theme_pattern, match, re.IGNORECASE):
                            return {
                                'name': theme_name.title(),
                                'confidence': 70,
                                'detected_patterns': [f'Asset path: {theme_pattern}']
                            }
        return None
    
    def _check_theme_patterns(self, html_content, url):
        """Check general theme patterns - Enhanced version"""
        # Method 1: Look for Shopify.theme object (most accurate)
        result = self._extract_shopify_theme_object(html_content)
        if result:
            return result
        
        # Method 2: Check CSS file headers as backup
        result = self._check_css_theme_headers(html_content, url)
        if result:
            return result
        
        return None
    
    def _extract_shopify_theme_object(self, html_content):
        """Extract theme info from Shopify.theme JavaScript object"""
        # Enhanced patterns to catch various Shopify.theme formats
        patterns = [
            r'Shopify\.theme\s*=\s*({[^}]*?})',
            r'window\.Shopify\.theme\s*=\s*({[^}]*?})',
            r'Shopify\["theme"\]\s*=\s*({[^}]*?})',
            r'window\["Shopify"\]\.theme\s*=\s*({[^}]*?})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    # Try to parse as JSON-like object
                    theme_data = self._parse_theme_object(match)
                    if theme_data:
                        return theme_data
                except Exception:
                    continue
        
        return None
    
    def _parse_theme_object(self, theme_obj_str):
        """Parse theme object string and extract relevant information"""
        detected_patterns = []
        confidence = 90
        
        # Extract name (try both name and schema_name)
        name_match = re.search(r'["\']?name["\']?\s*:\s*["\']([^"\']+)["\']', theme_obj_str, re.IGNORECASE)
        schema_name_match = re.search(r'["\']?schema_name["\']?\s*:\s*["\']([^"\']+)["\']', theme_obj_str, re.IGNORECASE)
        
        theme_name = None
        schema_name = None
        
        if name_match:
            theme_name = name_match.group(1).strip()
            detected_patterns.append('Shopify.theme.name')
            
        if schema_name_match:
            schema_name = schema_name_match.group(1).strip()
            detected_patterns.append('Shopify.theme.schema_name')
        
        # Extract theme_store_id (most reliable identifier)
        store_id_match = re.search(r'["\']?theme_store_id["\']?\s*:\s*(\d+)', theme_obj_str, re.IGNORECASE)
        theme_store_id = None
        if store_id_match:
            theme_store_id = int(store_id_match.group(1))
            detected_patterns.append('Shopify.theme.theme_store_id')
            confidence = 98  # Higher confidence with store ID
        
        # Extract role
        role_match = re.search(r'["\']?role["\']?\s*:\s*["\']([^"\']+)["\']', theme_obj_str, re.IGNORECASE)
        role = None
        if role_match:
            role = role_match.group(1).strip()
            detected_patterns.append('Shopify.theme.role')
        
        # Extract id
        id_match = re.search(r'["\']?id["\']?\s*:\s*(\d+)', theme_obj_str, re.IGNORECASE)
        theme_id = None
        if id_match:
            theme_id = int(id_match.group(1))
            detected_patterns.append('Shopify.theme.id')
        
        if theme_name or schema_name or theme_store_id:
            result = {
                'confidence': confidence,
                'detected_patterns': detected_patterns
            }
            
            # Determine the best theme name to use
            final_theme_name = None
            
            # Priority 1: theme_store_id verification
            if theme_store_id:
                verified_name = self._verify_theme_by_store_id(theme_store_id)
                if verified_name:
                    final_theme_name = verified_name
                    result['verified_name'] = True
                    result['theme_store_id'] = theme_store_id
                    result['confidence'] = 99
            
            # Priority 2: schema_name (usually more reliable than name)
            if not final_theme_name and schema_name:
                validated_schema = self._validate_theme_name(schema_name)
                if validated_schema:
                    final_theme_name = validated_schema
                    result['confidence'] = 85
            
            # Priority 3: regular name field
            if not final_theme_name and theme_name:
                validated_name = self._validate_theme_name(theme_name)
                if validated_name:
                    final_theme_name = validated_name
                    result['confidence'] = 80
            
            # Final assignment or fallback
            if final_theme_name:
                result['name'] = final_theme_name
                if theme_store_id and not result.get('verified_name'):
                    result['theme_store_id'] = theme_store_id
            else:
                # No valid name found, but we have some theme info
                if theme_store_id or schema_name or theme_name:
                    result['name'] = 'Custom Theme'
                    result['confidence'] = 50
                    if theme_store_id:
                        result['theme_store_id'] = theme_store_id
                else:
                    # No useful information found
                    return None
            
            # Add additional metadata
            if role:
                result['role'] = role
            if theme_id:
                result['theme_id'] = theme_id
                
            return result
        
        return None
    
    def _validate_theme_name(self, theme_name):
        """Validate and filter theme names to avoid promotional content"""
        if not theme_name or len(theme_name.strip()) == 0:
            return None
            
        theme_name = theme_name.strip()
        
        # Convert to lowercase for checking
        name_lower = theme_name.lower()
        
        # Invalid patterns that indicate promotional content or invalid names
        invalid_patterns = [
            # Date patterns
            r'\d{1,2}\/\d{1,2}',  # 7/24, 3/15, etc.
            r'\d{4}-\d{1,2}-\d{1,2}',  # 2024-07-24
            r'\d{1,2}-\d{1,2}-\d{4}',  # 07-24-2024
            
            # Promotional keywords
            r'\b(launch|sale|promo|campaign|event|day|week|month)\b',
            r'\b(national|international|world|global)\b.*\bday\b',
            r'\b(black friday|cyber monday|christmas|halloween|valentine)\b',
            r'\b(spring|summer|fall|winter|holiday)\b.*\b(sale|collection)\b',
            
            # Version-like patterns that are too specific
            r'^\[[\d\.]+\]',  # [3.5.1]
            r'^v\d+\.\d+',    # v1.2
            
            # Generic or temporary names
            r'^(temp|tmp|test|dev|staging|beta|alpha)[\s\-\_]',
            r'\b(lipstick|cosmetic|makeup|beauty)\b.*\b(day|launch|event)\b',
            
            # Too long or contains excessive special characters
            r'.{50,}',  # Names longer than 50 characters are likely invalid
            r'[^\w\s\-\_]{3,}',  # Too many special characters
        ]
        
        # Check against invalid patterns
        for pattern in invalid_patterns:
            if re.search(pattern, name_lower):
                return None
        
        # Known valid theme names (whitelist approach)
        known_themes = {
            'dawn', 'debut', 'brooklyn', 'minimal', 'supply', 'narrative', 'simple',
            'craft', 'venture', 'boundless', 'testament', 'sense', 'taste', 'prestige',
            'warehouse', 'impulse', 'motion', 'woodstock', 'refresh', 'split', 'avenue',
            'pipeline', 'context', 'editions', 'symmetry', 'focal', 'publisher',
            'streamline', 'broadcast', 'district', 'expression', 'flow', 'influence',
            'blockshop', 'canopy', 'flex', 'origin', 'studio', 'colorblock', 'spotlight',
            'ride', 'expanse', 'local', 'baseline', 'trade', 'highlights', 'combine',
            'enterprise', 'crave', 'fashionopolism', 'pacific',
            # Add some common custom theme names
            'allbirds-theme', 'gymshark', 'colourpop', 'custom', 'theme'
        }
        
        # Check if it's a known theme name
        theme_base = re.sub(r'[-_\s]+theme$', '', name_lower)  # Remove "-theme" suffix
        if name_lower in known_themes or theme_base in known_themes:
            return theme_name.title()
        
        # For unknown names, apply more flexible validation
        # Must be reasonable length and not match invalid patterns
        if (2 <= len(theme_name) <= 40 and 
            re.match(r'^[a-zA-Z][a-zA-Z0-9\s\-\_]*[a-zA-Z0-9]$', theme_name) and
            not re.search(r'\d{4,}', theme_name)):  # Allow shorter number sequences
            return theme_name.title()
        
        return None
    
    def _verify_theme_by_store_id(self, store_id):
        """Verify theme name by checking Shopify theme store"""
        try:
            # Comprehensive theme store IDs mapping
            known_themes = {
                # Free themes
                887: 'Dawn',
                796: 'Debut', 
                808: 'Brooklyn',
                384: 'Minimal',
                580: 'Supply',
                578: 'Narrative',
                730: 'Simple',
                
                # Premium themes
                862: 'Craft',
                775: 'Venture',
                686: 'Boundless',
                829: 'Testament',
                898: 'Sense',
                844: 'Taste',
                793: 'Prestige',
                787: 'Warehouse',
                851: 'Impulse',
                847: 'Motion',
                836: 'Woodstock',
                888: 'Refresh',
                869: 'Split',
                816: 'Avenue',
                813: 'Pipeline',
                841: 'Context',
                834: 'Editions',
                845: 'Symmetry',
                839: 'Focal',
                876: 'Publisher',
                858: 'Streamline',
                879: 'Broadcast',
                885: 'District',
                824: 'Expression',
                833: 'Flow',
                860: 'Influence',
                864: 'Blockshop',
                856: 'Canopy',
                877: 'Flex',
                890: 'Origin',
                892: 'Studio',
                894: 'Colorblock',
                896: 'Spotlight',
                900: 'Ride',
                902: 'Expanse',
                904: 'Local',
                906: 'Baseline',
                908: 'Trade',
                910: 'Be Yours',
                912: 'Highlights',
                914: 'Combine',
                916: 'Enterprise',
                918: 'Crave',
                920: 'Fashionopolism',
                922: 'Pacific'
            }
            
            if store_id in known_themes:
                return known_themes[store_id]
            
            # For unknown store IDs, you could make a request to Shopify theme store
            # but for now, we'll return None to avoid external dependencies
            return None
            
        except Exception:
            return None
    
    def _check_css_theme_headers(self, html_content, base_url):
        """Check CSS file headers for theme information as backup method"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find CSS links
            css_links = soup.find_all('link', {'rel': 'stylesheet'})
            
            for link in css_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Focus on main theme CSS files
                if any(keyword in href.lower() for keyword in ['theme', 'base', 'main', 'style']):
                    css_url = urljoin(base_url, href) if not href.startswith('http') else href
                    
                    # Download and check CSS file header
                    theme_info = self._analyze_css_header(css_url)
                    if theme_info:
                        return theme_info
            
        except Exception as e:
            logger.debug(f"CSS header check failed: {e}")
        
        return None
    
    def _analyze_css_header(self, css_url):
        """Analyze CSS file header comments for theme information"""
        try:
            response = self.session.get(css_url, timeout=10)
            response.raise_for_status()
            
            css_content = response.text
            
            # Look for header comments (first 2000 characters should be enough)
            header = css_content[:2000]
            
            # Common patterns in CSS headers
            patterns = {
                'theme_name': [
                    r'Theme Name\s*:\s*([^\n\r]+)',
                    r'Theme\s*:\s*([^\n\r]+)',
                    r'/\*\s*([A-Za-z\s]+)\s+Theme\s*\*/',
                    r'@name\s+([^\n\r]+)'
                ],
                'author': [
                    r'Author\s*:\s*([^\n\r]+)',
                    r'By\s*:\s*([^\n\r]+)',
                    r'@author\s+([^\n\r]+)'
                ],
                'version': [
                    r'Version\s*:\s*([^\n\r]+)',
                    r'@version\s+([^\n\r]+)'
                ]
            }
            
            extracted_info = {}
            for info_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, header, re.IGNORECASE)
                    if match:
                        extracted_info[info_type] = match.group(1).strip()
                        break
            
            if 'theme_name' in extracted_info:
                return {
                    'name': extracted_info['theme_name'].title(),
                    'confidence': 75,
                    'detected_patterns': ['CSS header comment'],
                    'source': 'css_header',
                    'css_url': css_url,
                    **{k: v for k, v in extracted_info.items() if k != 'theme_name'}
                }
        
        except Exception as e:
            logger.debug(f"CSS analysis failed for {css_url}: {e}")
        
        return None
    
    def detect_theme(self, url):
        """Detect Shopify theme for specified URL"""
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Check if it's a Shopify site
            if not self.is_shopify_site(url):
                return {
                    'success': False,
                    'error': 'This website is not a Shopify store or cannot be accessed',
                    'url': url
                }
            
            # Get website content
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Extract theme information
            theme_info = self.extract_theme_info(response.text, url)
            
            return {
                'success': True,
                'url': url,
                'theme': theme_info,
                'site_title': self._extract_site_title(response.text)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network request failed: {str(e)}',
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error occurred during detection: {str(e)}',
                'url': url
            }
    
    def _extract_site_title(self, html_content):
        """Extract website title"""
        try:
            # Use regex to extract title tag content
            title_pattern = r'<title[^>]*>([^<]*)</title>'
            title_match = re.search(title_pattern, html_content, re.IGNORECASE)
            return title_match.group(1).strip() if title_match else 'Unknown'
        except:
            return 'Unknown'

class BlogManager:
    """Blog Article Manager"""
    
    def __init__(self, blog_dir='blog'):
        self.blog_dir = blog_dir
        self.posts_dir = os.path.join(blog_dir, 'posts')
        self.config_file = os.path.join(blog_dir, 'config.json')
        self.posts_cache = {}
        self.config = self._load_config()
        self.md = markdown.Markdown(extensions=['toc', 'codehilite', 'fenced_code'])
        
    def _load_config(self):
        """Load blog configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "blog": {
                    "title": "Blog",
                    "description": "Blog Articles",
                    "author": "Admin",
                    "posts_per_page": 10,
                    "date_format": "%B %d, %Y"
                }
            }
    
    def _parse_post_file(self, file_path):
        """Parse individual article file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Extract information from filename
            filename = os.path.basename(file_path)
            file_slug = os.path.splitext(filename)[0]
            
            # Process metadata
            metadata = post.metadata
            
            # Ensure required fields exist
            if 'title' not in metadata:
                metadata['title'] = file_slug
            
            if 'date' not in metadata:
                # Try to extract date from filename
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
                if date_match:
                    metadata['date'] = date_match.group(1)
                else:
                    metadata['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Parse date
            if isinstance(metadata['date'], str):
                metadata['date'] = date_parse(metadata['date']).date()
            
            # Generate slug
            if 'slug' not in metadata:
                metadata['slug'] = file_slug
            
            # Generate HTML content
            html_content = self.md.convert(post.content)
            
            # Generate summary
            if 'description' not in metadata:
                # Generate summary from content (first 150 characters)
                text_content = re.sub(r'<[^>]+>', '', html_content)
                metadata['description'] = text_content[:150] + '...' if len(text_content) > 150 else text_content
            
            return {
                'metadata': metadata,
                'content': post.content,
                'html': html_content,
                'file_path': file_path,
                'url': f"/blog/{metadata['slug']}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing post file {file_path}: {e}")
            return None
    
    def load_posts(self, force_reload=False):
        """Load all articles"""
        if self.posts_cache and not force_reload:
            return self.posts_cache
        
        posts = {}
        
        if not os.path.exists(self.posts_dir):
            logger.warning(f"Posts directory {self.posts_dir} does not exist")
            return posts
        
        # Find all markdown files
        post_files = glob.glob(os.path.join(self.posts_dir, '*.md'))
        
        for file_path in post_files:
            post = self._parse_post_file(file_path)
            if post:
                slug = post['metadata']['slug']
                posts[slug] = post
        
        # Sort by date
        self.posts_cache = dict(sorted(posts.items(), 
                                     key=lambda x: x[1]['metadata']['date'], 
                                     reverse=True))
        
        return self.posts_cache
    
    def get_post(self, slug):
        """Get single article"""
        posts = self.load_posts()
        return posts.get(slug)
    
    def get_posts_list(self, page=1, per_page=None):
        """Get article list (paginated)"""
        posts = self.load_posts()
        posts_list = list(posts.values())
        
        if per_page is None:
            per_page = self.config['blog']['posts_per_page']
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return {
            'posts': posts_list[start_idx:end_idx],
            'total': len(posts_list),
            'page': page,
            'per_page': per_page,
            'has_prev': page > 1,
            'has_next': end_idx < len(posts_list),
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if end_idx < len(posts_list) else None
        }
    
    def get_featured_posts(self, limit=5):
        """Get featured articles"""
        posts = self.load_posts()
        featured = [post for post in posts.values() if post['metadata'].get('featured', False)]
        return featured[:limit]
    
    def get_posts_by_tag(self, tag):
        """Get articles by tag"""
        posts = self.load_posts()
        tagged_posts = []
        
        for post in posts.values():
            tags = post['metadata'].get('tags', [])
            if tag in tags:
                tagged_posts.append(post)
        
        return tagged_posts
    
    def get_all_tags(self):
        """Get all tags"""
        posts = self.load_posts()
        tags = set()
        
        for post in posts.values():
            post_tags = post['metadata'].get('tags', [])
            tags.update(post_tags)
        
        return sorted(list(tags))

# Create instances
detector = ShopifyThemeDetector()
blog_manager = BlogManager()
i18n = MultilingualManager()

@app.route('/set_language/<language_code>')
def set_language(language_code):
    """Set language and redirect back to referrer"""
    if i18n.set_language(language_code):
        logger.info(f"Language set to: {language_code}")
    else:
        logger.warning(f"Invalid language code: {language_code}")
    
    # Redirect back to the page the user came from
    return redirect(request.referrer or '/')

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact Us page"""
    return render_template('contact.html')

@app.route('/disclaimer')
def disclaimer():
    """Disclaimer page"""
    return render_template('disclaimer.html')

@app.route('/blog')
def blog_index():
    """Blog homepage"""
    try:
        page = request.args.get('page', 1, type=int)
        posts_data = blog_manager.get_posts_list(page=page)
        blog_config = blog_manager.config['blog']
        
        return render_template('blog/index.html', 
                             posts_data=posts_data,
                             blog_config=blog_config)
    except Exception as e:
        logger.error(f"Blog index error: {e}")
        return render_template('blog/index.html', 
                             posts_data={'posts': [], 'total': 0},
                             blog_config=blog_manager.config['blog'])

@app.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post"""
    try:
        post = blog_manager.get_post(slug)
        if not post:
            abort(404)
        
        blog_config = blog_manager.config['blog']
        
        # Get related articles (same tags)
        related_posts = []
        if post['metadata'].get('tags'):
            for tag in post['metadata']['tags'][:2]:  # Take up to first 2 tags
                tag_posts = blog_manager.get_posts_by_tag(tag)
                for related_post in tag_posts:
                    if (related_post['metadata']['slug'] != slug and 
                        related_post not in related_posts):
                        related_posts.append(related_post)
                if len(related_posts) >= 3:  # Show up to 3 related articles
                    break
        
        return render_template('blog/post.html', 
                             post=post,
                             related_posts=related_posts[:3],
                             blog_config=blog_config)
    except Exception as e:
        logger.error(f"Blog post error: {e}")
        abort(404)

@app.route('/blog/tag/<tag>')
def blog_tag(tag):
    """Filter articles by tag"""
    try:
        posts = blog_manager.get_posts_by_tag(tag)
        blog_config = blog_manager.config['blog']
        
        return render_template('blog/tag.html', 
                             posts=posts,
                             tag=tag,
                             blog_config=blog_config)
    except Exception as e:
        logger.error(f"Blog tag error: {e}")
        return render_template('blog/tag.html', 
                             posts=[],
                             tag=tag,
                             blog_config=blog_manager.config['blog'])

@app.route('/blog/feed')
def blog_feed():
    """RSS Feed"""
    try:
        posts = list(blog_manager.load_posts().values())[:10]  # Latest 10 articles
        blog_config = blog_manager.config['blog']
        
        # Generate RSS XML
        from flask import Response
        
        rss_items = []
        for post in posts:
            metadata = post['metadata']
            rss_items.append(f"""
        <item>
            <title><![CDATA[{metadata['title']}]]></title>
            <link>http://example.com{post['url']}</link>
            <description><![CDATA[{metadata.get('description', '')}]]></description>
            <pubDate>{metadata['date'].strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            <guid>http://example.com{post['url']}</guid>
        </item>""")
        
        rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title><![CDATA[{blog_config['title']}]]></title>
        <link>http://example.com/blog</link>
        <description><![CDATA[{blog_config['description']}]]></description>
        <language>zh-CN</language>
        {''.join(rss_items)}
    </channel>
</rss>"""
        
        return Response(rss_content, mimetype='application/rss+xml')
    except Exception as e:
        logger.error(f"RSS feed error: {e}")
        return Response("", mimetype='application/rss+xml')

@app.route('/api/detect', methods=['POST'])
def detect_theme_api():
    """Theme detection API endpoint"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid URL'
            }), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL cannot be empty'
            }), 400
        
        # Detect theme
        result = detector.detect_theme(url)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file for search engine crawlers"""
    try:
        with open('robots.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        response = app.response_class(
            content,
            mimetype='text/plain'
        )
        return response
    except FileNotFoundError:
        # If file doesn't exist, return basic robots.txt content
        basic_robots = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /health
Crawl-delay: 1"""
        response = app.response_class(
            basic_robots,
            mimetype='text/plain'
        )
        return response

@app.route('/sitemap.xml')
def sitemap_xml():
    """Generate dynamic sitemap.xml including blog posts"""
    try:
        from flask import Response
        from datetime import datetime
        
        # Base pages
        base_urls = [
            {
                'loc': 'https://shopify-theme-detector.com/',
                'lastmod': '2025-01-06',
                'changefreq': 'weekly',
                'priority': '1.0'
            },
            {
                'loc': 'https://shopify-theme-detector.com/about',
                'lastmod': '2025-01-06', 
                'changefreq': 'monthly',
                'priority': '0.8'
            },
            {
                'loc': 'https://shopify-theme-detector.com/contact',
                'lastmod': '2025-01-06',
                'changefreq': 'monthly', 
                'priority': '0.7'
            },
            {
                'loc': 'https://shopify-theme-detector.com/disclaimer',
                'lastmod': '2025-01-06',
                'changefreq': 'yearly',
                'priority': '0.5'
            },
            {
                'loc': 'https://shopify-theme-detector.com/blog',
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '0.9'
            }
        ]
        
        # Get all blog posts
        posts = blog_manager.load_posts()
        blog_urls = []
        
        for post in posts.values():
            blog_urls.append({
                'loc': f"https://shopify-theme-detector.com{post['url']}",
                'lastmod': post['metadata']['date'].strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.8'
            })
        
        # Get all tags
        tags = blog_manager.get_all_tags()
        tag_urls = []
        
        for tag in tags:
            tag_urls.append({
                'loc': f"https://shopify-theme-detector.com/blog/tag/{tag}",
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.6'
            })
        
        # Merge all URLs
        all_urls = base_urls + blog_urls + tag_urls
        
        # Generate XML
        url_entries = []
        for url_data in all_urls:
            url_entry = f"""  <url>
    <loc>{url_data['loc']}</loc>
    <lastmod>{url_data['lastmod']}</lastmod>
    <changefreq>{url_data['changefreq']}</changefreq>
    <priority>{url_data['priority']}</priority>
  </url>"""
            url_entries.append(url_entry)
        
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(url_entries)}
</urlset>"""
        
        response = Response(sitemap_content, mimetype='application/xml')
        return response
        
    except Exception as e:
        logger.error(f"Sitemap generation error: {e}")
        # If dynamic generation fails, fallback to static file
        try:
            with open('sitemap.xml', 'r', encoding='utf-8') as f:
                content = f.read()
            return Response(content, mimetype='application/xml')
        except FileNotFoundError:
            return "Sitemap not found", 404

# Error Handlers
@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 error page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Custom 500 error page"""
    return render_template('500.html'), 500

@app.context_processor
def inject_i18n():
    """Make i18n functions available to all templates"""
    return {
        'i18n': i18n,
        'current_language': i18n.get_language(),
        'supported_languages': i18n.supported_languages,
        'get_language_name': i18n.get_language_name
    }

@app.context_processor
def inject_seo_helpers():
    """Make SEO helper functions available to all templates"""
    def canonical_url():
        """Generate canonical URL for current page"""
        # Remove query parameters for canonical URL
        base_url = request.base_url
        # Handle language switching - use default language for canonical
        if '/set_language/' in base_url:
            return request.referrer or '/'
        return base_url
    
    def page_title():
        """Generate proper page title based on current route"""
        route = request.endpoint
        if route == 'index':
            return i18n.get_text('site.title') + ' - ' + i18n.get_text('hero.title')
        elif route == 'blog_index':
            return 'Blog - ' + i18n.get_text('site.title')
        elif route == 'blog_post':
            # Get blog post title if available
            return 'Blog Post - ' + i18n.get_text('site.title')
        elif route == 'about':
            return 'About Us - ' + i18n.get_text('site.title')
        elif route == 'contact':
            return 'Contact - ' + i18n.get_text('site.title')
        elif route == 'disclaimer':
            return 'Disclaimer - ' + i18n.get_text('site.title')
        else:
            return i18n.get_text('site.title')
    
    return {
        'canonical_url': canonical_url,
        'page_title': page_title
    }

if __name__ == '__main__':
    # Use environment variable for debug mode (default: False for production safety)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))