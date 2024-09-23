from collections import OrderedDict
import os
from ebooklib import epub

from scraper.utils import resp2image


class Book:
    scraper = None
    novel_title: str = None
    vol_title: str = None
    cover: str = None
    authors: list[str] = []
    imgs: dict[str, str] = {}
    chapters: OrderedDict[str, list[str]] = {}

    def save(self):
        title = f"{self.novel_title} {self.vol_title}"
        print(f"Saving {title}")

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

        print("Fetching Cover...")
        if self.cover is not None:
            resp = self.scraper.get_image(self.cover)
            book.set_cover(f"{self.vol_title}_cover.png", resp2image(resp))

        print("Inserting Content...")
        for key, value in self.chapters.items():
            chapter = epub.EpubHtml(title=key, file_name=f"{key}.xhtml")
            chapter.add_item(css)
            chapter.set_content(f"<h1>{key}</h1>{''.join(value)}")

            book.add_item(chapter)
            book.toc.append(chapter)
            book.spine.append(chapter)

        print("Fetching Images...")
        # TODO asynchronously fetch all images
        for key, value in self.imgs.items():
            resp = self.scraper.get_image(value)
            if not resp.ok:
                raise Exception(f"Failed to fetch image: {resp.status_code}")

            img = epub.EpubImage(
                uid=key,
                file_name=f"static/{key}.png",
                media_type="image/png",
                content=resp2image(resp),
            )
            book.add_item(img)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        os.makedirs("outputs", exist_ok=True)
        epub.write_epub(f"outputs/{title}.epub", book=book)
