from __future__ import print_function

import os
import json
from GoogleDrive import GoogleDrive

from utility import isEmpty

def main():
    drives = dict()
    gdrives = list()

    if not os.path.isdir("drives"):
        os.mkdir("drives")

    if os.path.exists("drives\\collection.json"):
        with open("drives\\collection.json", "r") as f:
            drives = json.load(f)

        for id, path in drives.items():
            gdrives.append(GoogleDrive(path))

    if isEmpty(gdrives):
        # Let the user log in using primiary account
        gdrives.append(GoogleDrive())
        gdrives[0].signup()
        gdrives[0].save_token("drives\\0.json")

        # Add the primary account to the collection
        drives[gdrives[0].id] = gdrives[0].token_path
        with open("drives\\collection.json", "w") as f:
            json.dump(drives, f)
    
    if not isEmpty(gdrives) and gdrives[0].is_not_valid():
        if gdrives[0].is_expired() and gdrives[0].has_refresh_token():
            gdrives[0].refresh()
            gdrives[0].save_token()


    print(gdrives[0])

if __name__ == "__main__":
    main()