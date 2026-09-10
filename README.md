# mlops-cd-demo (`ml-api`)

Continuous Delivery for a small Flask ML inference API. One image is built per release tag, pushed to GHCR, deployed to staging and checked with a smoke test, then promoted to production after manual approval. Production can be rolled back to any earlier version.

## Pipeline

```
pull request ──> CI: pytest                                   ci.yml

tag vX.Y.Z ──> test (pytest)
           ──> build once, push ghcr.io/mustafaahsankhan/ml-api:X.Y.Z and :latest
           ──> deploy-staging    (localhost:5002) ──> GET /health smoke test
           ──> approve-production (issue opens; owner comments "approve")
           ──> deploy-production (localhost:5003) ──> GET /health   cd.yml

manual     ──> Rollback Production (input: version) ──> GET /health  rollback.yml
```

Staging and production pull the same immutable image by version tag. Nothing is rebuilt per environment.

## Assignment checklist (section 30)

| Requirement | Where |
|---|---|
| PRs run CI only | `ci.yml` runs on `pull_request`; `cd.yml` runs only on `v*.*.*` tags |
| Semantic version tag starts CD | `cd.yml` trigger; version = tag without the `v` |
| Publish `ml-api:X.Y.Z` and `:latest` | `build` job |
| Deploy to staging automatically | `deploy-staging` job |
| `/health` must pass before production | `deploy-staging` smoke test gates `approve-production` |
| Manual approval for production | `approve-production` job |
| `/health` returns `application_version`, `model_version`, `status` | `app.py`; version is baked in as a Docker build arg |
| Bonus: `git_commit` in `/health` | `GIT_COMMIT` build arg from `GITHUB_SHA` |
| Rollback 1.3.0 to 1.2.0 | `rollback.yml` |

```json
{"application_version": "1.2.0", "git_commit": "8299516", "model_version": "model-7", "status": "healthy"}
```

## Differences from the tutorial

- **Deploy targets are containers on a self-hosted runner** (macOS with Colima) instead of Ubuntu servers reached over SSH, because no VM was available. As a result there are no `STAGING_*`/`PRODUCTION_*` SSH secrets. The only credential is the automatically generated `GITHUB_TOKEN`, which is used for GHCR.
- **Approval uses a GitHub issue** ([trstringer/manual-approval](https://github.com/trstringer/manual-approval)). GitHub rejects environment "Required reviewers" for this private repo on its current plan (HTTP 422). The `staging` and `production` environments still record deployment history.
- **Ports are 5002 (staging) and 5003 (production)**, because macOS AirPlay Receiver holds port 5000.
- **The image name is lowercased.** `ghcr.io/${{ github.repository }}` fails because the owner name contains uppercase letters.
- **`pytest.ini` sets `pythonpath = .`** Without it, plain `pytest` cannot import `app` from `tests/`.

## Release

```bash
git checkout main && git pull
git tag -a v1.3.0 -m "Release 1.3.0"
git push origin v1.3.0
```

When staging passes, comment `approve` on the "Promote ml-api X.Y.Z to production" issue.

## Rollback

Go to Actions → **Rollback Production** → Run workflow and enter `1.2.0`, or run:

```bash
gh workflow run rollback.yml -f version=1.2.0
```

The manual equivalent on the host (tutorial step 25):

```bash
docker rm -f mlops-api-production
docker run -d --name mlops-api-production --restart unless-stopped -p 5003:5000 ghcr.io/mustafaahsankhan/ml-api:1.2.0
curl http://localhost:5003/health
```

## Run locally

```bash
docker compose up --build   # http://localhost:5001/health
```
