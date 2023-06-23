import pytest

from envparse import env


@pytest.mark.activation_key_conversion
def test_activation_key_conversion(convert2rhel):
    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} -k {env.str("RHSM_KEY")} -o {env.str("RHSM_ORG")} --debug') as c2r:
        c2r.expect("Conversion successful!")
    assert c2r.exitstatus == 0
