# Blog Article Management Guide

## Directory Structure
```
blog/
├── config.json          # Blog configuration file
├── posts/               # Articles directory
│   ├── 2024-08-14-welcome-to-blog.md
│   └── ...
├── assets/              # Asset files
│   └── images/          # Image assets
└── README.md           # This guide file
```

## Article Writing Guidelines

### 1. File Naming
Article filename format: `YYYY-MM-DD-article-slug.md`
- Date: Article publication date
- slug: Article URL identifier (lowercase English, separated by hyphens)

### 2. Article Format
Each article must include YAML Front Matter:

```markdown
---
title: "Article Title"
date: "2024-08-14"
author: "Author Name"
tags: ["tag1", "tag2"]
description: "Article summary for SEO and social sharing"
featured: false
slug: "article-slug"
---

# Article Content

This is the article content...
```

### 3. Required Fields
- `title`: Article title
- `date`: Publication date (YYYY-MM-DD format)
- `author`: Author name
- `description`: Article description (within 150 characters)
- `slug`: URL identifier

### 4. Optional Fields
- `tags`: Array of tags
- `featured`: Whether it's a featured article (true/false)
- `image`: Featured image path
- `updated`: Last update date

## Publishing Workflow

### Git Workflow
1. Create a new markdown file in the `blog/posts/` directory
2. Write article content following the guidelines
3. Commit to git repository:
   ```bash
   git add blog/posts/new-article.md
   git commit -m "Publish new article: Article Title"
   git push origin main
   ```
4. Server automatically restarts, new article becomes accessible

### Image Assets
- Place images in the `blog/assets/images/` directory
- Reference in articles using relative paths: `![Image description](/blog/assets/images/image.jpg)`

## Article Management

### Editing Articles
Directly edit the corresponding markdown file, then commit to git.

### Deleting Articles
Delete the corresponding markdown file, then commit to git.

### Featured Articles
Set `featured: true` in the article's Front Matter.

## Important Notes
- Ensure article slugs are unique to avoid URL conflicts
- Recommended image size should not exceed 1MB
- Article content supports standard Markdown syntax
- Service restart required after modifying configuration files