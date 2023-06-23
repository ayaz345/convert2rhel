from conftest import SYSTEM_RELEASE_ENV
from envparse import env


def test_single_yum_transaction(convert2rhel, shell):
    """Run the conversion using the single yum transaction.

    This will run the conversion up until the point of the single yum
    transaction package replacements.
    """
    pkgmanager = "yum"

    if "centos-8" in SYSTEM_RELEASE_ENV or "oracle-8" in SYSTEM_RELEASE_ENV:
        pkgmanager = "dnf"

    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} --username {env.str("RHSM_USERNAME")} --password {env.str("RHSM_PASSWORD")} --pool {env.str("RHSM_POOL")} --debug') as c2r:
        c2r.expect("no modifications to the system will happen this time.", timeout=1200)
        c2r.expect(
            f"Successfully validated the {pkgmanager} transaction set.",
            timeout=600,
        )
        c2r.expect("This process may take some time to finish.", timeout=300)
        c2r.expect("System packages replaced successfully.", timeout=900)
        c2r.expect("Conversion successful!")
    assert c2r.exitstatus == 0
