class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def header(str):
    return f"{bcolors.HEADER}{str}{bcolors.ENDC}"

def warn(str):
    return f"{bcolors.WARNING}{str}{bcolors.ENDC}"

def ok(str):
    return f"{bcolors.OKGREEN}{str}{bcolors.ENDC}"

def blue(str):
    return f"{bcolors.OKBLUE}{str}{bcolors.ENDC}"

def bold(str):
    return f"{bcolors.BOLD}{str}{bcolors.ENDC}"
