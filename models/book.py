from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from ebooklib import epub

from scraper.utils import resp2image

MAX_WORKERS = 10


class Book:
    scraper = None
    novel_title: str = None
    vol_title: str = None
    cover: str = None
    authors: list[str] = []
    imgs: dict[str, str] = {}
    chapters: OrderedDict[str, list[str]] = {}

    def __add_image(self, key, value, book, imgs_format):
        resp = self.scraper.get_image(value)
        if not resp.ok:
            raise Exception(f"Failed to fetch image: {resp.status_code}")

        bytes_, format_ = resp2image(resp)
        imgs_format[f"{key}.format"] = f"{key}.{format_}"

        img = epub.EpubImage(
            uid=key,
            file_name=f"static/{key}.{format_}",
            media_type=f"image/{format_}",
            content=bytes_,
        )
        book.add_item(img)

    def save(self):
        title = f"{self.novel_title} {self.vol_title}"
        print(f"[Saving] {title}")

        book = epub.EpubBook()
        book.set_title(title)
        book.set_language("zh")
        [book.add_author(i) for i in self.authors]

        style = "p {text-indent:2em;padding:0;margin:0;line-height:1.5}"
        css = epub.EpubItem(
            file_name="style/default.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(css)

        print("[Fetching] Cover")
        if self.cover is not None:
            resp = self.scraper.get_image(self.cover)
            bytes_, format_ = resp2image(resp)
            book.set_cover(f"{self.vol_title}_cover.{format_}", bytes_)

        imgs_format = {}
        print("[Fetching] Images")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.__add_image, key, value, book, imgs_format)
                for key, value in self.imgs.items()
            ]

            [future.result() for future in as_completed(futures)]

        print("[Inserting] Content")
        for key, value in self.chapters.items():
            flatten = "".join(value)
            for old, new in imgs_format.items():
                flatten = flatten.replace(old, new)

            chapter = epub.EpubHtml(title=key, file_name=f"{key}.xhtml")
            chapter.add_item(css)
            chapter.set_content(f"<h1>{key}</h1>{flatten}")

            book.add_item(chapter)
            book.toc.append(chapter)
            book.spine.append(chapter)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        os.makedirs("outputs", exist_ok=True)
        epub.write_epub(f"outputs/{title}.epub", book=book)
        print(f"[Saved] {title}.epub")
