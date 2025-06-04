#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - Shopify主题检测器
包含应用配置、主题数据库和检测规则
"""

import os

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'shopify-theme-detector-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 网络请求配置
    REQUEST_TIMEOUT = 15  # 请求超时时间（秒）
    MAX_RETRIES = 3       # 最大重试次数
    
    # 用户代理配置
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]

class ThemeDatabase:
    """主题数据库类 - 包含已知的Shopify主题信息"""
    
    # 官方主题
    OFFICIAL_THEMES = {
        'dawn': {
            'name': 'Dawn',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify官方免费主题，现代简洁设计',
            'patterns': [
                r'dawn[_-]?theme',
                r'shopify[_-]?dawn',
                r'assets/dawn',
                r'dawn.*\.css',
                r'dawn.*\.js'
            ],
            'css_signatures': [
                'dawn-theme',
                'dawn.css',
                'theme.dawn'
            ],
            'js_signatures': [
                'dawn.js',
                'theme.dawn.js'
            ]
        },
        'debut': {
            'name': 'Debut',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify经典免费主题',
            'patterns': [
                r'debut[_-]?theme',
                r'shopify[_-]?debut',
                r'assets/debut',
                r'debut.*\.css',
                r'debut.*\.js'
            ],
            'css_signatures': [
                'debut-theme',
                'debut.css',
                'theme.debut'
            ],
            'js_signatures': [
                'debut.js',
                'theme.debut.js'
            ]
        },
        'brooklyn': {
            'name': 'Brooklyn',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify官方付费主题，适合时尚品牌',
            'patterns': [
                r'brooklyn[_-]?theme',
                r'shopify[_-]?brooklyn',
                r'assets/brooklyn',
                r'brooklyn.*\.css',
                r'brooklyn.*\.js'
            ],
            'css_signatures': [
                'brooklyn-theme',
                'brooklyn.css',
                'theme.brooklyn'
            ],
            'js_signatures': [
                'brooklyn.js',
                'theme.brooklyn.js'
            ]
        },
        'minimal': {
            'name': 'Minimal',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify官方免费主题，极简设计',
            'patterns': [
                r'minimal[_-]?theme',
                r'shopify[_-]?minimal',
                r'assets/minimal',
                r'minimal.*\.css',
                r'minimal.*\.js'
            ],
            'css_signatures': [
                'minimal-theme',
                'minimal.css',
                'theme.minimal'
            ],
            'js_signatures': [
                'minimal.js',
                'theme.minimal.js'
            ]
        },
        'supply': {
            'name': 'Supply',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify官方免费主题，适合大库存商店',
            'patterns': [
                r'supply[_-]?theme',
                r'shopify[_-]?supply',
                r'assets/supply',
                r'supply.*\.css',
                r'supply.*\.js'
            ],
            'css_signatures': [
                'supply-theme',
                'supply.css',
                'theme.supply'
            ],
            'js_signatures': [
                'supply.js',
                'theme.supply.js'
            ]
        },
        'narrative': {
            'name': 'Narrative',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify官方免费主题，讲故事风格',
            'patterns': [
                r'narrative[_-]?theme',
                r'shopify[_-]?narrative',
                r'assets/narrative',
                r'narrative.*\.css',
                r'narrative.*\.js'
            ],
            'css_signatures': [
                'narrative-theme',
                'narrative.css',
                'theme.narrative'
            ],
            'js_signatures': [
                'narrative.js',
                'theme.narrative.js'
            ]
        },
        'venture': {
            'name': 'Venture',
            'author': 'Shopify',
            'type': 'Official',
            'description': 'Shopify官方免费主题，适合户外品牌',
            'patterns': [
                r'venture[_-]?theme',
                r'shopify[_-]?venture',
                r'assets/venture',
                r'venture.*\.css',
                r'venture.*\.js'
            ],
            'css_signatures': [
                'venture-theme',
                'venture.css',
                'theme.venture'
            ],
            'js_signatures': [
                'venture.js',
                'theme.venture.js'
            ]
        }
    }
    
    # 流行的第三方主题
    THIRD_PARTY_THEMES = {
        'impulse': {
            'name': 'Impulse',
            'author': 'Archetype Themes',
            'type': 'Premium',
            'description': '高转化率的电商主题',
            'patterns': [
                r'impulse[_-]?theme',
                r'archetype[_-]?impulse',
                r'assets/impulse'
            ]
        },
        'turbo': {
            'name': 'Turbo',
            'author': 'Out of the Sandbox',
            'type': 'Premium',
            'description': '快速加载的多功能主题',
            'patterns': [
                r'turbo[_-]?theme',
                r'outofthesandbox[_-]?turbo',
                r'assets/turbo'
            ]
        },
        'empire': {
            'name': 'Empire',
            'author': 'Pixel Union',
            'type': 'Premium',
            'description': '适合大型商店的主题',
            'patterns': [
                r'empire[_-]?theme',
                r'pixelunion[_-]?empire',
                r'assets/empire'
            ]
        },
        'prestige': {
            'name': 'Prestige',
            'author': 'Maestrooo',
            'type': 'Premium',
            'description': '高端奢侈品牌主题',
            'patterns': [
                r'prestige[_-]?theme',
                r'maestrooo[_-]?prestige',
                r'assets/prestige'
            ]
        },
        'warehouse': {
            'name': 'Warehouse',
            'author': 'Out of the Sandbox',
            'type': 'Premium',
            'description': '工业风格主题',
            'patterns': [
                r'warehouse[_-]?theme',
                r'outofthesandbox[_-]?warehouse',
                r'assets/warehouse'
            ]
        },
        'focal': {
            'name': 'Focal',
            'author': 'Maestrooo',
            'type': 'Premium',
            'description': '现代响应式主题',
            'patterns': [
                r'focal[_-]?theme',
                r'maestrooo[_-]?focal',
                r'assets/focal'
            ]
        }
    }
    
    # 合并所有主题
    ALL_THEMES = {**OFFICIAL_THEMES, **THIRD_PARTY_THEMES}
    
    @classmethod
    def get_theme_info(cls, theme_key):
        """获取主题信息"""
        return cls.ALL_THEMES.get(theme_key.lower())
    
    @classmethod
    def get_all_patterns(cls):
        """获取所有主题的检测模式"""
        patterns = {}
        for theme_key, theme_info in cls.ALL_THEMES.items():
            patterns[theme_key] = theme_info.get('patterns', [])
        return patterns

class DetectionRules:
    """检测规则类 - 定义主题检测的各种规则和权重"""
    
    # Shopify网站标识符
    SHOPIFY_INDICATORS = [
        'Shopify.shop',
        'shopify-section',
        'shopify-block',
        'cdn.shopify.com',
        'myshopify.com',
        'Shopify.theme',
        'shopify_pay',
        'shopify-features',
        'shopify.com/s/files',
        'Shopify.routes'
    ]
    
    # 检测方法权重（置信度）
    DETECTION_WEIGHTS = {
        'meta_tags': 90,           # meta标签中的主题信息
        'shopify_theme_object': 95, # Shopify.theme对象
        'css_files': 85,           # CSS文件名
        'js_files': 80,            # JavaScript文件名
        'html_comments': 75,       # HTML注释
        'asset_paths': 70,         # 资源路径
        'theme_patterns': 65,      # 通用主题模式
        'liquid_templates': 60     # Liquid模板标识
    }
    
    # 常见的主题文件模式
    THEME_FILE_PATTERNS = [
        r'/assets/theme[._-].*\.(css|js)',
        r'/assets/[^/]*theme[^/]*\.(css|js)',
        r'/assets/application[._-].*\.(css|js)',
        r'/assets/style[._-].*\.(css|js)',
        r'/assets/main[._-].*\.(css|js)'
    ]
    
    # Liquid模板标识符
    LIQUID_INDICATORS = [
        r'\{\{[^}]+\}\}',  # Liquid变量
        r'\{%[^%]+%\}',   # Liquid标签
        r'shopify\.',     # Shopify对象
        r'product\.',     # 产品对象
        r'collection\.',  # 集合对象
        r'cart\.',        # 购物车对象
        r'customer\.'     # 客户对象
    ]

# 导出配置
__all__ = ['Config', 'ThemeDatabase', 'DetectionRules']