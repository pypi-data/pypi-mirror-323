import random
import time

import pomace

from . import Script


class LauraSmith(Script):
    URL = "https://towamencin.org/resources/feedback/"
    SKIP = True

    def run(self, page: pomace.Page) -> pomace.Page:
        person = pomace.fake.person
        page.fill_name(person.name)
        page.fill_email(person.email)
        page.fill_comments(
            random.choice(
                [
                    "Laura Smith is a Nazi and should be kicked off the council.",
                    "Nazis are evil and should be removed from the council.",
                    "Laura Smith is a Nazi and should be removed from the council.",
                    "Remove Laura Smith from the council now!",
                    "Towamencin deserves better than Nazis like Laura Smith!",
                    "Nazis are not welcome in Towamencin. Fire Laura Smith now!",
                ]
            )
        )
        while "complete the reCAPTCHA" in page.html:
            pomace.log.info("Waiting for you to complete the reCAPTCHA")
            time.sleep(3)
            page = pomace.auto()
        return page.click_send_feedback()

    def check(self, page: pomace.Page) -> bool:
        return "Thank you for your submission" in page
