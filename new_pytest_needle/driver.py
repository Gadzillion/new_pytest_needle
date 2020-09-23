"""new_pytest_needle

.. codeauthor:: P.Serega

"""

import base64
from errno import EEXIST
import math
import os
import io
import re
import time
import pytest
import allure
import pathlib
from contextlib import contextmanager
from PIL import Image, ImageDraw, ImageColor
from new_pytest_needle.engines.pil_engine import ImageDiff
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from io import BytesIO as IOClass

basestring = str  # pylint: disable=W0622,C0103

DEFAULT_BASELINE_DIR = os.path.realpath(os.path.join(os.getcwd(),
                                                     os.path.pardir, 'screenshots', 'baseline'))
DEFAULT_BASELINE_DIR_REM = os.path.realpath(os.path.join(os.getcwd(),
                                                         os.path.pardir, 'screenshots'))
DEFAULT_BASELINE_DIR_HAND = os.path.realpath(os.path.join(os.getcwd(),
                                                          os.path.pardir, 'test', 'screenshots', 'baseline'))
DEFAULT_BASELINE_DIR_HAND_REM = os.path.realpath(os.path.join(os.getcwd(),
                                                              os.path.pardir, 'test', 'screenshots'))
DEFAULT_LANDING_BASELINE_DIR = os.path.realpath(os.path.join(os.getcwd(), 'l_screenshots', 'baseline'))
DEFAULT_OUTPUT_DIR = os.path.realpath(os.path.join(os.getcwd(), os.path.pardir, 'screenshots'))
DEFAULT_DOCKER_DIR = "/builds/qa/layout-tests/screenshots"
DEFAULT_ENGINE = 'new_pytest_needle.engines.imagemagick_engine.Engine'
DEFAULT_VIEWPORT_SIZE = '1024x768'
DEFAULT_BROWSER = 'chrome'


class NeedleDriver(object):
    """NeedleDriver instance
    """

    ENGINES = {
        'pil': 'new_pytest_needle.engines.pil_engine.Engine',
        'imagemagick': DEFAULT_ENGINE,
        'perceptualdiff': 'new_pytest_needle.engines.perceptualdiff_engine.Engine'
    }

    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"

    def __init__(self, **kwargs):

        self.options = kwargs

        def _set_options(option_s):
            option_a = option_s
            option_a.add_argument('--headless')
            option_a.add_argument('--no-sandbox')
            option_a.add_argument('--disable-gpu')
            option_a.add_argument('--autoplay-policy=user-required')
            option_a.set_capability("acceptInsecureCerts", True)
            return option_a

        browser = self.get_driver

        if browser == self.CHROME:
            options = _set_options(ChromeOptions())
            options.add_experimental_option("detach", True)
            self.driver = webdriver.Chrome(options=options)
        elif browser == self.FIREFOX:
            options = _set_options(FirefoxOptions())
            self.driver = webdriver.Firefox(options=options)
        elif browser == self.SAFARI:
            self.driver = webdriver.Safari()
        else:
            raise ValueError(f"Unknown browser type: {browser}")

        self._wait = WebDriverWait(self.driver, 20).until

        self.driver.set_window_position(0, 0)
        self.set_viewport()

    @staticmethod
    def _create_dir(directory):
        """Recursively create a directory

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L125

        :param str directory: Directory path to create
        :return:
        """

        try:

            os.makedirs(directory)

        except OSError as err:

            if err.errno == EEXIST and os.path.isdir(directory):
                return

            raise err

    def _find_element(self, element_or_selector=None):
        """Returns an element

        :param element_or_selector: WebElement or tuple containing selector ex. ('id', 'mainPage')
        :return:
        """

        if isinstance(element_or_selector, tuple):

            elements = self.driver.find_elements(*element_or_selector)
            return elements[0] if elements else None

        elif isinstance(element_or_selector, WebElement):
            return element_or_selector

    @staticmethod
    def _get_element_dimensions(element):
        """Returns an element's position and size

        :param WebElement element: Element to get dimensions for
        :return:
        """

        if isinstance(element, WebElement):
            # Get dimensions of element
            location = element.location
            size = element.size

            return {
                'top': int(location['y']),
                'left': int(location['x']),
                'width': int(size['width']),
                'height': int(size['height'])
            }

    def _get_element_rect(self, element):
        """Returns the two points that define the rectangle

        :param WebElement element: Element to get points for
        :return:
        """

        dimensions = self._get_element_dimensions(element)

        if dimensions:
            return (
                dimensions['left'],
                dimensions['top'],
                (dimensions['left'] + dimensions['width']),
                (dimensions['top'] + dimensions['height'])
            )

    @staticmethod
    def _get_ratio(image_size, window_size):

        return max((
            math.ceil(image_size[0] / float(window_size[0])),
            math.ceil(image_size[1] / float(window_size[1]))
        ))

    def _get_window_size(self):

        window_size = self.driver.get_window_size()
        return window_size['width'], window_size['height']

    @property
    def baseline_dir(self):
        """Return baseline image path

        :return:
        :rtype: str
        """

        return self.options.get('baseline_dir', DEFAULT_BASELINE_DIR)

    @baseline_dir.setter
    def baseline_dir(self, value):
        """Set baseline image directory

        :param str value: File path
        :return:
        """

        assert isinstance(value, basestring)
        self.options['baseline_dir'] = value

    @property
    def engine(self):
        """Return image processing engine

        :return:
        """

        return self.import_from_string(self.engine_class)()

    @property
    def engine_class(self):
        """Return image processing engine name

        :return:
        :rtype: str
        """

        return self.ENGINES.get(self.options.get('needle_engine', 'imagemagick').lower(), DEFAULT_ENGINE)

    @engine_class.setter
    def engine_class(self, value):
        """Set image processing engine name

        :param str value: Image processing engine name (pil, imagemagick, perceptualdiff)
        :return:
        """

        assert value.lower() in self.ENGINES
        self.options['needle_engine'] = value.lower()

    @property
    def get_driver(self):
        return self.options.get('xbrowser', DEFAULT_BROWSER).lower()

    @get_driver.setter
    def get_driver(self, value):
        assert isinstance(value, basestring)
        self.options['xbrowser'] = value.lower()

    def resolution_screen(self, width=None, height=None):
        def page_length(x):
            return self.driver.execute_script('return document.body.parentNode.scroll' + x)

        if width is None:
            s_width = page_length('Width')
        else:
            s_width = width

        if height is None:
            s_height = page_length('Height')
        else:
            s_height = height

        return s_width, s_height

    def get_screenshot(self, element=None):
        """Returns screenshot image
        :param WebElement element: Crop image to element (Optional)
        :return:
        """
        time.sleep(2)
        stream = IOClass(base64.b64decode(self.driver.get_screenshot_as_base64().encode('ascii')))
        image = Image.open(stream).convert('RGB')

        if isinstance(element, WebElement):

            window_size = self._get_window_size()

            image_size = image.size

            # Get dimensions of element
            dimensions = self._get_element_dimensions(element)

            if not image_size == (dimensions['width'], dimensions['height']):
                ratio = self._get_ratio(image_size, window_size)

                return image.crop([point * ratio for point in self._get_element_rect(element)])

        return image

    def get_screenshot_as_image(self, element=None, exclude=None):
        """
        :param WebElement element: Crop image to element (Optional)
        :param list exclude: Elements to exclude
        :return:
        """

        image = self.get_screenshot(element)

        # Mask elements in exclude if element is not included
        # if isinstance(exclude, (list, tuple)) and exclude and not element:

        # Gather all elements to exclude
        elements = [self._find_element(element) for element in exclude]
        elements = [element for element in elements if element]

        canvas = ImageDraw.Draw(image)

        window_size = self._get_window_size()

        image_size = image.size

        ratio = self._get_ratio(image_size, window_size)

        for ele in elements:
            canvas.rectangle([point * ratio for point in self._get_element_rect(ele)],
                             fill=ImageColor.getrgb('black'))

        del canvas

        return image

    def prepare_window(self, width, height):
        self.driver.set_window_size(width, height)
        self.clear_site()

    def assert_screenshot(self, file_path, element_or_selector=None, threshold=0, exclude=None):
        """Fail if new fresh image is too dissimilar from the baseline image
        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L161
        :param str file_path: File name for baseline image
        :param element_or_selector: WebElement or tuple containing selector ex. ('id', 'mainPage')
        :param threshold: Distance threshold
        :param list exclude: Elements or element selectors for areas to exclude
        :return:
        """

        element = self._find_element(element_or_selector) if element_or_selector else None

        # Get baseline screenshot
        self._create_dir(self.baseline_dir)
        baseline_image = os.path.join(self.baseline_dir, '%s.png' % file_path) \
            if isinstance(file_path, basestring) else Image.open(file_path).convert('RGB')

        # Take screenshot and exit if in baseline saving mode
        if self.save_baseline:
            self.get_screenshot_as_image(element, exclude=exclude).save(baseline_image)
            return

        # Get fresh screenshot
        self._create_dir(self.output_dir)
        fresh_image = self.get_screenshot_as_image(element, exclude=exclude)
        fresh_image_file = os.path.join(self.output_dir, '%s.png' % file_path)
        fresh_image.save(fresh_image_file)

        # Error if there is not a baseline image to compare
        if not self.save_baseline and not isinstance(file_path, basestring) and not os.path.exists(baseline_image):
            raise IOError('The baseline screenshot %s does not exist. You might want to '
                          're-run this test in baseline-saving mode.' % baseline_image)

        # Compare images
        if isinstance(baseline_image, basestring):
            # try:
            value, output_width, output_height, baseline_width, baseline_height = self.engine.assertSameFiles(
                fresh_image_file, baseline_image, threshold)
            if isinstance(value, float):
                # if value <= threshold:
                #     par_dif = Path(fresh_image_file)
                #     filelist = [f for f in os.listdir(par_dif.parent) if f.endswith(".png")]
                #     for f in filelist:
                #         os.remove(os.path.join(par_dif.parent, f))
                #     return
                # else:
                raise AssertionError("The new screenshot did not match the baseline. Diff: {difference}. "
                                     "output_width: {output_width}, output_height: {output_height}, "
                                     "baseline_width: {baseline_width}, baseline_height: {baseline_height}"
                                     .format(difference=str(value * 100),
                                             output_width=output_width,
                                             output_height=output_height,
                                             baseline_width=baseline_width,
                                             baseline_height=baseline_height))
            else:
                raise AssertionError("Error {difference}. "
                                     "output_width: {output_width}, output_height: {output_height}, "
                                     "baseline_width: {baseline_width}, baseline_height: {baseline_height}"
                                     .format(difference=str(value),
                                             output_width=output_width,
                                             output_height=output_height,
                                             baseline_width=baseline_width,
                                             baseline_height=baseline_height))
        else:
            diff = ImageDiff(fresh_image, baseline_image)
            distance = abs(diff.get_distance())

            if distance > threshold:
                pytest.fail('Fail: New screenshot did not match the baseline (by a distance of %.2f)' % distance)

    @allure.step("Проводим сравнение screenshot'ов страницы {name}")
    def attach_img_allure(self, name, e):

        # когда стравниваемые скриншоты отличаются по размеру (меньше чем для ошибки)
        # imagemagick иногда обрезаемую часть сохраняет отдельной картинкой .diff-1.png
        # для тестов была сделана выборка из ".diff.png" или ".diff-0.png"

        x = str(e)
        if "did not match the baseline" in str(e):
            img_file = None
            done = False
            for d_name in [".diff.png", ".diff-0.png"]:
                for p_name in [DEFAULT_BASELINE_DIR_REM, DEFAULT_BASELINE_DIR_HAND_REM, DEFAULT_DOCKER_DIR]:
                    img_name = os.path.join(p_name, name + d_name)
                    if pathlib.Path(img_name).exists():
                        done = True
                        img_file = os.path.join(img_name)
                        break
                if done:
                    break

            if img_file is not None:
                self.zwait(str(os.path.exists(img_file)))
                img = Image.open(img_file, mode="r")
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="PNG")
                img_byte_arr = img_byte_arr.getvalue()
                allure.attach(
                    body=img_byte_arr,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
                raise e
        else:
            raise e

    @allure.step('Открываем страницу "{link}" на языке "{lang}"')
    def open_site_page_with_lang(self, cfg, link: str, lang: str):
        self.driver.get(f"{cfg['web']['url']}{link}?lang={lang}")
        self._wait_for_load()

    @allure.step('Открываем страницу {page}')
    def print_url(self, page):
        print(page)

    def get_current_url(self):
        return self.driver.current_url

    def stale_el(self, cfg, link: str, lang: str):
        with self._wait_for_staleness(timeout=5):
            self.open_site_page_with_lang(cfg, link, lang)

    def _wait_for_load(self):
        return self.wait(
            lambda d: self.driver.execute_script('return document.readyState') == 'complete',
            f"{self.__class__.__name__} can't complete load"
        )

    def _wait_for_onload(self):
        return self.wait(
            lambda d: self.driver.execute_script('window.onload=function(){}'),
            f"{self.__class__.__name__} can't complete load"
        )

    def _wait_for_hash(self, driver, sleep_time=2):
        '''Waits for page to completely load by comparing current page hash values.'''

        def get_page_hash(driver):
            # can find element by either 'html' tag or by the html 'root' id
            dom = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
            # dom = driver.find_element_by_id('root').get_attribute('innerHTML')
            dom_hash = hash(dom.encode('utf-8'))
            return dom_hash

        page_hash = 'empty'
        page_hash_new = ''

        # comparing old and new page DOM hash together to verify the page is fully loaded
        while page_hash != page_hash_new:
            page_hash = get_page_hash(driver)
            time.sleep(sleep_time)
            page_hash_new = get_page_hash(driver)

    @contextmanager
    def _wait_for_staleness(self, timeout=30):
        old_page = self.driver.find_element_by_tag_name('html')
        yield
        return self.wait(staleness_of(old_page))

    def clear_site(self):
        self._stop_animation()
        self._disable_chat()
        self._stop_video()
        self._delete_ads()
        self._hide_pops()

    def _stop_animation(self):  # динамический элемент tradeth
        self.driver.execute_script(
            'try { '
            '   document.querySelectorAll("*").forEach(element => {element.style.transition = "none";});'
            '}'
            'catch(e) {}'
        )

    def _disable_chat(self):  # чат
        self.driver.execute_script(
            'try { '
            'document.querySelector("#launcher").remove();'
            '}'
            'catch(e) {}'
        )

    def _stop_video(self):  # видео на заднем фоне
        self.driver.execute_script(
            'try { '
            '   document.querySelectorAll(".video").forEach(video => {video.pause(); video.currentTime = 0;})'
            '}'
            'catch(e) {}'
        )

    def _delete_ads(self):  # img google ads
        self.driver.execute_script(
            'try { '
            '   document.querySelectorAll("body > img").forEach(element => {element.remove();})'
            '}'
            'catch(e) {}'
        )

    def _hide_pops(self):  # GDPR pop-up
        self.driver.execute_script(
            'try { '
            '   document.querySelector(".js-gdpr-popup").remove();'
            '}'
            'catch(e) {}'
        )

    @property
    def wait(self):
        return self._wait

    def get_site_name(self, link, lang, width):
        return f'{link.replace("/", "_")}_{lang}_{width}'

    def import_from_string(self, path):
        """Recursively create a directory

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L36

        :param str path: engine to import
        :return:
        """

        module_name, klass = path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[klass])
        return getattr(module, klass)

    def zwait(cond, msg: str = "", retries: int = 10, delay: float = 1.0):
        """
        :param cond: лямбда-функция, в которой содержится код события, который мы ждём
        :param msg: сообщение, если мы не дождались события
        :param retries: кол-во попыток на проверку события
        :param delay: задержка при проверке события
        :return: если результатом выполнения лямбды будет значение типа bool, то мы проверяем, дождались мы события или нет
                 если результатом выполнения лямбы будет значение НЕ типа bool, то мы его просто возвращаем
        """
        actual_retries = 0
        result = None

        while 1:
            try:
                result = cond()
            except Exception:
                pass

            if result:
                break

            actual_retries += 1

            if actual_retries == retries:
                break

            if delay:
                time.sleep(delay)

        if isinstance(result, bool):
            assert result, msg
        else:
            return result

    @property
    def output_dir(self):
        """Return output image path

        :return:
        :rtype: str
        """

        return self.options.get('output_dir', DEFAULT_OUTPUT_DIR)

    @output_dir.setter
    def output_dir(self, value):
        """Set output image directory

        :param str value: File path
        :return:
        """

        assert isinstance(value, basestring)
        self.options['output_dir'] = value

    @property
    def save_baseline(self):
        """Returns True, if save baseline flag is set

        :return:
        :rtype: bool
        """

        return self.options.get('save_baseline', False)

    @save_baseline.setter
    def save_baseline(self, value):
        """Set save baseline flag

        :param bool value: Save baseline flag
        :return:
        """

        self.options['save_baseline'] = bool(value)

    @property
    def headless(self):
        """Returns True, if save headless flag is set

        :return:
        :rtype: bool
        """

        return self.options.get('headless', True)

    @headless.setter
    def headless(self, value):
        """Set headless flag

        :param bool value: Save baseline flag
        :return:
        """

        self.options['headless'] = bool(value)

    def set_viewport(self):
        """Set viewport width, height based off viewport size

        :return:
        """

        viewport_size = re.match(r'(?P<width>\d+)\s?[xX]\s?(?P<height>\d+)', self.viewport_size)

        viewport_dimensions = (viewport_size.group('width'), viewport_size.group('height')) if viewport_size \
            else DEFAULT_VIEWPORT_SIZE.split('x')

        self.driver.set_window_size(*[int(dimension) for dimension in viewport_dimensions])

    @property
    def viewport_size(self):
        """Return setting for browser window size

        :return:
        :rtype: str
        """

        return self.options.get('viewport_size', DEFAULT_VIEWPORT_SIZE)

    @viewport_size.setter
    def viewport_size(self, value):
        """Set setting for browser window size

        :param value: Browser window size, as string or (x,y)
        :return:
        """

        assert isinstance(value, (basestring, list, tuple))
        assert len(value) == 2 and all([isinstance(i, int) for i in value]) \
            if isinstance(value, (list, tuple)) else True
        self.options['viewport_size'] = value if isinstance(value, basestring) else '{}x{}'.format(*value)
