import maya.api.OpenMaya as om
from cwmaya.template.helpers import attribute_factory as attrs
from cwmaya.template.helpers import environment
from cwmaya.template.helpers import context as ctx
from cwstorm.dsl.task import Task
from cwstorm.dsl.cmd import Cmd


def initialize(longPrefix, shortPrefix, outputPlug):
    """Create the static attributes for the export column."""
    result = {}

    result["label"] = attrs.makeStringAttribute(
        f"{longPrefix}Label", f"{shortPrefix}lb"
    )

    commands = attrs.makeCommandsAttribute(
        f"{longPrefix}Commands", f"{shortPrefix}cm", array=True
    )
    result["commands"] = commands["compound"]
    result["commandsArgv"] = commands["argv"]

    environment = attrs.makeKvPairsAttribute(
        f"{longPrefix}Environment", f"{shortPrefix}nv"
    )

    result["environment"] = environment["compound"]
    result["environmentKey"] = environment["key"]
    result["environmentValue"] = environment["value"]
    result["extraAssets"] = attrs.makeStringAttribute(
        f"{longPrefix}ExtraAssets", f"{shortPrefix}ea", array=True
    )

    result["output_path"] = attrs.makeStringAttribute(
        f"{longPrefix}OutputPath", f"{shortPrefix}op"
    )

    top_level_attrs = [
        "label",
        "commands",
        "environment",
        "extraAssets",
        "output_path",
    ]
    for attr in top_level_attrs:
        om.MPxNode.addAttribute(result[attr])
        om.MPxNode.attributeAffects(result[attr], outputPlug)

    return result


def getValues(data, task_attrs):
    result = {}

    result["label"] = data.inputValue(task_attrs["label"]).asString()

    result["output_path"] = data.inputValue(task_attrs["output_path"]).asString()


    result["commands"] = []
    commands_handle = data.inputArrayValue(task_attrs["commands"])
    while not commands_handle.isDone():
        argv_handle = commands_handle.inputValue().child(task_attrs["commandsArgv"])
        argv_array_handle = om.MArrayDataHandle(argv_handle)

        argv = []
        while not argv_array_handle.isDone():
            arg = argv_array_handle.inputValue().asString().strip()
            argv.append(arg)
            argv_array_handle.next()
        result["commands"].append(argv)
        commands_handle.next()

    result["environment"] = []
    array_handle = data.inputArrayValue(task_attrs["environment"])
    while not array_handle.isDone():
        key = (
            array_handle.inputValue()
            .child(task_attrs["environmentKey"])
            .asString()
            .strip()
        )
        value = (
            array_handle.inputValue()
            .child(task_attrs["environmentValue"])
            .asString()
            .strip()
        )
        if key and value:
            result["environment"].append({"key": key, "value": value})
        array_handle.next()

    result["extra_assets"] = []
    array_handle = data.inputArrayValue(task_attrs["extraAssets"])
    while not array_handle.isDone():
        path = array_handle.inputValue().asString().strip()
        if path:
            result["extra_assets"].append(path)
        array_handle.next()

    return result


def computeTask(task_values, context=None, env_amendments=[]):
    """Compute the common task."""

    name = ctx.interpolate(task_values["label"], context)
    task = Task(name)

    for argv in task_values["commands"]:
        args = [ctx.interpolate(arg, context) for arg in argv]
        task.push_commands(Cmd(*args))
    env_entries = task_values["environment"] + env_amendments

    env_entries = [
        {"key": entry["key"], "value": ctx.interpolate(entry["value"], context)}
        for entry in env_entries
    ]
 
    env_dict = environment.composeEnvVars(env_entries)
    task.env(env_dict)

    task.lifecycle({"minsec": 0, "maxsec": 3600})
    task.status("open")

    output_path = ctx.interpolate(task_values["output_path"], context)
    task.output_path(output_path)

    return task
