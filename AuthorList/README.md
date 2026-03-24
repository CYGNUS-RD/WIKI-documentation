# LaTeX Author List Generator

Generates a LaTeX author list from the [CYGNO RL author sheet](https://docs.google.com/spreadsheets/d/1eEDZST-gUF1IELlRzGcLxuxVkPNnKTLbI-eTdULwKU0/edit?usp=sharing), sorted alphabetically by last name. Also produces a `.png` image of the author list with affiliation numbers.

## Usage

### Read directly from Google Sheets (recommended)
```bash
python3 GetAuthorList.py --gsheet
```
No download needed. Uses the default CYGNO sheet. Pass a custom URL to use a different sheet:
```bash
python3 GetAuthorList.py --gsheet "https://docs.google.com/spreadsheets/d/<ID>/edit?usp=sharing"
```

### Read from a local CSV
Download the sheet as `.csv` and run:
```bash
python3 GetAuthorList.py --csv <csvName>.csv
```

## Flags

| Flag | Description |
|------|-------------|
| `--gsheet [URL]` | Read from Google Sheets (default CYGNO sheet if no URL given) |
| `--csv <file>` | Read from a local CSV file |
| `--gid <id>` | Select a specific sheet tab by GID (default: `0`) |
| `--out` | Save the LaTeX output to `latex_author.txt` |
| `--NoOrcid` | Omit ORCID links from the output (not recommended) |
| `--image_file <file>` | Path for the output image (default: `authors.png`) |
| `--debug` | Print column names and sample rows to diagnose empty output |

## Output

- **Terminal / `latex_author.txt`** — ready-to-paste `\author[...]` and `\affil[...]` LaTeX entries
- **`authors.png`** — landscape image of the full author list with affiliation indices

## Test
Working example on Overleaf: <https://www.overleaf.com/read/pyxdxswqpgsm#cbe7d7>