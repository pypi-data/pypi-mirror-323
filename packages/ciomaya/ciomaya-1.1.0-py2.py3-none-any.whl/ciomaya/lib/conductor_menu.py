from __future__ import unicode_literals
import pymel.core as pm

import os
import glob
import webbrowser
import importlib
import ciocore.loggeria

# Setup logging
ciocore.loggeria.setup_conductor_logging(
    logger_level =  ciocore.loggeria.LEVEL_MAP.get(ciocore.config.get()['log_level']),
    log_filename="conductor_maya.log",
 )

from ciomaya.lib import about_window
from ciomaya.lib import software
from ciomaya.lib import const as k
from ciomaya.lib import node_utils

MAYA_PARENT_WINDOW = "MayaWindow"
CONDUCTOR_MENU = "ConductorMenu"
CONDUCTOR_DOCS = "https://docs.conductortech.com/"
LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
DEFAULT_LOG_LEVEL = LOG_LEVELS[2]
CONDUCTOR_RENDER_NODE = "conductorRender"


def unload():

    if pm.menu(CONDUCTOR_MENU, q=True, exists=True):
        pm.menu(CONDUCTOR_MENU, e=True, deleteAllItems=True)
        pm.deleteUI(CONDUCTOR_MENU)


def load():
    unload()
    ConductorMenu()


class ConductorMenu(object):
    def __init__(self):
        if not pm.about(batch=True):
            pm.setParent(MAYA_PARENT_WINDOW)
            self.menu = pm.menu(
                CONDUCTOR_MENU,
                label="Conductor",
                tearOff=True,
                pmc=pm.Callback(self.post_menu_command),
            )
            self.jobs_menu = pm.menuItem(label="Submitter", subMenu=True)

            pm.setParent(self.menu, menu=True)

            pm.menuItem(divider=True)

            pm.setParent(self.menu, menu=True)

            pm.menuItem(divider=True)

            self.help_menu = pm.menuItem(
                label="Help",
                command=pm.Callback(webbrowser.open, CONDUCTOR_DOCS, new=2),
            )
            self.about_menu = pm.menuItem(
                label="About", command=pm.Callback(about_window.show)
            )

    def post_menu_command(self):
        """
        Build the Select/Create submenu just before the menu is opened.
        """
        pm.setParent(self.jobs_menu, menu=True)
        pm.menu(self.jobs_menu, edit=True, deleteAllItems=True)
        for j in pm.ls(type=CONDUCTOR_RENDER_NODE):

            pm.menuItem(
                label="Select {}".format(str(j)),
                command=pm.Callback(select_and_show, j),
            )
        pm.menuItem(divider=True)

        pm.menuItem(label="Create", command=pm.Callback(create_render_node))
        pm.setParent(self.menu, menu=True)


def create_render_node():
    node = pm.createNode(CONDUCTOR_RENDER_NODE)

    setup_render_node(node)
    select_and_show(node)


def select_and_show(node):
    pm.select(node)

    if not pm.mel.isAttributeEditorRaised():
        pm.mel.openAEWindow()


def setup_render_node(node):

    node.attr("hostSoftware").set(software.detect_host())

    # TODO: Combine with sw detect code in AEsoftware
    i = 0
    for plugin_software_name in [
        sw
        for sw in [
            software.detect_mtoa(),
            software.detect_rfm(),
            software.detect_vray(),
            software.detect_redshift(),
            software.detect_yeti(),
        ]
        if sw
    ]:
        node.attr("pluginSoftware")[i].set(plugin_software_name)
        i += 1

    node.attr("destinationDirectory").set(k.DEFAULT_DESTINATION_DIR_TEMPLATE)
    node.attr("taskTemplate").set(k.DEFAULT_TEMPLATE)
    node.attr("autosaveTemplate").set(k.DEFAULT_AUTOSAVE_TEMPLATE)
    node.attr("instanceTypeName").set(k.DEFAULT_INSTANCE_TYPE)
    node.attr("title").set(k.DEFAULT_TITLE)

    node.attr("customRange").set("1-10")
    node.attr("scoutFrames").set("auto:3")

    node_utils.ensure_connections(node)

    # asset scrapers
    script_path = os.path.join(
        pm.moduleInfo(path=True, moduleName="conductor"), "scripts"
    )

    files = sorted(glob.glob("{}/scrape_*.py".format(script_path)))
    for i, scraper in enumerate(files):
        scraper_name = os.path.splitext(os.path.basename(scraper))[0]
        nodeattr = node.attr("assetScrapers")[i]
        nodeattr.attr("assetScraperName").set(scraper_name)
        try:
            scraper_module = importlib.import_module(scraper_name)
            if hasattr(scraper_module, "EXPERIMENTAL") and scraper_module.EXPERIMENTAL:
                nodeattr.attr("assetScraperActive").set(False)
        except BaseException:
            nodeattr.attr("assetScraperActive").set(False)

