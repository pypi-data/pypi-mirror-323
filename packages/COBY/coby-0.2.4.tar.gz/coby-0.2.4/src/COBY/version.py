__version__="0.2.4"

major_changes = [
    "Added new method 'COBY.Library' which can be used to interactively look through the parameter libraries (for lipids, solvents, ions and protein residue charges).",
]

minor_changes = [
    "Added lipid definitions for some of the lipid task force (LTF) lipids.",
    "Restructured how ion libraries are written. Done to improve data formatting consistency between different library types (lipid, solvent, positive ions and negative ions). Should only impact the user if they import their own custom ions definitions.",
    [
        "Old:",
        [
            "ion_defs = {}",
            "params = 'default'",
            "ion_defs[params] = {}",
            "ion_defs[params]['positive'] = {}",
            "ion_defs[params]['negative'] = {}",
        ],
        "New:",
        [
            "pos_ion_defs = {}",
            "neg_ion_defs = {}",
            "params = 'default'",
            "pos_ion_defs[params] = {}",
            "neg_ion_defs[params] = {}",
        ],
    ],
]

bug_fixes = [
    "'itp_reader' no longer crashes if '[ VARIABLE ]' in topology files are preceeded by blank spaces.",
    "Fixed solvents and solutes not being properly moved inside the solvent box if they end up outside due to too small grid size during placement.",
]

documentation_changes = [
    "Added documentation for 'COBY.Library'.",
]

tutorial_changes = [
]

def version_change_writer(iterable, recursion_depth = 0):
    list_of_strings = []
    for i in iterable:
        if type(i) == str:
            ### Headers
            if recursion_depth == 0:
                list_of_strings.append(i)
            ### Changes. -1 to have no spaces for first recursion. Two spaces "  " to fit with GitHub list formatting.
            else:
                list_of_strings.append("  " * (recursion_depth - 1) + "-" + " " + i)

        elif type(i) in [list, tuple]:
            list_of_strings.extend(version_change_writer(i, recursion_depth + 1))
    return list_of_strings

### Extra empty "" is to add a blank line between sections
all_changes = []
if len(major_changes) > 0:
    all_changes += ["Major changes:", major_changes, ""]

if len(minor_changes) > 0:
    all_changes += ["Minor changes:", minor_changes, ""]

if len(bug_fixes) > 0:
    all_changes += ["Bug fixing:", bug_fixes, ""]

if len(documentation_changes) > 0:
    all_changes += ["Documentation changes:", documentation_changes, ""]

if len(tutorial_changes) > 0:
    all_changes += ["Tutorial changes:", tutorial_changes, ""]

if len(all_changes) > 0:
    all_changes = all_changes[:-1] # Removes the last ""

version_changes_list = version_change_writer(all_changes)
version_changes_str = "\n".join(version_changes_list)

def version_changes():
    print(version_changes_str)

### Abbreviations
changes   = version_changes
changelog = version_changes

