from conftest import SYSTEM_RELEASE_ENV
from envparse import env


def set_latest_kernel(shell):
    # We need to get the name of the latest kernel
    # present in the repositories

    # Install 'yum-utils' required by the repoquery command
    shell("yum install yum-utils -y")

    # Get the name of the latest kernel
    latest_kernel = shell(
        "repoquery --quiet --qf '%{BUILDTIME}\t%{VERSION}-%{RELEASE}' kernel 2>/dev/null | tail -n 1 | awk '{printf $NF}'"
    ).output

    # Get the full name of the kerenl
    full_name = shell(
        f"""grubby --info ALL | grep \"title=.*{latest_kernel}\" | tr -d '\"' | sed 's/title=//'"""
    ).output

    # Set the latest kernel as the one we want to reboot to
    shell(f"grub2-set-default '{full_name.strip()}'")


def test_non_latest_kernel(shell, convert2rhel):
    """
    System has non latest kernel installed, thus the conversion
    has to be inhibited.
    """

    with convert2rhel(f'-y --no-rpm-va --serverurl {env.str("RHSM_SERVER_URL")} --username {env.str("RHSM_USERNAME")} --password {env.str("RHSM_PASSWORD")} --pool {env.str("RHSM_POOL")} --debug') as c2r:
        if "centos-8" in SYSTEM_RELEASE_ENV:
            c2r.expect(
                "The version of the loaded kernel is different from the latest version in repositories defined in the"
            )
        else:
            c2r.expect(
                "The version of the loaded kernel is different from the latest version in the enabled system repositories."
            )
    assert c2r.exitstatus != 0

    # Clean up, reboot is required after setting the newest kernel
    set_latest_kernel(shell)
