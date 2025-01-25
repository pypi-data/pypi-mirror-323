import sys


def myfunc(*args, **kwargs):
    return True


module = type(sys)("mymodule")
module.myfunc = myfunc
sys.modules["mymodule"] = module
