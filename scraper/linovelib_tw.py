from datetime import datetime
import hashlib
import re
from time import sleep
from typing import Callable
from bs4 import BeautifulSoup
import requests
import requests.sessions
from models.book import Book
from models.novel import Chapter, Novel, Volume
from models.progress import Progress, Status, default_progress_handler
from models.scraper import Scraper
from utils.constants import MAX_RETRIES

TIMEOUT = 1


class linovelib_TW(Scraper):
    name = "linovelib (TW)"
    base_url = "tw.linovelib.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "Accept-Language": "zh-HK",
        "Accept-Encoding": "gzip, deflate, br",
    }

    @staticmethod
    def get(id: str | int):
        resp = requests.get(f"https://{linovelib_TW.base_url}/novel/{id}.html")

        if not resp.ok:
            raise Exception(f"Failed to fetch info: {resp.status_code}")

        soup = BeautifulSoup(resp.content, features="lxml")
        novel = Novel()

        novel.scraper = linovelib_TW
        novel.id = id
        novel.title = soup.find("h1", class_="book-title").text.strip()
        novel.thumbnail = soup.find("img", class_="book-cover")["src"]
        novel.authors = [
            i.text.strip() for i in soup.find("div", class_="book-rand-a").find_all("a")
        ]
        novel.description = soup.find(id="bookSummary").find("content").text.strip()
        novel.update_time = int(
            datetime.strptime(
                list(soup.find("div", class_="book-meta-l").stripped_strings)[-1],
                "%Y-%m-%d",
            ).timestamp()
        )
        novel.latest = soup.find("div", class_="book-meta-r").text.strip()

        return novel

    @staticmethod
    def get_catalog(id: str | int) -> list[Volume]:
        resp = requests.get(f"https://{linovelib_TW.base_url}/novel/{id}/catalog")
        if not resp.ok:
            raise Exception(f"Failed to fetch catalog: {resp.status_code}")

        soup = BeautifulSoup(resp.content, features="lxml")
        result = []

        volumes = soup.find_all("ul", class_="volume-chapters")
        for v in volumes:
            volume = Volume()
            volume.title = v.find("li", class_="chapter-bar").text.strip()
            volume.chapters = []

            tryThumbnail = v.find("li", class_="volume-cover")
            if tryThumbnail is not None:
                volume.thumbnail = tryThumbnail.find("img")["data-src"]

            for c in v.find_all("li", class_="jsChapter"):
                chapter = Chapter()
                chapter.title = c.text.strip()

                search = re.search(r".*\/(.*)\.html", c.find("a")["href"])
                if search is not None:
                    chapter.id = int(search.group(1))

                volume.chapters.append(chapter)

            for idx, chapter in enumerate(volume.chapters):
                if chapter.id is not None:
                    continue

                if (
                    idx >= 1
                    and idx < len(volume.chapters) - 1
                    and volume.chapters[idx + 1].id - volume.chapters[idx - 1].id == 2
                ):
                    chapter.id = volume.chapters[idx + 1].id - 1

            result.append(volume)

        return result

    @staticmethod
    def get_book(
        id: str | int,
        volume: Volume,
        progress_handler: Callable[[Progress], None] = default_progress_handler,
    ) -> Book:
        progress_handler(Progress(status=Status.FETCHING, title=volume.title))

        session = requests.Session()
        session.cookies.set("night", "0")

        book = Book()
        book.scraper = linovelib_TW
        book.cover = volume.thumbnail
        book.vol_title = volume.title
        book.chapters = {}

        next_id = volume.chapters[0].id
        index = 0

        imgs = {}

        while next_id is not None:
            next_page = None
            retries = 0
            title = None
            content = []

            # Get all pages of a chapter
            while retries <= MAX_RETRIES:
                progress_handler(
                    Progress(
                        status=Status.FETCHING,
                        title=volume.chapters[index].title,
                        page=next_page,
                        current=index + 1,
                        total=len(volume.chapters),
                    )
                )

                # Fetch the chapter
                resp = session.get(
                    f"https://{linovelib_TW.base_url}/novel/{id}/{next_id}{f'_{next_page}' if next_page is not None else ''}.html",
                    headers=linovelib_TW.headers,
                )
                sleep(TIMEOUT)

                if not resp.ok:
                    retries += 1
                    progress_handler(
                        Progress(status=Status.ERROR, title=resp.status_code)
                    )
                    continue
                else:
                    retries = 0

                soup = BeautifulSoup(resp.text, features="lxml")

                # Save the chapter title
                if title is None:
                    title = soup.find("h1", id="atitle").text

                for i in soup.find("div", id="acontent1").children:
                    if not i.name:
                        continue

                    if i.name == "center":
                        raise Exception(f"Failed to load {title} ({resp.url})")
                    elif i.name != "div":
                        content.append(str(i))

                # get the next page or chapter
                next_url = re.search(r"url_next:'/novel/.*?/(.*?)\.html'", resp.text)

                if next_url is None:
                    next_id = None
                    break

                next_url = next_url.group(1)
                page = re.search(r".*_(.*)", next_url)
                if page is None:
                    next_id = (
                        None
                        if next_url == next_id or title == volume.chapters[-1].title
                        else next_url
                    )
                    break

                next_page = page.group(1)

            filtered_content = []
            index += 1
            if len(content) != 0:
                for i in content:
                    is_img = re.search(r"<img.*data-src=\"(.*?)\".*/>", i) or re.search(
                        r"<img.*src=\"(.*?)\".*/>", i
                    )

                    if is_img is None:
                        filtered_content.append(i)
                        continue

                    filename = hashlib.md5(is_img.group(1).encode("utf-8")).hexdigest()
                    imgs[filename] = is_img.group(1)

                    filtered_content.append(f'<img src="static/{filename}.format"/>')

                book.chapters[title] = filtered_content

        book.imgs = imgs

        progress_handler(Progress(status=Status.FINISHED, title=volume.title))

        return book

    @staticmethod
    def get_books(
        id: str | int,
        volumes: list[Volume],
        progress_handler: Callable[[Progress], None] = default_progress_handler,
    ) -> list[Book]:
        result = [linovelib_TW.get_book(id, v, progress_handler) for v in volumes]

        return result

    @staticmethod
    def get_image(url: str) -> requests.Response:
        return requests.get(url, headers={"Referer": linovelib_TW.base_url})
