from pathlib import Path

# Main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Folder containing the public website files
PUBLIC_DIR = PROJECT_ROOT / "public"

# Source website containing the SRD pages
BASE_URL = "https://www.d20srd.org"
SITE_URL = "https://d20srdhub.com"

# Identifies this importer when requesting pages
USER_AGENT = (
    "d20srdhub importer "
    "(https://d20srdhub.com)"
)
