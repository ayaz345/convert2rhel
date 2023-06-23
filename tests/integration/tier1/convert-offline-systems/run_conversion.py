from envparse import env


def test_convert_offline_systems(convert2rhel):
    """Test converting systems not connected to the Internet but requiring sub-mgr (e.g. managed by Satellite)."""

    with convert2rhel(f'-y --no-rpm-va -k {env.str("SATELLITE_KEY")} -o {env.str("SATELLITE_ORG")} --keep-rhsm --debug') as c2r:
        pass
    assert c2r.exitstatus == 0
