from ics import Calendar, Event
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup


def parse_date_time(date_str, time_str, timezone_str):
    # Convert time strings into datetime objects in the correct time zone
    start_time_str, end_time_str = time_str.split(" - ")
    start_datetime_str = f"{date_str} {start_time_str}"
    end_datetime_str = f"{date_str} {end_time_str}"

    # Use the correct format here
    timezone = pytz.timezone(timezone_str)
    start_datetime = datetime.strptime(start_datetime_str, "%B %d, %Y %I:%M %p")
    end_datetime = datetime.strptime(end_datetime_str, "%B %d, %Y %I:%M %p")

    # Localize the datetime objects to the specified timezone
    start_datetime = timezone.localize(start_datetime)
    end_datetime = timezone.localize(end_datetime)

    return start_datetime, end_datetime


def scrape_food_truck_data(location_name, address, url, timezone_str):
    events = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    schedules = soup.find_all("div", class_="schedule-info")

    for schedule in schedules:
        event = Event()
        truck_name = schedule.find("h3", class_="truck-name").get_text(strip=True)
        date = schedule.find("div", class_="date").get_text(strip=True)
        time = schedule.find("div", class_="time").get_text(strip=True)

        start_datetime, end_datetime = parse_date_time(date, time, timezone_str)

        event.begin = start_datetime
        event.end = end_datetime
        event.location = address
        event.url = url
        event.name = f"{truck_name} ({location_name})"

        events.append(event)

    return events


# Create a calendar
cal = Calendar()

# Time Zone (change this to the correct one)
timezone_str = "America/New_York"

# URLs of the two sites
urls = [
    ("Riverwalk Place", "55 Riverwalk Pl, West New York, NJ 07093", "https://www.foodtrucksonthemove.com/clients/55-riverwalk/"),
    ("Riverbend", "Riverbend Rd, West New York, NJ 07093", "https://www.foodtrucksonthemove.com/clients/riverbend/"),
]

for location_name, address, url in urls:
    events = scrape_food_truck_data(location_name, address, url, timezone_str)
    for event in events:
        cal.events.add(event)

# Save the calendar to an ICS file
with open("food_truck_schedule.ics", "w") as my_file:
    my_file.writelines(cal)
