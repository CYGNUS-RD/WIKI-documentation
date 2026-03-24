import pandas as pd
import argparse
import matplotlib.pyplot as plt
import re

# ── Google Sheets helpers ────────────────────────────────────────────────────

DEFAULT_GSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1eEDZST-gUF1IELlRzGcLxuxVkPNnKTLbI-eTdULwKU0/edit?usp=sharing"
)

def gsheet_to_csv_url(url: str, gid: str = "0") -> str:
    """
    Convert any Google Sheets sharing/edit URL into a direct CSV export URL.

    Supports URLs in the form:
      https://docs.google.com/spreadsheets/d/<ID>/edit?...
      https://docs.google.com/spreadsheets/d/<ID>/pub?...
    An optional sheet tab can be selected via the `gid` parameter
    (default "0" = first sheet).
    """
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError(
            f"Could not extract a spreadsheet ID from the URL:\n  {url}\n"
            "Make sure you pass the full Google Sheets URL."
        )
    spreadsheet_id = match.group(1)
    return (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        f"/export?format=csv&gid={gid}"
    )


def read_source(
    csv_file: str | None,
    gsheet_url: str | None,
    gid: str = "0",
    debug: bool = False,
) -> pd.DataFrame:
    """
    Return a DataFrame from either a local CSV path or a Google Sheets URL.
    Google Sheets takes priority when both are supplied.
    Falls back to the bundled default Google Sheet when neither is provided.
    """
    if gsheet_url:
        export_url = gsheet_to_csv_url(gsheet_url, gid)
        print(f"[INFO] Reading from Google Sheets:\n       {export_url}")
        df = pd.read_csv(export_url)
    elif csv_file:
        print(f"[INFO] Reading from local file: {csv_file}")
        df = pd.read_csv(csv_file, comment='#')
    else:
        export_url = gsheet_to_csv_url(DEFAULT_GSHEET_URL, gid)
        print(f"[INFO] No source specified – using default Google Sheet:\n       {export_url}")
        df = pd.read_csv(export_url)

    # ── Normalise column names: strip leading/trailing whitespace ──────────
    df.columns = df.columns.str.strip()

    # ── Drop rows that are entirely comment lines (start with #) ───────────
    first_col = df.columns[0]
    df = df[~df[first_col].astype(str).str.startswith('#')]

    # ── Normalise values: everything to str, NaN → '' ──────────────────────
    df = df.astype(str).fillna('').apply(lambda col: col.str.strip())

    if debug:
        print("\n[DEBUG] ── Column names ──────────────────────────────────────")
        for i, col in enumerate(df.columns):
            print(f"  [{i:02d}] {repr(col)}")
        print(f"\n[DEBUG] ── Total rows loaded: {len(df)} ──────────────────────")
        print("[DEBUG] ── First 5 rows of key columns ──────────────────────")
        key_cols = ['authorship status', 'Last Name', 'First Name',
                    'abbreviation', 'Institution 1', 'Institution 2 ...', 'ORCID']
        available = [c for c in key_cols if c in df.columns]
        print(df[available].head(5).to_string())
        print()
        # Show unique values in authorship status so we can see what filter needs
        if 'authorship status' in df.columns:
            vals = df['authorship status'].unique()
            print(f"[DEBUG] Unique 'authorship status' values: {vals}")
        print("[DEBUG] ─────────────────────────────────────────────────────\n")

    return df


# ── Core logic ───────────────────────────────────────────────────────────────

def _collect_authors_and_affiliations(df: pd.DataFrame):
    """
    Shared parsing logic used by both generate_latex() and create_author_image().
    Returns (author_list, affiliations_dict) after sorting by last name and
    assigning affiliation indices.
    """
    author_list = []
    affiliations_dict = {}
    affiliation_index = 1

    for _, row in df.iterrows():
        if row['authorship status'].strip() != '1':
            continue

        # Name: prefer abbreviation field, else build from initials
        if row['abbreviation'].strip() and row['abbreviation'].lower() != 'nan':
            full_name = row['abbreviation'].strip()
        else:
            first_initial  = f"{row['First Name'][0]}."  if row['First Name']  else ''
            middle_initial = (
                f"{row['Middle Name'][0]}."
                if row['Middle Name'] and row['Middle Name'].lower() != 'nan'
                else ''
            )
            full_name = f"{first_initial}{middle_initial} {row['Last Name']}".strip()

        if not full_name:
            continue

        inst1 = row.get('Institution 1', row.get('Institution 1 ', '')).strip()
        inst2 = row.get('Institution 2 ...', '').strip()
        inst1 = '' if inst1.lower() == 'nan' else inst1
        inst2 = '' if inst2.lower() == 'nan' else inst2

        for inst in (inst1, inst2):
            if inst and inst not in affiliations_dict:
                affiliations_dict[inst] = None

        author_list.append((row['Last Name'], full_name, inst1, inst2))

    # Sort alphabetically by last name
    author_list.sort(key=lambda x: x[0])

    # Assign affiliation numbers in the order authors appear after sorting
    for _, _full_name, inst1, inst2 in author_list:
        for inst in (inst1, inst2):
            if inst and affiliations_dict[inst] is None:
                affiliations_dict[inst] = affiliation_index
                affiliation_index += 1

    return author_list, affiliations_dict


# ── Public functions ─────────────────────────────────────────────────────────

def generate_latex(
    csv_file: str | None = None,
    outfile: bool = False,
    noorcid: bool = False,
    gsheet_url: str | None = None,
    gid: str = "0",
    debug: bool = False,
):
    df = read_source(csv_file, gsheet_url, gid, debug=debug)

    # We need ORCID before _collect_authors_and_affiliations because it mutates full_name
    # so we inline the loop here (keeping ORCID logic).
    author_list_raw = []
    affiliations_dict = {}
    affiliation_index = 1

    for _, row in df.iterrows():
        if row['authorship status'].strip() != '1':
            continue

        if row['abbreviation'].strip() and row['abbreviation'].lower() != 'nan':
            full_name = row['abbreviation'].strip()
        else:
            first_initial  = f"{row['First Name'][0]}."  if row['First Name']  else ''
            middle_initial = (
                f"{row['Middle Name'][0]}."
                if row['Middle Name'] and row['Middle Name'].lower() != 'nan'
                else ''
            )
            full_name = f"{first_initial}{middle_initial} {row['Last Name']}".strip()

        if not full_name:
            continue

        inst1 = row.get('Institution 1', row.get('Institution 1 ', '')).strip()
        inst2 = row.get('Institution 2 ...', '').strip()
        inst1 = '' if inst1.lower() == 'nan' else inst1
        inst2 = '' if inst2.lower() == 'nan' else inst2

        for inst in (inst1, inst2):
            if inst and inst not in affiliations_dict:
                affiliations_dict[inst] = None

        if not noorcid:
            if row['ORCID'].strip() and row['ORCID'].lower() != 'nan':
                full_name += f" \\orcidlink{{{row['ORCID'].strip()}}}"

        author_list_raw.append((row['Last Name'], full_name, inst1, inst2))

    author_list_raw.sort(key=lambda x: x[0])

    for _, _fn, inst1, inst2 in author_list_raw:
        for inst in (inst1, inst2):
            if inst and affiliations_dict[inst] is None:
                affiliations_dict[inst] = affiliation_index
                affiliation_index += 1

    # Build LaTeX lines
    latex_lines = []
    for _, full_name, inst1, inst2 in author_list_raw:
        inst_indices = ','.join(
            str(affiliations_dict[i.strip()])
            for i in (inst1, inst2) if i.strip()
        )
        latex_lines.append(f"\\author[{inst_indices}]{{{full_name}}}")

    sorted_affiliations = sorted(affiliations_dict.items(), key=lambda item: item[1])
    affiliations = [
        f"\\affil[{index}]{{{inst}}}"
        for inst, index in sorted_affiliations if index is not None
    ]

    latex_content = "\n".join(latex_lines + affiliations)

    if outfile:
        with open("latex_author.txt", 'w') as fh:
            fh.write(latex_content)
        print("[INFO] LaTeX content saved to latex_author.txt")

    print(latex_content)


def create_author_image(
    csv_file: str | None = None,
    image_file: str = 'authors.png',
    gsheet_url: str | None = None,
    gid: str = "0",
    debug: bool = False,
):
    df = read_source(csv_file, gsheet_url, gid, debug=debug)
    author_list, affiliations_dict = _collect_authors_and_affiliations(df)

    author_text = ", ".join([
        f"{full_name}$^{{{', '.join([str(affiliations_dict[i.strip()]) for i in (inst1, inst2) if i.strip()])}}}$"
        for _, full_name, inst1, inst2 in author_list
    ])

    sorted_affiliations = sorted(affiliations_dict.items(), key=lambda item: item[1])
    affiliation_text = "\n".join([
        f"{index}: {inst}" for inst, index in sorted_affiliations if index is not None
    ])

    # ── Step 1: wrap the author string at author boundaries ───────────────
    # IMPORTANT: splitting on ", " splits INSIDE "$^{3, 5}$" superscripts too,
    # breaking the first/last author on each line.
    # The inter-author separator is always "}$, " (closing superscript then comma).
    # We split on that pattern and restore the "}$" suffix on every token.
    BASE_AUTHOR_FONTSIZE = 11
    BASE_AFFIL_FONTSIZE  = 9
    MAX_LINE_CHARS = 120      # target max characters per author line

    # Split only at the boundary between authors: "}$, "
    # Every token except the last needs its "}$" restored after splitting.
    raw_tokens = re.split(r'\}\$, ', author_text)
    author_tokens = [t + '}$' for t in raw_tokens[:-1]] + [raw_tokens[-1]]

    lines, current_line = [], ""
    for token in author_tokens:
        candidate = current_line + ", " + token if current_line else token
        if len(candidate) > MAX_LINE_CHARS and current_line:
            lines.append(current_line)
            current_line = token
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)

    wrapped_authors = "\n".join(lines)

    # ── Step 2: build a figure tall enough to hold both blocks ────────────
    # Count lines in each block and size the figure accordingly.
    n_author_lines = wrapped_authors.count('\n') + 1
    n_affil_lines  = affiliation_text.count('\n') + 1
    # Each author line ~0.30 in, each affil line ~0.22 in, plus 1.5 in margin
    fig_height = max(8, 1.5 + n_author_lines * 0.30 + n_affil_lines * 0.22)
    fig_width  = 20   # wide canvas so text has plenty of room

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # ── Step 3: draw both text blocks ────────────────────────────────────
    # Anchor authors at top (va='top'), affiliations at bottom (va='bottom').
    # Using ax.transAxes keeps coordinates in [0,1] space regardless of fig size.
    t_authors = ax.text(
        0.5, 0.97, wrapped_authors,
        fontsize=BASE_AUTHOR_FONTSIZE,
        ha='center', va='top',
        transform=ax.transAxes,
        multialignment='center',
        linespacing=1.5,
    )
    t_affil = ax.text(
        0.5, 0.03, affiliation_text,
        fontsize=BASE_AFFIL_FONTSIZE,
        ha='center', va='bottom',
        transform=ax.transAxes,
        multialignment='left',
        linespacing=1.3,
        family='monospace',
    )

    # ── Step 4: measure rendered widths and rescale so they match ─────────
    # We draw the figure once into a temporary renderer to get real bounding
    # boxes, then adjust the affiliation font size to match the author width.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def get_width_in_axes_coords(text_obj):
        """Return the rendered width of a Text object in axes-fraction units."""
        bb = text_obj.get_window_extent(renderer=renderer)   # pixels
        # Convert pixel width → axes-fraction width
        ax_bb = ax.get_window_extent(renderer=renderer)      # axes box in pixels
        return bb.width / ax_bb.width

    w_authors = get_width_in_axes_coords(t_authors)
    w_affil   = get_width_in_axes_coords(t_affil)

    if w_affil > 0 and w_authors > 0:
        # Scale affiliation font so its rendered width matches the author block.
        # fontsize scales linearly with rendered width.
        new_affil_fontsize = BASE_AFFIL_FONTSIZE * (w_authors / w_affil)
        # Clamp: don't go below 6pt or above the author font size
        new_affil_fontsize = max(6, min(new_affil_fontsize, BASE_AUTHOR_FONTSIZE))
        t_affil.set_fontsize(new_affil_fontsize)

    plt.tight_layout(pad=0.5)
    plt.savefig(image_file, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"[INFO] Author image saved to {image_file}")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate a LaTeX author list and an author image from a CSV file "
            "or directly from a Google Spreadsheet."
        )
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        '--csv',
        type=str,
        default=None,
        help='Path to a local CSV file (mutually exclusive with --gsheet).'
    )
    source.add_argument(
        '--gsheet',
        type=str,
        nargs='?',
        const=DEFAULT_GSHEET_URL,   # used when --gsheet is given with no value
        default=None,
        help=(
            'Google Sheets sharing URL. '
            'If omitted entirely the default CYGNO sheet is used. '
            'Mutually exclusive with --csv.'
        )
    )

    parser.add_argument(
        '--gid',
        type=str,
        default='0',
        help='Sheet tab GID (default: 0 = first tab). Find it in the URL after "gid=".'
    )
    parser.add_argument('--out',      help='Save the LaTeX output to latex_author.txt', action='store_true', default=True)
    parser.add_argument('--NoOrcid',  help='Omit ORCID links from the LaTeX output',    action='store_true', default=False)
    parser.add_argument('--image_file', type=str, default='authors.png', help='Path to save the author image.')
    parser.add_argument('--debug',    help='Print column names and sample rows to diagnose empty output', action='store_true')

    args = parser.parse_args()

    generate_latex(
        csv_file=args.csv,
        outfile=args.out,
        noorcid=args.NoOrcid,
        gsheet_url=args.gsheet,
        gid=args.gid,
        debug=args.debug,
    )
    create_author_image(
        csv_file=args.csv,
        image_file=args.image_file,
        gsheet_url=args.gsheet,
        gid=args.gid,
        debug=args.debug,
    )