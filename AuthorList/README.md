# LaTeX Author List Generator

Generates the CYGNO LaTeX author list from the [CYGNO RL author sheet](https://docs.google.com/spreadsheets/d/1eEDZST-gUF1IELlRzGcLxuxVkPNnKTLbI-eTdULwKU0/edit?usp=sharing), sorted alphabetically by last name.

Outputs:

* `latex_author.txt` — ready-to-use `\author[...]` and `\affil[...]` entries
* `authors.png` — author list with affiliation indices

## Usage

Recommended:

```bash
python3 GetAuthorList.py --gsheet
```

A different Google Sheet can be specified with:

```bash
python3 GetAuthorList.py --gsheet "https://docs.google.com/spreadsheets/d/<ID>/edit"
```

A local CSV can also be used:

```bash
python3 GetAuthorList.py --csv <file>.csv
```

## Options

| Flag                  | Description                            |
| --------------------- | -------------------------------------- |
| `--gsheet [URL]`      | Read from Google Sheets                |
| `--csv <file>`        | Read from a local CSV                  |
| `--gid <id>`          | Select sheet tab by GID (default: `0`) |
| `--NoOrcid`           | Omit ORCID links                       |
| `--image_file <file>` | Set output image path                  |
| `--debug`             | Print diagnostic information           |

## Automatic update

GitHub Actions runs the generator automatically every Monday at 08:00 Europe/Rome.

If the generated `latex_author.txt` or `authors.png` changes, the updated files are automatically committed to the repository. The workflow can also be run manually from the **Actions** tab.

## Example

Working Overleaf example: https://www.overleaf.com/read/pyxdxswqpgsm#cbe7d7
