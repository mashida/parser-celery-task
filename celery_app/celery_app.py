from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import requests
from io import StringIO
from celery import Celery, group
from celery.utils.log import get_task_logger

app = Celery('my_project', broker='pyamqp://guest@localhost//')

logger = get_task_logger(__name__)

HEADERS: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Cookie': 'userRegionName=%D0%92%D0%BE%D0%BB%D0%BE%D0%B3%D0%BE%D0%B4%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C; yandexRegionName=Vologda%20Oblast%2C%20Cherepovets; detectedRegionId=null; doNotShowKladrPopUp=true; userRegionId=5277340; doNotAdviseToChangeLocation=true; selectElementName=%D0%92%D0%BE%D0%BB%D0%BE%D0%B3%D0%BE%D0%B4%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'}


@app.task
def fetch_data(url: str) -> list[str]:
    links_result: list[str] = []
    result = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(result.content, "html.parser")
    products = soup.find_all('div',
                             class_=['w-space-nowrap', 'ml-auto', 'registry-entry__header-top__icon'])
    for product in products:
        a_tags = product.find_all('a', href=True)  # Find all <a> tags with a href attribute
        if len(a_tags) > 1:  # Check if there are at least two <a> tags
            second_a_tag: str = a_tags[1]['href']  # Select the second <a> tag
            second_a_tag = 'https://zakupki.gov.ru' + second_a_tag.replace('view.html', 'viewXml.html')
            links_result.append(second_a_tag)
            logger.info(f'{second_a_tag=}')  # Print the href attribute of the second <a> tag

    return links_result


def get_namespaces(xml_string):
    namespaces = dict([
        node for _, node in ET.iterparse(
            StringIO(xml_string), events=['start-ns']
        )
    ])
    namespaces["ns0"] = namespaces[""]
    return namespaces


COUNTER: int = 0


@app.task
def process_xml(page: str) -> str:
    global COUNTER
    xml_content = requests.get(page, headers=HEADERS)
    with open(f'xml_{COUNTER}.txt', 'wb') as f:
        f.write(xml_content.content)
        COUNTER = COUNTER + 1
    logger.info(f'process_xml | {xml_content.content=}')
    root = ET.fromstring(xml_content.content.decode('utf-8'))
    namespaces = get_namespaces(xml_content.content.decode('utf-8'))

    xml = root.find('.//ns0:publishDTInEIS', namespaces)

    logger.info(xml.text if xml is not None else None)
    return xml.text if xml is not None else ""


def process_pages(pages: list[str]) -> None:
    # For each page, fetch the data and then process each link individually
    tasks = [group(process_xml.s(link) for link in fetch_data(page)) for page in pages]

    # Execute all tasks
    for task in tasks:
        task.apply_async()
