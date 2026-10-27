# Release Runbook

## Before a release

Run this from a clean checkout of `main`:

```bash
make check
git diff --check
git status --short
```

`make check` rebuilds the static output from committed canonical records, runs importer regression tests, and checks the generated public/Pages assets. Do not publish a change if it adds a raw source upload, a source-derived claim represented as a verified fact, or any facility coordinate.

Review the P1/P2 human checks in [TEST_REPORT.md](TEST_REPORT.md) and the data/source checks in [MAINTAINER_CHECKLIST.md](MAINTAINER_CHECKLIST.md). The test report distinguishes completed automated/browser checks from review that must still be performed by a qualified person.

## Commit and push

Commit source modules, canonical artifacts, generated `public/` and `docs/` output, and documentation together. Do not manually modify `docs/`; regenerate it with `make build`.

Push the reviewed commit to `main`. The workflow in `.github/workflows/site.yml` first runs `make check`. A failed verification job means the proposed output was not packaged or deployed.

## One-time GitHub Pages activation

This repository includes an artifact deployment workflow but does **not** change GitHub repository settings. A repository owner must take this one-time action:

1. Open the repository’s **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Review or add protection for the `github-pages` deployment environment. Only reviewed `main` commits should deploy.
4. Push a verified `main` commit or run the workflow manually from the **Actions** tab.
5. Open the URL reported by the `Deploy Pages artifact` workflow step and verify the landing page, one district filter, an exported CSV, and the map’s uncertainty statement.

Until the owner completes this setting change and a deployment workflow succeeds, no production Pages URL should be represented as live.

## If a release needs to be rolled back

1. Identify the last known-good commit and inspect its `make check` evidence.
2. Revert the problematic commit using a normal new commit; do not force-push or rewrite `main`.
3. Run `make check` on the revert.
4. Push the revert. When GitHub Actions is the configured Pages source, the Pages workflow will deploy the resulting artifact after its checks succeed.
5. Confirm the deployment job reports the expected Pages URL and inspect the landing page.

For an urgent pause, a repository owner can disable GitHub Pages in repository settings. Re-enable only after a reviewed version is ready.

## Supporting references

GitHub’s custom Pages workflow guide documents `configure-pages`, `upload-pages-artifact`, the required `pages: write` / `id-token: write` deployment permissions, and the `github-pages` environment. GitHub’s publishing-source guide documents the owner setting required to select GitHub Actions as the Pages source.

**References**

[1]: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages "Using custom workflows with GitHub Pages"
[2]: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site "Configuring a publishing source for your GitHub Pages site"
