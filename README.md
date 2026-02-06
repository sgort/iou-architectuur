# IOU Architecture Documentation

[![MkDocs](https://img.shields.io/badge/docs-MkDocs-blue)](https://www.mkdocs.org/)
[![Material for MkDocs](https://img.shields.io/badge/theme-Material-00897B)](https://squidfunk.github.io/mkdocs-material/)
[![License](https://img.shields.io/badge/license-EUPL--1.2-blue)](LICENSE)

> Comprehensive documentation for the IOU Architecture Framework and RONL ecosystem, deployed to [iou-architectuur.open-regels.nl](https://iou-architectuur.open-regels.nl)

## 📋 Overview

This repository contains the source files for the IOU Architecture documentation website. The site provides comprehensive technical documentation for:

- **IOU Architecture Framework** - Information architecture for IOU
- **RONL Business API** - Business API layer for Dutch government services
- **CPSV Editor** - React application for creating CPSV-AP compliant RDF/Turtle files
- **Linked Data Explorer** - SPARQL visualization and DMN orchestration tool
- **Shared Backend** - Node.js API providing TriplyDB and Operaton integration

## 🌐 Live Documentation

**Production**: [https://iou-architectuur.open-regels.nl](https://iou-architectuur.open-regels.nl)

## 🏗️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Static Site Generator** | MkDocs | 1.5+ |
| **Theme** | Material for MkDocs | 9.5+ |
| **Internationalization** | mkdocs-static-i18n | 1.2+ |
| **Version Control** | Git | - |
| **Hosting** | Azure Static Web Apps | - |
| **CI/CD** | GitHub Actions | - |

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- A text editor (VS Code recommended)

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://git.open-regels.nl/showcases/iou-architectuur.git
cd iou-architectuur

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start development server
mkdocs serve
```

The site will be available at: **http://127.0.0.1:8000**

The development server features **hot reload** - changes to markdown files are reflected immediately in your browser.

## 📂 Repository Structure

```
iou-architectuur/
├── docs/
│   ├── en/                          # English documentation
│   │   ├── index.md                 # Homepage
│   │   ├── cpsv-editor/             # CPSV Editor docs
│   │   ├── linked-data-explorer/    # Linked Data Explorer docs
│   │   ├── ronl-business-api/       # RONL Business API docs
│   │   ├── shared-backend/          # Shared Backend docs
│   │   ├── contributing/            # Contribution guidelines
│   │   ├── assets/                  # Images and diagrams
│   │   └── stylesheets/             # Custom CSS
│   ├── nl/                          # Dutch documentation (translations)
│   │   └── [mirrors en/ structure]
│   └── includes/
│       └── abbreviations.md         # Common abbreviations
├── mkdocs.yml                       # MkDocs configuration
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
├── staticwebapp.config.json         # Azure SWA configuration
├── .github/workflows/               # GitHub Actions workflows
└── README.md                        # This file
```

## ✍️ Content Management

### Adding New Pages

1. Create a markdown file in `docs/en/[section]/`
2. Add the page to `mkdocs.yml` navigation:

```yaml
nav:
  - Section Name:
    - New Page: section/new-page.md
```

3. Create Dutch translation in `docs/nl/[section]/`
4. Test locally with `mkdocs serve`

### Markdown Features

The documentation supports:

- **Admonitions**: Info boxes, warnings, notes
- **Code blocks**: Syntax highlighting for 100+ languages
- **Mermaid diagrams**: Flowcharts, sequence diagrams, etc.
- **Tables**: GitHub-flavored markdown tables
- **Cross-references**: Internal links between pages
- **Emoji**: `:material-check:` renders as ✅

**Example:**

```markdown
!!! note "Important"
    This is an important note.

```python
def hello_world():
    print("Hello, World!")
```

[Link to another page](other-page.md)
```

### Images

Place images in `docs/en/assets/` and reference them:

```markdown
![Description](../assets/image.png)
```

Images are shared between English and Dutch versions (symlinked in `docs/nl/assets/`).

## 🌍 Multilingual Support

The site supports English (primary) and Dutch (translation).

### File Structure

```
docs/
├── en/
│   └── section/
│       └── page.md          # English content
└── nl/
    └── section/
        └── page.md          # Dutch translation
```

### Translation Workflow

1. Write content in English first (`docs/en/`)
2. Create Dutch translation (`docs/nl/`)
3. Keep folder structure identical
4. Use English filenames (e.g., `overview.md` not `overzicht.md`)

### Language Switcher

The language switcher in the top-right corner allows users to toggle between English and Dutch versions of the same page.

## 🔨 Building the Site

### Development Build

```bash
mkdocs serve
```

- Includes live reload
- Draft content visible
- Fast build times

### Production Build

```bash
mkdocs build
```

- Outputs to `site/` directory
- Minified assets
- Optimized for deployment
- Strict mode enabled (fails on warnings)

### Testing the Build

```bash
# Build and check for warnings
mkdocs build --strict

# Serve the production build
mkdocs serve --strict
```

## 🚢 Deployment

### Automatic Deployment (Recommended)

Every push to the `main` branch automatically deploys to production via GitHub Actions:

```bash
git add .
git commit -m "docs: update content"
git push origin main
```

**Pipeline Steps:**
1. ✅ Install Python dependencies
2. ✅ Build site with MkDocs
3. ✅ Deploy to Azure Static Web Apps
4. ✅ Invalidate CDN cache

**Deployment time**: ~2-3 minutes

### Manual Deployment

If needed, you can deploy manually using Azure CLI:

```bash
# Build locally
mkdocs build

# Deploy to Azure
az staticwebapp upload \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --source site/ \
  --token $AZURE_STATIC_WEB_APPS_API_TOKEN
```

## 🛠️ Development Tools

### Useful Scripts

```bash
# Check for broken links (after manual edits)
./find-broken-links.sh report

# Clean up old files
./cleanup-ronl-setup.sh
```

### Recommended VS Code Extensions

- **Python** - Python language support
- **Markdown All in One** - Markdown editing tools
- **markdownlint** - Markdown linting
- **Code Spell Checker** - Spell checking for documentation

### Linting

```bash
# Markdown linting
markdownlint docs/**/*.md

# Link checking
mkdocs build --strict
```

## 🎨 Styling

### Custom CSS

Custom styles are defined in `docs/stylesheets/extra.css` and follow the NL Design System:

- **Primary color**: `#154273` (Rijksoverheid blue)
- **Accent color**: `#e17000` (Orange)
- **Status colors**: Green, blue, orange, red for compliance states

### Theme Configuration

Theme settings in `mkdocs.yml`:

```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: orange
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/en/contributing/index.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test locally: `mkdocs serve`
5. Commit with clear messages: `git commit -m "docs: add XYZ section"`
6. Push to your fork: `git push origin feature/my-feature`
7. Open a merge request

### Commit Message Convention

```
docs: add new section about X
fix: correct typo in Y
feat: add multilingual support for Z
```

## 📊 Site Analytics

The site uses Azure Static Web Apps built-in analytics:

- Page views
- Unique visitors
- Geographic distribution
- Referral sources

Access analytics in the Azure Portal.

## 🔒 Security

### HTTPS

- Automatic SSL certificate via Let's Encrypt
- Forced HTTPS redirects
- Certificate auto-renewal

### Content Security Policy

Configured in `staticwebapp.config.json`:

```json
{
  "globalHeaders": {
    "Content-Security-Policy": "default-src 'self'; ...",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY"
  }
}
```

## 🐛 Troubleshooting

### Build Fails

**Check Python version:**
```bash
python --version  # Must be 3.10+
```

**Reinstall dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

### Links Not Working

**Check file paths:**
- Use relative paths: `../other-page.md`
- Check file actually exists
- Ensure proper casing (case-sensitive on Linux)

### Images Not Displaying

**Verify image path:**
```bash
ls -la docs/en/assets/your-image.png
```

**Use correct relative path from the markdown file.**

### Dutch Pages Showing English Content

**Check symlinks:**
```bash
ls -la docs/nl/assets
# Should show: assets -> ../en/assets
```

## 📞 Support

### Documentation Issues

- **Issue tracker**: [GitLab Issues](https://git.open-regels.nl/showcases/iou-architectuur/-/issues)
- **Email**: mailto:steven.gort@ictu.nl

### Technical Support

- **MkDocs**: [https://www.mkdocs.org/](https://www.mkdocs.org/)
- **Material Theme**: [https://squidfunk.github.io/mkdocs-material/](https://squidfunk.github.io/mkdocs-material/)
- **Azure Static Web Apps**: [https://docs.microsoft.com/azure/static-web-apps/](https://docs.microsoft.com/azure/static-web-apps/)

## 📚 Additional Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Azure Static Web Apps Documentation](https://docs.microsoft.com/azure/static-web-apps/)

## 📄 License

This documentation is licensed under the **European Union Public License v1.2** (EUPL-1.2).

## 🎯 Project Information

- **Organization**: Provincie Flevoland & RONL Initiative
- **Project**: IOU Architecture Framework
- **Status**: ✅ Production
- **Version**: 0.4
- **Last Updated**: February 2026

