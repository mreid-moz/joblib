"""
Test the numpy pickler as a replacement of the standard pickler.

"""

from tempfile import mkdtemp
import copy
import shutil
import os

import nose

from .testing_utils import np, with_numpy

# numpy_pickle is not a drop-in replacement of pickle, as it takes
# filenames instead of open files as arguments.
from .. import numpy_pickle as pickle

################################################################################
# Define a list of standard types.
# Borrowed from dill, initial author: Micheal McKerns:
# http://dev.danse.us/trac/pathos/browser/dill/dill_test2.py

typelist = []

# testing types
_none = None; typelist.append(_none)
_type = type; typelist.append(_type)
_bool = bool(1); typelist.append(_bool)
_int = int(1); typelist.append(_int)
_long = long(1); typelist.append(_long)
_float = float(1); typelist.append(_float)
_complex = complex(1); typelist.append(_complex)
_string = str(1); typelist.append(_string)
_unicode = unicode(1); typelist.append(_unicode)
_tuple = (); typelist.append(_tuple)
_list = []; typelist.append(_list)
_dict = {}; typelist.append(_dict)
_file = file; typelist.append(_file)
_buffer = buffer; typelist.append(_buffer)
_builtin = len; typelist.append(_builtin)
class _class:
    def _method(self):
        pass
class _newclass(object):
    def _method(self):
        pass
typelist.append(_class)
typelist.append(_newclass) # <type 'type'>
_instance = _class(); typelist.append(_instance)
_object = _newclass(); typelist.append(_object) # <type 'class'>
def _function(x): yield x; typelist.append(_function)


################################################################################
# Test fixtures

cachedir = None
filename = None

def setup():
    """ Test setup.
    """
    global cachedir, filename
    cachedir = mkdtemp()
    filename = os.path.join(cachedir, 'test.pkl')


def teardown():
    """ Test teardown.
    """
    shutil.rmtree(cachedir)


################################################################################
# Tests

def test_standard_types():
  """ Test pickling and saving with standard types.
  """
  for member in typelist:
      pickle.dump(member, filename)
      _member = pickle.load(filename)
      # We compare the pickled instance to the reloaded one only if it
      # can be compared to a copied one
      if member == copy.deepcopy(member):
          yield nose.tools.assert_equal, member, _member


@with_numpy
def test_numpy_pickling():
    a = np.random.random(10)
    for obj in (a,), (a, a), [a, a, a]:
        filenames = pickle.dump(obj, filename)
        # Check that one file was created per array
        yield nose.tools.assert_equal, len(filenames), len(obj) + 1
        # Check that these files do exist
        for file in filenames:
            yield nose.tools.assert_true, \
                os.path.exists(os.path.join(cachedir, file))

        # Unpickle the object
        obj_ = pickle.load(filename)
        # Check that the items are indeed arrays
        for item in obj_:
            yield nose.tools.assert_true, isinstance(item, np.ndarray)
        # And finally, check that all the values are equal.
        yield nose.tools.assert_true, np.all(np.array(obj) == 
                                             np.array(obj_))


