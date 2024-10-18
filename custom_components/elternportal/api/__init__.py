"""Elternprotal API."""

from __future__ import annotations

import aiohttp
import bs4
import datetime
import logging
import pytz
import re
import socket
import urllib.parse

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.exceptions import HomeAssistantError
from ..const import (
    CONF_SCHOOL,
    CONF_REGISTER_START_MIN,
    CONF_REGISTER_START_MAX,
    CONF_SECTION_APPOINTMENTS,
    CONF_SECTION_LESSONS,
    CONF_SECTION_LETTERS,
    CONF_SECTION_POLLS,
    CONF_SECTION_REGISTERS,
    CONF_SECTION_SICKNOTES,
    DEFAULT_REGISTER_START_MIN,
    DEFAULT_REGISTER_START_MAX,
    DEFAULT_SECTION_APPOINTMENTS,
    DEFAULT_SECTION_LESSONS,
    DEFAULT_SECTION_LETTERS,
    DEFAULT_SECTION_POLLS,
    DEFAULT_SECTION_REGISTERS,
    DEFAULT_SECTION_SICKNOTES,
)

_LOGGER = logging.getLogger(__name__)

BeautifulSoupParser = "html5lib"

FACHS = [
    {
        "Kurz": "Eth",
        "Name": "Ethik",
    },
    {
        "Kurz": "D",
        "Name": "Deutsch",
    },
    {
        "Kurz": "E",
        "Name": "Englisch",
    },
    {
        "Kurz": "M",
        "Name": "Mathematik",
    },
    {
        "Kurz": "NuT",
        "Name": "Natur und Technik",
    },
    {
        "Kurz": "Geo",
        "Name": "Geographie",
    },
    {
        "Kurz": "Ku",
        "Name": "Kunst",
    },
    {
        "Kurz": "Mu",
        "Name": "Musik",
    },
    {
        "Kurz": "Sw",
        "Name": "Sport",
    },
]

LEHRERS = [
    {
        "Kurz": "FIE",
        "Anrede": "Frau",
        "Titel": "Dr.",
        "Vorname": "Sonja",
        "Nachname": "Fiedler",
    },
    {
        "Kurz": "FIL",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Wolfgang",
        "Nachname": "Filser",
    },
    {
        "Kurz": "HAU",
        "Anrede": "Frau",
        "Titel": "",
        "Vorname": "Magdalena",
        "Nachname": "Haug",
    },
    {
        "Kurz": "KFM",
        "Anrede": "Frau",
        "Titel": "",
        "Vorname": "Franziska",
        "Nachname": "Kaufmann",
    },
    {
        "Kurz": "KEL",
        "Anrede": "Frau",
        "Titel": "",
        "Vorname": "Verena",
        "Nachname": "Keller",
    },
    {
        "Kurz": "ROT",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Nils",
        "Nachname": "Roth",
    },
    {
        "Kurz": "STÖ",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Daniel",
        "Nachname": "Stöhr",
    },
    {
        "Kurz": "WEI",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Christian",
        "Nachname": "Weiß",
    },
]


class ResolveHostnameError(HomeAssistantError):
    """Error to indicate we cannot resolve the hostname."""


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class BadCredentialsError(HomeAssistantError):
    """Error to indicate there are bad credentials."""


class PupilListError(HomeAssistantError):
    """Error to indicate there are no pupils."""


class ElternPortalAPI:
    """API to retrieve the data."""

    def __init__(self):
        """Initialize the API."""
        self.session = None
        self.timezone = pytz.timezone("Europe/Berlin")

    async def async_set_config_data(self, config_data):
        """Initialize the config data."""

        #_LOGGER.debug(f"config_data={config_data}")
        self.school = config_data.get(CONF_SCHOOL).lower().strip()
        self.username = config_data.get(CONF_USERNAME).lower().strip()
        self.password = config_data.get(CONF_PASSWORD).strip()

        self.school = (
            self.school.removeprefix("http://")
            .removeprefix("https://")
            .removesuffix(".eltern-portal.de")
        )
        self.hostname = f"{self.school}.eltern-portal.org"
        self.base_url = f"https://{self.hostname}"
        #self.timezone = await aiozoneinfo.async_get_time_zone("Europe/Berlin")

    async def async_set_option_data(self, option_data):
        """Initialize the option data."""

        #_LOGGER.debug(f"option_data={option_data}")
        self.section_appointments = option_data.get(
            CONF_SECTION_APPOINTMENTS, DEFAULT_SECTION_APPOINTMENTS
        )
        self.section_lessons = option_data.get(
            CONF_SECTION_LESSONS, DEFAULT_SECTION_LESSONS
        )
        self.section_letters = option_data.get(
            CONF_SECTION_LETTERS, DEFAULT_SECTION_LETTERS
        )
        self.section_polls = option_data.get(CONF_SECTION_POLLS, DEFAULT_SECTION_POLLS)
        self.section_registers = option_data.get(
            CONF_SECTION_REGISTERS, DEFAULT_SECTION_REGISTERS
        )
        self.section_sicknotes = option_data.get(
            CONF_SECTION_SICKNOTES, DEFAULT_SECTION_SICKNOTES
        )

        # REGISTERS (Klassenbuch)
        self.register_start_min = option_data.get(
            CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN
        )
        self.register_start_max = option_data.get(
            CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX
        )

    async def async_school_name(self) -> str | None:
        """Elternportal school name."""

        school_name: str = None
        async with aiohttp.ClientSession(self.base_url) as session:
            async with session.get("/") as response:
                # _LOGGER.debug(f"status={response.status}")
                html = await response.text()
                soup = bs4.BeautifulSoup(html, BeautifulSoupParser)
                tag = soup.find("h2", {"id": "schule"})
                school_name = tag.get_text()
                # _LOGGER.debug(f"school_name={school_name}")
                self.school_name = school_name
        return school_name

    async def async_validate_config_data(self):

        try:
            _LOGGER.debug(f"socket.gethostbyname {self.hostname}")
            socket.gethostbyname(self.hostname)
        except socket.gaierror:
            _LOGGER.exception(f"Cannot resolve hostname({self.hostname})")
            raise ResolveHostnameError(
                f"The hostname {self.hostname} cannot be resolved."
            )

        async with aiohttp.ClientSession(self.base_url) as self.session:
            await self.async_base()
            await self.async_login()
            await self.async_logout()

    async def async_update(self) -> None:
        """Elternportal start page."""

        offline = False
        if offline:
            _LOGGER.debug(f"ElternPortalAPI.async_update (offline)")
            self.pupils = {
                "demo": {
                    "id": "demo",
                    "fullname": "Erika Mustermann (1a)",
                    "firstname": "Erika",
                    "lastname": "Mustermann",
                    "class": "1a",
                    "native_value": 0,
                    "appointments": [],
                    "lessons": [],
                    "letters": [],
                    "polls": [],
                    "registers": [],
                    "sicknotes": [],
                }
            }
            self.last_update = datetime.datetime.now()
            return

        _LOGGER.debug(f"ElternPortalAPI.async_update")

        async with aiohttp.ClientSession(self.base_url) as self.session:

            await self.async_base()
            await self.async_login()

            for pupil in self.pupils.values():
                self.pupil_id = pupil["id"]
                await self.async_set_child()

                count = 0
                if self.section_appointments:
                    await self.async_appointment()
                    count += len(pupil["appointments"])

                if self.section_lessons:
                    await self.async_lesson()
                    count += len(pupil["lessons"])

                if self.section_letters:
                    await self.async_letter()
                    count += len(pupil["letters"])

                if self.section_polls:
                    await self.async_poll()
                    count += len(pupil["polls"])

                if self.section_registers:
                    await self.async_register()
                    count += len(pupil["registers"])

                if self.section_sicknotes:
                    await self.async_sicknote()
                    count += len(pupil["sicknotes"])

                pupil["native_value"] = count
                pupil["last_update"] = datetime.datetime.now()

            await self.async_logout()
            self.last_update = datetime.datetime.now()

    async def async_base(self) -> None:
        """Elternportal base."""

        url = "/"
        _LOGGER.debug(f"base.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"base.status={response.status}")
            html = await response.text()

            if "Dieses Eltern-Portal existiert nicht" in html:
                raise CannotConnectError(
                    f"The elternportal {self.base_url} does not exist, most likely you have entered the name of the school incorrectly."
                )
            else:
                soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

                tag = soup.find("input", {"name": "csrf"})
                csrf = tag["value"]
                # _LOGGER.debug(f"csrf={csrf}")
                self.csrf = csrf

                tag = soup.find("h2", {"id": "schule"})
                school_name = tag.get_text()
                # _LOGGER.debug(f"school_name={school_name}")
                self.school_name = school_name

    async def async_login(self) -> None:
        """Elternportal login."""

        url = "/includes/project/auth/login.php"
        _LOGGER.debug(f"login.url={url}")
        login_data = {
            "csrf": self.csrf,
            "username": self.username,
            "password": self.password,
            "go_to": "",
        }
        async with self.session.post(url, data=login_data) as response:
            if response.status!=200:
                _LOGGER.debug(f"login.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            tag = soup.select_one(".pupil-selector")
            if tag is None:
                raise BadCredentialsError()

            pupils = {}
            tags = soup.select(".pupil-selector select option")
            if not tags:
                raise PupilListError()

            for tag in tags:
                pupil_id = tag["value"]
                fullname = tag.get_text()
                try:
                    match = re.search(r"^(\S+)\s+(.*)\s+\((\S+)\)$", fullname)
                    firstname = match[1]
                    lastname = match[2]
                    classname = match[3]
                except:
                    firstname = f"PID{pupil_id}"
                    lastname = None
                    classname = None

                pupil = {
                    "id": pupil_id,
                    "fullname": fullname,
                    "firstname": firstname,
                    "lastname": lastname,
                    "class": classname,
                    "native_value": 0,
                    "appointments": [],
                    "lessons": [],
                    "letters": [],
                    "polls": [],
                    "registers": [],
                    "sicknotes": [],
                }
                pupils[pupil_id] = pupil

            self.pupils = pupils

    async def async_set_child(self) -> None:
        """Elternportal set child."""

        url = "/api/set_child.php?id=" + self.pupil_id
        _LOGGER.debug(f"set_child.url={url}")
        async with self.session.post(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"set_child.status={response.status}")

    async def async_appointment(self) -> None:
        """Elternportal appointment."""

        url = "/api/ws_get_termine.php"
        _LOGGER.debug(f"appointment.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"appointment.status={response.status}")

            appointments = []
            json = await response.json(
                content_type="text/html"
            )  # process malformed JSON response
            for result in json["result"]:
                start = int(str(result["start"])[0:-3])
                start = datetime.datetime.fromtimestamp(start, self.timezone).date()
                end = int(str(result["end"])[0:-3])
                end = datetime.datetime.fromtimestamp(end, self.timezone).date()

                appointment = {
                    "id": result["id"],
                    "title": result["title"],
                    "short": result["title_short"],
                    "class": result["class"],
                    "start": start,
                    "end": end,
                }
                appointments.append(appointment)

            self.pupils[self.pupil_id]["appointments"] = appointments

    async def async_lesson(self) -> None:
        """Elternportal lesson."""

        url = "/service/stundenplan"
        _LOGGER.debug(f"lesson.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"lesson.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            lessons = []
            table_rows = soup.select("#asam_content div.table-responsive table tr")
            for table_row in table_rows:
                table_cells = table_row.select("td")

                if len(table_cells) == 6:
                    # Column 0
                    content = table_cells[0].get_text()
                    lines = table_cells[0].find_all(string=True)
                    number = lines[0] if len(lines) > 0 else ""
                    time = lines[1] if len(lines) > 1 else ""

                    # Column 1-5: Monday to Friday
                    for weekday in range(1, 5):
                        span = table_cells[weekday].select_one("span span")
                        if span is not None:
                            lines = span.find_all(string=True)
                            subject = lines[0].strip() if len(lines) > 0 else ""
                            room = lines[1].strip() if len(lines) > 1 else ""

                            if subject != "":
                                lesson = {
                                    "weekday": weekday,
                                    "number": number,
                                    "subject": subject,
                                    "room": room,
                                }
                                lessons.append(lesson)

            self.pupils[self.pupil_id]["lessons"] = lessons

    async def async_letter(self) -> None:
        """Elternportal letter."""

        letters = []
        url = "/aktuelles/elternbriefe"
        _LOGGER.debug(f"letter.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"letter.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            tags = soup.select(".link_nachrichten")
            for tag in tags:
                try:
                    match = re.search(r"\d+", tag.get("onclick"))
                    lid = match[0]
                except:
                    lid = "0"

                try:
                    attachment = tag.name == "a"
                except:
                    attachment = False

                try:
                    match = re.search(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}", tag.get_text())
                    sent = datetime.datetime.strptime(match[0], "%d.%m.%Y %H:%M:%S")
                    sent = self.timezone.localize(sent)
                except:
                    sent = None

                try:
                    cell = soup.find("td", {"id": "empf_" + lid})
                    new = cell.get_text() == "Empfang noch nicht bestätigt."
                    try:
                        cell2 = cell.find_previous_sibling()
                        number = cell2.get_text()
                    except:
                        number = "0"
                except:
                    new = True
                    number = "0"

                try:
                    cell = tag.find("h4")
                    subject = cell.get_text()
                except:
                    subject = None

                try:
                    cell = tag.parent

                    try:
                        span = cell.select_one("span[style='font-size: 8pt;']")
                        text = span.get_text()
                        liste = text.split("Klasse/n: ")
                        liste = [x for x in liste if x]
                        verteiler = ", ".join(liste)
                    except:
                        verteiler = None

                    try:
                        lines = cell.find_all(string=True)

                        description = ""
                        skip = True
                        for i in range(1, len(lines)):
                            line = lines[i].replace("\r", "").replace("\n", "")
                            if not skip:
                                description += line + "\n"
                            if line.startswith("Klasse/n: "):
                                skip = False
                    except:
                        description = None

                except:
                    verteiler = None
                    description = None

                letter = {
                    "id": lid,
                    "number": number,
                    "attachment": attachment,
                    "sent": sent,
                    "new": new,
                    "subject": subject,
                    "verteiler": verteiler,
                    "description": description,
                }
                letters.append(letter)

        self.pupils[self.pupil_id]["letters"] = letters

    async def async_poll(self) -> None:
        """Elternportal poll."""

        polls = []
        url = "/aktuelles/umfragen"
        _LOGGER.debug(f"poll.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"poll.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            try:
                base_tag = soup.find("base")
                baseurl = base_tag["href"] if base_tag else url
            except:
                baseurl = ""

            rows = soup.select("#asam_content div.row.m_bot")
            for row in rows:
                try:
                    tag = row.select_one("div div:nth-child(1) a.umf_list")
                    title = tag.get_text()
                    href = urllib.parse.urljoin(baseurl, tag["href"])
                except:
                    title = None
                    href = None

                try:
                    tag = row.select_one("div div:nth-child(1) a[title='Anhang']")
                    attachment = tag is not None
                except:
                    attachment = False

                try:
                    tag = row.select_one("div div:nth-child(2)")
                    match = re.search(r"\d{2}\.\d{2}\.\d{4}", tag.get_text())
                    end = datetime.datetime.strptime(match[0], "%d.%m.%Y").date()
                except:
                    end = None

                try:
                    tag = row.select_one("div div:nth-child(3)")
                    match = re.search(r"\d{2}\.\d{2}\.\d{4}", tag.get_text())
                    vote = datetime.datetime.strptime(match[0], "%d.%m.%Y").date()
                except:
                    vote = None

                if href is None:
                    detail = None
                else:
                    async with self.session.get(href) as response2:
                        html2 = await response2.text()
                        soup2 = bs4.BeautifulSoup(html2, BeautifulSoupParser)

                        try:
                            div2 = soup2.select_one(
                                "#asam_content form.form-horizontal div.form-group:nth-child(3)"
                            )
                            detail = div2.get_text()
                        except:
                            detail = None

                poll = {
                    "title": title,
                    "href": href,
                    "attachment": attachment,
                    "vote": vote,
                    "end": end,
                    "detail": detail,
                }
                polls.append(poll)

        self.pupils[self.pupil_id]["polls"] = polls

    async def async_register(self) -> None:
        """Elternportal register."""

        registers = []
        date_current = datetime.date.today() + datetime.timedelta(
            days=self.register_start_min
        )
        date_until = datetime.date.today() + datetime.timedelta(
            days=self.register_start_max
        )
        while date_current <= date_until:

            url = "/service/klassenbuch?cur_date=" + date_current.strftime("%d.%m.%Y")
            _LOGGER.debug(f"register.url={url}")
            async with self.session.get(url) as response:
                if response.status!=200:
                    _LOGGER.debug(f"register.status={response.status}")
                html = await response.text()
                soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

                tags = soup.select("#asam_content table.table.table-bordered")
                for tag in tags:
                    table_cells = tag.select("th")
                    content = table_cells[1].get_text() if len(table_cells) > 1 else ""
                    subject = None
                    subject_short = None
                    teacher = None
                    teacher_short = None
                    lesson = None
                    substitution = False
                    match = re.search(
                        r"(.*) - Lehrkraft: (.*) \((Einzel|Doppel)stunde(, Vertretung)?\)",
                        content,
                    )
                    if match is not None:
                        subject = match[1].replace("Fach: ", "")
                        teacher = match[2]
                        lesson = (
                            match[3]
                            .replace("Einzel", "single")
                            .replace("Doppel", "double")
                        )
                        substitution = match[4] is not None

                    for fach in FACHS:
                        if fach["Name"] == subject:
                            subject_short = fach["Kurz"]

                    for lehrer in LEHRERS:
                        if lehrer["Anrede"] + " " + lehrer["Nachname"] == teacher:
                            teacher_short = lehrer["Kurz"]
                        if (
                            lehrer["Anrede"]
                            + " "
                            + lehrer["Titel"]
                            + " "
                            + lehrer["Nachname"]
                            == teacher
                        ):
                            teacher_short = lehrer["Kurz"]

                    table_cells = tag.select("td")
                    rtype = table_cells[0].get_text() if len(table_cells) > 0 else ""
                    rtype = rtype.replace("Hausaufgabe", "homework")

                    lines = table_cells[1].find_all(string=True)
                    description = lines[0] if len(lines) > 0 else ""

                    if description != "Keine Hausaufgabe eingetragen.":
                        date_completion = date_current
                        if len(lines) > 2:
                            match = re.search(r"\d{2}\.\d{2}\.\d{4}", lines[2])
                            if match is not None:
                                date_completion = datetime.datetime.strptime(
                                    match[0], "%d.%m.%Y"
                                ).date()

                        register = {
                            "subject": subject,
                            "subject_short": subject_short,
                            "teacher": teacher,
                            "teacher_short": teacher_short,
                            "lesson": lesson,
                            "substitution": substitution,
                            "type": rtype,
                            "start": date_current,
                            "completion": date_completion,
                            "description": description,
                        }
                        registers.append(register)

            date_current += datetime.timedelta(days=1)

        self.pupils[self.pupil_id]["registers"] = registers

    async def async_sicknote(self) -> None:
        """Elternportal sick note."""

        sicknotes = []
        url = "/meldungen/krankmeldung"
        _LOGGER.debug(f"sicknote.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"sicknote.status={response.status}")
            html = await response.text()

            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            rows = soup.select("#asam_content table.ui.table tr")
            for row in rows:
                cells = row.select("td")

                # link, query
                try:
                    tag = cells[0].find("a")
                    link = tag["href"]
                except TypeError:
                    link = None

                result = urllib.parse.urlparse(link)
                query = urllib.parse.parse_qs(result.query)
                # _LOGGER.debug(f"query={query}")

                # date_from
                try:
                    df = int(query["df"][0])
                    date_from = datetime.datetime.fromtimestamp(
                        df, self.timezone
                    ).date()
                except KeyError:
                    try:
                        lines = cells[1].find_all(string=True)
                        match = re.search(r"\d{2}\.\d{2}\.\d{4}", lines[0])
                        date_from = datetime.datetime.strptime(
                            match[0], "%d.%m.%Y"
                        ).date()
                    except TypeError:
                        date_from = None
                # _LOGGER.debug(f"date_from={date_from}")

                # date_to
                try:
                    dt = int(query["dt"][0])
                    date_to = datetime.datetime.fromtimestamp(dt, self.timezone).date()
                except KeyError:
                    date_to = date_from
                # _LOGGER.debug(f"date_to={date_to}")

                try:
                    comment = str(query["k"][0])
                except KeyError:
                    try:
                        comment = cells[2].get_text()
                    except IndexError:
                        comment = None
                # _LOGGER.debug(f"comment={comment}")

                sicknote = {
                    "date_from": date_from,
                    "date_to": date_to,
                    "comment": comment,
                }
                # _LOGGER.debug(f"sicknote={sicknote}")
                sicknotes.append(sicknote)

        self.pupils[self.pupil_id]["sicknotes"] = sicknotes

    async def async_logout(self) -> None:
        """Elternportal logout."""

        url = "/logout"
        _LOGGER.debug(f"logout.url={url}")
        async with self.session.get(url) as response:
            if response.status!=200:
                _LOGGER.debug(f"logout.status={response.status}")
