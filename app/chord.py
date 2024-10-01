import os
import webbrowser

import requests

from app.helpers import USER_AGENT

class Chord:
    def __init__(self, name: str, url: str):
        self.name = name.strip("Аккрод ")
        self.url = url

    def open_in_browser(self):
        webbrowser.open_new(self.url)

    def get_all_mode(self):
        chords = []
        mode_counter = 0
        base_url = os.path.split(self.url)[0]
        while True:
            chord_name = f"{self.name}_{mode_counter}"
            url = f"{base_url}/{chord_name}.gif"
            response = requests.get(url, headers={'user-agent':USER_AGENT})
            if response.status_code == 200:
                chord = Chord(chord_name, url)
                chords.append(chord)
                mode_counter += 1
            else:
                break
        return chords

    def __repr__(self):
        return self.name