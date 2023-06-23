from envparse import env


def test_removed_pkgs_centos_85(convert2rhel, shell):
    assert shell("rpm -qi subscription-manager-initial-setup-addon").returncode == 0

    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} --username {env.str("RHSM_USERNAME")} --password {env.str("RHSM_PASSWORD")} --pool {env.str("RHSM_POOL")} --debug') as c2r:
        c2r.expect("Conversion successful!")
    assert c2r.exitstatus == 0
