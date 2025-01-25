import importlib
import mcvqoe.base.version
import os
import platform
import traceback
import warnings

import numpy as np


def fill_log(test_obj):
    """
    Take in QoE measurement class and fill in standard log entries.
    
    Used for the tests.log files found in the measurement folder, and
    the test specific folder.

    ...

    Parameters
    ----------
    test_obj : QoE measurement class
        Class to generate test info for
    """

    # initialize info
    info = {}

    # ---------------------------[RadioInterface info]---------------------------
    
    # Skip the RI version info change if running soft timecode or no RI
    # Without this the test will error out
    skip_ri = False

    try:
        # Get ID and Version number from RadioInterface
        info["RI version"] = test_obj.ri.get_version()
        info["RI id"] = test_obj.ri.get_id()
    except AttributeError:
        # no RI for this object
        skip_ri = True

    # ---------------------[Get traceback for calling info]---------------------

    # Get a stack trace
    tb = traceback.extract_stack()

    # Remove the last one cause that's this function
    tb = tb[:-1]

    # Extract important info from traceback
    tb_info = [(os.path.basename(fs.filename), fs.name if fs.name != "<module>" else None) for fs in tb]

    # Add entry for calling file
    info["filename"] = tb_info[-1][0]

    # Format string with '->' between files
    info["traceback"] = "->".join([f"{f}({n})" if n is not None else f for f, n in tb_info])

    # ---------------------------[Add MCV QoE version]---------------------------

    info["mcvqoe version"] = mcvqoe.base.version
    
    if skip_ri == False:
        # Change RI Version if running simulation
        if info["RI version"] == info["mcvqoe version"]:
            
            info["RI version"] = "Simulation (no real RI)"

    # ----------------------[Add Measurement class version]----------------------

    if test_obj.__class__.__name__ == "measure":
        # Get module for test_obj
        module = test_obj.__class__.__module__
    else:
        # base.__name__ provides only the most recently inherited class. mro() finds ALL inherited classes
        # Need this deeper search to find the base "measure" class for the characterization test
        for base in test_obj.__class__.mro():
            # See if we have inherited from measure class
            if base.__name__ == "measure":
                # Get module from this class
                module = base.__module__
                # We are done
                break
        else:
            # Could not find module
            module = None
            warnings.warn(f"Unable to find measure class for {test_obj.__class__.__name__}", category=RuntimeWarning)

    # Set default version
    info["test version"] = "Unknown"

    if module:
        # Import base level module
        mod = importlib.import_module(module)
        try:
            info["test version"] = mod.version
        except AttributeError as e:
            warnings.warn(f"Unable to get version {e}", category=RuntimeWarning)
            pass
        
    # ------------------------------[Add OS info]------------------------------

    info["os name"] = platform.system()
    info["os release"] = platform.release()
    info["os version"] = platform.version()

    # ---------------------------[Fill Arguments list]---------------------------

    # Class properties to skip in all cases
    standard_skip = ["no_log", "info", "progress_update", "rng", "user_check"]
    arg_list = []

    np.set_string_function(lambda x: f"np.ndarray(dtype={x.dtype}, shape={x.shape})")
    for k, v in vars(test_obj).items():
        if not k.startswith("_") and k not in test_obj.no_log and k not in standard_skip:
            arg_list.append(k + " = " + repr(v))
    np.set_string_function(None)

    info["Arguments"] = ",".join(arg_list)

    # -------------------------------[Return info]-------------------------------

    return info

def format_text_block(text):
    """
    Format text block for log.

    This writes out a, possibly, multi line text block to the log. It is used to
    write out both pre and post test notes.

    Parameters
    ----------
    text : str
        String containing the block of text to format.
    """

    if text is None:
        return ""

    return "".join(["\t" + line + "\n" for line in text.splitlines(keepends=False)])

def pre(info={}, outdir="", test_folder=""):
    """
    Take in a QoE measurement class info dictionary and write pre-test to tests.log
    found in the measurement folder, and the test's specific folder.

    ...

    Parameters
    ----------
    info : dict
        The <measurement>.info dictionary used to write to tests.log.
    outdir : str
        The outer test directory to write to. (Access, M2E, etc.)
    test_folder : str
        The current test directory to write to.
    """

    # Length to pad test params to
    pad_len = 10

    # Add 'outdir' to tests.log path
    log_datadir = os.path.join(outdir, "tests.log")

    skip_keys = ["test", "Tstart", "Pre Test Notes"]

    # Write all necessary arguments/test params into tests.log
    with open(log_datadir, "a") as file:

        file.write(f"\n>>{info['test']} started at {info['Tstart'].strftime('%d-%b-%Y %H:%M:%S')}\n")
        for key in info:
            if key not in skip_keys:
                file.write(f"\t{key:<{pad_len}} : {info[key]}\n")

        file.write("===Pre-Test Notes===\n")
        file.write(format_text_block(info["Pre Test Notes"]))
    
    # Add test's specific log file to folder if given
    if test_folder != "":
        
        # Do the same for the inner specific test directory if given
        log_folder = os.path.join(test_folder, "tests.log")
        
        # Write all necessary arguments/test params into tests.log
        with open(log_folder, "a") as file:
            
            file.write(f"\n>>{info['test']} started at {info['Tstart'].strftime('%d-%b-%Y %H:%M:%S')}\n")
            for key in info:
                if key not in skip_keys:
                    file.write(f"\t{key:<{pad_len}} : {info[key]}\n")

            file.write("===Pre-Test Notes===\n")
            file.write(format_text_block(info["Pre Test Notes"]))

def post(info={}, outdir="", test_folder=""):
    """
    Take in a QoE measurement class info dictionary to write post-test to tests.log
    found in the measurement folder, and the test's specific folder.

    ...

    Parameters
    ----------
    info : dict
        The <measurement>.info dictionary.
    outdir : str
        The directory to write to.
    test_folder : str
        Folder for this particular test's log file.

    """

    # Add 'outdir' to tests.log path
    log_datadir = os.path.join(outdir, "tests.log")

    with open(log_datadir, "a") as file:
        if "Error Notes" in info:
            notes = info["Error Notes"]
            header = "===Test-Error Notes==="
        else:
            header = "===Post-Test Notes==="
            notes = info.get("Post Test Notes", "")

        # Write header
        file.write(header + "\n")
        # Write notes
        file.write(format_text_block(notes))
        # Write end
        file.write("===End Test===\n\n")
        
    # Add test's specific log file to folder if given
    if test_folder != "":
        
        # Add test_folder path
        log_folder = os.path.join(test_folder, "tests.log")
        
        # Open and write test_folder log file
        with open(log_folder, "a") as file:
            if "Error Notes" in info:
                notes = info["Error Notes"]
                header = "===Test-Error Notes==="
            else:
                header = "===Post-Test Notes==="
                notes = info.get("Post Test Notes", "")

            # Write header
            file.write(header + "\n")
            # Write notes
            file.write(format_text_block(notes))
            # Write end
            file.write("===End Test===\n\n")