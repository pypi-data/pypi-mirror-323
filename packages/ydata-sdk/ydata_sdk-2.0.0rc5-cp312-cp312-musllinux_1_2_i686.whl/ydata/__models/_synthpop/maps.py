"""File with the utils methods for the definition of the synthpop model."""
from enum import Enum

from ydata.__models._synthpop._methods import (CARTMethod, EmptyMethod, NormMethod, NormRankMethod, PerturbMethod,
                                               PolyregMethod, SampleMethod, SeqCARTMethod, SeqEmptyMethod)
from ydata.__models._synthpop._utils import generate_function_map
from ydata.utils.data_types import DataType


class SYNTHPOP_FLAVOR(Enum):  # noqa: N801
    TAB = 0, "Tabular"
    SEQ = 1, "Sequential"


NAME_TO_FLAVOR = {"Synthpop": SYNTHPOP_FLAVOR.TAB,
                  "SeqSynthpop": SYNTHPOP_FLAVOR.SEQ}


# Possible DataTypes that Synthpop can handle
# TODO: We should define the enabled types at the method level!
ENABLED_DATATYPES = {
    SYNTHPOP_FLAVOR.TAB: [DataType.NUMERICAL, DataType.DATE, DataType.CATEGORICAL, DataType.STR],
    SYNTHPOP_FLAVOR.SEQ: [DataType.NUMERICAL, DataType.DATE, DataType.CATEGORICAL, DataType.STR],
}


class BaseMethods(Enum):
    """Default list of methods.

    These methods are not directly available to Synthpop flavors. Most
    methods should be similar between all Synthpop flavors. However, in
    case it cannot be the case for technical reasons, we can override
    the method with a flavor-specific one. This prevented regression as
    a bug introduced in a specific flavor operator will not be
    propagated to another flavor silently. It also allows for
    experimentation and side-by-side comparison of methods.
    """

    EMPTY = 0, EmptyMethod
    SAMPLE = 1, SampleMethod
    CART = 2, CARTMethod
    NORM = 3, NormMethod
    NORMRANK = 4, NormRankMethod
    POLYREG = 5, PolyregMethod
    PARAMETRIC = 6, None  # None functions should be defined later
    # XGBOOST = 7, "xgboost", XGBMethod
    PERTURB = 8, PerturbMethod
    SEQ_EMPTY = 9, SeqEmptyMethod
    SEQ_CART = 10, SeqCARTMethod

    @property
    def id(self):
        return self.value[0]

    @property
    def function(self):
        return self.value[1]


# It is possible to override each base method at data type level.
# In particular, method for which 'function' is None should define a function per type define in ENABLED_DATATYPES.
DATATYPE_TO_FUNCTION = {
    BaseMethods.PARAMETRIC: {
        DataType.NUMERICAL: NormRankMethod,
        DataType.DATE: NormRankMethod,
        DataType.CATEGORICAL: PolyregMethod,
        DataType.STR: PolyregMethod,
    }
}

# Define the list of methods available for each Synthpop flavor.
ENABLED_METHODS = {
    SYNTHPOP_FLAVOR.TAB: {
        "empty": BaseMethods.EMPTY,
        "sample": BaseMethods.SAMPLE,
        "cart": BaseMethods.CART,
        "norm": BaseMethods.NORM,
        "normrank": BaseMethods.NORMRANK,
        "polyreg": BaseMethods.POLYREG,
        "parametric": BaseMethods.PARAMETRIC,
        "perturb": BaseMethods.PERTURB,
    },
    SYNTHPOP_FLAVOR.SEQ: {
        "empty": BaseMethods.SEQ_EMPTY,
        "sample": BaseMethods.SAMPLE,
        "cart": BaseMethods.SEQ_CART,
        "norm": BaseMethods.NORM,
        "normrank": BaseMethods.NORMRANK,
        "polyreg": BaseMethods.POLYREG,
        "parametric": BaseMethods.PARAMETRIC,
        "perturb": BaseMethods.PERTURB,
    },
}

# Create the Enum from the list of enabled method for type checking and user-friendly interface
METHODS_MAP = {
    k: Enum("Methods", list(map(str.upper, list(methods.keys()))))
    for k, methods in ENABLED_METHODS.items()
}


# Create the final mapping:
#     1. Flavor
#         2. Method
#             3. Type -> Function
METHOD_TO_TYPE_TO_FUNCTION = {
    k: generate_function_map(
        base_methods=ENABLED_METHODS[k],
        method_to_enum=METHODS_MAP[k],
        enabled_datatypes=ENABLED_DATATYPES[k],
        datatype_to_function=DATATYPE_TO_FUNCTION,
    )
    for k in SYNTHPOP_FLAVOR
}

INIT_METHODS_MAP = {
    SYNTHPOP_FLAVOR.TAB: ["sample"],
    SYNTHPOP_FLAVOR.SEQ: ["empty", "perturb"],
}

DEFAULT_METHODS_MAP = {
    SYNTHPOP_FLAVOR.TAB: ["cart", "parametric"],
    SYNTHPOP_FLAVOR.SEQ: ["cart", "parametric"],
}

NA_METHODS = [
    BaseMethods.SAMPLE,
    BaseMethods.CART,
    BaseMethods.NORM,
    BaseMethods.NORMRANK,
    BaseMethods.POLYREG,
]


class Smoothing(Enum):
    NA = "NA"
    DENSITY = "density"


# TODO: cont_to_cat_methods_map
