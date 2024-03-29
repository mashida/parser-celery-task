from celery_app.celery_app import process_pages

if __name__ == '__main__':

    pages = [
        'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1',
        'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=2',
        # Add more pages as needed
    ]
    process_pages(pages)
