import logging
import re
import subprocess

import typer
import typer.main

REALM = "APPLECONNECT.APPLE.COM"
LDAP_URL = "ldap://nod.apple.com"

logger = logging.getLogger('amp-ds-platform-cli')


class AppleConnect:
    def authenticate(self) -> str:
        """Uses appleconnect to authenticate user and return its username.

        :return: str
        """
        cmd = ['appleconnect', 'a', '--realm', REALM, '-show-signIn-dialog']
        logger.debug('appleconnect authenticate command: {}'.format(cmd))

        apc_output = subprocess.run(cmd, check=True, capture_output=True, text=True)

        auth_success = re.search("Success: (.+)@(.+) signed in", apc_output.stdout)

        if not auth_success:
            typer.echo("Authentication failed!")
            raise typer.Exit(1)

        username = auth_success.group(1)

        return username


class AppleDirectory:
    def user_belongs_to_group(self, username: str) -> bool:
        """Checks if user belongs to desired group.

        :param username: username returned by appleconnect
        :return: bool
        """
        cmd = ['ldapsearch', '-LLL', '-x', '-H', LDAP_URL, '-b',
               'cn=groups,dc=apple,dc=com', 'cn=amp-ds-platform-team', 'memberUid']
        logger.debug('ldapsearch find group command: {}'.format(cmd))

        ldap_output = subprocess.run(cmd, check=True, capture_output=True, text=True)

        users_in_group = [line.split(' ')[1] for line in ldap_output.stdout.splitlines()[1:] if len(line)]
        user_belongs_to_group = username in users_in_group

        return user_belongs_to_group


def auth_callback(ctx: typer.Context) -> None:
    """Callback function to enforce authentication in all CLI commands.

    :param ctx: typer Context
    :return: None
    """
    username = AppleConnect().authenticate()
    user_belongs_to_group = AppleDirectory().user_belongs_to_group(username=username)
    if not user_belongs_to_group:
        typer.echo("Authentication failed!", err=True)
        raise typer.Exit(1)
