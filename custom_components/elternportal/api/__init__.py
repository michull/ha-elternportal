"""Elternprotal API."""

from __future__ import annotations

import aiohttp
import logging
import datetime
import re
import pytz

from bs4 import BeautifulSoup
from requests import Session

_LOGGER = logging.getLogger(__name__)

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

    def __init__(self, school: str, username: str, password: str):
        """Initialize the API."""

        self.school = school
        self.username = username
        self.password = password
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
                soup = BeautifulSoup(html, "html.parser")                
                tag = soup.find("h2", {"id": "schule"})
                school_name = tag.get_text()
                #_LOGGER.debug(f"school_name={school_name}")
                self.school_name = school_name                
        return school_name

    async def async_update(self) -> None:
        """Elternportal start page."""
        
        _LOGGER.debug(f"ElternPortalAPI.async_online")
        async with aiohttp.ClientSession(self.base_url) as self.session:

            await self.async_base()
            await self.async_login()
                
            for pupil in self.pupils.values():
                self.pupil_id = pupil["id"]
                await self.async_set_child()
                await self.async_aktuelles_elternbriefe()
                await self.async_service_klassenbuch()
                await self.async_service_stundenplan()
                # await self.async_service_termine()
                await self.async_ws_termine()

                pupil = self.pupils[self.pupil_id]
                native_value = len(pupil["letters"]) + len(pupil["registers"])
                self.pupils[self.pupil_id]["native_value"] = native_value

            await self.async_logout()
            self.last_update = datetime.datetime.now()

    async def async_base(self) -> None:
        """Elternportal base."""

        url = "/"
        _LOGGER.debug(f"base.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"base.status={response.status}")
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")                

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
            soup = BeautifulSoup(html, "html.parser")

            pupils = {}
            tags = soup.select(".pupil-selector select option")
            for tag in tags:
                #_LOGGER.debug(tag)
                pupil_id = tag["value"]
                fullname = tag.get_text()
                firstname = None
                lastname = None
                classname = None
                match = re.search(r"(.*) (.*) \((.*)\)", fullname)
                if match is not None:
                    firstname = match[1]
                    lastname = match[2]
                    classname = match[3]
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
                }
                pupils[pupil_id] = pupil
                    
            self.pupils = pupils

    async def async_set_child(self) -> None:
        """Elternportal set child."""

        url = "/api/set_child.php?id=" + self.pupil_id;
        _LOGGER.debug(f"set_child.url={url}")
        async with self.session.post(url) as response:
            _LOGGER.debug(f"set_child.status={response.status}")

    async def async_aktuelles_elternbriefe(self) -> None:
        """Elternportal aktuelles elternbriefe."""

        letters = []
        url = "/aktuelles/elternbriefe"
        _LOGGER.debug(f"elternbriefe.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"elternbriefe.status={response.status}")
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

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

    async def async_service_klassenbuch(self) -> None:
        """Elternportal service klassenbuch."""

        registers = []
        date_current = datetime.date.today() - datetime.timedelta(days=7)
        while date_current <= datetime.date.today():

            url = "/service/klassenbuch?cur_date=" + date_current.strftime("%d.%m.%Y")
            _LOGGER.debug(f"klassenbuch.url={url}")
            async with self.session.get(url) as response:
                _LOGGER.debug(f"klassenbuch.status={response.status}")
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

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

    async def async_service_stundenplan(self) -> None:
        """Elternportal service stundenplan."""
        
        url = "/service/stundenplan"
        _LOGGER.debug(f"stundenplan.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"stundenplan.status={response.status}")
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

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

    async def async_service_termine(self) -> None:
        """Elternportal service termine."""
        
        url = "/service/termine/liste"
        _LOGGER.debug(f"termine.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"termine.status={response.status}")
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            appointments = []
            table_rows = soup.select("#asam_content .table2 tr")
            for table_row in table_rows:
                #_LOGGER.debug(f"table_row={table_row}")
                table_cells = table_row.select("td")
                        
                if len(table_cells)==3:
                    # Column 0 (date)
                    date = None
                    match = re.search(r"\d{2}\.\d{2}\.\d{4}", table_cells[0].get_text())
                    if match is not None:
                        date = datetime.datetime.strptime(match[0], "%d.%m.%Y").date()
                        #date = self.timezone.localize(date)

                    # Column 2 (subject)
                    subject = table_cells[2].get_text()

                    if date is not None:
                        appointment = {
                            "date": date,
                            "subject": subject
                        }
                        appointments.append(appointment)
                        _LOGGER.debug(f"appointment={appointment}")

            self.pupils[self.pupil_id]["appointments"] = appointments

    async def async_ws_termine(self) -> None:
        """Elternportal webservice termine."""
        
        url = "/api/ws_get_termine.php"
        _LOGGER.debug(f"termine.url={url}")
        async with self.session.get(url) as response:
            _LOGGER.debug(f"termine.status={response.status}")

            json = await response.json(content_type="text/html") # process malformed JSON response
            success = json["success"]
            results = json["result"]

            appointments = []
            for result in results:
                start = int(str(result["start"])[0:-3])
                start = datetime.datetime.fromtimestamp(start, self.timezone)
                end = int(str(result["end"])[0:-3])
                end = datetime.datetime.fromtimestamp(end, self.timezone)

                # day events ends after 78400s instead of 86400s

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
