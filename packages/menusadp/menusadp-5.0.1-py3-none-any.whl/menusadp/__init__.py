# -*- coding: utf-8 -*-

"""Top-level package for menusADP."""
import getpass
from os.path import join as pjoin
from pathlib import Path
from configparser import ConfigParser, ExtendedInterpolation

from appdirs import AppDirs

from menusadp.utils import echo_info, echo_warning, get_binary_info, infos

__version__ = "5.0.1"
__appname__ = "menusadp"


def create_config_file(configfile):
    """create (overwrite if existing) configuration file,
    and return a `config` object
    """
    config = ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
    for chapter, content in DEFAULT_CONFIG.items():
        config[chapter] = content
    with open(configfile, "w") as fh:
        config.write(fh)
        echo_warning('created config file "%s"' % configfile)
    return config


CONFIG_VERSION = "3.0"

PANDOC_BIN, PANDOC_VERSION = get_binary_info("pandoc")
PDFLATEX_BIN, PDFLATEX_VERSION = get_binary_info("pdflatex")

user = getpass.getuser()
dirs = AppDirs(__appname__, user)
userdir = Path(dirs.user_data_dir)
configdir = Path(dirs.user_config_dir)
configfile = configdir / "config.ini"

DEFAULT_CONFIG = dict(
    MISC={
        "config_version": CONFIG_VERSION,
        "pandoc_bin": PANDOC_BIN,
        "pdflatex_bin": PDFLATEX_BIN,
        "index_filename": "index.html",
    },
    PATHS={
        "home_dir": str(userdir),
        "source_dir": pjoin("${home_dir}", "source"),
        "output_dir": pjoin("${home_dir}", "out"),
        "preview_output_dir": pjoin("${home_dir}", "out_preview"),
        "last_valid_data_dir": pjoin("${home_dir}", "last_valids"),
    },
    FILES={"wines_file": "vins.xlsx", "menus_file": "menus.xlsx"},
    LOGGING={
        "log_file": pjoin("${PATHS:home_dir}", "menusadp.log"),
        "console_log_level": "INFO",
        "file_log_level": "DEBUG",
    },
    FTP={
        "upload_url": "",
        "upload_username": "",
        "upload_password": "",
    },
    LAST_VALIDS={"wines": "", "menus": ""},
    LAST_VALIDS_PREVIEW={"wines": "", "menus": ""},
    ASK_MODE={
        "ask_for_prod": "1",
        "default_prod": "1",
        "ask_for_upload": "0",
        "default_upload": "1",
        "ask_for_force": "0",
        "default_force": "0",
    },
    COLORS={
        "defaultcolor": "#000000",
        "adp": "#F7AE70",
        "battleshipgrey": "#848482",
        "darkblue": "#000080",
        "darkgray": "#A9A9A9",
    },
)

# ============================================================================
# manage configuration
# ============================================================================

if configfile.exists():
    configdir.mkdir(parents=True, exist_ok=True)
    # ------------------------------------------------------------------------
    # read existing config
    CONFIG = ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
    CONFIG.read(configfile)
    if float(CONFIG["MISC"].get("config_version", 0.0)) < float(CONFIG_VERSION):
        CONFIG = create_config_file(configfile)
else:
    # ------------------------------------------------------------------------
    # create config
    configdir.mkdir(parents=True, exist_ok=True)
    CONFIG = create_config_file(configfile)

COLORS = dict(CONFIG["COLORS"].items())

if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    infos(CONFIG, configfile=configfile)
