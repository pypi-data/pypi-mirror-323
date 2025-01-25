from typing import Final
from volworld_common.api.CA import CA


# ====== A: Attribute ======
class AA(CA):
    Account: Final[str] = "aco"
    AppBar: Final[str] = "ab"

    Bar: Final[str] = "bar"
    Bean: Final[str] = "ben"
    BottomAppBar: Final[str] = "btmab"

    CheckBox: Final[str] = "chkbx"
    Circle: Final[str] = "cce"

    Dialog: Final[str] = "dlg"

    Edit: Final[str] = "edt"
    Editor: Final[str] = "edr"
    ElementR: Final[str] = "elmr"
    ElementG: Final[str] = "elmg"
    ElementB: Final[str] = "elmb"
    ElementY: Final[str] = "elmy"
    ElementV: Final[str] = "elmv"
    Existing: Final[str] = "extg"

    Filled: Final[str] = "fld"

    Gold: Final[str] = "g"

    Image: Final[str] = "img"

    LearnerRefWf: Final[str] = "lwf"
    LearnerSaLogId: Final[str] = "lrsalid"
    Left: Final[str] = "lft"
    Link: Final[str] = "lnk"
    Load: Final[str] = "lod"
    Logout: Final[str] = "lgo"

    Memorized: Final[str] = "mmd"
    Menu: Final[str] = "mu"
    MoreActions: Final[str] = "mact"

    NextPage: Final[str] = "nxp"

    PreviousPage: Final[str] = "prp"

    QuestWfCycleId: Final[str] = "qwcid"
    QuestWfCycleElmId: Final[str] = "qwcelmId"

    Resource: Final[str] = "res"

    Slot: Final[str] = "slt"
    SoulSpark: Final[str] = "solspk"
    Switch: Final[str] = "sth"

    To: Final[str] = "to"
    Token: Final[str] = "tk"

    Waiting: Final[str] = "wtg"
    WordIndexList: Final[str] = "windlst"
    WordLearningState: Final[str] = "wls"
    WordSimilarity: Final[str] = "wsmy"
    WordTags: Final[str] = "wtgs"

AAList = [AA, CA]
