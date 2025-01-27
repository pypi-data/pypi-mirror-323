import time

import ast
import math
import numpy as np
import random
import copy
import os

### Placeholders in case none are defined in "COBY.molecule_definitions.__init__" and "COBY.fragment_definitions.__init__"
lipid_scaffolds = {}
lipid_defs      = {}
solvent_defs    = {}
ion_defs        = {}
prot_defs       = {}
fragment_defs   = {}

from COBY.molecule_definitions.__init__ import *
from COBY.fragment_definitions.__init__ import *
from COBY.structure_classes.__init__ import *
from COBY.general_functions.__init__ import *

from COBY.main_class.structure_file_handlers.__init__ import *
from COBY.main_class.topology_handlers.__init__ import *
from COBY.main_class.general_tools.__init__ import *
from COBY.main_class.definition_preprocessors.__init__ import *
from COBY.main_class.molecule_fragment_builder.__init__ import *

class Library(
    structure_file_handlers,
    topology_handlers,
    general_tools,
    definition_preprocessors,
    molecule_fragment_builder,
):
    
    def __init__(self, run = True, terminal_run_kwargs = False, **kwargs):
        self.COBY_run_tic = time.time()
        self.PROGRAM = "COBY"

        self.RUN = run
        
        self.debug_prints = False
        self.debug_keys   = []
        self.extra_info   = True
        self.warnings     = True
        self.quiet        = False
        self.verbose      = 1
        
        if terminal_run_kwargs:
            kwargs.update(terminal_run_kwargs)
        
        self.MOLECULE_IMPORT_cmds = []

        self.MOLECULE_FRAGMENT_BUILDER_cmds = []
        
        self.PLOT_cmd        = []
        self.plot_data       = {}
        self.plots_requested = False
        
        self.plot_grid = False
        
        self.PICKLE_cmd = False
        
        self.randseed = round(time.time())
        
        self.sys_params      = "default"
        self.prot_params     = False # Only used if specifically set
        self.lipid_params    = False # Only used if specifically set
        self.solv_params     = False # Only used if specifically set
        self.topology_params = False # Only used if specifically set
        
        self.itp_defs = {
            "atomtypes":       {},
            "bondtypes":       {},
            "pairtypes":       {},
            "angletypes":      {},
            "dihedraltypes":   {},
            "constrainttypes": {},
        }
        self.itp_defs_all_defnames  = set()
        self.itp_moleculetypes      = {}
        self.ITP_INPUT_cmds         = []
        self.TOP_include_statements = []

        self.system_charge = 0
        self.system_name = "PLACEHOLDER_TITLE"
        
#         self.output_system_file_name     = "output"
        self.output_system_pdb_file_name = False
        self.output_system_gro_file_name = False
        self.output_topol_file_name      = "topol.top"
        
        self.LOG_FILE                     = []
        self.output_log_file_name         = False
        self.terminalupdate_string_length = 80

        ### Adds given commands to log file
        self.LOG_FILE.append("The following COBY arguments will be processed:" + "\n")
        self.LOG_FILE.append("COBY(" + "\n")
        for key, val in kwargs.copy().items():
            if type(val) == str:
                val = "\"" + val + "\""
                self.LOG_FILE.append("    " + str(key) + " = " + str(val) + "," + "\n")
            elif type(val) in [list, tuple]:
                self.LOG_FILE.append("    " + str(key) + " = " + "[" + "\n")
                for subval in val:
                    if type(subval) == str:
                        subval = "\"" + subval + "\""
                    self.LOG_FILE.append("    " + "    " + str(subval) + "," + "\n")
                self.LOG_FILE.append("    " + "]," + "\n")
        self.LOG_FILE.append(")" + "\n")
            
        self.pbc_set  = []
        self.pbc_type = "rectangular"
        self.backup   = True
        self.pickle   = False
        
        self.gro_unitcell = []
        self.pdb_unitcell = []

        self.pbcx = 0
        self.pbcy = 0
        self.pbcz = 0
        
        try:
            self.lipid_scaffolds = copy.deepcopy(lipid_scaffolds)
        except:
            self.print_term("WARNING: No lipid scaffolds found", warn=True)
            self.lipid_scaffolds = {}
        
        try:
            self.lipid_defs = copy.deepcopy(lipid_defs)
        except:
            self.print_term("WARNING: No lipid definitions found", warn=True)
            self.lipid_defs = {}
        
        try:
            self.solvent_defs = copy.deepcopy(solvent_defs)
        except:
            self.print_term("WARNING: No solvent definitions found", warn=True)
            self.solvent_defs = {}
        
        try:
            self.ion_defs = copy.deepcopy(ion_defs)
        except:
            self.print_term("WARNING: No ion definitions found", warn=True)
            self.ion_defs = {}
        
        try:
            self.fragment_defs = copy.deepcopy(fragment_defs)
        except:
            self.print_term("WARNING: No fragment definitions found", warn=True)
            self.fragment_defs = {}
        
        try:
            self.prot_defs = copy.deepcopy(prot_defs)
        except:
            self.print_term("WARNING: No protein charge definitions found", warn=True)
            self.prot_defs = {}
        
        self.lipid_dict   = {}
        self.solvent_dict = {}
        self.ion_dict     = {}
        self.prot_dict    = {}

        self.lipid_defs_built   = {}
        self.solvent_defs_built = {}
        self.ion_defs_built     = {}

        self.lipid_defs_imported   = {}
        self.solvent_defs_imported = {}
        self.ion_defs_imported     = {}
        
        if self.RUN:
            self.run(kwargs)
    
    ##############################
    ### GIVE COMMANDS TO CLASS ###
    ##############################
    def commands_handler(self, kwargs):
        invalid_args_given = False

        for key, cmd in kwargs.items():
            ### Molecule definitions and scaffolds
            if key in ["import_library"]:
                if type(cmd) not in [list, tuple]:
                    cmd = [cmd]
                for subcmd in cmd:
                    assert subcmd.endswith(".py"), "Molecule definitions / lipid scaffolds / fragment definitions file must be a python file: '" + subcmd + "'"
                    if subcmd.startswith("file:"):
                        assert subcmd != "file:", "'file' subargument given to 'import_library' argument but no destination was given alongside 'file:'."
                        subcmd = subcmd[subcmd.index(":")+1:]
                    
                    self.import_library(subcmd)
            
            ### Importing charges and lipid fragment builder arguments from topology files
            elif key in ["itp_input", "itp_in"]:
                if type(cmd) != list:
                    cmd = [cmd]
                for subcmd in cmd:
                    self.ITP_INPUT_cmds.extend([subcmd])
            
            ### Importing molecules from pdb/gro files
            elif key in ["molecule_import"]:
                ### Puts individual string inside list
                if type(cmd) not in [list, tuple]:
                    cmd = [cmd]
                ### Converts tuple to list
                if type(cmd) == tuple:
                    cmd = list(cmd)
                for subcmd in cmd:
                    self.MOLECULE_IMPORT_cmds.extend([subcmd])
            
            ### Molecule fragment builder
            elif key in ["molecule_builder"]:
                ### Puts individual string inside list
                if type(cmd) not in [list, tuple]:
                    cmd = [cmd]
                ### Converts tuple to list
                if type(cmd) == tuple:
                    cmd = list(cmd)
                for subcmd in cmd:
                    self.MOLECULE_FRAGMENT_BUILDER_cmds.extend([subcmd])
            
            ### Outputs
            elif key in ["out_all", "o_all"]:
                ### Cuts the extension if present so that all files can be generated with proper extensions
                if any(cmd.lower().endswith(string) for string in [".log"]):
                    cmd = cmd[:-4]
                self.output_log_file_name = os.path.join(cmd + ".log")
            
            elif key in ["out_log", "o_log"]:
                if not cmd.lower().endswith(".log"):
                    cmd = cmd + ".log"
                self.output_log_file_name = os.path.join(cmd)
                
            elif key in ["backup"]:
                assert cmd in ["False", "True", "0", "1", False, True, 0, 1], "Value given to 'backup' must be False/True/0/1 (strings allowed): " + cmd
                if type(cmd) == str:
                    cmd = ast.literal_eval(cmd)
                self.backup = cmd
            
            elif key in ["rand", "randseed"]:
                cmd = self.get_number_from_string(cmd)
                assert type(cmd) in [int, float], "Value given to rand/randseed must be a number (string-numbers are allowed): " + str(cmd)
                self.randseed = round(cmd)
                    
            elif key in ["params", "sys_params"]:
                self.sys_params = cmd
                
            elif key in ["prot_params"]:
                self.prot_params = cmd
                
            elif key in ["lipid_params"]:
                self.lipid_params = cmd
                
            elif key in ["solv_params"]:
                self.solv_params = cmd
            
            ### Printer settings
            elif key in ["quiet"]:
                assert cmd in ["False", "True", "0", "1", False, True, 0, 1], "Value given to 'quiet' must be False/True/0/1 (strings allowed): " + cmd
                if type(cmd) == str:
                    cmd = ast.literal_eval(cmd)
                self.quiet = cmd
                
            elif key in ["debug"]:
                assert cmd in ["False", "True", "0", "1", False, True, 0, 1], "Value given to 'debug' must be False/True/0/1 (strings allowed): " + cmd
                if type(cmd) == str:
                    cmd = ast.literal_eval(cmd)
                self.debug_prints = cmd
                
            elif key in ["debug_keys"]:
                if type(cmd) == str:
                    self.debug_keys.append(cmd)
                elif type(cmd) in [list, tuple]:
                    for subcmd in cmd:
                        self.debug_keys.append(subcmd)
                
            elif key in ["warn"]:
                assert cmd in ["False", "True", "0", "1", False, True, 0, 1], "Value given to 'warn' must be False/True/0/1 (strings allowed): " + cmd
                if type(cmd) == str:
                    cmd = ast.literal_eval(cmd)
                self.warnings = cmd
                
            elif key == "verbose":
                number = self.get_number_from_string(cmd)
                if number is False:
                    self.verbose = len(cmd)
                else:
                    self.verbose = number
                
            ### Run the program
            elif key == "run":
                if type(cmd) == str:
                    cmd = ast.literal_eval(cmd)
                self.RUN = cmd
            
            else:
                if not invalid_args_given:
                    self.print_term("This is the COBY.Library() method. Arguments given to COBY.Library() that are not in the list of valid arguments will not stop the program, but will also not be processed.", warn=True)
                    invalid_args_given = True
                self.print_term("Invalid argument detected:", str((key, cmd)), spaces=1, warn=True)
        
        ### Setting randseed
        self.print_term("Setting random seed to:", self.randseed, verbose=1)
        random.seed(self.randseed)
        np.random.seed(self.randseed)
        
        ################################
        ### DEFINITION PREPROCESSING ###
        ################################
        string = " ".join(["", "PREPROCESSING DEFINITIONS", ""])
        self.print_term("{string:-^{string_length}}".format(string=string, string_length=self.terminalupdate_string_length), spaces=0, verbose=1)
        preprocessing_tic = time.time()
        
        self.itp_read_initiater()
        
        self.molecule_importer()

        self.lipid_scaffolds_preprocessor()

        ### Fragment builder before defs as it adds to "self.lipid_defs_built", "self.solvent_defs_built", "self.ion_defs_built" dicts
        self.molecule_fragment_builder()

        self.lipid_defs_preprocessor()

        ### Preprocess ions first as they add the "default" parameter libraries of "neg_ions" and "pos_ions" to solvent defs
        self.ion_defs_preprocessor()
        self.solvent_defs_preprocessor()

        preprocessing_toc = time.time()
        preprocessing_time = round(preprocessing_toc - preprocessing_tic, 4)
        string1 = " ".join(["", "DEFINITIONS PREPROCESSING COMPLETE", ""])
        string2 = " ".join(["", "(Time spent:", str(preprocessing_time), "[s])", ""])
        self.print_term("{string:-^{string_length}}".format(string=string1, string_length=self.terminalupdate_string_length), spaces=0, verbose=1)
        self.print_term("{string:^{string_length}}".format(string=string2, string_length=self.terminalupdate_string_length), spaces=0, verbose=1)
        self.print_term("", spaces=0, verbose=1)
        
    def run(self, kwargs):
        '''
        Runs the entire system creation process
        '''
        
        self.commands_handler(kwargs)

        self.ILR_layer0_main()

        ####################
        ### FILE WRITING ###
        ####################
        string = " ".join(["", "WRITING FILES", ""])
        self.print_term("{string:-^{string_length}}".format(string=string, string_length=self.terminalupdate_string_length), spaces=0, verbose=1)
        filewriting_tic = time.time()

        self.log_file_writer()

        filewriting_toc = time.time()
        filewriting_time = round(filewriting_toc - filewriting_tic, 4)
        string1 = " ".join(["", "FILE WRITING COMPLETE", ""])
        string2 = " ".join(["", "(Time spent:", str(filewriting_time), "[s])", ""])
        self.print_term("{string:-^{string_length}}".format(string=string1, string_length=self.terminalupdate_string_length), spaces=0, verbose=1)
        self.print_term("{string:^{string_length}}".format(string=string2, string_length=self.terminalupdate_string_length), spaces=0, verbose=1)
        self.print_term("", spaces=0, verbose=1)

        ######################
        ### END OF PROGRAM ###
        ######################
        self.print_term("My task is complete. Did i do a good job?", verbose=1)
        COBY_run_toc  = time.time()
        COBY_run_time = round(COBY_run_toc - self.COBY_run_tic, 4)
        self.print_term("Time spent running COBY:", COBY_run_time, verbose=1)

    def ILR_invalid_answer(self, val):
        self.print_term("I did not understand your answer: '{}'.".format(val), verbose=0)
        self.print_term("", verbose=0)

    def print_lipid_data(self, parameter_library, lipid_name):
        self.print_term("Below information is for the lipid '{}' from the parameter library '{}'".format(lipid_name, parameter_library), verbose=0)
        self.print_term("    ", "General data:", verbose=0)
        self.print_term("    ", "    ", "Number of residues:", self.lipid_dict[parameter_library][lipid_name].n_residues, verbose=0)
        self.print_term("    ", "    ", "Number of beads:", len(self.lipid_dict[parameter_library][lipid_name].get_bead_charges()), verbose=0)
        self.print_term("    ", "    ", "Total charge:", self.lipid_dict[parameter_library][lipid_name].get_mol_charge(), verbose=0)
        self.print_term("    ", "    ", "Tags:", " ".join(["'"+tag+"'" for tag in self.lipid_dict[parameter_library][lipid_name].tags]), verbose=0)

        self.print_term("    ", "Residues:", verbose=0)
        for residue in self.lipid_dict[parameter_library][lipid_name].residues:
            self.print_term("    ", "    ", "Residue number "+str(residue.resnr)+":", verbose=0)
            self.print_term("    ", "    ", "    ", "Residue name:", residue.resname, verbose=0)
            self.print_term("    ", "    ", "    ", "Number of beads in residue:", len(residue.beads), verbose=0)
            self.print_term("    ", "    ", "    ", "Total charge of residue:", round(sum(bead.charge for bead in residue.beads), 3), verbose=0)
            self.print_term("    ", "    ", "    ", "Beads:", verbose=0)
            table_values  = {"numbers": [], "names": [], "xs": [], "ys": [], "zs": [], "charges": []}
            for bead in residue.beads:
                table_values["numbers"].append(str(bead.beadnr))
                table_values["names"].append(bead.bead)
                table_values["xs"].append(str(round(bead.x, 3)))
                table_values["ys"].append(str(round(bead.y, 3)))
                table_values["zs"].append(str(round(bead.z, 3)))
                table_values["charges"].append(str(round(bead.charge, 3)))
            
            ### Centers all numbers on the decimal position.
            for key in ["numbers", "xs", "ys", "zs", "charges"]:
                ### Adds "+" to all positive values to help with alignment if any value is negative. Plusses are removed later and replaced with empty spaces " ".
                if any(val.startswith("-") for val in table_values[key]):
                    table_values[key] = [val if val.startswith("-") else "+"+val for val in table_values[key]]

                ### Splitting values based on decimal position
                split_vals = [val.split(".") for val in table_values[key]]

                ### Obtaining number of digits to the left and right of the decimal position
                max_left   = max(len(split_val[0]) for split_val in split_vals)
                max_right  = max(len(split_val[1]) if len(split_val) > 1 else 0 for split_val in split_vals)

                ### Adds blank spaces (with rjust and ljust) to each value to align them according to decimal position
                for i, split_val in enumerate(split_vals):
                    left_digits = split_val[0]
                    right_digits = split_val[1] if len(split_val) > 1 else ''
                    table_values[key][i] = left_digits.rjust(max_left) + "." + right_digits.ljust(max_right)
                table_values[key] = [val.replace("+", " ") for val in table_values[key]]
                table_values[key] = [val.replace(".", " ") if len(val.split(".")[1]) == 0 else val for val in table_values[key]]

            columns = [["number"], ["name"], ["x"], ["y"], ["z"], ["charge"]]
            for beadi in range(len(table_values["names"])):
                for vali, val in enumerate([table_values["numbers"][beadi], table_values["names"][beadi], table_values["xs"][beadi], table_values["ys"][beadi], table_values["zs"][beadi], table_values["charges"][beadi]]):
                    columns[vali].append(str(val))

            max_column_lengths = [max([len(val) for val in col]) for col in columns]

            tot_length = sum(max_column_lengths) + len(" : ")*5 + len(" ")*2
            for rowi in range(len(columns[0])):
                string = '{nr:^{L0}} : {name:^{L1}} : {x:^{L2}} : {y:^{L3}} : {z:^{L4}} : {charge:^{L5}}'.format(
                    nr     = columns[0][rowi], L0 = max_column_lengths[0],
                    name   = columns[1][rowi], L1 = max_column_lengths[1],
                    x      = columns[2][rowi], L2 = max_column_lengths[2],
                    y      = columns[3][rowi], L3 = max_column_lengths[3],
                    z      = columns[4][rowi], L4 = max_column_lengths[4],
                    charge = columns[5][rowi], L5 = max_column_lengths[5],
                )

                self.print_term("    ", "    ", "    ", "    ", string, verbose=0)

        self.print_term("", verbose=0)
        self.print_term("    ", "    ", "This lipid can be accessed in 'membrane' arguments via the following subargument:", verbose=0)
        self.print_term("    ", "    ", "    ", "'lipid:params:{params}:name:{lipid}'".format(lipid = lipid_name, params = parameter_library), verbose=0)

        self.print_term("", verbose=0)

    def print_solvent_data(self, parameter_library, solvent_name):
        self.print_term("Below information is for the solvent '{}' from the parameter library '{}'".format(solvent_name, parameter_library), verbose=0)
        self.print_term("    ", "General data:", verbose=0)
        self.print_term("    ", "    ", "Number of residues:", self.solvent_dict[parameter_library][solvent_name].n_residues, verbose=0)
        self.print_term("    ", "    ", "Number of beads:", len(self.solvent_dict[parameter_library][solvent_name].get_bead_charges()), verbose=0)
        self.print_term("    ", "    ", "Total charge:", self.solvent_dict[parameter_library][solvent_name].get_mol_charge(), verbose=0)
        self.print_term("    ", "    ", "Tags:", " ".join(["'"+tag+"'" for tag in self.solvent_dict[parameter_library][solvent_name].tags]), verbose=0)

        self.print_term("    ", "Residues:", verbose=0)
        for residue in self.solvent_dict[parameter_library][solvent_name].residues:
            self.print_term("    ", "    ", "Residue number "+str(residue.resnr)+":", verbose=0)
            self.print_term("    ", "    ", "    ", "Residue name:", residue.resname, verbose=0)
            self.print_term("    ", "    ", "    ", "Number of beads in residue:", len(residue.beads), verbose=0)
            self.print_term("    ", "    ", "    ", "Total charge of residue:", round(sum(bead.charge for bead in residue.beads), 3), verbose=0)
            self.print_term("    ", "    ", "    ", "Beads:", verbose=0)
            table_values  = {"numbers": [], "names": [], "xs": [], "ys": [], "zs": [], "charges": []}
            for bead in residue.beads:
                table_values["numbers"].append(str(bead.beadnr))
                table_values["names"].append(bead.bead)
                table_values["xs"].append(str(round(bead.x, 3)))
                table_values["ys"].append(str(round(bead.y, 3)))
                table_values["zs"].append(str(round(bead.z, 3)))
                table_values["charges"].append(str(round(bead.charge, 3)))
            
            ### Centers all numbers on the decimal position.
            for key in ["numbers", "xs", "ys", "zs", "charges"]:
                ### Adds "+" to all positive values to help with alignment if any value is negative. Plusses are removed later and replaced with empty spaces " ".
                if any(val.startswith("-") for val in table_values[key]):
                    table_values[key] = [val if val.startswith("-") else "+"+val for val in table_values[key]]

                ### Splitting values based on decimal position
                split_vals = [val.split(".") for val in table_values[key]]

                ### Obtaining number of digits to the left and right of the decimal position
                max_left   = max(len(split_val[0]) for split_val in split_vals)
                max_right  = max(len(split_val[1]) if len(split_val) > 1 else 0 for split_val in split_vals)

                ### Adds blank spaces (with rjust and ljust) to each value to align them according to decimal position
                for i, split_val in enumerate(split_vals):
                    left_digits = split_val[0]
                    right_digits = split_val[1] if len(split_val) > 1 else ''
                    table_values[key][i] = left_digits.rjust(max_left) + "." + right_digits.ljust(max_right)
                table_values[key] = [val.replace("+", " ") for val in table_values[key]]
                table_values[key] = [val.replace(".", " ") if len(val.split(".")[1]) == 0 else val for val in table_values[key]]

            columns = [["number"], ["name"], ["x"], ["y"], ["z"], ["charge"]]
            for beadi in range(len(table_values["names"])):
                for vali, val in enumerate([table_values["numbers"][beadi], table_values["names"][beadi], table_values["xs"][beadi], table_values["ys"][beadi], table_values["zs"][beadi], table_values["charges"][beadi]]):
                    columns[vali].append(str(val))

            max_column_lengths = [max([len(val) for val in col]) for col in columns]

            tot_length = sum(max_column_lengths) + len(" : ")*5 + len(" ")*2
            for rowi in range(len(columns[0])):
                string = '{nr:^{L0}} : {name:^{L1}} : {x:^{L2}} : {y:^{L3}} : {z:^{L4}} : {charge:^{L5}}'.format(
                    nr     = columns[0][rowi], L0 = max_column_lengths[0],
                    name   = columns[1][rowi], L1 = max_column_lengths[1],
                    x      = columns[2][rowi], L2 = max_column_lengths[2],
                    y      = columns[3][rowi], L3 = max_column_lengths[3],
                    z      = columns[4][rowi], L4 = max_column_lengths[4],
                    charge = columns[5][rowi], L5 = max_column_lengths[5],
                )

                self.print_term("    ", "    ", "    ", "    ", string, verbose=0)

        self.print_term("", verbose=0)
        self.print_term("    ", "    ", "This solvent can be accessed in 'solvation' arguments via the following subargument:", verbose=0)
        self.print_term("    ", "    ", "    ", "'solvent:params:{params}:name:{solvent}'".format(solvent = solvent_name, params = parameter_library), verbose=0)
        self.print_term("", verbose=0)
        self.print_term("    ", "    ", "This solvent can be accessed in 'flooding' arguments via the following subargument:", verbose=0)
        self.print_term("    ", "    ", "    ", "'solute:params:{params}:name:{solvent}'".format(solvent = solvent_name, params = parameter_library), verbose=0)

        self.print_term("", verbose=0)

    ### ILR = interactive library roamer
    def ILR_layer0_main(self):
        ILR_restart_layer = self.ILR_layer0_main
        self.print_term("-"*self.terminalupdate_string_length, verbose=0)

        val = self.print_term(
            "\n".join([
                "What library would you like to investigate? Your options are shown below:",
                "    "+"Quit:                           'q' or 'quit' ",
                "    "+"For the lipid library:          'lipid(s)'",
                "    "+"For the solvent/solute library: 'solvent'    (not implemented)",
                "    "+"For the positive ion library:   'pos_ion(s)' (not implemented)",
                "    "+"For the negative ion library:   'neg_ion(s)' (not implemented)",
                "    "+"For the protein charge library: 'protein'    (not implemented)",
                "",
            ]),
            inp=True
        )
        self.print_term("", verbose=0)
        val = val.lstrip(" ").rstrip(" ")
        # print("Going to the '{}' library.".format(val))

        if val.lower() in ["q", "quit"]:
            pass
        elif val.lower() in ["lipid", "lipids"]:
            self.ILR_layer1_lipids()
        elif val.lower() in ["solvent"]:
            self.ILR_layer1_solvent()
        # elif val.lower() in ["pos_ion", "pos_ions"]:
        #     self.ILR_layer1_pos_ions()
        # elif val.lower() in ["neg_ion", "neg_ions"]:
        #     self.ILR_layer1_neg_ions()
        # elif val.lower() in ["protein"]:
        #     self.ILR_layer1_protein()
        else:
            self.ILR_invalid_answer(val)
            ILR_restart_layer()

    def ILR_layer1_lipids(self):
        ILR_restart_layer = self.ILR_layer1_lipids
        self.print_term("-"*self.terminalupdate_string_length, verbose=0)
        
        parameter_libraries = sorted(list(self.lipid_dict.keys()))
        all_tags = sorted(list(set([
            tag
            for parameter_library in parameter_libraries
            for lipid in self.lipid_dict[parameter_library].values()
            for tag in lipid.tags
        ])))
        val = self.print_term(
            "\n".join([
                "You are in the general lipid library. The names of all available lipid parameter libraries are shown below:",
                "    "+" ".join(["'"+parameter_library+"'" for parameter_library in parameter_libraries]),
                "",
                "What would you like to do? Your options are shown below:",
                "    "+"Quit:                                         'q' or 'quit'",
                "    "+"Return to previous question:                  'r' or 'return'",
                "    "+"Examine parameter library:                    'param(s):[parameter library name]' or '[parameter library name]'",
                "    "+"Print all lipid names in a parameter library: 'printparam(s):[parameter library name]' or 'pp:[parameter library name]'",
                "    "+""+"Print names of lipids with given tag(s):",
                "    "+"    "+"- Only this specific tag:                      'tag:[tag1]' (only 1 tag)",
                "    "+"    "+"- With any of these tags:                      'any:[tag1]:[tag2]:[etc.]' (any number of tags)",
                "    "+"    "+"- With all of these tags:                      'all:[tag1]:[tag2]:[etc.]' (any number of tags)",
                "    "+"    "+"- Combining the above:                         'tag:[tag1]:any:[tag2]:[etc.]:all:[tag3]:[etc.]'",
                "    "+"Print all tags:                               'printtags' or 'pt",
                "    "+"Examine lipid from given parameter library:   'lipid(s):[parameter library name]:[lipid name]'",
                "",
            ]),
            inp=True
        )
        self.print_term("", verbose=0)
        val = val.lstrip(" ").rstrip(" ")
        # print("tuple(parameter_libraries)", tuple(parameter_libraries))
        # print("val.endswith(tuple(parameter_libraries))", val.endswith(tuple(parameter_libraries)))
        # print('val.lower().startswith("print:")', val.lower().startswith("p:"))

        if val.lower() in ["q", "quit"]:
            pass
        
        elif val in ["r", "return"]:
            self.ILR_layer0_main()
        
        elif val.lower().startswith(("param:", "params:")) or val in parameter_libraries:
            parameter_library = False
            if val.lower().startswith(("param:", "params:")):
                if len(val.split(":")) == 2:
                    parameter_library = val.split(":")[1]
                else:
                    self.print_term("You must specify exactly one parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                parameter_library = val
            
            if parameter_library is not False:
                if parameter_library in parameter_libraries:
                    self.ILR_layer2_lipids(parameter_library=parameter_library)
                else:
                    self.print_term("Parameter library not found. You must specify an existing parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
                    ILR_restart_layer()
            else:
                ILR_restart_layer()
        
        elif val.lower().startswith(("printparam", "printparams", "pp")):
            if len(val.split(":")) == 2:
                parameter_library = val.split(":")[1]
                if parameter_library in parameter_libraries:
                    self.print_term(*list(self.lipid_dict[parameter_library].keys()), verbose=0)
                    self.print_term("", verbose=0)
                else:
                    self.print_term("Parameter library not found. You must specify an existing parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                self.print_term("You must specify exactly one parameter library: '{}'.".format(val), verbose=0)
                self.print_term("", verbose=0)
            ILR_restart_layer()

        elif val.lower().startswith(("tag:", "any:" ,"all:")):
            for parameter_library in parameter_libraries:
                found_mols_with_tags = []
                func_str = False
                func = False
                given_tags = []
                breaked_loop = False
                for subval in val.split(":") + ["end"]:
                    if func_str is not False and subval.lower() in ["tag", "any", "all", "end"]:
                        if len(given_tags) == 0:
                            self.print_term("No tags have ben given to the '{}' subargument. Please try again.".format(str(func_str)), verbose=0)
                            self.print_term("", verbose=0)
                            breaked_loop = True
                            break

                        if func_str == "tag":
                            if len(given_tags) > 1:
                                self.print_term("More than 1 tag has been given to the 'tag' subargument. Please try again with only 1 tag.".format(str(func_str)), verbose=0)
                                self.print_term("", verbose=0)
                                breaked_loop = True
                                break

                            found_mols_with_tags.append(sorted(list(set([
                                key
                                for key, val in self.lipid_dict[parameter_library].items()
                                if given_tags[0] in val.tags and len(val.tags) > 0
                            ]))))
                        else:
                            found_mols_with_tags.append(sorted(list(set([
                                key
                                for key, val in self.lipid_dict[parameter_library].items()
                                if func([tag in val.tags for tag in given_tags]) and len(val.tags) > 0
                            ]))))
                        func_str = False
                        func = False
                        given_tags = []
                    
                    if subval.lower() == "tag":
                        func_str = "tag"
                    elif subval.lower() == "any":
                        func_str = "any"
                        func = any
                    elif subval.lower() == "all":
                        func_str = "all"
                        func = all
                    elif subval.lower() == "end":
                        break
                    else:
                        given_tags.append(subval)

                if breaked_loop:
                    ILR_restart_layer(parameter_library)
                else:
                    lipids_with_tags_in_params = {}
                    for l in found_mols_with_tags:
                        for m in l:
                            if m not in lipids_with_tags_in_params:
                                lipids_with_tags_in_params[m] = 1
                            else:
                                lipids_with_tags_in_params[m] += 1
                    lipids_with_tags_in_params = [key for key, val in lipids_with_tags_in_params.items() if val == len(found_mols_with_tags)]

                    self.print_term("Parameter library name:", parameter_library, verbose=0)
                    self.print_term("    "+" ".join(lipids_with_tags_in_params), verbose=0)
                    self.print_term("", verbose=0)
                        
            ILR_restart_layer()

        elif val.lower() in ("printtags", "pt"):
            self.print_term("Following tags are present across all lipid parameter libraries:", verbose=0)
            self.print_term("    "+" ".join(["'"+tag+"'" for tag in all_tags]), verbose=0)
            self.print_term("", verbose=0)
            ILR_restart_layer()
        
        elif val.lower().startswith(("lipid:", "lipids:")):
            if len(val.split(":")) == 3:
                parameter_library, lipid_name = val.split(":")[1:]
                if parameter_library in parameter_libraries:
                    if lipid_name in self.lipid_dict[parameter_library].keys():
                        self.print_lipid_data(parameter_library, lipid_name)
                    else:
                        self.print_term("Lipid name not found in parameter library. You must specify an existing lipid in the parameter library: '{}'.".format(val), verbose=0)
                        self.print_term("", verbose=0)
                else:
                    self.print_term("Parameter library not found. You must specify an existing parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                self.print_term("You must specify both a parameter library and a lipid name: '{}'.".format(val), verbose=0)
                self.print_term("", verbose=0)
            ILR_restart_layer()
        
        else:
            self.ILR_invalid_answer(val)
            ILR_restart_layer()

    def ILR_layer2_lipids(self, parameter_library, lipid_name = False):
        ILR_restart_layer = self.ILR_layer2_lipids
        self.print_term("-"*self.terminalupdate_string_length, verbose=0)
        
        tags_in_parameter_library = sorted(list(set([
            tag
            for lipid in self.lipid_dict[parameter_library].values()
            for tag in lipid.tags
        ])))

        lipid_names_in_parameter_library = sorted([lipid for lipid in self.lipid_dict[parameter_library].keys()])

        val = self.print_term(
            "\n".join([
                "You are in the lipid parameter library '{}':".format(parameter_library),
                "",
                "What would you like to do? Your options are shown below:",
                "    "+""+"Quit:                                              'q' or 'quit'",
                "    "+""+"Return to previous question:                       'r' or 'return'",
                "    "+""+"Print names of lipids with given tag(s):",
                "    "+"    "+"- Only this specific tag:                      'tag:[tag1]' (only 1 tag)",
                "    "+"    "+"- With any of these tags:                      'any:[tag1]:[tag2]:[etc.]' (any number of tags)",
                "    "+"    "+"- With all of these tags:                      'all:[tag1]:[tag2]:[etc.]' (any number of tags)",
                "    "+"    "+"- Combining the above:                         'tag:[tag1]:any:[tag2]:[etc.]:all:[tag3]:[etc.]'",
                "    "+""+"Print all tags used in the parameter library:      'printtags' or 'pt'",
                "    "+""+"Print names of all lipid in the parameter library: 'printlipids' or 'pl'",
                "    "+""+"Examine a specific lipid in the parameter library: 'lipid(s):[lipid name]' or '[lipid name]'",
                "",
            ]),
            inp=True
        )
        self.print_term("", verbose=0)
        val = val.lstrip(" ").rstrip(" ")
        
        if val.lower() in ["q", "quit"]:
            pass
        
        elif val in ["r", "return"]:
            self.ILR_layer1_lipids()
        
        elif val.lower() in ("printlipids", "pl"):
            self.print_term("All lipids in the '{}' parameter library:".format(parameter_library), verbose=0)
            self.print_term("    "+" ".join(lipid_names_in_parameter_library), verbose=0)
            self.print_term("", verbose=0)
            ILR_restart_layer(parameter_library)
        
        elif val.lower().startswith(("tag:", "any:" ,"all:")):
            found_mols_with_tags = []
            func_str = False
            func = False
            given_tags = []
            breaked_loop = False
            for subval in val.split(":") + ["end"]:
                if func_str is not False and subval.lower() in ["tag", "any", "all", "end"]:
                    if len(given_tags) == 0:
                        self.print_term("No tags have ben given to the '{}' subargument. Please try again.".format(str(func_str)), verbose=0)
                        self.print_term("", verbose=0)
                        breaked_loop = True
                        break

                    if func_str == "tag":
                        if len(given_tags) > 1:
                            self.print_term("More than 1 tag has been given to the 'tag' subargument. Please try again with only 1 tag.".format(str(func_str)), verbose=0)
                            self.print_term("", verbose=0)
                            breaked_loop = True
                            break

                        found_mols_with_tags.append(sorted(list(set([
                            key
                            for key, val in self.lipid_dict[parameter_library].items()
                            if given_tags[0] in val.tags and len(val.tags) > 0
                        ]))))
                    else:
                        found_mols_with_tags.append(sorted(list(set([
                            key
                            for key, val in self.lipid_dict[parameter_library].items()
                            if func([tag in val.tags for tag in given_tags]) and len(val.tags) > 0
                        ]))))
                    func_str = False
                    func = False
                    given_tags = []
                
                if subval.lower() == "tag":
                    func_str = "tag"
                elif subval.lower() == "any":
                    func_str = "any"
                    func = any
                elif subval.lower() == "all":
                    func_str = "all"
                    func = all
                elif subval.lower() == "end":
                    break
                else:
                    given_tags.append(subval)

            if breaked_loop:
                ILR_restart_layer(parameter_library)
            else:
                lipids_with_tags_in_params = {}
                for l in found_mols_with_tags:
                    for m in l:
                        if m not in lipids_with_tags_in_params:
                            lipids_with_tags_in_params[m] = 1
                        else:
                            lipids_with_tags_in_params[m] += 1
                lipids_with_tags_in_params = [key for key, val in lipids_with_tags_in_params.items() if val == len(found_mols_with_tags)]

                self.print_term("Parameter library name:", parameter_library, verbose=0)
                self.print_term("    "+" ".join(lipids_with_tags_in_params), verbose=0)
                self.print_term("", verbose=0)
                    
                ILR_restart_layer(parameter_library)
        
        elif val.lower() in ("printtags", "pt"):
            self.print_term("Following tags are present in this lipid parameter library:", verbose=0)
            self.print_term("    "+" ".join(["'"+tag+"'" for tag in tags_in_parameter_library]), verbose=0)
            self.print_term("", verbose=0)
            ILR_restart_layer(parameter_library)
        
        elif val.startswith(("lipid:", "lipids:")) or val in lipid_names_in_parameter_library:
            lipid = False
            if val.startswith(("lipid:", "lipids:")):
                if len(val.split(":")) == 2:
                    lipid = val.split(":")[1]
                else:
                    self.print_term("You must specify exactly one lipid name: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                lipid = val
            
            if lipid is not False:
                if lipid in self.lipid_dict[parameter_library].keys():
                    self.print_lipid_data(parameter_library, lipid)
                else:
                    self.print_term("Lipid name not found in parameter library. You must specify an existing lipid in the parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            ILR_restart_layer(parameter_library)
        
        else:
            self.ILR_invalid_answer(val)
            ILR_restart_layer(parameter_library)

    def ILR_layer1_solvent(self):
        ILR_restart_layer = self.ILR_layer1_solvent
        self.print_term("-"*self.terminalupdate_string_length, verbose=0)
        
        parameter_libraries = sorted(list(self.solvent_dict.keys()))
        all_tags = sorted(list(set([
            tag
            for parameter_library in parameter_libraries
            for solvent in self.solvent_dict[parameter_library].values()
            for tag in solvent.tags
        ])))
        val = self.print_term(
            "\n".join([
                "You are in the general solvent library. The names of all available solvent parameter libraries are shown below:",
                "    "+" ".join(["'"+parameter_library+"'" for parameter_library in parameter_libraries]),
                "",
                "What would you like to do? Your options are shown below:",
                "    "+"Quit:                                           'q' or 'quit'",
                "    "+"Return to previous question:                    'r' or 'return'",
                "    "+"Examine parameter library:                      'param(s):[parameter library name]' or '[parameter library name]'",
                "    "+"Print all solvent names in a parameter library: 'printparam(s):[parameter library name]' or 'pp:[parameter library name]'",
                "    "+""+"Print names of solvents with given tag(s):",
                "    "+"    "+"- Only this specific tag:                        'tag:[tag1]' (only 1 tag)",
                "    "+"    "+"- With any of these tags:                        'any:[tag1]:[tag2]:[etc.]' (any number of tags)",
                "    "+"    "+"- With all of these tags:                        'all:[tag1]:[tag2]:[etc.]' (any number of tags)",
                "    "+"    "+"- Combining the above:                           'tag:[tag1]:any:[tag2]:[etc.]:all:[tag3]:[etc.]'",
                "    "+"Print all tags:                                 'printtags' or 'pt",
                "    "+"Examine solvent from given parameter library:   'solvent(s):[parameter library name]:[solvent name]'",
                "",
            ]),
            inp=True
        )
        self.print_term("", verbose=0)
        val = val.lstrip(" ").rstrip(" ")
        # print("tuple(parameter_libraries)", tuple(parameter_libraries))
        # print("val.endswith(tuple(parameter_libraries))", val.endswith(tuple(parameter_libraries)))
        # print('val.lower().startswith("print:")', val.lower().startswith("p:"))

        if val.lower() in ["q", "quit"]:
            pass
        
        elif val in ["r", "return"]:
            self.ILR_layer0_main()
        
        elif val.lower().startswith(("param:", "params:")) or val in parameter_libraries:
            parameter_library = False
            if val.lower().startswith(("param:", "params:")):
                if len(val.split(":")) == 2:
                    parameter_library = val.split(":")[1]
                else:
                    self.print_term("You must specify exactly one parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                parameter_library = val
            
            if parameter_library is not False:
                if parameter_library in parameter_libraries:
                    self.ILR_layer2_solvent(parameter_library=parameter_library)
                else:
                    self.print_term("Parameter library not found. You must specify an existing parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
                    ILR_restart_layer()
            else:
                ILR_restart_layer()
        
        elif val.lower().startswith(("printparam", "printparams", "pp")):
            if len(val.split(":")) == 2:
                parameter_library = val.split(":")[1]
                if parameter_library in parameter_libraries:
                    self.print_term(*list(self.solvent_dict[parameter_library].keys()), verbose=0)
                    self.print_term("", verbose=0)
                else:
                    self.print_term("Parameter library not found. You must specify an existing parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                self.print_term("You must specify exactly one parameter library: '{}'.".format(val), verbose=0)
                self.print_term("", verbose=0)
            ILR_restart_layer()

        elif val.lower().startswith(("tag:", "any:" ,"all:")):
            for parameter_library in parameter_libraries:
                found_mols_with_tags = []
                func_str = False
                func = False
                given_tags = []
                breaked_loop = False
                for subval in val.split(":") + ["end"]:
                    if func_str is not False and subval.lower() in ["tag", "any", "all", "end"]:
                        if len(given_tags) == 0:
                            self.print_term("No tags have ben given to the '{}' subargument. Please try again.".format(str(func_str)), verbose=0)
                            self.print_term("", verbose=0)
                            breaked_loop = True
                            break

                        if func_str == "tag":
                            if len(given_tags) > 1:
                                self.print_term("More than 1 tag has been given to the 'tag' subargument. Please try again with only 1 tag.".format(str(func_str)), verbose=0)
                                self.print_term("", verbose=0)
                                breaked_loop = True
                                break

                            found_mols_with_tags.append(sorted(list(set([
                                key
                                for key, val in self.solvent_dict[parameter_library].items()
                                if given_tags[0] in val.tags and len(val.tags) > 0
                            ]))))
                        else:
                            found_mols_with_tags.append(sorted(list(set([
                                key
                                for key, val in self.solvent_dict[parameter_library].items()
                                if func([tag in val.tags for tag in given_tags]) and len(val.tags) > 0
                            ]))))
                        func_str = False
                        func = False
                        given_tags = []
                    
                    if subval.lower() == "tag":
                        func_str = "tag"
                    elif subval.lower() == "any":
                        func_str = "any"
                        func = any
                    elif subval.lower() == "all":
                        func_str = "all"
                        func = all
                    elif subval.lower() == "end":
                        break
                    else:
                        given_tags.append(subval)

                if breaked_loop:
                    ILR_restart_layer(parameter_library)
                else:
                    solvents_with_tags_in_params = {}
                    for l in found_mols_with_tags:
                        for m in l:
                            if m not in solvents_with_tags_in_params:
                                solvents_with_tags_in_params[m] = 1
                            else:
                                solvents_with_tags_in_params[m] += 1
                    solvents_with_tags_in_params = [key for key, val in solvents_with_tags_in_params.items() if val == len(found_mols_with_tags)]

                    self.print_term("Parameter library name:", parameter_library, verbose=0)
                    self.print_term("    "+" ".join(solvents_with_tags_in_params), verbose=0)
                    self.print_term("", verbose=0)
                        
            ILR_restart_layer()

        elif val.lower() in ("printtags", "pt"):
            self.print_term("Following tags are present across all solvent parameter libraries:", verbose=0)
            self.print_term("    "+" ".join(["'"+tag+"'" for tag in all_tags]), verbose=0)
            self.print_term("", verbose=0)
            ILR_restart_layer()
        
        elif val.lower().startswith(("solvent:", "solvents:")):
            if len(val.split(":")) == 3:
                parameter_library, solvent_name = val.split(":")[1:]
                if parameter_library in parameter_libraries:
                    if solvent_name in self.solvent_dict[parameter_library].keys():
                        self.print_solvent_data(parameter_library, solvent_name)
                    else:
                        self.print_term("Lipid name not found in parameter library. You must specify an existing solvent in the parameter library: '{}'.".format(val), verbose=0)
                        self.print_term("", verbose=0)
                else:
                    self.print_term("Parameter library not found. You must specify an existing parameter library: '{}'.".format(val), verbose=0)
                    self.print_term("", verbose=0)
            else:
                self.print_term("You must specify both a parameter library and a solvent name: '{}'.".format(val), verbose=0)
                self.print_term("", verbose=0)
            ILR_restart_layer()
        
        else:
            self.ILR_invalid_answer(val)
            ILR_restart_layer()

    # def ILR_layer2_lipids(self, parameter_library, lipid_name = False):
    #     ILR_restart_layer = self.ILR_layer2_lipids
    #     self.print_term("-"*self.terminalupdate_string_length, verbose=0)
        
    #     tags_in_parameter_library = sorted(list(set([
    #         tag
    #         for lipid in self.lipid_dict[parameter_library].values()
    #         for tag in lipid.tags
    #     ])))

    #     lipid_names_in_parameter_library = sorted([lipid for lipid in self.lipid_dict[parameter_library].keys()])

    #     val = self.print_term(
    #         "\n".join([
    #             "You are in the lipid parameter library '{}':".format(parameter_library),
    #             "",
    #             "What would you like to do? Your options are shown below:",
    #             "    "+""+"Quit:                                              'q' or 'quit'",
    #             "    "+""+"Return to previous question:                       'r' or 'return'",
    #             "    "+""+"Print names of lipids with given tag(s):",
    #             "    "+"    "+"- Only this specific tag:                      'tag:[tag1]' (only 1 tag)",
    #             "    "+"    "+"- With any of these tags:                      'any:[tag1]:[tag2]:[etc.]' (any number of tags)",
    #             "    "+"    "+"- With all of these tags:                      'all:[tag1]:[tag2]:[etc.]' (any number of tags)",
    #             "    "+"    "+"- Combining the above:                         'tag:[tag1]:any:[tag2]:[etc.]:all:[tag3]:[etc.]'",
    #             "    "+""+"Print all tags used in the parameter library:      'printtags' or 'pt'",
    #             "    "+""+"Print names of all lipid in the parameter library: 'printlipids' or 'pl'",
    #             "    "+""+"Examine a specific lipid in the parameter library: 'lipid(s):[lipid name]' or '[lipid name]'",
    #             "",
    #         ]),
    #         inp=True
    #     )
    #     self.print_term("", verbose=0)
    #     val = val.lstrip(" ").rstrip(" ")
        
    #     if val.lower() in ["q", "quit"]:
    #         pass
        
    #     elif val in ["r", "return"]:
    #         self.ILR_layer1_lipids()
        
    #     elif val.lower() in ("printlipids", "pl"):
    #         self.print_term("All lipids in the '{}' parameter library:".format(parameter_library), verbose=0)
    #         self.print_term("    "+" ".join(lipid_names_in_parameter_library), verbose=0)
    #         self.print_term("", verbose=0)
    #         ILR_restart_layer(parameter_library)
        
    #     elif val.lower().startswith(("tag:", "any:" ,"all:")):
    #         found_mols_with_tags = []
    #         func_str = False
    #         func = False
    #         given_tags = []
    #         breaked_loop = False
    #         for subval in val.split(":") + ["end"]:
    #             if func_str is not False and subval.lower() in ["tag", "any", "all", "end"]:
    #                 if len(given_tags) == 0:
    #                     self.print_term("No tags have ben given to the '{}' subargument. Please try again.".format(str(func_str)), verbose=0)
    #                     self.print_term("", verbose=0)
    #                     breaked_loop = True
    #                     break

    #                 if func_str == "tag":
    #                     if len(given_tags) > 1:
    #                         self.print_term("More than 1 tag has been given to the 'tag' subargument. Please try again with only 1 tag.".format(str(func_str)), verbose=0)
    #                         self.print_term("", verbose=0)
    #                         breaked_loop = True
    #                         break

    #                     found_mols_with_tags.append(sorted(list(set([
    #                         key
    #                         for key, val in self.lipid_dict[parameter_library].items()
    #                         if given_tags[0] in val.tags and len(val.tags) > 0
    #                     ]))))
    #                 else:
    #                     found_mols_with_tags.append(sorted(list(set([
    #                         key
    #                         for key, val in self.lipid_dict[parameter_library].items()
    #                         if func([tag in val.tags for tag in given_tags]) and len(val.tags) > 0
    #                     ]))))
    #                 func_str = False
    #                 func = False
    #                 given_tags = []
                
    #             if subval.lower() == "tag":
    #                 func_str = "tag"
    #             elif subval.lower() == "any":
    #                 func_str = "any"
    #                 func = any
    #             elif subval.lower() == "all":
    #                 func_str = "all"
    #                 func = all
    #             elif subval.lower() == "end":
    #                 break
    #             else:
    #                 given_tags.append(subval)

    #         if breaked_loop:
    #             ILR_restart_layer(parameter_library)
    #         else:
    #             lipids_with_tags_in_params = {}
    #             for l in found_mols_with_tags:
    #                 for m in l:
    #                     if m not in lipids_with_tags_in_params:
    #                         lipids_with_tags_in_params[m] = 1
    #                     else:
    #                         lipids_with_tags_in_params[m] += 1
    #             lipids_with_tags_in_params = [key for key, val in lipids_with_tags_in_params.items() if val == len(found_mols_with_tags)]

    #             self.print_term("Parameter library name:", parameter_library, verbose=0)
    #             self.print_term("    "+" ".join(lipids_with_tags_in_params), verbose=0)
    #             self.print_term("", verbose=0)
                    
    #             ILR_restart_layer(parameter_library)
        
    #     elif val.lower() in ("printtags", "pt"):
    #         self.print_term("Following tags are present in this lipid parameter library:", verbose=0)
    #         self.print_term("    "+" ".join(["'"+tag+"'" for tag in tags_in_parameter_library]), verbose=0)
    #         self.print_term("", verbose=0)
    #         ILR_restart_layer(parameter_library)
        
    #     elif val.startswith(("lipid:", "lipids:")) or val in lipid_names_in_parameter_library:
    #         lipid = False
    #         if val.startswith(("lipid:", "lipids:")):
    #             if len(val.split(":")) == 2:
    #                 lipid = val.split(":")[1]
    #             else:
    #                 self.print_term("You must specify exactly one lipid name: '{}'.".format(val), verbose=0)
    #                 self.print_term("", verbose=0)
    #         else:
    #             lipid = val
            
    #         if lipid is not False:
    #             if lipid in self.lipid_dict[parameter_library].keys():
    #                 self.print_lipid_data(parameter_library, lipid)
    #             else:
    #                 self.print_term("Lipid name not found in parameter library. You must specify an existing lipid in the parameter library: '{}'.".format(val), verbose=0)
    #                 self.print_term("", verbose=0)
    #         ILR_restart_layer(parameter_library)
        
    #     else:
    #         self.ILR_invalid_answer(val)
    #         ILR_restart_layer(parameter_library)


