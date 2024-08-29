import pandas as pd
import argparse
import matplotlib.pyplot as plt
import textwrap

def generate_latex(csv_file, outfile=None,noorcid=False):
    # Read the CSV file
    df = pd.read_csv(csv_file, comment='#')

    # Convert all columns to string type to avoid FutureWarning and fill NaN values with empty strings
    df = df.astype(str).fillna('')

    # Create a list to hold authors and their affiliations
    author_list = []
    affiliations_dict = {}
    affiliation_index = 1

    # Collect authors and affiliations
    for _, row in df.iterrows():
        # Include only authors with authorship status of 1
        if row['authorship status'].strip() != '1':
            continue

        # Check if abbreviation is available and use it, otherwise construct the name
        if row['abbreviation'].strip() and row['abbreviation'].lower() != 'nan':
            full_name = row['abbreviation'].strip()
        else:
            first_initial = f"{row['First Name'][0]}." if row['First Name'] else ''
            middle_initial = f"{row['Middle Name'][0]}." if row['Middle Name'] and row['Middle Name'].lower() != 'nan' else ''
            full_name = f"{first_initial}{middle_initial} {row['Last Name']}".strip()

        # Skip rows with no name
        if not full_name:
            continue

        # Collect institutions
        inst1 = row['Institution 1 '].strip() if row['Institution 1 '].lower() != 'nan' else ''
        inst2 = row['Institution 2 ...'].strip() if row['Institution 2 ...'].lower() != 'nan' else ''

        if inst1 and inst1 not in affiliations_dict:
            affiliations_dict[inst1] = None
        if inst2 and inst2 not in affiliations_dict:
            affiliations_dict[inst2] = None

        if noorcid is False: 
            # Add ORCID if available
            if row['ORCID'].strip() and row['ORCID'].lower() != 'nan':
                orcid = row['ORCID'].strip()
                full_name += f" \\orcidlink{{{orcid}}}"

        # Add to author list
        author_list.append((row['Last Name'], full_name, inst1, inst2))

    # Sort authors by family name (last name)
    author_list.sort(key=lambda x: x[0])

    # Reassign affiliation numbers based on the sorted order of authors
    for _, full_name, inst1, inst2 in author_list:
        if inst1 and affiliations_dict[inst1] is None:
            affiliations_dict[inst1] = affiliation_index
            affiliation_index += 1
        if inst2 and affiliations_dict[inst2] is None:
            affiliations_dict[inst2] = affiliation_index
            affiliation_index += 1

    # Generate LaTeX author entries
    latex_lines = []
    for _, full_name, inst1, inst2 in author_list:
        inst_indices = ','.join(str(affiliations_dict[i.strip()]) for i in [inst1, inst2] if i.strip())
        author_entry = f"\\author[{inst_indices}]{{{full_name}}}"
        latex_lines.append(author_entry)

    # Generate LaTeX affiliation entries in order of their assigned numbers
    sorted_affiliations = sorted(affiliations_dict.items(), key=lambda item: item[1])
    affiliations = [f"\\affil[{index}]{{{inst}}}" for inst, index in sorted_affiliations if index is not None]

    # Combine authors and affiliations
    latex_content = "\n".join(latex_lines + affiliations)

    # Print or save the LaTeX content
    if outfile:
        with open("latex_author.txt", 'w') as file:
            file.write(latex_content)
    print(latex_content)

def create_author_image(csv_file, image_file='authors.png'):
    # Read the CSV file
    df = pd.read_csv(csv_file, comment='#')

    # Convert all columns to string type and fill NaN values with empty strings
    df = df.astype(str).fillna('')

    # Create a list to hold authors and their affiliations
    author_list = []
    affiliations_dict = {}
    affiliation_index = 1

    # Collect authors and affiliations
    for _, row in df.iterrows():
        # Include only authors with authorship status of 1
        if row['authorship status'].strip() != '1':
            continue

        # Construct the full name
        if row['abbreviation'].strip() and row['abbreviation'].lower() != 'nan':
            full_name = row['abbreviation'].strip()
        else:
            first_initial = f"{row['First Name'][0]}." if row['First Name'] else ''
            middle_initial = f"{row['Middle Name'][0]}." if row['Middle Name'] and row['Middle Name'].lower() != 'nan' else ''
            full_name = f"{first_initial}{middle_initial} {row['Last Name']}".strip()

        # Skip rows with no name
        if not full_name:
            continue

        # Collect institutions
        inst1 = row['Institution 1 '].strip() if row['Institution 1 '].lower() != 'nan' else ''
        inst2 = row['Institution 2 ...'].strip() if row['Institution 2 ...'].lower() != 'nan' else ''

        if inst1 and inst1 not in affiliations_dict:
            affiliations_dict[inst1] = None
        if inst2 and inst2 not in affiliations_dict:
            affiliations_dict[inst2] = None

        # Add to author list with last name for sorting
        author_list.append((row['Last Name'], full_name, inst1, inst2))

    # Sort authors by family name (last name)
    author_list.sort(key=lambda x: x[0])

    # Reassign affiliation numbers based on the sorted order of authors
    for _, full_name, inst1, inst2 in author_list:
        if inst1 and affiliations_dict[inst1] is None:
            affiliations_dict[inst1] = affiliation_index
            affiliation_index += 1
        if inst2 and affiliations_dict[inst2] is None:
            affiliations_dict[inst2] = affiliation_index
            affiliation_index += 1

    # Prepare text for the image in the correct alphabetical order
    author_text = ", ".join([
        f"{full_name}$^{{{', '.join([str(affiliations_dict[i.strip()]) for i in [inst1, inst2] if i.strip()])}}}$"
        for _, full_name, inst1, inst2 in author_list
    ])

    sorted_affiliations = sorted(affiliations_dict.items(), key=lambda item: item[1])
    affiliation_text = "\n".join([f"{index}: {inst}" for inst, index in sorted_affiliations if index is not None])

    # Create the image in landscape orientation
    plt.figure(figsize=(16, 9))  # Landscape orientation
    plt.text(0.5, 0.7, author_text, fontsize=18, ha='center', va='center', wrap=True)  # Larger font for authors
    plt.text(0.5, 0.2, affiliation_text, fontsize=10, ha='center', va='center', wrap=True)  # Smaller font for affiliations
    plt.axis('off')

    # Save the image
    plt.savefig(image_file, bbox_inches='tight')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate LaTeX author list from a CSV file and create an author image.')
    parser.add_argument('--csv', type=str, default='CYGNO_RL_form_authors.csv', help='Path to the CSV file')
    parser.add_argument('--out', help='Save the output to file', action='store_true')
    parser.add_argument('--NoOrcid', help='Remove ORCID part', action='store_true')
    parser.add_argument('--image_file', type=str, default='authors.png', help='Path to save the image file')
    
    args = parser.parse_args()
    generate_latex(args.csv,args.out,args.NoOrcid)
    create_author_image(args.csv, args.image_file)