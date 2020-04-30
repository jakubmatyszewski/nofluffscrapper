from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time

MAX_WAIT = 10
URL = 'https://nofluffjobs.com/'

driver = webdriver.Firefox()
driver.get(URL)


def close_browser():
    driver.quit()


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn


class Scrapper:
    def __init__(self):
        self.not_specified = []
        self.report = []

    @wait
    def wait_for(self, fn):
        return fn()

    def set_language_to_english(self):
        current_language = driver.find_element_by_class_name(
            'language-picker__lang-selected')
        if current_language.text != "English":
            current_language.click()
            flags = driver.find_elements_by_class_name('language-picker__flag')
            for flag in flags:
                if flag.get_attribute('src').endswith("EN.svg"):
                    flag.click()
                    break

    def apply_button(self):
        [button for button in driver.find_elements_by_class_name('btn-link')
         if button.text == 'Apply'][0].click()

    def get_filters_done(
                        self,
                        cities=['Warszawa'],
                        seniority=['trainee', 'junior'],
                        categories=[]
                        ):
        filters = driver.find_elements_by_class_name('filter-name')
        for filtr in filters:
            if filtr.text == 'Location':
                location = filtr
            elif filtr.text == 'Category':
                category = filtr
            elif filtr.text == 'More':
                more = filtr

        location.click()
        for button in driver.find_elements_by_class_name('filters-btn'):
            if button.text.lower() in cities:
                button.click()
        self.apply_button()

        category.click()
        for button in driver.find_elements_by_class_name('filters-btn'):
            if button.text.lower() in categories:
                button.click()
        self.apply_button()

        more.click()
        for level in seniority:
            driver.find_element_by_xpath(f"//label[@for='{level}']").click()
        self.apply_button()

    @wait
    def check_if_in_offer(self):
        crumbs = driver.find_elements_by_tag_name('nfj-posting-breadcrumbs')
        assert len(crumbs) > 0

    @wait
    def check_if_on_list_view(self):
        jobs = driver.find_elements_by_class_name('posting-title__position')
        assert len(jobs) > 0

    @wait
    def get_requirements(self):
        reqs = []
        for re in driver.find_elements_by_tag_name('nfj-posting-requirements'):
            reqs += [button.text.lower()
                     for button in re.find_elements_by_tag_name('button')]
        return reqs

    @wait
    def get_description(self):
        description = driver.find_element_by_class_name('posting-details-description')
        position = description.find_element_by_tag_name('h1').text
        try:
            company = description.find_element_by_class_name('company-name').text
        except:
            company = description.find_element_by_tag_name('dd').text
        _url = driver.current_url
        salary = driver.find_element_by_tag_name('nfj-posting-salaries').text
        return f'{position} @ {company}\n{_url}\n{salary}'

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
        rate = sum(reqs)/len(reqs)
        if rate > 0.5:
            # print(self.get_description())
            # print(f'Suited in {rate:.2f}\n')
            self.report.append(f"{self.get_description()}\nSuited in {rate:.2f}/1.\n\n")
        return False

    def check_offers(self, stack, nonos):
        is_it_last_page = False
        while is_it_last_page is False:
            offers = driver.find_elements_by_class_name('posting-list-item')
            for i in range(len(offers)):
                self.check_if_on_list_view()
                link = offers[i].get_property('href')
                driver.execute_script(
                    f"window.scrollTo(0, {offers[i].rect['y']-200})")
                driver.execute_script(f"window.open('{link}');")
                driver.switch_to.window(driver.window_handles[1])
                self.check_if_in_offer()
                time.sleep(0.5)
                self.check_if_i_am_suited(stack, nonos)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            driver.execute_script(
                f"window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
            is_it_last_page = self.page_flipping()
        print(f'Could you reconsider some of this skills?\n\
{list(set(self.not_specified))}')

    def page_flipping(self):
        page_links = driver.find_elements_by_class_name('page-link')
        for i, page in enumerate(page_links):
            if 'current' in page.text:
                current_page = page.text.split('\n')[0]
                if page_links[i+1].text == '»':
                    return True
                else:
                    page_links[i+1].click()
                    return False
