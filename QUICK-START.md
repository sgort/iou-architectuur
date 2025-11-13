# Quick Start - Azure Deployment

## 🚀 Get Your Documentation Live in 2 Hours

This guide gets your Information Architecture Framework documentation deployed to `https://iou-architectuur.open-regels.nl` with multilingual support (Dutch/English).

## What You'll Get

✅ Static documentation site with beautiful Material Design theme  
✅ Dutch and English versions with language switcher  
✅ Automatic deployment from GitLab on every commit  
✅ Free Azure hosting with SSL certificate  
✅ Search functionality  
✅ Mobile responsive  
✅ Professional styling matching NL Design System  

## Prerequisites (5 minutes to verify)

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Azure CLI
az --version

# Check Git
git --version

# All installed? ✅ Continue!
```

If anything is missing, install from:
- Python: https://www.python.org/downloads/
- Azure CLI: https://learn.microsoft.com/cli/azure/install-azure-cli
- Git: https://git-scm.com/downloads

## Three-Phase Deployment

### Phase 1: GitLab Setup (15 minutes)

```bash
# 1. Create repository in GitLab
#    Go to https://git.open-regels.nl
#    Click "New project" → Name: iou-architectuur

# 2. Clone and setup
git clone https://git.open-regels.nl/your-group/iou-architectuur.git
cd iou-architectuur

# 3. Copy all files from this package into the repository
cp -r /path/to/iou-architectuur-deployment/* .

# 4. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 5. Test locally
mkdocs serve
# Open http://127.0.0.1:8000 - Does it work? ✅

# 6. Initial commit
git add .
git commit -m "Initial commit: Documentation framework"
git push origin main
```

### Phase 2: Azure Setup (15 minutes)

```bash
# 1. Login to Azure
az login

# 2. Run automated setup
chmod +x setup-azure.sh
./setup-azure.sh

# 3. SAVE THE DEPLOYMENT TOKEN shown at the end!
#    You'll need it in the next step
```

### Phase 3: Connect GitLab to Azure (10 minutes)

```bash
# 1. Add token to GitLab
#    Go to: https://git.open-regels.nl/your-group/iou-architectuur/-/settings/ci_cd
#    Click "Variables" → "Add variable"
#    Key: AZURE_STATIC_WEB_APPS_API_TOKEN
#    Value: [paste token from Phase 2]
#    Check: Protected, Masked
#    Click: Add variable

# 2. Trigger deployment
echo "# Test" >> README.md
git add README.md
git commit -m "Trigger first deployment"
git push origin main

# 3. Watch deployment
#    Go to: https://git.open-regels.nl/your-group/iou-architectuur/-/pipelines
#    Wait for ✅ Success (2-3 minutes)

# 4. Test your site
#    Open the Azure default URL (shown in setup script output)
#    Site works? ✅ Continue to custom domain!
```

### Phase 4: Custom Domain (20 minutes + DNS wait)

```bash
# 1. Get DNS values
az staticwebapp show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --query "defaultHostname" \
  --output tsv

# 2. Add DNS records in your DNS provider:

# CNAME Record:
# Name: iou-architectuur
# Value: [output from command above]
# TTL: 3600

# TXT Record (for validation):
# Name: _dnsauth.iou-architectuur
# Value: [run command below to get this]
# TTL: 3600

# Get validation token:
az staticwebapp hostname show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --hostname iou-architectuur.open-regels.nl \
  --query "validationToken" \
  --output tsv

# 3. Wait 10-15 minutes for DNS propagation

# 4. Validate in Azure Portal:
#    portal.azure.com → Static Web Apps → iou-architectuur
#    → Custom domains → Click "Validate"

# 5. Wait 5-10 minutes for SSL certificate

# 6. Test custom domain:
#    Open https://iou-architectuur.open-regels.nl
#    Works with HTTPS? ✅ You're done!
```

## Converting Your Framework Content

You need to convert your three framework parts from the current format to Markdown for the `docs/` directory.

### Quick Conversion Checklist

For each part, create both NL and EN versions:

```
docs/nl/deel-1-ontologie.md       ← Framework_Part_1_Sections_1-3.md
docs/nl/deel-2-implementatie.md   ← Framework_Part2_Sections_4-7.md  
docs/nl/deel-3-roadmap.md         ← Framework Part 3

docs/en/part-1-ontology.md        ← Translate deel-1
docs/en/part-2-implementation.md  ← Translate deel-2
docs/en/part-3-roadmap.md         ← Translate deel-3
```

### Conversion Tips

1. **Keep the structure**: Use the same headings and sections
2. **Code blocks**: Use proper syntax highlighting
   ```turtle
   @prefix flvl: <https://data.flevoland.nl/def/> .
   ```
3. **Admonitions**: Use for important notes
   ```markdown
   !!! note "Important"
       This is a note box
   ```
4. **Tables**: Keep as Markdown tables (they'll render beautifully)

**Need help with conversion?** I can assist with converting your framework parts to the proper Markdown format.

## Daily Updates Workflow

Once deployed, updating is simple:

```bash
# 1. Edit content
vim docs/nl/deel-1-ontologie.md

# 2. Test locally
mkdocs serve

# 3. Deploy
git add docs/
git commit -m "Update: brief description"
git push origin main

# Wait 2-3 minutes → Live! 🎉
```

## Troubleshooting

### "Pipeline failed"
- Check GitLab CI/CD logs
- Verify AZURE_STATIC_WEB_APPS_API_TOKEN is correct

### "Custom domain not working"
- Verify DNS with: `nslookup iou-architectuur.open-regels.nl`
- Wait longer (DNS can take 24 hours)
- Check Azure Portal validation status

### "Site shows old content"
- Hard refresh: Ctrl+Shift+R
- Clear browser cache
- Check deployment succeeded in GitLab

## Success Checklist

Your deployment is complete when you can check all these:

- ✅ https://iou-architectuur.open-regels.nl loads
- ✅ Green padlock (HTTPS works)
- ✅ Dutch content displays
- ✅ English content displays
- ✅ Language switcher works
- ✅ Search works
- ✅ All three framework parts are accessible
- ✅ Code blocks show syntax highlighting
- ✅ Pushing to GitLab triggers auto-deployment

## What's Next?

1. **Content migration**: Convert your full framework to Markdown
2. **Stakeholder review**: Share the URL
3. **Feedback process**: Set up GitLab issues
4. **Team training**: Show colleagues how to make updates
5. **Monitoring**: Optional Application Insights setup

## Cost

**Free Tier** (current setup):
- €0.00/month
- 100 GB bandwidth
- 0.5 GB storage
- Free SSL
- Perfect for documentation

## Getting Help

- **Detailed guide**: See `DEPLOYMENT-GUIDE.md` (complete step-by-step)
- **Technical reference**: See `README.md`
- **Azure docs**: https://learn.microsoft.com/azure/static-web-apps/
- **MkDocs docs**: https://www.mkdocs.org/

---

## Ready to Start?

Begin with **Phase 1: GitLab Setup** above! 🚀

**Estimated time to live site**: 90 minutes active work + 30 minutes DNS propagation

Good luck! You've got this. 💪
