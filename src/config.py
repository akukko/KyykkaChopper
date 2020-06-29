from terminal_colors import *
from files import get_lines

TITLE_FONT_KEY = "titlefont"
TITLE_SIZE_KEY = "titlesize"
TITLE_COLOR_KEY = "titlecolor"
VOL_FACTOR_KEY = "volfactor"


class Configuration:
    def __init__(self):
        self.titlefont = "roboto-mono"
        self.titlesize = 110
        self.titlecolor = "white"
        self.volfactor = 0.1
    
    def __str__(self):
        key_vals = { TITLE_FONT_KEY: self.titlefont
                   , TITLE_SIZE_KEY: self.titlesize
                   , TITLE_COLOR_KEY: self.titlecolor
                   , VOL_FACTOR_KEY: self.volfactor
                   }

        conf_str = ""
        for key, val in key_vals.items():
            conf_str += f"{key:<32}{val}\n"
        return conf_str

def make_default_config(configfile):
    lines = get_lines(configfile)
    if lines:
        print(warn("Requested creation of default configuration file, but configuration file already exists. Not overwriting."))
        return

    conf = Configuration()
    with open(configfile, "w") as f:
        f.write(str(conf))
    print(ok(f"Created new configuration file with default values at: {header(configfile)}"))

def read_config(configfile):
    # Create default configuration
    conf = Configuration()

    lines = get_lines(configfile)
    
    if lines:
        return handle_config_values(conf, lines)
    else:
        # Config was empty or didn't exist
        print(bold(header("Configuration file didn't exist or was empty. Using default values.\n")))

    return conf

def handle_config_values(conf, lines):
    for l in lines:
        vals = l.split()
        if len(vals) != 2:
            print(warn(f"\nIncorrect configuration syntax for line:\n    \"{l.strip()}\".\nExactly two values\
 are allowed per line, separated by whitespace. Ignoring line.\n"))
            continue

        key, value = vals 
        key_val_text = header(bold(f"[{key}: {value}]"))
        print(f"Read configuration value: {key_val_text}")
        if key == TITLE_FONT_KEY:
            conf.titlefont = value
        elif key == TITLE_COLOR_KEY:
            conf.titlecolor = value
        elif key == TITLE_SIZE_KEY:
            conf.titlesize = int(value)
        elif key == TITLE_SIZE_KEY:
            conf.volfactor = float(value)
        else:
            print(warn(f"\nConfiguration key not recognized, ignoring it: {header(bold(key))} \n"))
    print(ok("\nConfiguration read succesfully.\n"))
    return conf
