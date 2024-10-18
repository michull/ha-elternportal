import bs4
import datetime
import geopy
import requests
import json
import socket
import sys
from typing import Final

PATH_JSON: Final[str] = r"..\schools\schools.json"
PATH_MD: Final[str] = r"..\SCHOOLS.md"

month = datetime.date.today().isoformat()[:8]
geolocator = geopy.geocoders.Nominatim(user_agent="api-elternportal")

with open(PATH_JSON, mode="r", encoding="utf-8") as read_file:
    data = json.load(read_file)

for school in sys.argv[1:]:
    if next((s for s in data if s["school"] == school), None) is None:
        data.append({"school": school})

for s in data:
    if "domain" not in s and s["school"] is not None:
        s["domain"] = f"{s["school"]}.eltern-portal.org"

    if "url" not in s and s["domain"] is not None:
        s["url"] = f"https://{s["domain"]}"

    ipcheck = "ip" not in s or "ip_lastcheck" not in s or month not in s["ip_lastcheck"]
    if ipcheck and s["domain"] is not None:
        hostname = s["domain"]
        ip = socket.gethostbyname(hostname)
        print(f"resolve {hostname} to {ip}")
        s["ip"] = ip
        s["ip_lastcheck"] = datetime.date.today().isoformat()

    namecheck = (
        "name" not in s or "name_lastcheck" not in s or month not in s["name_lastcheck"]
    )
    if namecheck and s["url"] is not None:
        response = requests.get(s["url"])
        html = response.content
        if "Dieses Eltern-Portal existiert nicht" in html:
            print(f"resolve {s["url"]} to 'Eltern-Portal existiert nicht'")
            s["exists"] = False
            s["name"] = None
            s["name_lastcheck"] = datetime.date.today().isoformat()
        else:
            soup = bs4.BeautifulSoup(html, "html5lib")
            tag = soup.find("h2", {"id": "schule"})
            name = tag.get_text() if tag is not None else None
            print(f"resolve {s["url"]} to {name}")
            s["exists"] = True
            s["name"] = name
            s["name_lastcheck"] = datetime.date.today().isoformat()

    geocheck = (
        "geo" not in s or "geo_lastcheck" not in s or month not in s["geo_lastcheck"]
    )
    if geocheck and s["name"] is not None:
        name_geo = s["name"] if "name_geo" not in s else s["name_geo"]
        location = geolocator.geocode(
            name_geo, addressdetails=True, language="de", country_codes="de"
        )
        if location is None:
            print(f"resolve {s["name"]} to None")
            geo = None
        else:
            geotype = location.raw["type"]
            address = location.raw["address"]
            if geotype == "school":
                print(f"resolve {s["name"]} to {address["postcode"]}")
                geo = {
                    "type": geotype,
                    "lat": location.raw["lat"],
                    "lon": location.raw["lon"],
                    "name": location.raw["name"],
                    "road": address["road"],
                    "house_number": address.get("house_number"),
                    "postcode": address["postcode"],
                    "city": (
                        address["city"] if "city" in address else address.get("town")
                    ),
                    "country": address["country"],
                }
            else:
                print(f"resolve {s["name"]} to {geotype}")
                geo = {
                    "type": geotype,
                }
        s["geo"] = geo
        s["geo_lastcheck"] = datetime.date.today().isoformat()

with open(PATH_JSON, mode="w", encoding="utf-8") as write_file:
    json.dump(data, write_file, indent=4, sort_keys=True)

with open(PATH_MD, mode="w", encoding="utf-8") as write_file:
    write_file.write("# Known instances of Eltern-Portal\n")
    write_file.write("\n")
    write_file.write("Identifier | Url                                   | School\n")
    write_file.write(
        ":--------- | :------------------------------------ | :-------------------------------------------------------------\n"
    )
    for s in data:
        identifier = s["school"]
        url = s["url"]
        if s["exists"]:
            school = s["name"]
            if "geo" in s and s["geo"] is not None:
                geo = s["geo"]
                if "postcode" in geo and geo["postcode"] is not None:
                    school += ", " + geo["postcode"]
                    if "city" in geo and geo["city"] is not None:
                        school += " " + geo["city"]
                else:
                    if "city" in geo and geo["city"] is not None:
                        school += ", " + geo["city"]
        else:
            school = "[outdated]"

        write_file.write(f"{identifier:<10} | {url:<37} | {school}\n")
    write_file.close
