import inquirer


from models.novel import Novel
from models.scraper import Scraper
from scraper.linovelib_tw import linovelib_TW


SCRAPER_LIST: tuple[Scraper] = [linovelib_TW]


if __name__ == "__main__":
    # Get the scraper
    question = [
        inquirer.List(
            "scraper",
            message="Scraper",
            choices=list(map(lambda x: (x.name, x), SCRAPER_LIST)),
        ),
        inquirer.Text("id", message="Novel's ID"),
    ]
    answer = inquirer.prompt(question)

    scraper = answer["scraper"]
    id = answer["id"]

    novel: Novel = scraper.get(id)
    print()
    print("Novel's Information: ")
    print(f"[Name] {novel.title}")
    print(f"[Authors] {', '.join(novel.authors)}")
    print(f"[Description] \n{novel.description}")
    print()

    # confirm information
    question = [
        inquirer.Confirm(
            "confirm",
            message=f"Are you sure you want to download this novel?",
            default=True,
        )
    ]
    answer = inquirer.prompt(question)

    if not answer["confirm"]:
        exit(0)

    novel.get_catalog()

    question = [
        inquirer.Confirm(
            "confirm",
            message=f"Download all volumes?",
            default=True,
        )
    ]
    answer = inquirer.prompt(question)

    if answer["confirm"]:
        novel.get_all_contents()
    else:
        questions = [
            inquirer.Checkbox(
                "volume",
                message="Select volume(s) to download",
                choices=list(map(lambda x: (x.title, x), novel.catalog)),
            ),
        ]

        answer = inquirer.prompt(questions)
        novel.get_contents(answer["volume"])
