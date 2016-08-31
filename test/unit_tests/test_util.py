from amazonia.classes.util import detect_unencrypted_access_keys, InsecureVariableError
from nose.tools import *


def test_detect_unencrypted_access_keys():
    """
    Detect unencrypted AWS access ID and AWS secret key
    """
    assert_raises(InsecureVariableError, detect_unencrypted_access_keys,
                  **{'userdata': '9VJrJAil2XtEC/B7g+Y+/Fmerk3iqyDH/UIhKjXk'})

    assert_raises(InsecureVariableError, detect_unencrypted_access_keys,
                  **{'userdata': 'AKI3ISW6DFTLGVWEDYMQ'})
