from models.book import Book


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

    def get_catalog(self) -> None:
        assert self.scraper is not None
        self.catalog = self.scraper.get_catalog(self.id)

    def get_content(self, volumes: list[Volume], save: bool = True) -> list[Book]:
        assert self.scraper is not None

        result = []
        for i in volumes:
            book = self.scraper.get_books(self.id, [i])[0]
            book.novel_title = self.title
            book.authors = self.authors

            result.append(book)

            if save:
                book.save()

        return result

    def get_all_content(self, save: bool = True) -> list[Book]:
        assert self.catalog is not None

        result = []
        for i in self.catalog:
            result.append(self.get_content([i], save)[0])

        return self.get_content(self.catalog, save)
