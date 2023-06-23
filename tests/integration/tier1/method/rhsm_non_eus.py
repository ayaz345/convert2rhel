import pytest

from envparse import env


@pytest.mark.rhsm_non_eus_account_conversion
def test_rhsm_non_eus_account(convert2rhel):
    """
    Verify that Convert2RHEL is working properly when EUS repositories are not available for conversions
    to RHEL EUS minor versions (8.6, ...) and there are the correct
    repositories attached to the system after the conversion.
    """

    # Mark the system so the check for the enabled repos after the conversion handles this special case
    with open("/non_eus_repos_used", mode="a"):
        pass

    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} --username {env.str("RHSM_USERNAME")} --password {env.str("RHSM_PASSWORD")} --pool {env.str("RHSM_NON_EUS_POOL")} --debug') as c2r:
        c2r.expect("WARNING - Some repositories are not available: rhel-8-for-x86_64-baseos-eus-rpms")
        c2r.expect("WARNING - Some repositories are not available: rhel-8-for-x86_64-appstream-eus-rpms")
        c2r.expect("Conversion successful!")
    assert c2r.exitstatus == 0
