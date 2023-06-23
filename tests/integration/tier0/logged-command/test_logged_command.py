import json
import os.path

import pytest


C2R_LOG = "/var/log/convert2rhel/convert2rhel.log"
C2R_FACTS = "/etc/rhsm/facts/convert2rhel.facts"


@pytest.mark.test_logfile_starts_with_command
def test_verify_logfile_starts_with_command(convert2rhel):
    """
    This test verifies, that the command passed to the command line is at the beginning of the log file.
    Also verify, that the passed password is obfuscated.
    """
    # Clean artifacts from previous run
    for artifact in [C2R_LOG, C2R_FACTS]:
        if os.path.exists(artifact):
            os.unlink(artifact)

    serverurl = "subscription.pls.register.me"
    username = "jdoe"
    password = "foobar"
    activation_key = "a-map-of-a-key"
    organization = "SoMe_NumberS-8_a_lettER"

    command_long = f"--debug --no-rpm-va --serverurl {serverurl} --username {username} --password {password} --activationkey {activation_key} --org {organization}"
    command_short = f"--debug --no-rpm-va --serverurl {serverurl} -u {username} -p {password} -k {activation_key} -o {organization}"
    command_verification = (
        f"convert2rhel --debug --no-rpm-va --serverurl {serverurl}"
    )

    commands = [command_long, command_short]

    # Run command twice with both long and short options to verify, the secrets
    # are obfuscated.
    for command in commands:
        with convert2rhel(command) as c2r:
            # We need to get past the data collection acknowledgement.
            c2r.expect("Continue with the system conversion?")
            c2r.sendline("y")

            # After that we can stop the execution.
            c2r.expect("Prepare: Clear YUM/DNF version locks")
            c2r.sendcontrol("c")

        with open(C2R_LOG, "r") as logfile:
            command_line = next(
                (line.strip() for i, line in enumerate(logfile) if i == 1),
                None,
            )
            assert command_verification in command_line
            assert password not in command_line
            assert activation_key not in command_line
            assert username not in command_line
            assert organization not in command_line

        with open(C2R_FACTS, "r") as breadcrumbs:
            data = json.load(breadcrumbs)
            command = data.get("conversions.executed")

            assert password not in command
            assert activation_key not in command
            assert username not in command
            assert organization not in command

        assert c2r.exitstatus != 0
