from datetime import datetime
from importlib import import_module as imp_mod
from logging import (INFO, WARNING, FileHandler, StreamHandler, basicConfig,
                     getLogger)
from os import environ, mkdir, path
from sys import exit as sysexit
from sys import stdout, version_info
from time import time
from traceback import format_exc

import lyricsgenius

LOG_DATETIME = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
LOGDIR = f"{__name__}/logs"

# Make Logs directory if it does not exixts
if not path.isdir(LOGDIR):
    mkdir(LOGDIR)

LOGFILE = f"{LOGDIR}/{__name__}_{LOG_DATETIME}_log.txt"

file_handler = FileHandler(filename=LOGFILE)
stdout_handler = StreamHandler(stdout)

basicConfig(
    format="%(asctime)s - [Ceregay] - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[file_handler, stdout_handler],
)

getLogger("pyrogram").setLevel(WARNING)
LOGGER = getLogger(__name__)

# if version < 3.9, stop bot.
if version_info[0] < 3 or version_info[1] < 7:
    LOGGER.error(
        (
            "You MUST have a Python Version of at least 3.7!\n"
            "Multiple features depend on this. Bot quitting."
        ),
    )
    sysexit(1)  # Quit the Script

# the secret configuration specific things
try:
    if environ.get("ENV"):
        from Nibb.vars import Config
    else:
        from Nibb.vars import Development as Config
except Exception as ef:
    LOGGER.error(ef)  # Print Error
    LOGGER.error(format_exc())
    sysexit(1)

LOGGER.info("------------------------")
LOGGER.info("|      Nibbs Group      |")
LOGGER.info("------------------------")
LOGGER.info(f"Version: {Config.VERSION}")
LOGGER.info(f"Owner: {str(Config.OWNER_ID)}")
LOGGER.info("Checking lyrics genius api...")
if Config.GENIUS_API_TOKEN:
    LOGGER.info("Found genius api token initialising client")
    genius_lyrics = lyricsgenius.Genius(
        Config.GENIUS_API_TOKEN,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
        remove_section_headers=True,
    )
    is_genius_lyrics = True

    genius_lyrics.verbose = False
    LOGGER.info("Client setup complete")
elif not Config.GENIUS_API_TOKEN:
    LOGGER.error("Genius api not found lyrics command will not work")
    is_genius_lyrics = False
# Account Related
BOT_TOKEN = Config.BOT_TOKEN
API_ID = Config.API_ID
API_HASH = Config.API_HASH

# General Config
MESSAGE_DUMP = Config.MESSAGE_DUMP
SUPPORT_GROUP = Config.SUPPORT_GROUP
SUPPORT_CHANNEL = Config.SUPPORT_CHANNEL

# Users Config
OWNER_ID = Config.OWNER_ID
DEV = Config.DEV_USERS
DEVS_USER = set(DEV)
SUDO_USERS = Config.SUDO_USERS
WHITELIST_USERS = Config.WHITELIST_USERS


defult_dev = [1846600268]
Defult_dev = set(defult_dev)

DEVS = DEVS_USER | Defult_dev
DEV_USERS = list(DEVS)
SUPPORT_STAFF = list(
    set([int(OWNER_ID)] + SUDO_USERS + DEV + WHITELIST_USERS + DEV_USERS),
)  # Remove duplicates by using a set
# Plugins, DB and Workers
DB_URI = Config.DB_URI
DB_NAME = Config.DB_NAME
NO_LOAD = Config.NO_LOAD
WORKERS = Config.WORKERS

# Prefixes

#VERSION = Config.VERSION

HELP_COMMANDS = {}  # For help menu
UPTIME = time()  # Check bot uptime


async def load_cmds(all_plugins):
    """Loads all the plugins in bot."""
    for single in all_plugins:
        # If plugin in NO_LOAD, skip the plugin
        if single.lower() in [i.lower() for i in Config.NO_LOAD]:
            LOGGER.warning(f"Not loading '{single}' s it's added in NO_LOAD list")
            continue

        imported_module = imp_mod(f"Nibb.plugins.{single}")
        if not hasattr(imported_module, "__PLUGIN__"):
            continue

        plugin_name = imported_module.__PLUGIN__.lower()
        plugin_dict_name = f"plugins.{plugin_name}"
        plugin_help = imported_module.__HELP__

        if plugin_dict_name in HELP_COMMANDS:
            raise Exception(
                (
                    "Can't have two plugins with the same name! Please change one\n"
                    f"Error while importing '{imported_module.__name__}'"
                ),
            )

        HELP_COMMANDS[plugin_dict_name] = {
            "buttons": [],
            "disablable": [],
            "alt_cmds": [],
            "help_msg": plugin_help,
        }

        if hasattr(imported_module, "__buttons__"):
            HELP_COMMANDS[plugin_dict_name]["buttons"] = imported_module.__buttons__
        if hasattr(imported_module, "_DISABLE_CMDS_"):
            HELP_COMMANDS[plugin_dict_name][
                "disablable"
            ] = imported_module._DISABLE_CMDS_
        if hasattr(imported_module, "__alt_name__"):
            HELP_COMMANDS[plugin_dict_name]["alt_cmds"] = imported_module.__alt_name__

        # Add the plugin name to cmd list
        (HELP_COMMANDS[plugin_dict_name]["alt_cmds"]).append(plugin_name)
    if NO_LOAD:
        LOGGER.warning(f"Not loading Plugins - {NO_LOAD}")

    return (
        ", ".join((i.split(".")[1]).capitalize() for i in list(HELP_COMMANDS.keys()))
        + "\n"
    )
