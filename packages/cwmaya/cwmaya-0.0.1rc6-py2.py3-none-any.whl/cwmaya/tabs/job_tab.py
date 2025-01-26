# -*- coding: utf-8 -*-

import pymel.core as pm
from cwmaya.tabs.base_tab import BaseTab
from cwmaya.widgets.kv_pairs import KvPairsControl
from cwmaya.widgets.single_option_menu import SingleOptionMenuControl
from cwmaya.widgets.text_area import TextAreaControl
from cwmaya.widgets.text_field import TextFieldControl

class JobTab(BaseTab):
    
    def __init__(self):
        
        self.label_ctl = None
        self.description_ctl = None
        self.metadata_ctl = None
        
        
        super(JobTab, self).__init__()
        self.build_ui()
        
    def build_ui(self):
        """
        Create the frame that contains the job options.
        """
        pm.setParent(self.column)
        frame = pm.frameLayout(label="General")

        self.label_ctl = self.create_label_control(frame)
        self.description_ctl = self.create_description_control(frame)
        self.metadata_ctl = self.create_metadata_control(frame)

    def bind(self, node):
        self.label_ctl.bind(node.attr("label"))
        self.description_ctl.bind(node.attr("description"))
        self.metadata_ctl.bind(node.attr("metadata"))

    def create_label_control(self, parent):
        pm.setParent(parent)
        result = TextFieldControl()
        result.set_label("Job label")
        return result

    def create_description_control(self, parent):
        pm.setParent(parent)
        result = TextAreaControl()
        result.set_label("Description")
        return result


    def create_metadata_control(self, parent):
        pm.setParent(parent)
        pm.frameLayout(label="Metadata")
        result = KvPairsControl()
        return result
