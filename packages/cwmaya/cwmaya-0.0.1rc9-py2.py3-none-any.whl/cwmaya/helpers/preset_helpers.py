# -*- coding: utf-8 -*-

import pymel.core as pm
import os
import cwmaya.helpers.const as k
import shutil
from cwmaya.logger_config import configure_logger

logger = configure_logger()

def save_preset(node, preset=None):
    """
    Save the current state of the node as a preset.
    """
    logger.debug(f"Attempting to save preset for node: {node}")
    if not preset:
        preset = prompt_for_preset_name()
    if not preset:
        logger.info("No preset name provided or invalid name, cancelling save")
        return

    try:
        pm.nodePreset(save=(node, preset))
        logger.info(f"Successfully saved preset: {preset} for node: {node}")
    except Exception as e:
        logger.error(f"Failed to save preset {preset} for node {node}: {str(e)}")
        raise

def load_preset(node, preset, dialog=None):
    """
    Load the specified preset onto the node.
    """
    logger.debug(f"Attempting to load preset: {preset} onto node: {node}")
    try:
        pm.nodePreset(load=(node, preset))
        logger.info(f"Successfully loaded preset: {preset} onto node: {node}")
        if dialog:
            logger.debug("Updating dialog with loaded template")
            dialog.load_template(node)
    except Exception as e:
        logger.error(f"Failed to load preset {preset} onto node {node}: {str(e)}")
        raise

def prompt_for_preset_name():
    """
    Prompt the user for a preset name.
    """
    logger.debug("Prompting user for preset name")
    result = pm.promptDialog(
        title='Save Preset',
        message='Enter Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if not (result == 'OK'):
        logger.debug("User cancelled preset name prompt")
        return None
    
    preset = pm.promptDialog(query=True, text=True)
    if not pm.nodePreset(isValidName=preset):
        logger.warning(f"Invalid preset name provided: {preset}")
        pm.error("Invalid preset name")
        return None
    
    logger.debug(f"User provided valid preset name: {preset}")
    return preset

def install_presets(force=False):
    """
    Install the presets that the developer has set up and included in the distribution.
    
    Should include a default preset for each node type, so that the new nodes are hydrated on creation.
    
    Only presets if that don't already exist in the user's presets folder.
    """
    logger.info(f"Installing presets (force={force})")
    logger.info(f"Module name: {k.MODULE_NAME}")
    mod_path = pm.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    
    logger.info(f"Module path: {mod_path}")
    mod_presets_folder = os.path.join(mod_path, "presets")
    logger.info(f"Module presets folder: {mod_presets_folder}")
    presets_folder = pm.internalVar(userPresetsDir=True)
    logger.info(f"User presets folder: {presets_folder}")
    
    logger.info(f"Module presets folder: {mod_presets_folder}")
    logger.info(f"User presets folder: {presets_folder}")
    
    # copy contents from mod_presets_folder to presets_folder unless they already exist
    some_presets_exist = False
    try:
        for file in os.listdir(mod_presets_folder):
            fn = os.path.join(mod_presets_folder, file)
            if not os.path.isfile(fn):
                logger.debug(f"Skipping non-file: {fn}")
                continue
                
            dest_path = os.path.join(presets_folder, file)
            if force or not os.path.exists(dest_path):
                logger.debug(f"Copying preset: {file}")
                try:
                    shutil.copy(fn, presets_folder)
                    logger.info(f"Successfully installed preset: {file}")
                except Exception as e:
                    logger.error(f"Failed to copy preset {file}: {str(e)}")
            else:
                logger.debug(f"Preset already exists: {file}")
                if not pm.about(batch=True):
                    some_presets_exist = True
    except Exception as e:
        logger.error(f"Failed to process presets folder: {str(e)}")
        raise
        
    if some_presets_exist:
        msg = "Some storm presets already exist and won't be copied to your prefs. If you want to force install the presets, open Storm Tools and go to Tools->Force install factory presets."
        logger.info(msg)
        print(msg)
            
def copy_presets_to_module(destination=None):
    """
    Copy the presets from the user's presets folder to the module's presets folder.
    
    This is not exposed to users, and is for the benefit of developers who want to copy their presets to the module for distribution.
    """
    logger.info("Copying presets to module")
    
    mod_path = pm.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    if not destination:
        mod_presets_folder = os.path.join(mod_path, "presets")
    else:
        mod_presets_folder = destination
        
    presets_folder = pm.internalVar(userPresetsDir=True)
    logger.debug(f"Source presets folder: {presets_folder}")
    logger.debug(f"Destination folder: {mod_presets_folder}")
    
    try:
        for file in os.listdir(presets_folder):
            fn = os.path.join(presets_folder, file)
            if os.path.isfile(fn):
                try:
                    shutil.copy(fn, mod_presets_folder)
                    logger.info(f"Successfully copied preset: {file}")
                except Exception as e:
                    logger.error(f"Failed to copy preset {file}: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to process presets folder: {str(e)}")
        raise
