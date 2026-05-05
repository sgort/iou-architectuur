#!/bin/bash

# Azure Static Web Apps Setup Script
# Creates and configures Azure resources for iou-architectuur.open-regels.nl

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="rg-iou-architectuur"
LOCATION="westeurope"
APP_NAME="iou-architectuur"
CUSTOM_DOMAIN="iou-architectuur.open-regels.nl"
SKU="Free"  # or "Standard" for production

echo "🚀 Setting up Azure Static Web Apps for Documentation Site"
echo "============================================================"

# Step 1: Login to Azure
echo "📝 Step 1: Azure Login"
az login

# Optional: Select subscription if you have multiple
# echo "Select your subscription:"
# az account list --output table
# read -p "Enter subscription ID: " SUBSCRIPTION_ID
# az account set --subscription "$SUBSCRIPTION_ID"

# Step 2: Create Resource Group
echo ""
echo "📦 Step 2: Creating Resource Group"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --tags "project=lelystad-ringweg" "environment=production" "type=documentation"

echo "✅ Resource group created: $RESOURCE_GROUP"

# Step 3: Create Static Web App
echo ""
echo "🌐 Step 3: Creating Static Web App"
echo "Note: You'll need to authorize Azure to access your GitLab repository"
echo "Since you're using self-hosted GitLab, we'll create the app without automatic GitHub integration"

az staticwebapp create \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku "$SKU" \
  --source "https://git.open-regels.nl/your-group/iou-architectuur" \
  --branch "main" \
  --app-location "/" \
  --output-location "site" \
  --tags "project=lelystad-ringweg" "environment=production"

echo "✅ Static Web App created: $APP_NAME"

# Step 4: Get deployment token
echo ""
echo "🔑 Step 4: Retrieving Deployment Token"
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.apiKey" \
  --output tsv)

echo "✅ Deployment token retrieved"
echo ""
echo "⚠️  IMPORTANT: Add this token to your GitLab CI/CD variables:"
echo "   Variable name: AZURE_STATIC_WEB_APPS_API_TOKEN"
echo "   Value: $DEPLOYMENT_TOKEN"
echo "   Protected: Yes"
echo "   Masked: Yes"
echo ""
echo "   Go to: https://git.open-regels.nl/your-group/iou-architectuur/-/settings/ci_cd"
echo ""

# Step 5: Get the default hostname
DEFAULT_URL=$(az staticwebapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "defaultHostname" \
  --output tsv)

echo "📍 Default URL: https://$DEFAULT_URL"

# Step 6: Add custom domain
echo ""
echo "🌍 Step 5: Setting up Custom Domain"
echo "Adding custom domain: $CUSTOM_DOMAIN"

az staticwebapp hostname set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --hostname "$CUSTOM_DOMAIN"

# Get validation token
VALIDATION_TOKEN=$(az staticwebapp hostname show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --hostname "$CUSTOM_DOMAIN" \
  --query "validationToken" \
  --output tsv 2>/dev/null || echo "")

echo ""
echo "✅ Custom domain configuration initiated"
echo ""
echo "📋 DNS Configuration Required:"
echo "================================"
echo "Add these DNS records to your DNS provider (open-regels.nl):"
echo ""
echo "1. CNAME Record:"
echo "   Type: CNAME"
echo "   Name: iou-architectuur"
echo "   Value: $DEFAULT_URL"
echo "   TTL: 3600"
echo ""
echo "2. TXT Record (for validation):"
echo "   Type: TXT"
echo "   Name: _dnsauth.iou-architectuur"
echo "   Value: [Will be provided by Azure Portal]"
echo "   TTL: 3600"
echo ""
echo "To get the exact validation token, run:"
echo "az staticwebapp hostname show --name $APP_NAME --resource-group $RESOURCE_GROUP --hostname $CUSTOM_DOMAIN"
echo ""

# Step 7: Enable App Insights (optional)
echo ""
read -p "Do you want to enable Application Insights for monitoring? (y/n): " ENABLE_INSIGHTS

if [ "$ENABLE_INSIGHTS" = "y" ]; then
  echo "📊 Enabling Application Insights..."
  
  INSIGHTS_NAME="${APP_NAME}-insights"
  
  az monitor app-insights component create \
    --app "$INSIGHTS_NAME" \
    --location "$LOCATION" \
    --resource-group "$RESOURCE_GROUP" \
    --application-type web \
    --retention-time 90
  
  INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app "$INSIGHTS_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "instrumentationKey" \
    --output tsv)
  
  echo "✅ Application Insights enabled"
  echo "   Instrumentation Key: $INSTRUMENTATION_KEY"
  echo "   Add this to your application if needed"
fi

# Summary
echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📝 Next Steps:"
echo "1. Add AZURE_STATIC_WEB_APPS_API_TOKEN to GitLab CI/CD variables"
echo "2. Configure DNS records as shown above"
echo "3. Wait 5-10 minutes for DNS propagation"
echo "4. Validate custom domain in Azure Portal"
echo "5. Push code to GitLab main branch to trigger deployment"
echo ""
echo "📍 URLs:"
echo "   Default: https://$DEFAULT_URL"
echo "   Custom:  https://$CUSTOM_DOMAIN (after DNS setup)"
echo ""
echo "🔧 Management:"
echo "   Azure Portal: https://portal.azure.com/#resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$APP_NAME"
echo ""
echo "💰 Cost Estimate:"
if [ "$SKU" = "Free" ]; then
  echo "   Free tier: €0.00/month"
  echo "   - 100 GB bandwidth/month"
  echo "   - 0.5 GB storage"
  echo "   - Free SSL certificate"
else
  echo "   Standard tier: ~€8/month"
  echo "   - 100 GB bandwidth/month (then €0.15/GB)"
  echo "   - 0.5 GB storage (then €0.15/GB)"
  echo "   - Custom authentication support"
fi
echo ""
