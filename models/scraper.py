from typing import Callable
import requests
from models.book import Book
from models.novel import Volume
from models.progress import Progress


class Scraper:
    name: str = None

    # Returns [Novel] instances
    @staticmethod
    def get(id: str | int):
        pass

    @staticmethod
    def get_catalog(id: str | int) -> list[Volume]:
        pass

    @staticmethod
    def get_book(
        id: str | int,
        volume: Volume,
        progress_handler: Callable[[Progress], None],
    ) -> Book:
        pass

    @staticmethod
    def get_books(
        id: str | int,
        volumes: list[Volume],
        progress_handler: Callable[[Progress], None],
    ) -> list[Book]:
        pass

    @staticmethod
    def get_image(url: str) -> requests.Response:
        pass
