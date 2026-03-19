#!/bin/bash
# Regenerate WCOA fixture files from the current running database.
#
# Usage (run from madrona_portal/):
#   ./backups/dump_fixtures.sh
#
# Requires the full stack to be running:
#   docker compose --env-file docker/.env.dev -f docker/docker-compose.yml up -d
#
# After running, review changes and commit the updated fixture files:
#   git diff ../madrona-apps/wcoa/wcoa/fixtures/
#   git add ../madrona-apps/wcoa/wcoa/fixtures/ && git commit -m "Update fixtures from db"

set -euo pipefail

DC="docker compose --env-file docker/.env.dev -f docker/docker-compose.yml"
WCOA_FX="../madrona-apps/wcoa/wcoa/fixtures"

echo "Exporting wcoa_init.json  (base, wagtailcore, wagtailimages, wcoa) ..."
$DC run --rm app \
    python marco/manage.py dumpdata --verbosity 0 \
        base wagtailcore wagtailimages wagtailredirects wcoa \
        --natural-foreign --indent 2 \
    > "$WCOA_FX/wcoa_init.json"
echo "  -> $WCOA_FX/wcoa_init.json  ($(wc -l < "$WCOA_FX/wcoa_init.json") lines)"

echo "Exporting wcoa_init_layers.json  (data_manager, sites) ..."
$DC run --rm app \
    python marco/manage.py dumpdata --verbosity 0 \
        data_manager sites \
        --natural-foreign --indent 2 \
    > "$WCOA_FX/wcoa_init_layers.json"
echo "  -> $WCOA_FX/wcoa_init_layers.json  ($(wc -l < "$WCOA_FX/wcoa_init_layers.json") lines)"

echo "Exporting wagtail_menus.json  (menu) ..."
$DC run --rm app \
    python marco/manage.py dumpdata --verbosity 0 \
        menu \
        --natural-foreign --indent 2 \
    > "$WCOA_FX/wagtail_menus.json"
echo "  -> $WCOA_FX/wagtail_menus.json  ($(wc -l < "$WCOA_FX/wagtail_menus.json") lines)"

echo ""
echo "Fixtures updated. Review with:"
echo "  git diff $WCOA_FX/"
