# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pymel.core as pm
import os

import webbrowser
import importlib
import logging

from cwmaya.windows import about_window, window
from cwmaya.helpers import reloader
from cwmaya.logger_config import configure_logger

logger = configure_logger()

MAYA_PARENT_WINDOW = "MayaWindow"
COREWEAVE_MENU = "CoreWeaveMenu"
CONDUCTOR_DOCS = "https://docs.conductortech.com/"
COREWEAVE_SUBMISSION_NODE = "cwSubmission"


def unload():

    if pm.menu(COREWEAVE_MENU, q=True, exists=True):
        pm.menu(COREWEAVE_MENU, e=True, deleteAllItems=True)
        pm.deleteUI(COREWEAVE_MENU)


def load():
    unload()
    CoreWeaveMenu()


class CoreWeaveMenu(object):
    def __init__(self):

        if not pm.about(batch=True):
            pm.setParent(MAYA_PARENT_WINDOW)

            self.menu = pm.menu(COREWEAVE_MENU, label="CoreWeave", tearOff=True)

            pm.menuItem(label="Storm Window", command=pm.Callback(show_storm_window))

            pm.menuItem(divider=True)
            
            pm.menuItem(label="Log level", subMenu=True)
            pm.radioMenuItemCollection()
            pm.menuItem(label="Debug", radioButton=False, command=pm.Callback(set_log_level, logging.DEBUG))
            pm.menuItem(label="Info", radioButton=True, command=pm.Callback(set_log_level, logging.INFO))
            pm.menuItem(label="Warning", radioButton=False, command=pm.Callback(set_log_level, logging.WARNING))
            pm.menuItem(label="Error", radioButton=False, command=pm.Callback(set_log_level, logging.ERROR))
            pm.menuItem(label="Critical", radioButton=False, command=pm.Callback(set_log_level, logging.CRITICAL))
            
            pm.setParent(self.menu, menu=True)

            pm.menuItem(divider=True)

            self.help_menu = pm.menuItem(
                label="Help",
                command=pm.Callback(webbrowser.open, CONDUCTOR_DOCS, new=2),
            )
            self.about_menu = pm.menuItem(
                label="About", command=pm.Callback(about_window.show)
            )

def set_log_level(level):
    logger.setLevel(level)
    print(f"Log level set to {level}")
    logger.debug("Debug test message")
    logger.info("Info test message")
    logger.warning("Warning test message")
    logger.error("Error test message")
    logger.critical("Critical test message")

def show_storm_window():
    if os.environ.get("CWMAYA_RELOAD_FOR_DEVELOPMENT"):
        importlib.reload(reloader)
        importlib.reload(window)
    window.StormWindow()
