import random

import pomace

from . import Script


class TommyBryant(Script):
    URL = "https://www.cityoftarrant.com/contact"

    def run(self, page: pomace.Page) -> pomace.Page:
        person = pomace.fake.person

        pomace.log.info(f"Beginning iteration as {person}")
        page.fill_first_name(person.first_name)
        page.fill_last_name(person.last_name)
        page.fill_email(person.email)
        page.fill_comment(
            random.choice(
                [
                    "Tommy Bryant must resign over his racist comments.",
                    "Tommy Bryant's racism doesn't belong in Alabama.",
                    "Get Tommy Bryant out of our city council.",
                    "Tarrant is better than Tommy Bryant. He must go!",
                    "I'm going to keep email the City of Tarrant until Tommy Bryant resigns.",
                ]
            )
        )
        page.fill_captcha("Blue")
        return page.click_submit()

    def check(self, page: pomace.Page) -> bool:
        return "submission has been received" in page


class PatriotPage(Script):
    URL = "https://patriotpage.org"

    def run(self, page: pomace.Page) -> pomace.Page:
        person = pomace.fake.person

        pomace.log.info(f"Beginning iteration as {person}")
        page = page.click_create_an_account()
        page.fill_email(person.email)
        page.fill_confirm_email(person.email)
        page.fill_password(person.password)
        page.fill_confirm_password(person.password)
        page.fill_first_name(person.first_name)
        page.fill_last_name(person.last_name)
        page.fill_nickname(person.nickname)
        page.fill_country("United States")
        page.fill_selection(
            random.choice(
                [
                    "Precinct delegate",
                    "Poll Watcher",
                    "Poll Challenger",
                    "Election Inspector",
                    "Patriot Approved Candidate",
                    "Grassroots Patriot Leader",
                    "Patriot Volunteer",
                ]
            )
        )
        page.browser.execute_script('document.getElementsByTagName("a")[3].remove()')
        page.browser.execute_script('document.getElementsByTagName("a")[3].remove()')
        page.click_agree(wait=0)

        pomace.log.info("Creating account")
        return page.click_create_account(wait=1)

    def check(self, page: pomace.Page) -> bool:
        return "We’re almost there!" in page
