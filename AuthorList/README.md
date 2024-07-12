# Create a Latex Author List based on the RL sheet

Creates the tex list of actual authors based on the information given by the RLs

## Pipeline

- Open `CYGNO_RL_form_authors.gsheet` in your Browser and download it in this folder `csvName.csv`
- Run `python3 GetAuthorList.py -csv csvName.csv`
  - It prints the author list on the terminal
  - It is possible to store the output with the `--out` flag
- Use flag `--NoOrcid` to not display the ORCID numbers (Not Suggested)

## Test

- Working Example <https://www.overleaf.com/read/pyxdxswqpgsm#cbe7d7>
