import time
import redis
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

MAX_WAIT = 60
URL = 'https://nofluffjobs.com/'

redis_client = redis.Redis(host='redis',
                           charset="utf-8",
                           decode_responses=True)


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(1)
    return modified_fn


class Scrapper:
    def __init__(self):
        self.not_specified = []
        self.report = []
        self.current_page = 1

        self.open_browser()
        self.set_language_to_english()

    @wait
    def open_browser(self):
        self.driver = webdriver.Remote(
            "http://selenium:4444/wd/hub",
            DesiredCapabilities.FIREFOX)
        self.driver.get(URL)

    def close_browser(self):
        self.driver.quit()

    @wait
    def wait_for(self, fn):
        return fn()

    def set_language_to_english(self):
        current_language = self.driver.find_element_by_class_name(
            'language-picker__lang-selected')
        if current_language.text != "English":
            current_language.click()
            flags = self.driver.find_elements_by_class_name('language-picker__flag')
            for flag in flags:
                if flag.get_attribute('src').endswith("EN.svg"):
                    flag.click()
                    break

    def apply_button(self):
        [button for button in self.driver.find_elements_by_class_name('btn-link')
         if button.text == 'Apply'][0].click()

    def get_filters_done(self,
                         cities=['warszawa'],
                         seniority=['trainee', 'junior'],
                         categories=[]
                         ):
        filters = self.driver.find_elements_by_class_name('filter-name')
        for filtr in filters:
            if filtr.text == 'Location':
                location = filtr
            elif filtr.text == 'Category':
                category = filtr
            elif filtr.text == 'More':
                more = filtr

        location.click()
        for button in self.driver.find_elements_by_class_name('filters-btn'):
            if button.text in cities:
                button.click()
        self.apply_button()

        category.click()
        for button in self.driver.find_elements_by_class_name('filters-btn'):
            if button.text in categories:
                button.click()
        self.apply_button()

        more.click()
        for level in seniority:
            self.driver.find_element_by_xpath(f"//label[@for='{level.lower()}']").click()
        self.apply_button()

    @wait
    def check_if_in_offer(self):
        crumbs = self.driver.find_elements_by_tag_name('nfj-posting-breadcrumbs')
        assert len(crumbs) > 0

    @wait
    def check_if_on_list_view(self):
        jobs = self.driver.find_elements_by_class_name('posting-title__position')
        assert len(jobs) > 0

    @wait
    def get_requirements(self):
        reqs = []
        for re in self.driver.find_elements_by_tag_name('nfj-posting-requirements'):
            reqs += [button.text.lower()
                     for button in re.find_elements_by_tag_name('button')]
        return reqs

    @wait
    def get_description(self):
        description = self.driver.find_element_by_class_name('posting-details-description')
        position = description.find_element_by_tag_name('h1').text
        try:
            company = description.find_element_by_class_name('company-name').text
        except:
            company = description.find_element_by_tag_name('dd').text
        _url = self.driver.current_url
        salary = self.driver.find_element_by_tag_name('nfj-posting-salaries').text
        return position, company, _url, salary

    def check_if_i_am_suited(self, stack, nonos=[]):
        reqs = self.get_requirements()
        for i, req in enumerate(reqs):
            if req in stack:
                reqs[i] = 1
            elif req in nonos:
                return False
            else:
                self.not_specified.append(req)
                reqs[i] = 0
        rate = sum(reqs) / len(reqs)
        if rate > 0.4:
            now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
            position, company, _url, salary = self.get_description()
            # -- email only --
            description = f'{position} @ {company}\n{_url}\n{salary}'
            self.report.append(f"{description}\nSuited in {rate:.2f}/1.\n\n")
            # --/ email only --
            redis_client.hset(f'result:{now}', 'position', position)
            redis_client.hset(f'result:{now}', 'company', company)
            redis_client.hset(f'result:{now}', 'url', _url)
            redis_client.hset(f'result:{now}', 'salary', salary)
        return False

    def check_offers(self, stack, nonos):
        is_it_last_page = False
        while is_it_last_page is False:
            time.sleep(1)
            offers = self.driver.find_elements_by_class_name('posting-list-item')
            for i in range(len(offers)):
                self.check_if_on_list_view()
                link = offers[i].get_property('href')
                self.driver.execute_script(
                    f"window.scrollTo(0, {offers[i].rect['y']-200})")
                self.driver.execute_script(f"window.open('{link}');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.check_if_in_offer()
                time.sleep(0.5)
                self.check_if_i_am_suited(stack, nonos)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

            self.driver.execute_script(
                f"window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
            is_it_last_page = self.page_flipping()
        for skill in self.not_specified:
            redis_client.set(f'skillproposal:{skill}', skill)

    def page_flipping(self):
        try:
            self.current_page += 1
            last_page = self.driver.find_elements_by_class_name('page-link')[-2]
            if self.current_page < int(last_page.text):
                page_link = self.driver.find_element_by_xpath(f"//*[contains(text(), '{self.current_page}') and @class='page-link']")
                self.driver.execute_script(
                    f"window.scrollTo(0, {page_link.rect['y']-200})")
                page_link.click()
                return False
        except Exception as e:
            print(e)
            print('Just one page available.', flush=True)
            return True
        return True
