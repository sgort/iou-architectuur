# Information Architecture Framework - Documentatie

Documentatie voor het Informatie Architectuur Framework van het Lelystad-Zuid Ringweg Project, gehost op Azure Static Web Apps.

## 📋 Overzicht

Deze repository bevat de bronbestanden voor de documentatiesite op `https://iou-architectuur.open-regels.nl`.

**Taal**: Nederlands

**Technische Stack**:
- **Static Site Generator**: MkDocs met Material Theme
- **Bronformaat**: Markdown
- **CI/CD**: GitHub Actions
- **Hosting**: Azure Static Web Apps
- **Versiebeheer**: GitLab CE (primair) + GitHub (deployment trigger)

## 🚀 Quick Start

### Vereisten

- Python 3.11+
- Git
- Azure CLI (alleen voor initiële setup)
- Toegang tot GitLab CE op `git.open-regels.nl`

### Lokale Ontwikkeling

1. **Clone de repository**:
```bash
git clone https://git.open-regels.nl/showcases/iou-architectuur.git
cd iou-architectuur
```

2. **Maak virtual environment aan**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Installeer dependencies**:
```bash
pip install -r requirements.txt
```

4. **Start lokale development server**:
```bash
mkdocs serve
```

5. **Open browser**: http://127.0.0.1:8000

De site herlaadt automatisch wanneer je wijzigingen maakt in de Markdown bestanden.

### Site Bouwen

```bash
mkdocs build
```

Dit maakt een `site/` directory aan met statische HTML bestanden.

## 📂 Repository Structuur

```
iou-architectuur/
├── docs/                           # Documentatie bronbestanden
│   ├── index.md                    # Homepage
│   ├── deel-1-ontologie.md         # Deel 1: Ontologische Architectuur
│   ├── deel-2-implementatie.md     # Deel 2: Implementatie Architectuur
│   ├── deel-3-roadmap.md           # Deel 3: Roadmap en Evaluatie
│   └── stylesheets/
│       └── extra.css               # NL Design System styling
├── mkdocs.yml                      # MkDocs configuratie
├── .github/workflows/
│   └── azure-static-web-apps.yml   # GitHub Actions workflow
├── requirements.txt                # Python dependencies
├── staticwebapp.config.json        # Azure SWA configuratie
├── .gitignore                      # Git ignore regels
└── README.md                       # Dit bestand
```

## 🔄 Deployment Workflow

### Automatische Deployment

Elke push naar de `main` branch triggert automatisch deployment:

```bash
git add .
git commit -m "Update: beschrijving van wijzigingen"
git push origin main   # GitLab (primaire bron)
git push github main   # GitHub (triggert Azure deployment)
```

**Of push naar beide tegelijk**:
```bash
git push --all
```

**Pipeline stappen**:
1. **Build**: MkDocs bouwt statische site vanuit Markdown
2. **Deploy**: Site wordt geüpload naar Azure Static Web Apps

**Deployment tijd**: ~2-3 minuten

### Handmatige Deployment

Indien nodig kun je handmatig deployen:

```bash
# Bouw lokaal
mkdocs build

# Deploy met Azure CLI
az staticwebapp upload \
  --name iou-architectuur \
  --resource-group rg-iou-architectuur \
  --source site/ \
  --token $AZURE_STATIC_WEB_APPS_API_TOKEN
```

## ✍️ Content Aanpassen

### Nieuwe Pagina's Toevoegen

1. Maak Markdown bestand aan in `docs/`:
```bash
touch docs/nieuwe-pagina.md
```

2. Voeg toe aan navigatie in `mkdocs.yml`:
```yaml
nav:
  - Home: index.md
  - Nieuwe Pagina: nieuwe-pagina.md
  - Deel 1: deel-1-ontologie.md
  # etc.
```

3. Commit en push

### Markdown Features

**Admonitions** (waarschuwingsblokken):
```markdown
!!! note "Titel"
    Inhoud hier

!!! warning
    Waarschuwing inhoud

!!! success
    Succes bericht
```

**Code blocks** met syntax highlighting:
````markdown
```turtle
@prefix flvl: <https://data.flevoland.nl/def/> .

flvl:LelystadProject a flvl:InfrastructureProject .
```
````

**Tabellen**:
```markdown
| Kolom 1 | Kolom 2 |
|---------|---------|
| Waarde 1| Waarde 2|
```

**Cross-references**:
```markdown
Zie [Deel 1](deel-1-ontologie.md#sectie-naam)
```

### RDF Voorbeelden Toevoegen

Gebruik de `turtle` taal identifier voor syntax highlighting:

````markdown
```turtle
@prefix flvl-sp: <https://data.flevoland.nl/def/spatial-planning/> .
@prefix dcterms: <http://purl.org/dc/terms/> .

flvl-id:LelystadRingwegProject 
    a flvl-sp:InfrastructureProject ;
    dcterms:title "Lelystad-Zuid Ringweg Project"@nl .
```
````

## 🎨 Styling Aanpassen

Custom CSS staat in `docs/stylesheets/extra.css`.

Kleuren volgen NL Design System:
- Primary: `#154273` (Rijksoverheid blauw)
- Accent: `#e17000` (Oranje)
- Status kleuren voor compliance states

### Theme Aanpassingen

Voor geavanceerde aanpassingen, zie [MkDocs Material documentatie](https://squidfunk.github.io/mkdocs-material/).

## 📊 Monitoring

### GitHub Actions

Bekijk deployment status:
`https://github.com/YOUR-USERNAME/iou-architectuur/actions`

**Beschikbare metrics**:
- Build tijd
- Deployment status
- Foutmeldingen

### Azure Portal

Bekijk hosting metrics:
`https://portal.azure.com` → Static Web Apps → `iou-architectuur`

**Beschikbare metrics**:
- Page views
- Bandwidth gebruik
- Response times

## 🔒 Beveiliging

### HTTPS

- Automatisch SSL certificaat via Let's Encrypt
- Certificaat vernieuwing door Azure
- Geforceerde HTTPS redirects

### Content Security Policy

Geconfigureerd in `staticwebapp.config.json`:
- Beperkt script bronnen
- Voorkomt XSS aanvallen
- Limiteert externe resources

### Access Control

Momenteel publiek toegankelijk. Voor beperkte toegang kan authenticatie worden toegevoegd via `staticwebapp.config.json`.

## 🐛 Troubleshooting

### Build Faalt

**Controleer Python versie**:
```bash
python --version  # Moet 3.11+ zijn
```

**Herinstalleer dependencies**:
```bash
pip install --upgrade -r requirements.txt
```

**Controleer MkDocs syntax**:
```bash
mkdocs build --strict
```

### Deployment Faalt

**Verifieer GitHub Secret**:
- Variabele naam exact: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- Geen extra spaties
- Protected en Masked enabled

**Controleer pipeline logs**:
GitHub → Actions → Laatste run → Bekijk logs

### Custom Domain Werkt Niet

**Verifieer DNS records**:
```bash
nslookup iou-architectuur.open-regels.nl
dig iou-architectuur.open-regels.nl CNAME
```

**Controleer Azure validatie**:
Azure Portal → Static Web App → Custom domains → Status

**Wacht op propagatie**: DNS wijzigingen kunnen tot 24 uur duren

### Site Toont Oude Content

**Controleer cache**:
- Hard refresh browser: `Ctrl+Shift+R` (of `Cmd+Shift+R` op Mac)
- Clear browser cache
- Test in incognito/privé modus

**Verifieer deployment**:
```bash
# Controleer laatste commit
git log --oneline -1

# Check GitHub Actions status
```

## 💰 Kosten

### Free Tier (Huidige Setup)
- **Maandelijkse kosten**: €0.00
- 100 GB bandwidth
- 0.5 GB storage
- Gratis SSL certificaat
- Unlimited static content

### Verwacht Gebruik
- Bandwidth: < 10 GB/maand
- Storage: < 100 MB
- **Aanbeveling**: Blijf op Free tier

## 📞 Support

### Voor Framework Inhoud Vragen
- **Organisatie**: Provincie Flevoland
- **Afdeling**: Infrastructuur & Omgeving
- **Project**: Lelystad-Zuid Ringweg

### Voor Technische/Deployment Issues
- **GitLab**: https://git.open-regels.nl/showcases/iou-architectuur/-/issues
- **Azure Docs**: https://learn.microsoft.com/azure/static-web-apps/
- **MkDocs Docs**: https://www.mkdocs.org/

## 📚 Resources

- [MkDocs Material Documentatie](https://squidfunk.github.io/mkdocs-material/)
- [Azure Static Web Apps Documentatie](https://learn.microsoft.com/azure/static-web-apps/)
- [GitHub Actions Documentatie](https://docs.github.com/actions)
- [Markdown Gids](https://www.markdownguide.org/)

## 🔧 Ontwikkelaar Workflow

### Dagelijkse Workflow

```bash
# Activeer virtual environment
source venv/bin/activate

# Start development server
mkdocs serve

# Maak wijzigingen in docs/...

# Test lokaal op http://127.0.0.1:8000

# Commit en deploy
git add .
git commit -m "Update: beschrijving"
git push --all

# Deactiveer venv wanneer klaar
deactivate
```

### Virtual Environment Beheer

```bash
# Activeren
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Deactiveren
deactivate

# Status checken
echo $VIRTUAL_ENV  # Laat venv path zien als actief
```

### Git Remote Beheer

```bash
# Bekijk remotes
git remote -v

# Push naar specifieke remote
git push origin main   # GitLab
git push github main   # GitHub

# Push naar beide
git push --all
```

## 📄 Licentie

Deze documentatie is eigendom van Provincie Flevoland.

## 🎯 Project Status

**Versie**: 1.0  
**Status**: ✅ Productie  
**Live URL**: https://iou-architectuur.open-regels.nl  
**Laatste Update**: November 2025

---

**Framework Componenten**:
- Deel 1: Ontologische Architectuur (Secties 1-3)
- Deel 2: Implementatie Architectuur (Secties 4-7)
- Deel 3: Roadmap en Evaluatie (Secties 8-10)

**Demonstrator**: https://iou.open-regels.nl

**Technische Standaarden**:
- MIM (Metamodel voor Informatiemodellering)
- NL-SBB (SKOS-gebaseerde begrippenbeschrijving)
- CPSV-AP (EU Public Service Vocabulary)
- DSO/RTR (Digitaal Stelsel Omgevingswet)