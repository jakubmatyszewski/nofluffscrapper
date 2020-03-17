from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time

MAX_WAIT = 10


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


class Scrapper():
    def __init__(self):
        self.not_specified = []

    def get_filters_done(
                        self,
                        city='Warszawa',
                        seniority=['trainee', 'junior']
                        ):
        filters = driver.find_elements_by_class_name('filter-name')
        for filtr in filters:
            if filtr.text == 'Location +':
                location = filtr
            elif filtr.text == 'More +':
                more = filtr
        location.click()
        for button in driver.find_elements_by_class_name('filters-btn'):
            if button.text == city:
                button.click()

        [button for button in driver.find_elements_by_class_name('btn-link')
         if button.text == 'Apply'][0].click()

        more.click()
        for level in seniority:
            driver.find_element_by_xpath(f"//label[@for='{level}']").click()

        [button for button in driver.find_elements_by_class_name('btn-link')
         if button.text == 'Apply'][0].click()

    @wait
    def check_if_in_offer(self):
        crumbs = driver.find_element_by_tag_name('nfj-posting-breadcrumbs')

    @wait
    def check_if_on_list_view(self):
        jobs = driver.find_elements_by_class_name('posting-title__position')
        assert len(jobs) > 0

    def get_requirements(self):
        for re in driver.find_elements_by_tag_name('nfj-posting-requirements'):
            return [button.text.lower()
                    for button in re.find_elements_by_tag_name('button')]

    def check_if_i_am_suited(self, stack, nonos=[]):
        reqs = self.get_requirements()
        for i, req in enumerate(reqs):
            if req in stack:
                reqs[i] = 1
            elif req in nonos:
                reqs[i] = 0
            else:
                self.not_specified.append(req)
                reqs[i] = 0
        rate = sum(reqs)/len(reqs)
        if rate > 0.5:
            print(driver.current_url)
            print(driver.find_element_by_id('posting-header').text)
            print(driver.find_element_by_tag_name('nfj-posting-salaries').text)
            print(f'Suited in {rate:.2f}\n')
            if len(self.not_specified) > 0:
                print(f'You have not specified your prefference towards \
following requirements:\n{self.not_specified}\n\n')

    def check_offers(self, stack, nonos):
        offers = driver.find_elements_by_class_name('posting-title__position')
        for i in range(len(offers)):
            self.check_if_on_list_view()
            offer = driver.\
                find_elements_by_class_name('posting-title__position')[i]
            driver.execute_script(f"window.scrollTo(0, {offer.rect['y']-200})")
            offer.click()
            self.check_if_in_offer()
            self.check_if_i_am_suited(my_stack, no_no)
            driver.execute_script("window.history.go(-1)")
        print(f'Could you reconsider some of this skills?\n\
{list(set(self.not_specified))}')


if __name__ == "__main__":
    my_stack = [
                'docker', 'bash', 'python', 'linux', 'windows', 'english',
                'polish', 'git', 'shell''team player', 'communication skills',
                'attention to detail', 'analytical skills', 'excel'
                'critical thinking', 'selenium', 'sql', 'team player',
                'proactivity', 'problem solving', 'jenkins'
                ]
    no_no = ['java', 'javascript', 'ruby', 'azure', 'typescript', 'android']
    url = 'https://nofluffjobs.com/'
    driver = webdriver.Firefox()
    driver.get(url)
    web_scrap = Scrapper()
    web_scrap.get_filters_done()
    web_scrap.check_offers(my_stack, no_no)
