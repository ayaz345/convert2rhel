import os

from envparse import env


def test_remove_excluded_pkgs(shell, convert2rhel):
    """
    Ensure Convert2RHEL removes packages, which are specified as excluded_pkgs in config.
    Verification scenarios cover just some packages causing major issues.
    Those are specified in their respective test plan (remove_excluded_pkgs_epel7 and remove_excluded_pkgs_epel8).
    Packages are set as an environment variable.
    """
    packages = os.environ["PACKAGES"]
    assert (
        shell(
            f"yum install -y {packages}",
        ).returncode
        == 0
    )

    # run utility until the reboot
    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} --username {env.str("RHSM_USERNAME")} --password {env.str("RHSM_PASSWORD")} --pool {env.str("RHSM_POOL")} --debug') as c2r:
        pass
    assert c2r.exitstatus == 0

    # check excluded packages were really removed
    assert shell(f"rpm -qi {packages}").returncode != 0
