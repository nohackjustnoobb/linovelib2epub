from time import strftime, localtime

from ebooklib import epub
from models.models import Novel
from scraper.linovelib_tw import linovelib_TW


if __name__ == "__main__":
    novel: Novel = linovelib_TW.get(input("ID: "))

    print(f"Thumbnail: {novel.thumbnail}")
    print(f"Title: {novel.title}")
    print(f"Author(s): {', '.join(novel.authors)}")
    print(f"latest: {novel.latest}")
    print(f"Update Date: {strftime('%Y-%m-%d', localtime(novel.update_time))}")
    print(f"Description: {novel.description}")
    print()

    if input("Fetch Catalog (Y/N): ").lower() != "y":
        exit(0)

    novel.get_catalog()

    show_chapters = input("Show Chapters (Y/N): ").lower() == "y"
    print()

    print("Volumes:")

    for i in novel.catalog:
        print(f"{i.title}: {i.thumbnail}")

        if show_chapters:
            for j in i.chapters:
                print(f"\t{j.title}: {j.id}")

            print()

    print()
    if input("Convert To EPUB (Y/N): ").lower() == "y":
        if input("Convert All (Y/N): ").lower() == "y":
            novel.get_all_content()
        else:
            # TODO
            pass

    # novel: Novel = linovelib_TW.get(2939)
    # novel.get_catalog()
    # result = novel.get_content([novel.catalog[0]])
