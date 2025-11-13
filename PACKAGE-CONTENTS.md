# Package Contents - Azure Deployment for iou-architectuur.open-regels.nl

## 📦 What's Included

This package contains everything you need to deploy your Information Architecture Framework documentation to Azure Static Web Apps with GitLab CI/CD integration.

## File Structure

```
iou-architectuur-deployment/
├── 📄 Core Configuration Files
│   ├── mkdocs.yml                      # MkDocs configuration with i18n
│   ├── requirements.txt                # Python dependencies
│   ├── staticwebapp.config.json        # Azure Static Web Apps config
│   └── .gitlab-ci.yml                  # CI/CD pipeline definition
│
├── 🚀 Setup & Deployment
│   ├── setup-azure.sh                  # Automated Azure setup script
│   ├── QUICK-START.md                  # Get started in 2 hours
│   ├── DEPLOYMENT-GUIDE.md             # Complete step-by-step guide
│   └── README.md                       # Technical reference
│
├── 📖 Documentation
│   ├── ARCHITECTURE.md                 # System architecture diagrams
│   └── PACKAGE-CONTENTS.md             # This file
│
└── 📁 Content Structure
    └── docs/
        ├── index.md                    # Root redirect page
        ├── nl/                         # Dutch content
        │   ├── index.md                # NL landing page
        │   └── [framework parts go here]
        ├── en/                         # English content
        │   ├── index.md                # EN landing page
        │   └── [framework parts go here]
        └── overrides/                  # Custom theme
            └── stylesheets/
                └── extra.css           # NL Design System styling
```

## 📋 File Descriptions

### Configuration Files

**mkdocs.yml**
- Main MkDocs configuration
- Multilingual setup (Dutch/English)
- Material theme customization
- Plugin configuration (search, i18n, git-revision)
- Navigation structure
- **Action needed**: Update `repo_url` with your GitLab group name

**.gitlab-ci.yml**
- CI/CD pipeline definition
- Build and deploy stages
- Azure Static Web Apps deployment
- Preview environment support
- **Action needed**: None (works out of the box)

**requirements.txt**
- Python package dependencies
- MkDocs and plugins
- Material theme
- **Action needed**: None

**staticwebapp.config.json**
- Azure Static Web Apps configuration
- Routing rules
- Security headers (CSP, X-Frame-Options)
- Cache control
- **Action needed**: None

### Setup Scripts

**setup-azure.sh**
- Automated Azure resource creation
- Creates resource group and Static Web App
- Generates deployment token
- Configures custom domain preparation
- Optionally enables Application Insights
- **Action needed**: Run once during initial setup

### Documentation

**QUICK-START.md**
- Fastest path to deployment
- 2-hour guide
- Three-phase approach
- Ideal for: Getting started quickly

**DEPLOYMENT-GUIDE.md**
- Comprehensive step-by-step instructions
- Complete with troubleshooting
- Testing checklists
- Ideal for: First-time deployment, reference

**README.md**
- Technical reference
- Repository structure
- Local development
- Content authoring guide
- Ideal for: Daily operations, team training

**ARCHITECTURE.md**
- System architecture diagrams
- Deployment flow
- Data flow
- Monitoring strategy
- Ideal for: Understanding the system

### Content Files

**docs/index.md**
- Root landing page
- Redirects to /nl/ by default
- Language selector

**docs/nl/index.md**
- Dutch landing page
- Framework overview
- Navigation to all parts
- **Action needed**: Customize with your content

**docs/en/index.md**
- English landing page
- Translated framework overview
- **Action needed**: Translate and customize

**docs/overrides/stylesheets/extra.css**
- Custom CSS matching NL Design System
- Status badge styles
- Namespace URI formatting
- MIM level indicators
- **Action needed**: Optional customization

## 🎯 Getting Started - Three Options

### Option 1: Quick Start (Recommended)
1. Read `QUICK-START.md`
2. Follow the three phases
3. Deploy in ~2 hours

### Option 2: Detailed Guide
1. Read `DEPLOYMENT-GUIDE.md`
2. Follow step-by-step instructions
3. Comprehensive with troubleshooting

### Option 3: Self-Directed
1. Read `README.md` for technical details
2. Customize as needed
3. Deploy using your own workflow

## ⚙️ Technical Specifications

### Technology Stack
- **Static Site Generator**: MkDocs 1.5.3+
- **Theme**: Material for MkDocs 9.5.0+
- **Languages**: Python 3.11+
- **CI/CD**: GitLab CI/CD
- **Hosting**: Azure Static Web Apps
- **SSL**: Let's Encrypt (automatic)

### Features
- ✅ Multilingual (Dutch/English)
- ✅ Full-text search
- ✅ Syntax highlighting (Turtle, SPARQL, RDF)
- ✅ Mobile responsive
- ✅ Dark mode support
- ✅ Automatic deployment (2-3 minutes)
- ✅ Custom domain with SSL
- ✅ Security headers (CSP, X-Frame-Options)
- ✅ NL Design System styling

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📊 What You Need to Provide

### Required
1. **Azure subscription** (Free tier works)
2. **GitLab account** on git.open-regels.nl
3. **DNS control** for open-regels.nl domain
4. **Framework content** in Markdown format

### Optional
5. **Application Insights** for monitoring
6. **Custom branding** (logo, colors)
7. **Additional pages** beyond the framework

## 🔧 Customization Points

### Easy Customizations
- Content (Markdown files)
- Colors (extra.css)
- Logo and favicon
- Navigation structure (mkdocs.yml)

### Moderate Customizations
- Theme templates (overrides/)
- Search configuration
- Plugin settings
- Security headers

### Advanced Customizations
- Custom plugins
- API integrations
- Authentication
- Advanced routing

## 💰 Cost Estimate

### Free Tier (Recommended)
- Monthly: €0.00
- Bandwidth: 100 GB/month
- Storage: 0.5 GB
- SSL: Included
- **Perfect for documentation**

### Standard Tier (Optional)
- Monthly: ~€8.00
- Same limits + overages
- Custom authentication
- SLA guarantee

### Expected Usage
- Bandwidth: < 10 GB/month
- Storage: < 100 MB
- **Recommendation**: Stay on Free tier

## 🎓 Learning Path

### For Content Authors
1. Read content authoring section in README.md
2. Learn basic Markdown
3. Practice with local development
4. Make small changes and deploy

### For Developers
1. Read ARCHITECTURE.md
2. Understand CI/CD pipeline
3. Customize as needed
4. Set up monitoring

### For Project Managers
1. Read QUICK-START.md
2. Understand deployment process
3. Review cost estimates
4. Plan content migration

## ✅ Pre-Deployment Checklist

Before starting deployment:

- [ ] Azure subscription ready
- [ ] Azure CLI installed
- [ ] GitLab account configured
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] DNS provider access confirmed
- [ ] Framework content prepared
- [ ] Stakeholders informed
- [ ] Backup plan in place

## 📞 Support Resources

### Included in Package
- Complete documentation
- Example configurations
- Sample content files
- Troubleshooting guides

### External Resources
- [Azure Static Web Apps Docs](https://learn.microsoft.com/azure/static-web-apps/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme Docs](https://squidfunk.github.io/mkdocs-material/)
- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)

### Community
- MkDocs Discussions: https://github.com/mkdocs/mkdocs/discussions
- Material Theme Discussions: https://github.com/squidfunk/mkdocs-material/discussions

## 🚨 Important Notes

### Security
- Deployment token is sensitive - store securely in GitLab
- Enable Protected and Masked for CI/CD variable
- Review security headers in staticwebapp.config.json
- Monitor access logs

### Maintenance
- Keep dependencies updated (requirements.txt)
- Monitor GitLab pipeline health
- Check Azure usage monthly
- Review content regularly

### Backup
- Git repository is primary backup
- Azure has no built-in backups
- Consider repository mirroring
- Document restoration process

## 🎉 Success Metrics

Your deployment is successful when:

- ✅ Site accessible at https://iou-architectuur.open-regels.nl
- ✅ SSL certificate valid (green padlock)
- ✅ Both languages work perfectly
- ✅ Search functionality works
- ✅ Mobile responsive
- ✅ Automatic deployment from GitLab
- ✅ Content updates deploy in 2-3 minutes
- ✅ No console errors
- ✅ Stakeholders can access
- ✅ Team knows how to update

## 📅 Timeline

### Initial Deployment
- Setup and testing: 2 hours
- DNS propagation: 15-30 minutes
- Content migration: 3-5 hours
- Total: ~1 business day

### Daily Operations
- Content updates: 5 minutes
- Deployment: Automatic (2-3 minutes)
- Review changes: As needed

## 🎁 Bonus Features

This package includes:

- NL Design System styling
- Status badge components
- Namespace URI formatting
- MIM level indicators
- Print-friendly styles
- Accessibility features (WCAG 2.1 AA)
- SEO-friendly markup

## 📝 Next Steps

1. **Start here**: Read QUICK-START.md
2. **Setup GitLab**: Create repository and copy files
3. **Setup Azure**: Run setup-azure.sh
4. **Connect**: Add token to GitLab CI/CD
5. **Test**: Verify deployment works
6. **Configure DNS**: Add custom domain
7. **Migrate content**: Convert framework to Markdown
8. **Launch**: Share with stakeholders

---

## Questions?

- Review documentation in this package
- Check Azure/GitLab/MkDocs documentation
- Contact your IT team for Azure support
- Reach out to project team for content questions

**Package Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Production Ready ✅

---

**Good luck with your deployment!** 🚀
