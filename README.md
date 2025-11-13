# Information Architecture Framework - Documentation Site

Comprehensive documentation for the Lelystad-Zuid Ring Road Information Architecture Framework, deployed via GitLab CI/CD to Azure Static Web Apps.

## 📋 Overview

This repository contains the source files for the multilingual documentation site hosted at `https://iou-architectuur.open-regels.nl`.

**Languages**: Nederlands (NL) | English (EN)

**Technology Stack**:
- **Static Site Generator**: MkDocs with Material Theme
- **Source Format**: Markdown
- **CI/CD**: GitLab CI/CD
- **Hosting**: Azure Static Web Apps
- **Version Control**: GitLab CE (self-hosted)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git
- Azure CLI (for initial setup)
- Access to self-hosted GitLab at `git.open-regels.nl`

### Local Development

1. **Clone the repository**:
```bash
git clone https://git.open-regels.nl/your-group/iou-architectuur.git
cd iou-architectuur
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run local development server**:
```bash
mkdocs serve
```

5. **Open browser**: http://127.0.0.1:8000

The site will auto-reload when you make changes to the Markdown files.

### Building the Site

```bash
mkdocs build
```

This creates a `site/` directory with static HTML files.

## 📂 Repository Structure

```
iou-architectuur/
├── docs/                           # Documentation source files
│   ├── index.md                    # Landing page (redirects to /nl/)
│   ├── nl/                         # Dutch documentation
│   │   ├── index.md
│   │   ├── deel-1-ontologie.md
│   │   ├── deel-2-implementatie.md
│   │   ├── deel-3-roadmap.md
│   │   └── assets/
│   ├── en/                         # English documentation
│   │   ├── index.md
│   │   ├── part-1-ontology.md
│   │   ├── part-2-implementation.md
│   │   ├── part-3-roadmap.md
│   │   └── assets/
│   ├── stylesheets/
│   │   └── extras.css
│   └── javascripts/                # Custom JavaScript
├── mkdocs.yml                      # MkDocs configuration
├── .gitlab-ci.yml                  # CI/CD pipeline
├── requirements.txt                # Python dependencies
├── staticwebapp.config.json        # Azure SWA configuration
├── setup-azure.sh                  # Azure setup script
└── README.md                       # This file
```

## 🔧 Initial Azure Setup

### Step 1: Run Setup Script

```bash
chmod +x setup-azure.sh
./setup-azure.sh
```

This script will:
1. Create Azure Resource Group
2. Create Static Web App
3. Generate deployment token
4. Configure custom domain
5. Optionally enable Application Insights

### Step 2: Configure GitLab CI/CD Variables

1. Go to your GitLab project: `https://git.open-regels.nl/your-group/iou-architectuur`
2. Navigate to **Settings > CI/CD > Variables**
3. Click **Add Variable**
4. Add the deployment token:
   - **Key**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - **Value**: [Token from setup script output]
   - **Type**: Variable
   - **Protected**: ✓ Yes
   - **Masked**: ✓ Yes
   - **Environment scope**: All

### Step 3: Configure DNS

Add these records to your DNS provider (where `open-regels.nl` is hosted):

**CNAME Record**:
```
Type: CNAME
Name: iou-architectuur
Value: [your-app].azurestaticapps.net
TTL: 3600
```

**TXT Record** (for domain validation):
```
Type: TXT
Name: _dnsauth.iou-architectuur
Value: [validation-token-from-azure]
TTL: 3600
```

To get the validation token:
```bash
az staticwebapp hostname show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --hostname iou-architectuur.open-regels.nl
```

### Step 4: Validate Custom Domain

1. Wait 5-10 minutes for DNS propagation
2. Go to Azure Portal: [Static Web Apps](https://portal.azure.com)
3. Select your app: `iou-architectuur`
4. Go to **Custom domains**
5. Click **Validate** next to `iou-architectuur.open-regels.nl`
6. Wait for SSL certificate provisioning (automatic via Let's Encrypt)

## 🔄 Deployment Workflow

### Automatic Deployment

Every push to the `main` branch automatically triggers deployment:

```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

**Pipeline stages**:
1. **Build**: MkDocs builds static site from Markdown
2. **Deploy**: Site uploaded to Azure Static Web Apps

**Deployment time**: ~2-3 minutes

### Manual Deployment

To deploy a specific branch manually:

```bash
# Build locally
mkdocs build

# Deploy using Azure CLI
az staticwebapp upload \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --source site/ \
  --token $AZURE_STATIC_WEB_APPS_API_TOKEN
```

### Preview Deployments

Merge requests can have preview deployments:

1. Create merge request in GitLab
2. Go to pipeline
3. Manually trigger `deploy:preview` job
4. Access at: `https://preview-[MR-ID].iou-architectuur.open-regels.nl`

## ✍️ Content Authoring

### Adding New Pages

1. Create Markdown file in appropriate language directory:
```bash
docs/nl/new-page.md
docs/en/new-page.md
```

2. Add to navigation in `mkdocs.yml`:
```yaml
nav:
  - New Page: nl/new-page.md
```

3. Commit and push

### Markdown Features

**Admonitions** (callout boxes):
```markdown
!!! note "Title"
    Content here

!!! warning
    Warning content

!!! success
    Success message
```

**Code blocks** with syntax highlighting:
````markdown
```turtle
@prefix flvl: <https://data.flevoland.nl/def/> .

flvl:LelystadProject a flvl:InfrastructureProject .
```
````

**Tables**:
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

**Cross-references**:
```markdown
See [Part 1](deel-1-ontologie.md#section-name)
```

### Adding RDF Examples

Use the `turtle` language identifier for syntax highlighting:

````markdown
```turtle
@prefix flvl-sp: <https://data.flevoland.nl/def/spatial-planning/> .
@prefix dcterms: <http://purl.org/dc/terms/> .

flvl-id:LelystadRingwegProject 
    a flvl-sp:InfrastructureProject ;
    dcterms:title "Lelystad-Zuid Ring Road Project"@en .
```
````

### Multilingual Content

Both Dutch and English versions must be maintained:

```
docs/
├── nl/
│   └── pagina.md          # Dutch version
└── en/
    └── page.md            # English version (same content, translated)
```

The i18n plugin handles language switching automatically.

## 🎨 Customization

### Styling

Custom CSS is in `docs/overrides/stylesheets/extra.css`.

Colors match NL Design System:
- Primary: `#154273` (Rijksoverheid blue)
- Accent: `#e17000` (Orange)
- Status colors for compliance states

### Theme Overrides

Custom HTML templates go in `docs/overrides/`.

Example: Custom footer in `docs/overrides/main.html`:
```html
{% extends "base.html" %}

{% block footer %}
  <!-- Your custom footer -->
{% endblock %}
```

## 📊 Monitoring

### Application Insights

If enabled during setup, view metrics at:
https://portal.azure.com → Application Insights → `iou-architectuur-insights`

**Metrics available**:
- Page views
- User sessions
- Performance
- Failures

### Build Logs

View CI/CD pipeline logs in GitLab:
`https://git.open-regels.nl/your-group/iou-architectuur/-/pipelines`

## 🔒 Security

### HTTPS

- Automatic SSL certificate via Let's Encrypt
- Certificate renewal handled by Azure
- Enforced HTTPS redirects

### Content Security Policy

Configured in `staticwebapp.config.json`:
- Restricts script sources
- Prevents XSS attacks
- Limits external resources

### Access Control

For restricted content (future):
```json
{
  "routes": [
    {
      "route": "/internal/*",
      "allowedRoles": ["authenticated"]
    }
  ]
}
```

## 🐛 Troubleshooting

### Build Fails

**Check Python version**:
```bash
python --version  # Should be 3.11+
```

**Reinstall dependencies**:
```bash
pip install --upgrade -r requirements.txt
```

**Check MkDocs syntax**:
```bash
mkdocs build --strict
```

### Deployment Fails

**Verify GitLab CI/CD variable**:
- Variable name exactly: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- No extra spaces
- Masked and Protected enabled

**Check pipeline logs**:
Go to GitLab → CI/CD → Pipelines → Latest run → View logs

### Custom Domain Not Working

**Verify DNS records**:
```bash
nslookup iou-architectuur.open-regels.nl
dig iou-architectuur.open-regels.nl CNAME
```

**Check Azure validation**:
Azure Portal → Static Web App → Custom domains → Status

**Wait for propagation**: DNS changes can take up to 24 hours

### Site Shows 404

**Check route configuration** in `staticwebapp.config.json`

**Verify build output**:
```bash
mkdocs build
ls -la site/
```

Should contain `index.html` and language directories.

## 💰 Cost Estimate

### Free Tier (Current)
- **Monthly cost**: €0.00
- 100 GB bandwidth
- 0.5 GB storage
- Free SSL certificate
- Unlimited static content

### Standard Tier (Optional Upgrade)
- **Monthly cost**: ~€8.00
- 100 GB bandwidth (then €0.15/GB)
- 0.5 GB storage (then €0.15/GB)
- Custom authentication
- SLA guarantee

**Expected usage** (documentation site):
- Bandwidth: < 10 GB/month
- Storage: < 100 MB
- **Recommendation**: Stay on Free tier

## 📞 Support

### For Framework Content Questions
- **Organization**: Provincie Flevoland
- **Department**: Infrastructure & Environment
- **Project**: Lelystad-Zuid Ring Road

### For Technical/Deployment Issues
- **GitLab**: https://git.open-regels.nl/your-group/iou-architectuur/-/issues
- **Azure Docs**: https://learn.microsoft.com/azure/static-web-apps/
- **MkDocs Docs**: https://www.mkdocs.org/

## 📚 Resources

- [MkDocs Material Documentation](https://squidfunk.github.io/mkdocs-material/)
- [Azure Static Web Apps Documentation](https://learn.microsoft.com/azure/static-web-apps/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Markdown Guide](https://www.markdownguide.org/)

## 📄 License

This documentation is proprietary to Provincie Flevoland.

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Maintained by**: Digital Infrastructure Team
