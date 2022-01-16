import os
import sys
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
from classes import Photo


# the main function used for getting info from NASA API for the provided date or without one
# gets date as a str to be more user-friendly
def request(link, api_key, date=datetime.today().strftime("%Y-%m-%d")):
    # checking if provided date is in the requested format and exiting if it is not
    try:
        date = datetime.strptime(date, "%Y-%m-%d").date()
        date = date.strftime("%Y-%m-%d")
    except ValueError:
        print("Provided date doesn't match YYYY-MM-DD format" + "\n")
        sys.exit()

    # creating directories if they don't exist
    directory = "data/"
    if not os.path.exists(directory):
        os.makedirs(directory)
        if not os.path.exists(directory + "daily/"):
            os.makedirs(directory + "daily/")
        if not os.path.exists(directory + "weekly/"):
            os.makedirs(directory + "weekly/")

    # several objects needed for further operations
    rovers = ["curiosity", "opportunity", "spirit"]
    params = {"earth_date": date, "api_key": api_key}

    # defining a dict for all the photos for each camera of each rover
    photos = defaultdict(lambda: defaultdict(list))
    # getting the data from API and putting it in a dict
    count = 0
    for rover in rovers:
        try:
            req = requests.get(link.format(rover), params=params)
        except requests.exceptions.ConnectionError:
            print("Please check your internet connection")
            sys.exit()
        req_dict = json.loads(req.text)
        if len(req_dict["photos"]) == 0:
            count += 1
            # safely aborting the script if there is no info from any of the rovers
            if count == 3:
                print("There is no data from any of the rovers of the provided date")
                sys.exit()
            print("No data from " + rover.capitalize() + " rover of the provided date" + "\n")
            continue
        for photo in req_dict["photos"]:
            id = photo["id"]
            sol = photo["sol"]
            camera = photo["camera"]["name"]
            pic = photo["img_src"]
            picture = Photo(id, sol, camera, pic)
            photos[rover][camera].append(picture)

    # iterating through photos to get rover name, camera name and photo data to put it in a json file with proper name
    for rover, cameras in photos.items():
        for camera, pictures in cameras.items():
            filename = rover + "." + camera.lower() + "-" + date + ".json"
            output_daily = {"photos": []}
            if len(pictures) != 0:
                for picture in pictures:
                    output_dict = {"id": picture.id, "sol": picture.sol, "picture": picture.picture}
                    output_daily["photos"].append(output_dict)
                with open("data/daily/" + filename, "w") as output_file:
                    output_daily = json.dumps(output_daily)
                    output_file.write(output_daily)

    # updating weekly stats
    update(date)
    print("All fetched data added to 'data' folder")


# used at the end of the request to update weekly stats
# gets date as a str to be more user-friendly
# might be used separately
def update(date):
    try:
        date = datetime.strptime(date, "%Y-%m-%d").date()
        # getting the start and the end of the week
        weekday = date.weekday()
        monday = (date - timedelta(days=weekday))
        sunday = (monday + timedelta(days=6))
    except ValueError:
        print("Provided date doesn't match YYYY-MM-DD format" + "\n")
        sys.exit()

    # defining dicts for output and as a storage for number of photos from each camera of each rover
    # stored as numbers of photos for each day for each camera of each rover to be able to find weekly stats easier
    photos = defaultdict(lambda: defaultdict(list))

    # getting the data for all the suitable daily stats files
    try:
        directory = os.fsencode("data/daily")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            # iterating through json files only in case there is something else in the folder
            if filename.endswith(".json"):
                date = datetime.strptime(filename[filename.find("-") + 1:filename.find("json") - 1], "%Y-%m-%d").date()
                rover = filename[:filename.find(".")]
                camera = filename[filename.find(".") + 1:filename.find("-")]
                # checking if the date of the file is within the range of the week
                if monday <= date <= sunday:
                    with open("data/daily/" + filename, "r") as input_file:
                        data = json.load(input_file)
                        photos_number = len(data["photos"])
                        photos[rover][camera.upper()].append(photos_number)
            else:
                continue
    except FileNotFoundError:
        print("You should have at least one file in data/weekly to perform this")
        sys.exit()

    # getting the data from "photos" dict and writing it into a file with a proper name
    monday = monday.strftime("%Y-%m-%d")
    for rover, cameras in photos.items():
        filename = rover + "-" + monday + ".json"
        output = {"cameras_summary": []}
        for camera, photos_numbers in cameras.items():
            if len(photos_numbers) != 0:
                avg_photos_amount = round(sum(photos_numbers) / len(photos_numbers))
                min_photos_amount = min(photos_numbers)
                max_photos_amount = max(photos_numbers)
                total_photos_amount = sum(photos_numbers)
                output_weekly = {"camera_name": camera, "avg_photos_amount": avg_photos_amount,
                                 "min_photos_amount": min_photos_amount, "max_photos_amount": max_photos_amount,
                                 "total_photos_amount": total_photos_amount}
                output["cameras_summary"].append(output_weekly)

        with open("data/weekly/" + filename, "w") as output_file:
            output_file.write(json.dumps(output))
