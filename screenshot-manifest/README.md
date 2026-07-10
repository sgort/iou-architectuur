# Screenshot manifests

Capture TODO lists produced by the `/iou-document-patch` skill — one file per
component (`<component>-screenshots-todo.md`). Each lists the screenshots a docs
sync introduced (**NEW**) or invalidated (**REPLACE**), with the embedding page,
required framing, and the version that triggered it.

These are **operational artifacts, not documentation content**, so they live
here at the repo root rather than under `docs/` — keeping them out of the MkDocs
source tree (no "not in nav" build warnings) while still versioning them with the
repo. The screenshots themselves are captured into `docs/assets/screenshots/`.

Delete or check off rows as the screenshots are captured; the file can be removed
once a component's list is fully done (the next sync regenerates it if needed).
