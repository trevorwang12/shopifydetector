#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shopify Theme Detector
This application can detect themes used by Shopify websites
"""

import re
import json
import requests
from urllib.parse import urlparse, urljoin
import html.parser
from flask import Flask, render_template, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
        """检查JavaScript文件中的主题信息"""
        # 使用正则表达式查找JavaScript文件
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
        """检查HTML注释中的主题信息"""
        # 使用正则表达式查找HTML注释
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
        """检查资源路径中的主题信息"""
        # 查找所有包含assets的链接
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
        """检查通用主题模式"""
        # 查找Shopify.theme对象
        theme_js_pattern = r'Shopify\.theme\s*=\s*{[^}]*name[^}]*}'
        matches = re.findall(theme_js_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            name_match = re.search(r'name["\']?\s*:\s*["\']([^"\',}]+)', match, re.IGNORECASE)
            if name_match:
                theme_name = name_match.group(1).strip()
                return {
                    'name': theme_name.title(),
                    'confidence': 95,
                    'detected_patterns': ['Shopify.theme object']
                }
        
        return None
    
    def detect_theme(self, url):
        """检测指定URL的Shopify主题"""
        try:
            # 标准化URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # 检查是否为Shopify网站
            if not self.is_shopify_site(url):
                return {
                    'success': False,
                    'error': '该网站不是Shopify网站或无法访问',
                    'url': url
                }
            
            # 获取网站内容
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 提取主题信息
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

# Create detector instance
detector = ShopifyThemeDetector()

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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))