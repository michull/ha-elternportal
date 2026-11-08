"""Extensions of the pyelternportal API for the elternportal integration."""

from __future__ import annotations

from urllib import parse

import aiohttp

from pyelternportal import CannotConnectException, ElternPortalAPI

from .const import LOGGER


class ElternPortalAPIExt(ElternPortalAPI):
    """ElternPortalAPI with a robust login."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        super().__init__(session)

    def clear_cookies(self) -> None:
        """Drop all cookies of the (dedicated) session."""
        cookie_jar = getattr(self._session, "cookie_jar", None)
        if cookie_jar is not None:
            cookie_jar.clear()

    async def async_base_online(self) -> None:
        """Start every login with a clean session.

        A stale session cookie (e.g. after a failed logout) makes the portal
        return the logged-in start page without a login form (no csrf token).
        """
        self.clear_cookies()
        try:
            await super().async_base_online()
        except CannotConnectException as ex:
            if "csrf" not in str(ex):
                raise
            LOGGER.debug("No csrf token found, logout and retry once")
            try:
                async with self._session.get(
                    parse.urljoin(self.base_url, "/logout")
                ) as response:
                    await response.read()
            except aiohttp.ClientError as logout_ex:
                LOGGER.debug("Logout before retry failed: %s", logout_ex)
            self.clear_cookies()
            await super().async_base_online()
