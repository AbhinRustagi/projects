from datetime import datetime

from .utils import PERSONAL_WEBSITE


class Project:
    '''
    A class to represent a project writeup
    '''

    def __init__(self, metadata, content):
        self.title = metadata.get("title")
        self.date = metadata.get("date", datetime.now())
        self.description = metadata.get("description", "")
        self.tags = metadata.get("tags", [])
        self.slug = metadata.get("path").split("/")[-1].replace(".md", "")
        self.canonical_url = metadata.get(
            "canonical_url", PERSONAL_WEBSITE + "projects/" + self.slug)
        self.thumbnail = metadata.get("thumbnail", None)
        self.published = metadata.get("published", False)
        self.path = metadata.get("path")
        self.content = content

    def __str__(self):
        return f"{self.slug} - {self.date.strftime('%Y-%m-%d')}"

    def __repr__(self):
        return f"<{self.title} - {self.date.strftime('%Y-%m-%d')}>"

    def __eq__(self, value) -> bool:
        return self.title == value.title and self.date == value.date and self.slug == value.slug

    def __ne__(self, value):
        return self.title != value.title or self.date != value.date or self.slug != value.slug

    def index_data(self):
        '''
        Return the data to be stored in the index.json file
        '''
        return {
            "title": self.title,
            "date": self.date.strftime("%Y-%m-%d"),
            "slug": self.slug,
            "path": self.path,
            "canonical_url": self.canonical_url,
            "description": self.description,
            "tags": self.tags,
            "thumbnail": self.thumbnail,
            "published": self.published
        }
