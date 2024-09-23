import requests
from models.book import Book
from models.models import Volume


class Scraper:
    # Returns [Novel] instances
    @staticmethod
    def get(id: str | int):
        pass

    @staticmethod
    def get_catalog(id: str | int) -> list[Volume]:
        pass

    @staticmethod
    def get_books(
        id: str | int, volumes: list[Volume], split: bool = True
    ) -> list[Book]:
        pass

    @staticmethod
    def get_image(url: str) -> requests.Response:
        pass
