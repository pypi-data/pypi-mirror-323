from cwmaya.tabs.base_tab import BaseTab


class TaskTab(BaseTab):

    def __init__(self):
        """
        Create the UI.
        """
        # Common task UI
        self.label_ctl = None
        self.commands_ctl = None
        self.extra_assets_ctl = None
        self.environment_ctl = None
        self.output_path_ctl = None

        super(TaskTab, self).__init__()

    def build_ui(self):
        self.label_ctl = self.create_text_control(self.column, "Label")

        self.commands_ctl = self.create_commands_control(self.column)
        self.extra_assets_ctl = self.create_extra_assets_control(self.column)
        self.environment_ctl = self.create_kvpairs_control(self.column, "Environment")
        self.output_path_ctl = self.create_output_path_control(self.column)

    def bind(self, node, prefix):

        if not prefix:
            raise ValueError("prefix must be set.")
        self.label_ctl.bind(node.attr(f"{prefix}Label"))

        self.environment_ctl.bind(node.attr(f"{prefix}Environment"))
        self.extra_assets_ctl.bind(node.attr(f"{prefix}ExtraAssets"))
        self.commands_ctl.bind(node.attr(f"{prefix}Commands"))
        self.output_path_ctl.bind(node.attr(f"{prefix}OutputPath"))
