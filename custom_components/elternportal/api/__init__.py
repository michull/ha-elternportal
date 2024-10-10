"""Elternprotal API."""

from __future__ import annotations

import aiohttp
# from bs4 import BeautifulSoup
import bs4
import datetime
import logging
import pytz
import re
import urllib.parse

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from ..const import (
    CONF_SCHOOL,
    CONF_REGISTER_START_MIN,
    CONF_REGISTER_START_MAX,
    DEFAULT_REGISTER_START_MIN,
    DEFAULT_REGISTER_START_MAX,
)

_LOGGER = logging.getLogger(__name__)

BeautifulSoupParser = "html5lib"

FACHS = [
    {
        "Kürzel": "Eth",
        "Name": "Ethik",
    },
    {
        "Kürzel": "D",
        "Name": "Deutsch",
    },
    {
        "Kürzel": "E",
        "Name": "Englisch",
    },
    {
        "Kürzel": "M",
        "Name": "Mathematik",
    },
    {
        "Kürzel": "NuT",
        "Name": "Natur und Technik",
    },
    {
        "Kürzel": "Geo",
        "Name": "Geographie",
    },
    {
        "Kürzel": "Ku",
        "Name": "Kunst",
    },
    {
        "Kürzel": "Mu",
        "Name": "Musik",
    },
    {
        "Kürzel": "Sw",
        "Name": "Sport",
    },
]

LEHRERS = [
    {
        "Kürzel": "FIE",
        "Anrede": "Frau",
        "Titel": "Dr.",
        "Vorname": "Sonja",
        "Nachname": "Fiedler",
    },
    {
        "Kürzel": "FIL",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Wolfgang",
        "Nachname": "Filser",
    },
    {
        "Kürzel": "HAU",
        "Anrede": "Frau",
        "Titel": "",
        "Vorname": "Magdalena",
        "Nachname": "Haug",
    },
    {
        "Kürzel": "KFM",
        "Anrede": "Frau",
        "Titel": "",
        "Vorname": "Franziska",
        "Nachname": "Kaufmann",
    },
    {
        "Kürzel": "KEL",
        "Anrede": "Frau",
        "Titel": "",
        "Vorname": "Verena",
        "Nachname": "Keller",
    },
    {
        "Kürzel": "ROT",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Nils",
        "Nachname": "Roth",
    },
    {
        "Kürzel": "STÖ",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Daniel",
        "Nachname": "Stöhr",
    },
    {
        "Kürzel": "WEI",
        "Anrede": "Herr",
        "Titel": "",
        "Vorname": "Christian",
        "Nachname": "Weiß",
    },
]

class ElternPortalAPI:
    """API to retrieve the data."""

    def __init__(self, config_data, option_data):
        """Initialize the API."""

        #_LOGGER.debug(f"config_data={config_data}")
        #_LOGGER.debug(f"option_data={option_data}")
        self.school = config_data.get(CONF_SCHOOL)
        self.username = config_data.get(CONF_USERNAME)
        self.password = config_data.get(CONF_PASSWORD)
        self.register_start_min = option_data.get(CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN)
        self.register_start_max = option_data.get(CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX)
        self.base_url = f"https://{self.school}.eltern-portal.org"
        self.timezone = pytz.timezone("Europe/Berlin")
        
        self.school_name = None
        self.pupils = {}
        self.session = None
        self.pupil_id = None
        self.last_update = None
        
    async def async_school_name(self) -> str | None:
        """Elternportal school name."""
        
        school_name: str = None
        async with aiohttp.ClientSession(self.base_url) as session:
            async with session.get("/") as response:
                #_LOGGER.debug(f"status={response.status}")
                html = await response.text()
                soup = bs4.BeautifulSoup(html, BeautifulSoupParser)                
                tag = soup.find("h2", {"id": "schule"})
                school_name = tag.get_text()
                #_LOGGER.debug(f"school_name={school_name}")
                self.school_name = school_name                
        return school_name

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
                await self.async_letter()
                await self.async_sick_note()
                await self.async_register()
                await self.async_lesson()
                await self.async_appointment()

                pupil["native_value"] = len(pupil["appointments"]) + len(pupil["lessons"]) + len(pupil["letters"]) + len(pupil["registers"]) + len(pupil["sicknotes"])
                pupil["last_update"] = datetime.datetime.now()

            await self.async_logout()
            self.last_update = datetime.datetime.now()

    async def async_base(self) -> None:
        """Elternportal base."""

        url = "/"
        _LOGGER.debug(f"base.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"base.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)                

            tag = soup.find("input", {"name": "csrf"})
            csrf = tag["value"]
            #_LOGGER.debug(f"csrf={csrf}")
            self.csrf = csrf
                
            tag = soup.find("h2", {"id": "schule"})
            school_name = tag.get_text()
            #_LOGGER.debug(f"school_name={school_name}")
            self.school_name = school_name

    async def async_login(self) -> None:
        """Elternportal login."""

        url = "/includes/project/auth/login.php"
        _LOGGER.debug(f"login.url={url}")
        login_data = {
            "csrf": self.csrf,
            "username": self.username,
            "password": self.password,
            "go_to": ""
        }        
        async with self.session.post(url, data=login_data) as response:
            _LOGGER.debug(f"login.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            pupils = {}
            tags = soup.select(".pupil-selector select option")
            for tag in tags:
                #_LOGGER.debug(tag)
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
                    "registers": [],
                    "sicknotes": [],
                }
                pupils[pupil_id] = pupil
                    
            self.pupils = pupils

    async def async_set_child(self) -> None:
        """Elternportal set child."""

        url = "/api/set_child.php?id=" + self.pupil_id;
        _LOGGER.debug(f"set_child.url={url}")
        async with self.session.post(url) as response:
            _LOGGER.debug(f"set_child.status={response.status}")

    async def async_letter(self) -> None:
        """Elternportal letter."""

        letters = []
        url = "/aktuelles/elternbriefe"
        _LOGGER.debug(f"letter.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"letter.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            tags = soup.select(".link_nachrichten")
            for tag in tags:
                number = "0"
                match = re.search(r"\d+", tag.get("onclick"))
                if match is not None:
                    number = match[0]

                attachment = tag.get("href") is not None
                        
                sent = None
                match = re.search(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}", tag.get_text())
                if match is not None:
                    sent = datetime.datetime.strptime(match[0], "%d.%m.%Y %H:%M:%S")
                    sent = self.timezone.localize(sent)
                        
                cell = soup.find("td", {"id": "empf_" + number})
                new = cell.get_text() == "Empfang noch nicht bestätigt." if cell is not None else True
    
                cell = tag.find("h4")
                subject = cell.get_text() if cell is not None else ""

                try:
                    cell = tag.parent

                    try:
                        spans = cell.select("span[style='font-size: 8pt;']")
                        text = spans[0].get_text() if len(spans)>0 else None
                        liste = text.split("Klasse/n: ")
                        liste = [x for x in liste if x]
                        verteiler = ", ".join(liste)
                    except:
                        verteiler = None

                    try:
                        lines = cell.find_all(string=True)
                        #_LOGGER.debug(f"lines={lines}")

                        description = ""
                        skip = True
                        for i in range(1,len(lines)):
                            line = lines[i].replace("\r","").replace("\n","")
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

    async def async_sick_note(self) -> None:
        """Elternportal sick note."""

        sicknotes = []
        url = "/meldungen/krankmeldung"
        _LOGGER.debug(f"sicknote.url={url}")
        async with self.session.get(url) as response:
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
                #_LOGGER.debug(f"query={query}")

                # date_from
                try:
                    df = int(query["df"][0])
                    date_from = datetime.datetime.fromtimestamp(df, self.timezone).date()
                except KeyError:
                    try:
                        lines = cells[1].find_all(string=True)
                        match = re.search(r"\d{2}\.\d{2}\.\d{4}", lines[0])
                        date_from = datetime.datetime.strptime(match[0], "%d.%m.%Y").date()
                    except TypeError:
                        date_from = None
                #_LOGGER.debug(f"date_from={date_from}")

                # date_to
                try:
                    dt = int(query["dt"][0])
                    date_to = datetime.datetime.fromtimestamp(dt, self.timezone).date()
                except KeyError:
                    date_to = date_from
                #_LOGGER.debug(f"date_to={date_to}")

                try:
                    comment = str(query["k"][0])
                except KeyError:
                    try:
                        comment = cells[2].get_text()
                    except IndexError:
                        comment = None
                #_LOGGER.debug(f"comment={comment}")

                sicknote = {
                    "date_from": date_from,
                    "date_to": date_to,
                    "comment": comment
                }
                #_LOGGER.debug(f"sicknote={sicknote}")
                sicknotes.append(sicknote)

        self.pupils[self.pupil_id]["sicknotes"] = sicknotes

    async def async_register(self) -> None:
        """Elternportal register."""

        registers = []
        date_current = datetime.date.today() + datetime.timedelta(days=self.register_start_min)
        date_until = datetime.date.today() + datetime.timedelta(days=self.register_start_max)
        while date_current <= date_until:

            url = "/service/klassenbuch?cur_date=" + date_current.strftime("%d.%m.%Y")
            _LOGGER.debug(f"register.url={url}")
            async with self.session.get(url) as response:
                _LOGGER.debug(f"register.status={response.status}")
                html = await response.text()
                soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

                tags = soup.select("#asam_content table.table.table-bordered")
                for tag in tags:
                    #_LOGGER.debug(f"tag={tag}")
                    table_cells = tag.select("th")
                    content = table_cells[1].get_text() if len(table_cells)>1 else ""
                    subject = None
                    subject_short = None
                    teacher = None
                    teacher_short = None
                    lesson = None
                    substitution = False
                    match = re.search(r"(.*) - Lehrkraft: (.*) \((Einzel|Doppel)stunde(, Vertretung)?\)", content)
                    if match is not None:
                        subject = match[1].replace("Fach: ","")
                        teacher = match[2]
                        lesson = match[3].replace("Einzel","single").replace("Doppel","double")
                        substitution = match[4] is not None

                    for fach in FACHS:
                        if fach["Name"]==subject:
                            subject_short = fach["Kürzel"]

                    for lehrer in LEHRERS:
                        if lehrer["Anrede"] + " " + lehrer["Nachname"]==teacher:
                            teacher_short = lehrer["Kürzel"]
                        if lehrer["Anrede"] + " " + lehrer["Titel"] + " " + lehrer["Nachname"]==teacher:
                            teacher_short = lehrer["Kürzel"]

                    table_cells = tag.select("td")
                    rtype = table_cells[0].get_text() if len(table_cells)>0 else ""
                    rtype = rtype.replace("Hausaufgabe","homework")

                    lines = table_cells[1].find_all(string=True)
                    description = lines[0] if len(lines)>0 else ""

                    if description != "Keine Hausaufgabe eingetragen.":
                        date_done = date_current
                        if len(lines)>2:
                            match = re.search(r"\d{2}\.\d{2}\.\d{4}", lines[2])
                            if match is not None:
                                date_done = datetime.datetime.strptime(match[0], "%d.%m.%Y").date()

                        register = {
                            "subject": subject,
                            "subject_short": subject_short,
                            "teacher": teacher,
                            "teacher_short": teacher_short,
                            "lesson": lesson,
                            "substitution": substitution,
                            "type": rtype,
                            "start": date_current,
                            "done": date_done,
                            "description": description,
                        }
                        registers.append(register)

            date_current += datetime.timedelta(days=1)

        self.pupils[self.pupil_id]["registers"] = registers

    async def async_lesson(self) -> None:
        """Elternportal lesson."""
        
        url = "/service/stundenplan"
        _LOGGER.debug(f"lesson.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"lesson.status={response.status}")
            html = await response.text()
            soup = bs4.BeautifulSoup(html, BeautifulSoupParser)

            lessons = []
            table_rows = soup.select("#asam_content div.table-responsive table tr")
            for table_row in table_rows:
                table_cells = table_row.select("td")
                        
                if len(table_cells)==6:
                    # Column 0
                    content = table_cells[0].get_text()
                    lines = table_cells[0].find_all(string=True)
                    number = lines[0] if len(lines)>0 else ""
                    time = lines[1] if len(lines)>1 else ""

                    # Column 1-5: Monday to Friday
                    for weekday in range(1, 5): 
                        span = table_cells[weekday].select_one("span span")
                        if span is not None:
                            lines = span.find_all(string=True)
                            subject = lines[0].strip() if len(lines)>0 else ""
                            room = lines[1].strip() if len(lines)>1 else ""
                                
                            if subject!="":
                                lesson = {
                                    "weekday": weekday,
                                    "number": number,
                                    "subject": subject,
                                    "room": room,
                                }
                                lessons.append(lesson)

            self.pupils[self.pupil_id]["lessons"] = lessons

    async def async_appointment(self) -> None:
        """Elternportal appointment."""
        
        url = "/api/ws_get_termine.php"
        _LOGGER.debug(f"appointment.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"appointment.status={response.status}")

            appointments = []
            json = await response.json(content_type="text/html") # process malformed JSON response
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

    async def async_logout(self) -> None:
        """Elternportal logout."""
        
        url = "/logout"
        _LOGGER.debug(f"logout.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"logout.status={response.status}")
