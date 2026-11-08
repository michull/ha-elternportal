"""Extensions of the pyelternportal API for the elternportal integration."""

from __future__ import annotations

import html as html_lib
import re
from typing import Any
from urllib import parse

import aiohttp

from pyelternportal import CannotConnectException, ElternPortalAPI

from .const import LOGGER


_RE_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
_RE_TAG = re.compile(r"<[^>]+>")
_RE_SPACE = re.compile(r"\s+")


def clean_html_text(text: str | None) -> str | None:
    """Remove html line breaks / tags and normalize whitespace."""
    if not text:
        return text
    text = _RE_BR.sub(" ", text)
    text = _RE_TAG.sub("", text)
    text = html_lib.unescape(text)
    return _RE_SPACE.sub(" ", text).strip()


class ElternPortalAPIExt(ElternPortalAPI):
    """ElternPortalAPI with a robust login and cleaned appointment titles."""

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

    async def async_appointment_parse(self, appointments: Any) -> None:
        """Remove html line breaks from appointment titles."""
        await super().async_appointment_parse(appointments)
        for appointment in self._student.appointments:
            appointment.title = clean_html_text(appointment.title)
            appointment.short = clean_html_text(appointment.short)
