---
title: "10. Management and continuity"
scope: cross-cutting
verified:
  date: 2026-11-06
  against:
    CPSV Editor: "0412e9b"
    Linked Data Explorer: "814c4bb"
    RONL Business API: "ff6c362"
    Norm Editor: "c47096b"
    CPRMV: "8262d3e"
---

# 10. Management and continuity

## What this chapter settles in your PSA

Who runs IOU, how new versions come in, how you notice that something goes wrong
and how you recover. The key distinction in this chapter: what you get with the
software, what the IOU team does, and what you arrange yourself.

## What IOU decides

**IOU adopts standards step by step and learns from them** (AB-01). Components,
statuses and decisions therefore change. This guide is re-checked every week
against the released versions; the date at the top of every page says when.

**Reproducible builds** (AB-28): pinned dependencies, an SBOM with every release, a
waiting period for updates, and a weekly measurement against the ICTU dependency
guideline.

**Independent releases with calendar versions; changes only through a pull
request** (AB-29). Every component has its own version and its own release
moment.

**Production through a standard delivery pipeline with a quality gate** (AB-30).
It does not exist yet: all components deliver through the rapid-prototyping track
(risk R-07).

### Who does what

| Topic | Comes with the software | IOU team's way of working | You arrange yourself |
|---|---|---|---|
| Dependencies | Pinned; SBOM per release | Updates through automated proposals, after a waiting period; daily check for vulnerabilities; quarterly review | Re-checking the SBOMs you run against new vulnerabilities; possibly your own package registry |
| Quality | Tested before every release; minimum test coverage per file | Test and check gates on every pull request | Your own acceptance test in your own environments |
| Version information | Every web interface and the backends show which build is running | | Using that information in monitoring and incidents |
| Licence | EUPL-1.2 (Norm Editor: Apache-2.0) | | Licences of your own additions |
| Releases | Calendar versions per component | Release and promotion to production through pull requests | Deciding when you take over a release |
| Source code | Public on GitHub; mirror on GitLab | Mirror updated at every release | Deciding which source you follow |
| Hosting and environments | | | Entirely ([chapter 9](09-technical-infrastructure.md)) |
| Monitoring and alerts | A health check on the backends | | Entirely: what you measure, when you are alerted |
| Incidents | | | Entirely: reporting, follow-up, communication |
| Back-up and restore | | | Entirely, including restore tests |
| Reporting vulnerabilities | No reporting point yet | | Your own reporting process; agreements with IOU |

This applies in full to the CPSV Editor, the Linked Data Explorer and the RONL
Business API. CPRMV and the Norm Editor are built on GitLab under a lighter regime
of their own: CPRMV tests before every build on its main branch; the Norm Editor
has no test coverage or check gates yet.

## Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Support | Internal service desk | An extensible incident and support process | Support for residents and businesses |
| Availability | Matched to working hours | Monitoring and alerts | Agreements on availability outside working hours |
| Releases | Taken over after your own acceptance test | A fixed rhythm for taking over releases | Releases without interruption for residents |

## What you fill in

- The roles: functional management, application management, technical
  management, and who handles security updates and incidents.
- How you follow and take over IOU releases, and who decides on that.
- How you follow changes in this guide: statuses, decisions under review, new
  versions of standards (AB-01).
- Monitoring, alerts and your incident process.
- Back-up and restore, and how often you test a restore.
- How you feed findings back to IOU, so that IOU learns from them too.

## Further reading

- [Overview of the controls](../contributing/controls.md)
- [The development workflow](../contributing/development-workflow/overview.md)
- [Build provenance: which build is running](../contributing/build-provenance.md)
- [Two delivery tracks](../contributing/ci-posture-deck.md)
- [The GitLab mirror](../contributing/the-gitlab-mirror.md)
