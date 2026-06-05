# OSF Submission Checklist

## Project Creation

1. Log in to OSF.
2. Click `Create new project`.
3. Enter the title from `publication/osf_metadata.md`.
4. Add Andrea Bertoldo as the project contributor and administrator.
5. Choose public visibility only after all files pass the privacy audit.

## File Upload

Upload the same curated package used for Zenodo:

- manuscript files in `paper/`
- final figures in `figures/`
- final tables in `tables/`
- derived CSV files in `data/`
- documentation in `docs/`
- reproducibility scripts in `scripts/`
- notebooks in `notebooks/`
- `README.md`, `LICENSE`, `CITATION.cff`, and release notes

Do not upload raw Garmin exports, route files, precise GPS coordinates, or private notes.

## Public Release

1. Review all files in OSF preview.
2. Confirm that no private identifiers, GPS coordinates, Garmin activity IDs, or unwanted screenshots are visible.
3. Add tags and description from `publication/osf_metadata.md`.
4. Choose the license.
5. Click `Make Public`.

## Citation Generation

After the project is public:

1. Open the OSF project overview.
2. Use the OSF citation widget or `Cite` button.
3. Copy the generated citation into the GitHub README and manuscript repository notes.
4. If a DOI is created or linked, add it to `CITATION.cff`.
