import pytest

from envparse import env


@pytest.mark.rhsm_conversion
def test_run_conversion(convert2rhel):
    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} --username {env.str("RHSM_USERNAME")} --password {env.str("RHSM_PASSWORD")} --pool {env.str("RHSM_POOL")} --debug') as c2r:
        c2r.expect("Conversion successful!")
    assert c2r.exitstatus == 0
