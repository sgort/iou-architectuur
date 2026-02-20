# Deployment

---

## Environments

| Environment | URL | Branch |
|---|---|---|
| Production | https://cpsv.open-regels.nl | `main` |
| Acceptance | https://acc.cpsv.open-regels.nl | `acc` |

All changes go to `acc` first. After acceptance testing, they are merged to `main` for production deployment.

---

## CI/CD pipeline

```
Git push to branch
       ↓
GitHub Actions workflow
(.github/workflows/azure-static-web-apps.yml)
       ↓
npm ci  →  npm run build
       ↓
Azure Static Web Apps deployment
       ↓
https://cpsv.open-regels.nl  (main)
https://acc.cpsv.open-regels.nl  (acc)
```

The workflow triggers on every push to `main` and `acc`. No manual deployment steps are required.

---

## Pull request workflow

1. Create a feature branch from `acc`.
2. Make changes and test locally.
3. Push the branch and open a PR targeting `acc`.
4. Review and merge to `acc`.
5. Verify behaviour on the ACC environment.
6. Open a PR from `acc` to `main` for production release.

---

## Azure Static Web Apps

The application is deployed as a static site. No server-side rendering is involved. The build output is the `build/` directory produced by `npm run build` (Create React App).

Configuration for routing and CORS is in `staticwebapp.config.json` at the repository root.

---

## Environment variables

The frontend has no required environment variables for basic operation. The TriplyDB base URL, account, dataset, and API token are entered by the user at runtime and stored in browser localStorage.

If the optional backend proxy is deployed, its URL can be configured — see the backend documentation in the Linked Data Explorer repository.
