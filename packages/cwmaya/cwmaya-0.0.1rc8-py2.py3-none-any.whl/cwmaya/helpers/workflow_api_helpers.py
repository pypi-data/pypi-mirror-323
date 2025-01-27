import json
import os
from contextlib import contextmanager

import pymel.core as pm

@contextmanager
def save_scene():
    """
    A context manager to save the current scene before executing the block of code.

    Yields:
        None: Yields control back to the context block after saving the scene.

    Usage Example:
    ```
    with save_scene():
        # Perform actions that require the scene to be saved
    ```
    """
    try:
        if pm.isModified():
            filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
            entries = pm.fileDialog2(
                caption="Save File As",
                okCaption="Save As",
                fileFilter=filters,
                dialogStyle=2,
                fileMode=0,
                dir=os.path.dirname(pm.sceneName()),
            )
            if entries:
                filepath = entries[0]
                pm.saveAs(filepath)
        yield
    except Exception as err:
        pm.displayError(str(err))
    finally:
        pass
