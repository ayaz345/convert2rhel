import re
import socket

from conftest import SATELLITE_PKG_DST, SATELLITE_PKG_URL, SATELLITE_URL
from envparse import env


# Replace urls in rhsm.conf file to the satellite server
# Without doing this we get obsolete dogfood server as source of repositories
def replace_urls_rhsm():
    with open("/etc/rhsm/rhsm.conf", "r+") as f:
        file = f.read()
        # Replacing the urls
        file = re.sub("hostname = .*", f"hostname = {SATELLITE_URL}", file)
        file = re.sub(
            "baseurl = .*",
            f"baseurl = https://{SATELLITE_URL}/pulp/repos",
            file,
        )

        # Setting the position to the top of the page to insert data
        f.seek(0)
        f.write(file)
        f.truncate()


# Configure and limit connection to the satellite server only
def configure_connection():
    satellite_ip = socket.gethostbyname(SATELLITE_URL)

    with open("/etc/dnsmasq.conf", "a") as f:
        # Satellite url
        f.write(f"address=/{SATELLITE_URL}/{satellite_ip}\n")

        # Everything else is resolved to localhost
        f.write("address=/#/127.0.0.1")

    with open("/etc/resolv.conf", "w") as f:
        f.write("nameserver 127.0.0.1")


def test_prepare_system(shell):
    assert shell("yum install dnsmasq wget -y").returncode == 0

    # Install katello package
    assert (
        shell(
            f"wget --no-check-certificate --output-document {SATELLITE_PKG_DST} {SATELLITE_PKG_URL}"
        ).returncode
        == 0
    )
    assert shell(f"rpm -i {SATELLITE_PKG_DST}").returncode == 0

    replace_urls_rhsm()
    shell("rm -rf /etc/yum.repos.d/*")

    # Subscribe system
    assert (
        shell(
            f'subscription-manager register --org={env.str("SATELLITE_ORG")} --activationkey={env.str("SATELLITE_KEY_CENTOS7")}'
        ).returncode
        == 0
    )

    configure_connection()

    assert shell("systemctl enable dnsmasq && systemctl restart dnsmasq").returncode == 0
