import os
import maya.cmds as cmds

import cwmaya.helpers.const as k
from cwmaya.template.helpers.scrapers import scrape_maya


def scrape_all(node):
    """Scrape all assets."""
    assets = scrape_maya_assets(node)
    assets += scrape_remote_module(node)
    return assets


def scrape_maya_assets(node):
    """Scrape Maya assets."""
    return scrape_maya.run(node)


def scrape_remote_module(node):
    """Scrape the remote tools."""
    modpath = cmds.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    packagedir = os.path.dirname(modpath)
    remotemodule = os.path.join(packagedir, "storm_remote")
    return [remotemodule]
