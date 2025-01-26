import os
from typing import Optional

import requests
from ovos_bus_client.message import Message
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_data_home

from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill


def get_wallpapers(query: Optional[str] = None,
                   cache=True, max_pics: int = 5):
    url = "https://wallhaven.cc/api/v1/search"
    params = {"sorting": "random",
              "categories": "100"}
    if query:
        params["q"] = query
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()["data"]
    except (requests.RequestException, KeyError, ValueError) as e:
        LOG.error(f"Error fetching wallpapers: {str(e)}")
        return []
    urls = [w["path"] for w in data][:max_pics]
    if cache:
        paths = []
        # standard path already used by the PHAL plugin
        local_wallpaper_storage = os.path.abspath(os.path.join(xdg_data_home(), "wallpapers"))
        os.makedirs(local_wallpaper_storage, exist_ok=True)
        for u in urls:
            LOG.debug(f"Downloading wallpaper: {u}")
            pic = requests.get(u).content
            p = os.path.join(local_wallpaper_storage, u.split("/")[-1])
            with open(p, "wb") as f:
                f.write(pic)
                paths.append(p)
        return paths
    return urls


class WallpapersSkill(OVOSSkill):

    def initialize(self):
        # state trackers
        self.pic_idx = 0
        self.picture_list = []
        self.bus.emit(Message("ovos.wallpaper.manager.register.provider",
                              {"provider_name": self.skill_id,
                               "provider_display_name": self.name}))
        self.add_event(f"{self.skill_id}.get.wallpaper.collection", self.handle_wallpaper_scan)
        self.add_event(f"{self.skill_id}.get.new.wallpaper", self.handle_wallpaper_get)
        self.bus.emit(Message(f"{self.skill_id}.get.wallpaper.collection"))  # download wallpapers on launch

    # PHAL wallpaper manager integrations
    def handle_wallpaper_scan(self, message: Message):
        self.fetch_wallpapers()
        self.bus.emit(message.reply("ovos.wallpaper.manager.collect.collection.response",
                                    {"provider_name": self.skill_id,
                                     "wallpaper_collection": self.picture_list}))

    def handle_wallpaper_get(self, message: Message):
        url = self.fetch_wallpapers()
        self.bus.emit(message.reply("ovos.wallpaper.manager.set.wallpaper",
                                    {"provider_name": self.skill_id,
                                     "url": url}))

    # skill internals
    def fetch_wallpapers(self, query=None) -> str:
        self.picture_list = get_wallpapers(query)
        self.pic_idx = 0
        self.set_context("SlideShow")
        return self.picture_list[self.pic_idx]

    def change_wallpaper(self, image):
        # update in homescreen skill / PHAL plugin
        self.bus.emit(Message("ovos.wallpaper.manager.set.wallpaper",
                              {"provider_name": self.skill_id, "url": image}))
        self.bus.emit(Message("homescreen.wallpaper.set", {"url": image}))

    # intents
    @intent_handler("wallpaper.random.intent")
    def handle_random_wallpaper(self, message):
        self.speak_dialog("searching_random")
        image = self.fetch_wallpapers()
        self.change_wallpaper(image)
        self.speak_dialog("wallpaper.changed")

    @intent_handler("picture.random.intent")
    def handle_random_picture(self, message=None):
        self.speak_dialog("searching_random")
        image = self.fetch_wallpapers()
        self.gui.show_image(image)

    @intent_handler("wallpaper.about.intent")
    def handle_wallpaper_about(self, message):
        query = message.data["query"]
        self.speak_dialog("searching", {"query": query})
        image = self.fetch_wallpapers(query)
        self.change_wallpaper(image)
        self.speak_dialog("wallpaper.changed")

    @intent_handler("picture.about.intent")
    def handle_picture_about(self, message=None):
        query = message.data["query"]
        self.speak_dialog("searching", {"query": query})
        image = self.fetch_wallpapers(query)
        self.gui.show_image(image)

    @intent_handler(IntentBuilder("NextPictureIntent")
                    .require("next").optionally("picture")
                    .require("SlideShow"))
    def handle_next(self, message=None):
        total = len(self.picture_list)
        self.pic_idx += 1
        if self.pic_idx >= total:
            self.pic_idx = total - 1
            self.speak_dialog("no.more.pictures")
        else:
            self.acknowledge()
            image = self.picture_list[self.pic_idx]
            self.gui.show_image(image)

    @intent_handler(IntentBuilder("PrevPictureIntent")
                    .require("previous").optionally("picture")
                    .require("SlideShow"))
    def handle_prev(self, message=None):
        self.pic_idx -= 1
        if self.pic_idx < 0:
            self.pic_idx = 0
            self.speak_dialog("no.more.pictures")
        else:
            self.acknowledge()
            image = self.picture_list[self.pic_idx]
            self.gui.show_image(image)

    @intent_handler(IntentBuilder("MakeWallpaperIntent")
                    .require("set").require("wallpapers").optionally("picture")
                    .require("SlideShow"))
    def handle_set_wallpaper(self, message=None):
        image = self.picture_list[self.pic_idx]
        self.change_wallpaper(image)
        self.speak_dialog("wallpaper.changed")
        self.gui.release()  # let home screen show the wallpaper
