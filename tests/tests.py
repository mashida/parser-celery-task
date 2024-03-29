from unittest import TestCase, main
from unittest.mock import patch
from celery_app.celery_app import fetch_data, process_xml
from content import request_content

LINKS = ['https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0888500000224000117',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338100008224000003',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338300047924000069',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338300004724000036',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338300047924000073',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0188300000924000041',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0138100004724000008',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338200013924000081',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338200013924000080',
         'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338200013924000079']


class TestCeleryTasks(TestCase):

    @patch('requests.get')
    def test_fetch_data(self, mock_get):
        # Mock the response
        mock_get.return_value.content = request_content
        mock_get.return_value.status_code = 200

        # Call the function
        result = fetch_data('https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1')
        sample = LINKS

        # Assert the result
        self.assertEqual(result, sample)

    @patch('requests.get')
    def test_process_xml(self, mock_get):
        # Mock the response
        with open('xml_content.txt', 'r', encoding='utf-8') as f:
            mock_get.return_value.content = f.read().encode('utf-8')
        mock_get.return_value.status_code = 200

        # Call the function
        result = process_xml(
            'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0888500000224000117')
        sample = '2024-03-29T17:29:57.657+12:00'
        # Assert the result (this might require checking logs or mocking the logger)
        # For simplicity, we'll assume the function logs the result
        self.assertEqual(result, sample)


class TestCeleryIntegration(TestCase):

    @patch('requests.get')
    def test_integration(self, mock_get):
        # Mock the fetch_data response
        mock_get.return_value.content = request_content
        mock_get.return_value.status_code = 200

        # Call the fetch_data task
        links = fetch_data('https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1')

        # Assert the result of fetch_data
        self.assertEqual(links, LINKS)

        # Mock the process_xml response
        with open('xml_content.txt', 'r', encoding='utf-8') as f:
            mock_get.return_value.content = f.read().encode('utf-8')
        mock_get.return_value.status_code = 200

        # Call the process_xml task
        result = process_xml(links[0])
        sample = '2024-03-29T17:29:57.657+12:00'
        # Assert the result of process_xml (this might require checking logs or mocking the logger)
        # For simplicity, we'll assume the function logs the result
        self.assertEqual(result, sample)


if __name__ == '__main__':
    main()
