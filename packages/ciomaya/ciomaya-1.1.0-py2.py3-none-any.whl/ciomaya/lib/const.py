import re
import os
AE_TEXT_WIDTH = 145
AE_SINGLE_WIDTH = 70
AE_TOTAL_WIDTH = AE_TEXT_WIDTH + (AE_SINGLE_WIDTH * 5)
SUPPRESS_EXTRA_ATTS = [
    "useCustomRange",
    "useScoutFrames",
    "doScrape",
    "output",
    "pluginSoftware",
    "instanceTypeName",
    "title",
    "projectName",
    "startFrame",
    "endFrame",
    "byFrame",
    "customRange",
    "scoutFrames",
    "locationTag",
]
USE_FIXTURES = True

CURRENT_LAYER = 0
LAYERS_ONE_JOB = 1
JOB_PER_LAYER = 2


POLICY_EXCLUSIVE = 0
POLICY_PREPEND = 1
POLICY_APPEND = 2
ENV_POLICIES = [
    "exclusive",
    "prepend",
    "append"
]


DEFAULT_TEMPLATE = 'Render -r <Renderer> -s <start> -e <end> -b <step> -rl "<RenderLayer>" -rd "<OutputPath>"  -proj "<WorkspacePath>" "<SceneFile>"'
DEFAULT_DESTINATION_DIR_TEMPLATE = "<ImagesPath>"
OTHER_TEMPLATES = [
    'Render -r <Renderer>  -ai:lve 3 -s <start> -e <end> -b <step> -rl "<RenderLayer>" -rd "<OutputPath>"  -proj "<WorkspacePath>" "<SceneFile>"'
]


DEFAULT_TITLE = "Maya:<Renderer> - <Scene> <RenderLayer>"
DEFAULT_AUTOSAVE_TEMPLATE = "cio_<Scene>"

DEFAULT_INSTANCE_TYPE = "n1-standard-4"
MAX_TASKS = int(os.environ.get("CONDUCTOR_MAX_TASKS", 1000))
