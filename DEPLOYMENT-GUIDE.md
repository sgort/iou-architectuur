# Azure Deployment Guide - Step by Step

Complete guide for deploying the Information Architecture Framework documentation to Azure Static Web Apps with GitLab CI/CD.

## Prerequisites Checklist

Before starting, ensure you have:

- ✅ Azure subscription with appropriate permissions
- ✅ Azure CLI installed ([Download](https://learn.microsoft.com/cli/azure/install-azure-cli))
- ✅ Git installed
- ✅ Access to self-hosted GitLab CE at git.open-regels.nl
- ✅ Control over DNS for open-regels.nl domain
- ✅ Python 3.11+ for local testing

## Part 1: Local Setup and Testing (30 minutes)

### Step 1: Create GitLab Repository

1. Log in to GitLab at `https://git.open-regels.nl`
2. Create new project:
   - Name: `iou-architectuur`
   - Visibility: Internal or Private (your choice)
   - Initialize with README: No (we'll add our own)

### Step 2: Clone and Setup Locally

```bash
# Clone the empty repository
git clone https://git.open-regels.nl/your-group/iou-architectuur.git
cd iou-architectuur

# Copy all deployment files to this directory
# (The files from this delivery package)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Convert Your Framework to Markdown

You need to convert your three framework parts to Markdown:

```bash
# Create the content files
docs/nl/deel-1-ontologie.md       # From Framework_Part_1_Sections_1-3.md
docs/nl/deel-2-implementatie.md   # From Framework_Part2_Sections_4-7.md
docs/nl/deel-3-roadmap.md         # From Framework part 3

# Create English versions
docs/en/part-1-ontology.md
docs/en/part-2-implementation.md
docs/en/part-3-roadmap.md
```

**Tip**: I can help you convert these files if needed. The conversion mainly involves:
- Adding proper frontmatter
- Adjusting heading levels for navigation
- Adding cross-references
- Formatting code blocks properly

### Step 4: Test Locally

```bash
# Start development server
mkdocs serve

# Open browser to http://127.0.0.1:8000
# Verify:
# - Both languages work (NL/EN switcher)
# - Navigation is correct
# - Code blocks render properly
# - Links work
# - Search works
```

### Step 5: Initial Git Commit

```bash
git add .
git commit -m "Initial commit: Documentation framework setup"
git push origin main
```

## Part 2: Azure Resource Setup (15 minutes)

### Step 6: Login to Azure

```bash
# Login to Azure
az login

# If you have multiple subscriptions, select the correct one
az account list --output table
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"
```

### Step 7: Run Setup Script

```bash
# Make script executable
chmod +x setup-azure.sh

# Run the setup script
./setup-azure.sh
```

The script will:
1. ✅ Create resource group: `rg-iou-architectuur`
2. ✅ Create static web app: `iou-architectuur`
3. ✅ Output deployment token
4. ✅ Configure custom domain preparation
5. ✅ Optionally setup Application Insights

**IMPORTANT**: Save the deployment token displayed at the end!

```
Example output:
============================================================
Deployment token retrieved
============================================================

⚠️  IMPORTANT: Add this token to your GitLab CI/CD variables:
   Variable name: AZURE_STATIC_WEB_APPS_API_TOKEN
   Value: abc123...xyz789
   Protected: Yes
   Masked: Yes
```

### Step 8: Get Azure URLs

```bash
# Get your default Azure URL
az staticwebapp show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --query "defaultHostname" \
  --output tsv
```

Example output: `happy-stone-1234abcd.azurestaticapps.net`

## Part 3: GitLab CI/CD Configuration (10 minutes)

### Step 9: Add Deployment Token to GitLab

1. Go to: `https://git.open-regels.nl/your-group/iou-architectuur/-/settings/ci_cd`
2. Expand **Variables** section
3. Click **Add variable**
4. Fill in:
   - **Key**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - **Value**: [Paste the token from Step 7]
   - **Type**: Variable
   - **Protect variable**: ✓ Checked
   - **Mask variable**: ✓ Checked
   - **Expand variable reference**: Leave unchecked
5. Click **Add variable**

### Step 10: Verify Pipeline Configuration

Ensure `.gitlab-ci.yml` is present in your repository root. The file should already be there from the initial commit.

### Step 11: Trigger First Deployment

```bash
# Make a small change to trigger pipeline
echo "# Documentation" >> docs/nl/index.md
git add docs/nl/index.md
git commit -m "Trigger first deployment"
git push origin main
```

### Step 12: Monitor Deployment

1. Go to: `https://git.open-regels.nl/your-group/iou-architectuur/-/pipelines`
2. Watch the pipeline run:
   - ⏳ Build stage (1-2 minutes)
   - ⏳ Deploy stage (1-2 minutes)
3. Wait for ✅ Success

### Step 13: Test Deployment

Open your browser to the Azure default URL:
```
https://[your-app-name].azurestaticapps.net
```

Verify the site loads correctly.

## Part 4: Custom Domain Setup (20 minutes + DNS propagation)

### Step 14: Get DNS Configuration Values

```bash
# Get your default hostname (for CNAME)
az staticwebapp show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --query "defaultHostname" \
  --output tsv

# Add custom domain to trigger validation token generation
az staticwebapp hostname set \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --hostname iou-architectuur.open-regels.nl
```

### Step 15: Configure DNS Records

Log in to your DNS provider where `open-regels.nl` is managed.

**Add CNAME Record**:
```
Type: CNAME
Name: iou-architectuur
Value: [your-app].azurestaticapps.net
TTL: 3600 (or automatic)
```

**Add TXT Record** (for validation):

First, get the validation token:
```bash
az staticwebapp hostname show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --hostname iou-architectuur.open-regels.nl \
  --query "validationToken" \
  --output tsv
```

Then add DNS record:
```
Type: TXT
Name: _dnsauth.iou-architectuur
Value: [validation-token-from-command-above]
TTL: 3600
```

### Step 16: Verify DNS Propagation

Wait 5-10 minutes, then check:

```bash
# Check CNAME record
nslookup iou-architectuur.open-regels.nl

# Check TXT record
nslookup -type=TXT _dnsauth.iou-architectuur.open-regels.nl

# Alternative: Use online tool
# https://www.whatsmydns.net/
```

### Step 17: Validate Domain in Azure

**Option A: Via Azure Portal**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: Static Web Apps → `iou-architectuur`
3. Click **Custom domains** in left menu
4. Find `iou-architectuur.open-regels.nl`
5. Click **Validate**
6. Wait for validation (can take a few minutes)

**Option B: Via Azure CLI**
```bash
# Check validation status
az staticwebapp hostname show \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --hostname iou-architectuur.open-regels.nl
```

### Step 18: Wait for SSL Certificate

Azure automatically provisions a free SSL certificate from Let's Encrypt. This takes 5-15 minutes after domain validation.

Check status:
```bash
# In Azure Portal: Custom domains → Status should show "Ready"
```

### Step 19: Test Custom Domain

Open browser to:
```
https://iou-architectuur.open-regels.nl
```

Verify:
- ✅ Site loads
- ✅ HTTPS works (green padlock)
- ✅ Certificate is valid
- ✅ Both languages work
- ✅ Navigation works

## Part 5: Validation and Handoff (15 minutes)

### Step 20: Complete Testing Checklist

Test all functionality:

```
✅ Homepage loads (both NL and EN)
✅ Language switcher works
✅ All three framework parts are accessible
✅ Navigation menu works
✅ Search functionality works
✅ Code blocks render correctly with syntax highlighting
✅ RDF/Turtle examples display properly
✅ Tables render correctly
✅ Cross-references work
✅ Mobile responsive design works
✅ Print styles work (Ctrl+P)
```

### Step 21: Performance Check

```bash
# Test page load time
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://iou-architectuur.open-regels.nl

# Should be < 3 seconds
```

### Step 22: Security Verification

Check security headers:
```bash
curl -I https://iou-architectuur.open-regels.nl | grep -E "(X-|Content-Security)"
```

Should see:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: [configured policy]

### Step 23: Setup Monitoring (Optional)

If you enabled Application Insights:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: Application Insights → `iou-architectuur-insights`
3. Create dashboard with:
   - Page views
   - Unique users
   - Response times
   - Failure rate

## Part 6: Ongoing Maintenance

### Making Content Updates

```bash
# 1. Pull latest changes
git pull origin main

# 2. Edit Markdown files in docs/
# e.g., vim docs/nl/deel-1-ontologie.md

# 3. Test locally
mkdocs serve

# 4. Commit and push
git add docs/
git commit -m "Update: description of changes"
git push origin main

# 5. Deployment happens automatically (2-3 minutes)
```

### Monitoring Deployments

GitLab Pipeline URL:
```
https://git.open-regels.nl/your-group/iou-architectuur/-/pipelines
```

Set up email notifications:
1. Go to Settings → Notifications
2. Enable "Failed pipeline"

### Backup Strategy

Azure Static Web Apps doesn't provide built-in backups, but:
- ✅ Source is in GitLab (version controlled)
- ✅ Can rebuild anytime from source
- ✅ GitLab has its own backup strategy

Optional: Enable GitLab repository mirroring to GitHub/Azure Repos for redundancy.

## Troubleshooting Common Issues

### Pipeline Fails: "Python not found"

**Solution**: Update `.gitlab-ci.yml` image:
```yaml
image: python:3.11-slim  # Ensure correct version
```

### Pipeline Fails: "az: command not found"

**Solution**: The deploy stage uses Azure CLI image:
```yaml
deploy:azure:
  image: mcr.microsoft.com/azure-cli:latest
```

### Custom Domain Shows "Not Found"

**Solutions**:
1. Verify DNS records: `nslookup iou-architectuur.open-regels.nl`
2. Wait longer for DNS propagation (up to 24 hours)
3. Check Azure validation status
4. Clear browser cache

### Site Shows Old Content

**Solutions**:
1. Clear browser cache (Ctrl+Shift+R)
2. Check deployment succeeded in GitLab
3. Verify Azure shows latest deployment time
4. Check caching headers in `staticwebapp.config.json`

### Search Not Working

**Solution**: Rebuild search index:
```bash
mkdocs build --clean
git add .
git commit -m "Rebuild search index"
git push origin main
```

## Cost Management

### Current Setup (Free Tier)
- Monthly cost: **€0.00**
- Bandwidth limit: 100 GB/month
- Expected usage: < 10 GB/month
- Recommendation: ✅ Stay on Free tier

### Monitoring Usage

```bash
# Check usage (requires Standard tier)
az monitor metrics list \
  --resource iou-architectuur \
  --resource-group rg-iou-architectuur \
  --resource-type "Microsoft.Web/staticSites" \
  --metric "BytesSent"
```

### When to Upgrade to Standard (€8/month)

Upgrade if you need:
- Custom authentication
- More than 100 GB bandwidth/month
- SLA guarantee
- Advanced security features

## Success Criteria

Your deployment is complete when:

✅ Site accessible at https://iou-architectuur.open-regels.nl  
✅ Both Dutch and English versions work  
✅ All three framework parts display correctly  
✅ Search functionality works  
✅ HTTPS certificate is valid  
✅ GitLab pipeline succeeds  
✅ Updates deploy automatically within 3 minutes  
✅ Mobile responsive  
✅ No console errors  

## Next Steps

1. **Content Migration**: Convert all three framework parts to Markdown
2. **Stakeholder Review**: Share URL with stakeholders
3. **Feedback Integration**: Set up GitLab issues for feedback
4. **Documentation**: Train team on making updates
5. **Monitoring**: Set up alerting for deployment failures

## Support Contacts

### Azure Issues
- Azure Support Portal: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- Documentation: https://learn.microsoft.com/azure/static-web-apps/

### GitLab Issues
- Your GitLab Admin
- GitLab Documentation: https://docs.gitlab.com/

### Content Questions
- Project Team
- Provincie Flevoland Infrastructure & Environment

---

## Estimated Total Time

- **Initial Setup**: 90 minutes
- **DNS Propagation Wait**: 15-30 minutes
- **Content Migration**: 3-5 hours (depending on amount of editing needed)
- **Testing**: 30 minutes

**Total First Deployment**: ~2 hours active work + waiting time

**Subsequent Updates**: ~5 minutes

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Ready for production deployment
