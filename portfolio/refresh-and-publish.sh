#!/bin/sh
# Refresh prices, rebuild the API, and publish — the whole loop in one command.
#
# Use this when the scheduled GitHub workflow is not an option, for example
# because .github/workflows/refresh-prices.yml cannot be put on the default
# branch. It does exactly what that workflow does, just on your machine.
#
# Run it by hand:
#     sh portfolio/refresh-and-publish.sh
#
# Or every 15 minutes while European markets are open, via crontab -e:
#     */15 7-17 * * 1-5  cd /path/to/ebsic-overview && sh portfolio/refresh-and-publish.sh >> /tmp/ebsic-prices.log 2>&1
#
# It only runs while your machine is awake, which is the one thing the hosted
# workflow does better.

set -eu

REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$REPO"

echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ)"

( cd portfolio && python3 refresh-prices.py )
python3 api/build-api.py

# api/*.json carry a "generated" stamp that changes every run, so prices.json
# is what decides whether there is anything worth committing.
if git diff --quiet -- portfolio/prices.json; then
  echo "No price change. Nothing to publish."
  exit 0
fi

git add portfolio/prices.json api/portfolio.json api/events.json
git commit -q -m "Refresh portfolio prices"

# The site is served from a different branch than this one, so publishing means
# pushing the three regenerated files there as well.
git push -q canavarr HEAD:club-site
echo "Pushed to club-site. Run the deploy to put it on ebsic.ee."
