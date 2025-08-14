---
title: "Shopify Liquid Template Language: Complete Beginner's Guide"
date: "2024-08-16"
author: "Sarah Johnson"
tags: ["liquid", "templates", "development", "tutorial"]
description: "Learn Shopify Liquid template language from scratch. Master basic syntax, common objects, and practical techniques to build a solid foundation for theme customization."
featured: false
slug: "liquid-template-basics"
---

# Shopify Liquid Template Language: Complete Beginner's Guide

Liquid is the core technology for Shopify theme development, and mastering Liquid syntax is an essential skill for theme customization. This tutorial will take you from zero to proficient in Liquid, helping you quickly get started with theme development.

## 🎨 What is Liquid?

Liquid is a safe, designer-friendly template language developed and open-sourced by Shopify. It has the following characteristics:

- **Safe and Reliable** - Cannot execute arbitrary code
- **Easy to Learn** - Intuitive syntax with a gentle learning curve
- **Powerful** - Supports complex template logic
- **High Performance** - Compiled execution, fast speed

## 📝 Basic Syntax

### 1. Output Tags `{{ }}`

Used to output variables and expressions:

```liquid
<!-- Output product title -->
{{ product.title }}

<!-- Output formatted price -->
{{ product.price | money }}

<!-- Output current date -->
{{ 'now' | date: '%B %d, %Y' }}
```

### 2. Logic Tags `{% %}`

Used to control template logic:

```liquid
<!-- Conditional statements -->
{% if product.available %}
  <button>Buy Now</button>
{% else %}
  <button disabled>Sold Out</button>
{% endif %}

<!-- Loop through items -->
{% for variant in product.variants %}
  <option value="{{ variant.id }}">{{ variant.title }}</option>
{% endfor %}
```

### 3. Comments `{% comment %}`

```liquid
{% comment %}
This is a comment that won't be displayed on the page
Can be used for code documentation and temporarily disabling code
{% endcomment %}
```

## 🏗️ Core Objects

### 1. Product Object

```liquid
<!-- Basic product information -->
<h1>{{ product.title }}</h1>
<p>{{ product.description }}</p>
<span>{{ product.price | money }}</span>

<!-- Product image -->
<img src="{{ product.featured_image | img_url: '500x500' }}" 
     alt="{{ product.title }}">

<!-- Product variants -->
{% for variant in product.variants %}
  <div data-variant-id="{{ variant.id }}">
    <span>{{ variant.title }}</span>
    <span>{{ variant.price | money }}</span>
    {% if variant.available %}
      <span class="in-stock">In Stock</span>
    {% endif %}
  </div>
{% endfor %}
```

### 2. Collection Object

```liquid
<!-- Collection information -->
<h2>{{ collection.title }}</h2>
<p>{{ collection.description }}</p>

<!-- Loop through products in collection -->
{% for product in collection.products %}
  <div class="product-card">
    <a href="{{ product.url }}">
      <img src="{{ product.featured_image | img_url: '300x300' }}" 
           alt="{{ product.title }}">
      <h3>{{ product.title }}</h3>
      <span>{{ product.price | money }}</span>
    </a>
  </div>
{% endfor %}
```

### 3. Cart Object

```liquid
<!-- Cart information -->
<div class="cart-summary">
  <span>Item Count: {{ cart.item_count }}</span>
  <span>Total: {{ cart.total_price | money }}</span>
</div>

<!-- Cart items -->
{% for item in cart.items %}
  <div class="cart-item">
    <img src="{{ item.image | img_url: '100x100' }}" alt="{{ item.title }}">
    <div>
      <h4>{{ item.product.title }}</h4>
      <span>{{ item.variant.title }}</span>
      <span>Quantity: {{ item.quantity }}</span>
      <span>Price: {{ item.price | money }}</span>
    </div>
  </div>
{% endfor %}
```

## 🔧 Common Filters

### 1. String Filters

```liquid
<!-- Case conversion -->
{{ product.title | upcase }}        <!-- Convert to uppercase -->
{{ product.title | downcase }}      <!-- Convert to lowercase -->
{{ product.title | capitalize }}    <!-- Capitalize first letter -->

<!-- String operations -->
{{ product.description | truncate: 50 }}  <!-- Truncate to 50 characters -->
{{ product.title | replace: 'iPhone', 'iPad' }}  <!-- Replace text -->
{{ product.tags | join: ', ' }}     <!-- Array to string -->
```

### 2. Number Filters

```liquid
<!-- Price formatting -->
{{ product.price | money }}                    <!-- $99.00 -->
{{ product.price | money_without_currency }}   <!-- 99.00 -->

<!-- Mathematical operations -->
{{ product.price | times: 0.8 }}              <!-- 20% discount -->
{{ collection.products.size | plus: 1 }}      <!-- Count + 1 -->
{{ product.price | divided_by: 100 }}         <!-- Division -->
```

### 3. Date Filters

```liquid
<!-- Date formatting -->
{{ article.published_at | date: '%B %d, %Y' }}
{{ 'now' | date: '%H:%M' }}
{{ order.created_at | date: '%B %d, %Y' }}
```

### 4. Image Filters

```liquid
<!-- Image sizes -->
{{ product.featured_image | img_url: '500x500' }}
{{ product.featured_image | img_url: '300x' }}  <!-- Width 300px -->
{{ product.featured_image | img_url: 'master' }} <!-- Original size -->

<!-- Image tags -->
{{ product.featured_image | img_url: '400x400' | img_tag: product.title }}
```

## 🎯 Practical Tips

### 1. Advanced Conditional Statements

```liquid
<!-- Multiple conditions -->
{% if product.available and product.price < 10000 %}
  <span class="special-offer">Special Offer</span>
{% endif %}

<!-- Contains check -->
{% if product.tags contains 'sale' %}
  <span class="sale-badge">On Sale</span>
{% endif %}

<!-- Range check -->
{% assign discount = product.compare_at_price | minus: product.price %}
{% if discount > 0 %}
  <span class="discount">Save {{ discount | money }}</span>
{% endif %}
```

### 2. Advanced Loops

```liquid
<!-- Loop with index -->
{% for product in collection.products %}
  <div class="product-{{ forloop.index }}">
    {% if forloop.first %}<span class="first">First</span>{% endif %}
    {% if forloop.last %}<span class="last">Last</span>{% endif %}
    <h3>{{ product.title }}</h3>
  </div>
{% endfor %}

<!-- Limit loop count -->
{% for product in collection.products limit: 4 %}
  <!-- Show only first 4 products -->
{% endfor %}

<!-- Skip first few items -->
{% for product in collection.products offset: 2 %}
  <!-- Start from 3rd product -->
{% endfor %}
```

### 3. Variable Assignment

```liquid
<!-- Simple assignment -->
{% assign sale_price = product.price | times: 0.8 %}
{% assign product_count = collection.products.size %}

<!-- String concatenation -->
{% assign image_alt = product.title | append: ' - ' | append: variant.title %}

<!-- Array operations -->
{% assign sorted_products = collection.products | sort: 'price' %}
{% assign featured_products = collection.products | where: 'tags', 'featured' %}
```

## 🚀 Real-World Examples

### Product Recommendation Component

```liquid
<div class="product-recommendations">
  <h3>Related Products</h3>
  {% assign related_products = collections[product.type].products | 
      where: 'available' | 
      limit: 4 %}
  
  {% for related in related_products %}
    {% unless related.id == product.id %}
      <div class="recommended-product">
        <a href="{{ related.url }}">
          <img src="{{ related.featured_image | img_url: '200x200' }}" 
               alt="{{ related.title }}">
          <h4>{{ related.title }}</h4>
          <span class="price">{{ related.price | money }}</span>
        </a>
      </div>
    {% endunless %}
  {% endfor %}
</div>
```

### Breadcrumb Navigation

```liquid
<nav class="breadcrumb">
  <a href="/">Home</a>
  {% if collection %}
    <span>/</span>
    <a href="{{ collection.url }}">{{ collection.title }}</a>
  {% endif %}
  {% if product %}
    <span>/</span>
    <span>{{ product.title }}</span>
  {% endif %}
</nav>
```

## 📚 Learning Resources

- [Shopify Liquid Official Documentation](https://shopify.dev/api/liquid)
- [Liquid Online Testing Tool](https://liquidjs.com/playground.html)
- [Shopify Developer Community](https://community.shopify.com/)

## 🎉 Summary

Mastering Liquid syntax is the foundation of Shopify theme development. Through this tutorial, you should now understand:

1. ✅ Liquid basic syntax
2. ✅ How to use core objects
3. ✅ Common filter applications
4. ✅ Practical development techniques

Keep practicing and exploring, and you'll soon become a Shopify theme development expert!

---

*Want to learn more Shopify development tips? Follow our blog for the latest tutorials!*