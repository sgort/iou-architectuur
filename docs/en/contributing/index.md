# Contributing to IOU Architecture

The IOU Architecture Framework is an open-source project published under the
[European Union Public Licence v1.2 (EUPL-1.2)](https://eupl.eu/1.2/en/). Contributions
of any kind — documentation improvements, bug reports, feature suggestions, or code — are
welcome from everyone.

---

## Code of Conduct

This project adheres to the principles of the
[Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
By participating you agree to uphold these principles:

- **Be respectful and inclusive.** Treat all participants with dignity regardless of background,
  experience level, gender, ethnicity, religion, or nationality.
- **Assume good faith.** Interpret ambiguous contributions charitably and ask for clarification
  before escalating concerns.
- **Be constructive.** Feedback should focus on the work, not the person. Offer concrete
  suggestions rather than criticism alone.
- **Respect the scope.** Keep discussions on-topic for the project. Off-topic, harassing, or
  abusive behaviour will not be tolerated.

Violations can be reported confidentially to [steven.gort@ictu.nl](mailto:steven.gort@ictu.nl).
All reports will be handled with discretion and care.

---

## Repositories

Each component of the IOU Architecture ecosystem lives in its own repository on the
[open-regels.nl GitLab instance](https://git.open-regels.nl).

| Component | Repository | Issues |
|---|---|---|
| IOU Architecture Docs | [showcases/iou-architectuur](https://git.open-regels.nl/showcases/iou-architectuur) | [Issues](https://git.open-regels.nl/showcases/iou-architectuur/-/issues) |
| RONL Business API | [hosting/ronl-business-api](https://git.open-regels.nl/hosting/ronl-business-api) | [Issues](https://git.open-regels.nl/hosting/ronl-business-api/-/issues) |
| CPSV Editor | [showcases/ttl-editor](https://git.open-regels.nl/showcases/ttl-editor) | [Issues](https://git.open-regels.nl/showcases/ttl-editor/-/issues) |
| Linked Data Explorer | [hosting/linked-data-explorer](https://git.open-regels.nl/hosting/linked-data-explorer) | [Issues](https://git.open-regels.nl/hosting/linked-data-explorer/-/issues) |
| CPRMV API | [standards/cprmv](https://git.open-regels.nl/standards/cprmv) | [Issues](https://git.open-regels.nl/standards/cprmv/-/issues) |

For component-specific development setup, refer to each component's Developer Docs:

- [RONL Business API — Local Development](../ronl-business-api/developer/local-development.md)
- [CPSV Editor — Local Development](../cpsv-editor/developer/local-development.md)
- [Linked Data Explorer — Local Development](../linked-data-explorer/developer/local-development.md)
- [CPRMV API — Local Development](../cprmv-api/developer/local-development.md)

---

## How to Contribute for Users

 [Submit a use case →](/use-case-form.html){ .md-button .md-button--primary }

## How to Contribute for Developers

### 1. Open an issue first

Before starting any significant work, open an issue in the relevant repository to describe
what you intend to do. This avoids duplicate effort and allows early feedback. For small
corrections (typos, broken links, formatting) you can skip straight to a merge request.

### 2. Fork the repository

Fork the relevant repository to your own GitLab account or namespace.

### 3. Create a feature branch

Always work on a dedicated branch, never directly on `main` or `acc`.

```bash
git checkout acc                          # start from the acceptance branch
git pull origin acc                       # make sure it is up to date
git checkout -b feature/your-topic-name  # create your feature branch
```

Branch naming convention:

| Prefix | Use for |
|---|---|
| `feature/` | New content or functionality |
| `fix/` | Corrections and bug fixes |
| `docs/` | Documentation-only changes |
| `refactor/` | Restructuring without content change |

### 4. Make your changes

Run the documentation site locally while you work:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

The site is then available at `http://127.0.0.1:8000/`.

For every English page you add or change, also update the corresponding Dutch placeholder
under `docs/nl/`. Dutch placeholders use an info admonition linking back to the English
source — see any existing file under `docs/nl/` for the correct format.

### 5. Commit your changes

Follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:

```
docs: add troubleshooting section to LDE user guide
fix: correct broken link in CPSV Editor overview
feat: add CPRMV API authentication reference page
```

### 6. Open a merge request

Push your branch to your fork and open a merge request against the `acc` branch of the
upstream repository.

```bash
git push origin feature/your-topic-name
```

In the merge request description:

- Reference the related issue (`Closes #123`)
- Briefly describe what changed and why
- Note any follow-up work that is out of scope for this MR

Merge requests are reviewed by the maintainer. Feedback is given directly in the MR thread.
Once approved, the maintainer merges into `acc` and promotes to `main` as part of the regular
release cycle.

[Read Code Standards →](code-standards.md)

---

## Contact

For questions, feature requests, or anything else related to the IOU Architecture that does
not fit a GitLab issue, you can reach the project maintainer directly:

**Steven Gort — ICTU**  
[steven.gort@ictu.nl](mailto:steven.gort@ictu.nl)

---

*Licensed under [EUPL-1.2](https://eupl.eu/1.2/en/).*