from typing import Callable
from models.book import Book
from models.progress import Progress, default_progress_handler


class Chapter:
    id: str | int = None
    title: str = None


class Volume:
    title: str = None
    thumbnail: str = None
    chapters: list[Chapter] = []


class Novel:
    scraper = None

    id: str | int = None
    title: str = None
    thumbnail: str = None
    authors: list[str] = None
    description: str = None
    update_time: int = None
    latest: str = None
    catalog: list[Volume] | None = None

    progress_handler: Callable[[Progress], None] = staticmethod(
        default_progress_handler
    )

    def get_catalog(self) -> None:
        assert self.scraper is not None
        self.catalog = self.scraper.get_catalog(self.id)

    def get_contents(self, volumes: list[Volume], save: bool = True) -> list[Book]:
        assert self.scraper is not None

        result = []
        for i in volumes:
            book = self.scraper.get_book(self.id, i, self.progress_handler)
            book.novel_title = self.title
            book.authors = self.authors
            book.progress_handler = self.progress_handler

            result.append(book)

            if save:
                book.save()

        return result

    def get_all_contents(self, save: bool = True) -> list[Book]:
        assert self.catalog is not None

        return self.get_contents(self.catalog, save)
