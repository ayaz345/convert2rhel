# -*- coding: utf-8 -*-
#
# Copyright(C) 2016 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import shutil

from convert2rhel.systeminfo import system_info
from convert2rhel.utils import BACKUP_DIR, DATA_DIR


DEFAULT_YUM_REPOFILE_DIR = "/etc/yum.repos.d/"
DEFAULT_YUM_VARS_DIR = "/etc/yum/vars"
DEFAULT_DNF_VARS_DIR = "/etc/dnf/vars"

loggerinst = logging.getLogger(__name__)


def get_rhel_repoids():
    """Get IDs of the Red Hat CDN repositories that correspond to the current system.

    In case the to-be-converted-OS minor version corresponds to RHEL Extended Update Support (EUS) release,
    we preferably enable the RHEL EUS repoids as those provide security updates over two years, in comparison to 6 months
    in case of the standard non-EUS repoids.
    """

    if system_info.corresponds_to_rhel_eus_release():
        repos_needed = system_info.eus_rhsm_repoids
    else:
        repos_needed = system_info.default_rhsm_repoids

    loggerinst.info(f'RHEL repository IDs to enable: {", ".join(repos_needed)}')

    return repos_needed


def backup_yum_repos():
    """Backup .repo files in /etc/yum.repos.d/ so the repositories can be restored on rollback."""
    loggerinst.info(f"Backing up .repo files from {DEFAULT_YUM_REPOFILE_DIR}.")
    repo_files_backed_up = False
    for repo in os.listdir(DEFAULT_YUM_REPOFILE_DIR):
        if repo.endswith(".repo") and repo != "redhat.repo":
            repo_path = os.path.join(DEFAULT_YUM_REPOFILE_DIR, repo)
            shutil.copy2(repo_path, BACKUP_DIR)
            loggerinst.debug(f"Backed up .repo file: {repo_path}")
            repo_files_backed_up = True
    if not repo_files_backed_up:
        loggerinst.info("No .repo files backed up.")
    return


def restore_yum_repos():
    """Rollback all .repo files in /etc/yum.repos.d/ that were backed up."""
    loggerinst.task("Rollback: Restore .repo files to /etc/yum.repos.d/")
    repo_has_restored = False
    for repo in os.listdir(BACKUP_DIR):
        if repo.endswith(".repo"):
            repo_path_from = os.path.join(BACKUP_DIR, repo)
            repo_path_to = os.path.join("/etc/yum.repos.d/", repo)
            shutil.move(repo_path_from, repo_path_to)
            loggerinst.info(f"Restored .repo file: {repo}")
            repo_has_restored = True

    if not repo_has_restored:
        loggerinst.info("No .repo files to rollback")


def get_hardcoded_repofiles_dir():
    """Get the path to the hardcoded repofiles for CentOS/Oracle Linux.

    We use hardcoded original vendor repofiles to be able to check whether the system is updated before the conversion.
    To be able to download backup of packages before we remove them, we can't rely on the repofiles available on
    the system.

    :return: The return can be either the path to the eus repos, or None, meaning we don't have any hardcoded repo files.
    :rtype: str | None
    """
    hardcoded_repofiles = os.path.join(
        DATA_DIR,
        f"repos/{system_info.id}-{system_info.version.major}.{system_info.version.minor}",
    )
    return hardcoded_repofiles if os.path.exists(hardcoded_repofiles) else None


def backup_varsdir():
    """Backup varsdir folder in /etc/{yum,dnf}/vars so the variables can be restored on rollback."""

    def _backup_variables(path):
        """Helper internal function to backup the variables.

        :parameter path: The path for the original variable.
        :type path: str
        """
        variable_files_backed_up = False
        backup_dir = os.path.join(BACKUP_DIR, path.rsplit("/etc/")[-1])
        for variable in os.listdir(path):
            variable_path = os.path.join(path, variable)
            # Create the directory if it doesn't exist
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            shutil.copy2(variable_path, backup_dir)
            loggerinst.debug(f"Backed up variable file: {variable_path}")
            variable_files_backed_up = True

        if not variable_files_backed_up:
            loggerinst.info("No variables files backed up.")

    loggerinst.info(f"Backing up variables files from {DEFAULT_YUM_VARS_DIR}.")
    _backup_variables(path=DEFAULT_YUM_VARS_DIR)

    if system_info.version.major == 8:
        loggerinst.info(f"Backing up variables files from {DEFAULT_DNF_VARS_DIR}.")
        _backup_variables(path=DEFAULT_DNF_VARS_DIR)
    return


def restore_varsdir():
    """Rollback all variables files in /etc/{yum,dnf}/vars that were backed up."""

    def _restore_varsdir(path):
        """Helper internal function to restore the variables.

        :parameter path: The path for the original variable.
        :type path: str
        """
        variables_is_restored = False
        backup_dir = os.path.join(BACKUP_DIR, path.rsplit("/etc/")[-1])

        if not os.path.exists(backup_dir):
            loggerinst.warning("Couldn't find backup directory at %s.", backup_dir)
            return

        for variable in os.listdir(backup_dir):
            variable_path_from = os.path.join(backup_dir, variable)
            variable_path_to = os.path.join(path, variable)

            shutil.move(variable_path_from, variable_path_to)
            loggerinst.info(f"Restored variable file: {variable}")
            variables_is_restored = True

        if not variables_is_restored:
            loggerinst.info("No varaibles files to rollback")

    loggerinst.task("Rollback: Restore variable files to %s", DEFAULT_YUM_VARS_DIR)
    _restore_varsdir(DEFAULT_YUM_VARS_DIR)

    if system_info.version.major == 8:
        loggerinst.task("Rollback: Restore variable files to %s", DEFAULT_DNF_VARS_DIR)
        _restore_varsdir(DEFAULT_DNF_VARS_DIR)
