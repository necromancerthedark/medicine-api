import re
import requests
from bs4 import BeautifulSoup
import itertools
import concurrent.futures

MAX_THREAD = 40

products = {}


def scraperdata(product, flag, header):
    regexTitle = re.compile('.*style__pro-title.*')
    regexLink = re.compile('.*style__product-link.*')
    regexQuantity = re.compile('.*style__pack-size.*')
    regexRating = re.compile('.*CardRatingDetail.*')
    regexPrice = re.compile('.*style__price-tag.*')
    regexDisccount = re.compile('.*style__off-badge.*')
    # scrapping attributes
    if flag == 1:
        title = product.find('span', class_=regexTitle).text
    else:
        title = product.find('div', class_=regexTitle).text

    if flag == 1:
        link = link = "https://www.1mg.com" + product.find('a')['href']
    else:
        link = "https://www.1mg.com" + \
            product.find('a', class_=regexLink)['href']
    # with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    data = scrapIndividualProduct(link, header)
    # data = executor.map(scrapIndividualProduct, link, header)

    quantity = product.find('div', class_=regexQuantity).text

    ratings = product.find('span', class_=regexRating)
    ratings = ratings.text if ratings != None else None  # if rating is not available

    price = product.find('div', class_=regexPrice).text

    discount = product.find('span', class_=regexDisccount)
    # if discount is not available
    discount = discount.text if discount != None else None

    # storing details
    object = {}  # individual product item
    object['title'] = title
    object['link'] = link
    object['quantity'] = quantity
    object['ratings'] = ratings
    object['price'] = price
    object['discount'] = discount
    object['composition'] = data['composition']
    object['usages'] = data['usages']
    object['sideEffects'] = data['sideEffects']
    object['safetyAdvice'] = data['safetyAdvice']
    object['alternateBrand'] = data['alternateBrand']
    object['expiry'] = data['expiry']

    products[title] = object  # storing an individual product


def scrapIndividualProduct(url, header):
    html = requests.get(url=url, headers=header)
    soup = BeautifulSoup(html.text, 'lxml')

    regexComposition = re.compile('.*saltInfo DrugHeader__meta-value.*')
    regexUsages = re.compile('.*DrugOverview__content.*')
    regexSideEffect = re.compile('.*DrugOverview__list-container.*')
    regexSafetyAdvice = re.compile('.*DrugOverview__warning-top.*')
    regexAlternateBrand = re.compile('.*SubstituteItem__name___PH8Al.*')
    regexExpiryDate1 = re.compile('.*DrugPage__vendors.*')
    regexExpiryDate2 = re.compile('.*VendorInfo__container.*')

    composition = soup.find('div', class_=regexComposition)
    # if composition is not available
    composition = composition.text if composition != None else None

    usages1 = soup.find('div', id='how_to_use')
    if usages1 != None:
        usages1 = usages1.find('div', class_=regexUsages)
        usages1 = usages1.text if usages1 != None else None  # if usages is not available
        usages = usages1
    else:
        usages2 = soup.find('div', class_=regexUsages)
        usages = usages2

    sideEffects = soup.find('div', class_=regexSideEffect)
    # if sideEffe#cts is not available
    sideEffects = sideEffects.text if sideEffects != None else None
    if sideEffects != None:
        sideEffects = [s for s in re.split("([A-Z][^A-Z]*)", sideEffects) if s]

    safetyAdvice = soup.find_all('div', class_=regexSafetyAdvice)
    safetyAdvice = [sa.span.text for sa in safetyAdvice]
    # safetyAdvice = safetyAdvice.text if safetyAdvice != None else None # if safetyAdvice is not available

    alternateBrand = soup.find('div', class_=regexAlternateBrand)
    # if alternateBrand is not available
    alternateBrand = alternateBrand.text if alternateBrand != None else None

    expiryDate = soup.find('div', class_=regexExpiryDate1)
    if expiryDate != None:
        expiryDate = expiryDate.div.text
    else:
        expiryDate = soup.find('div', class_=regexExpiryDate2)
        if expiryDate != None:
            expiryDate = expiryDate.div.text
    try:
        expiryDate = re.search(': *[a-zA-Z]*, \d{4}', expiryDate)
        expiryDate = expiryDate.group(0)[3:] if expiryDate else 'None'
    except:
        expiryDate = None
    data = {'composition': composition, 'usages': usages, 'sideEffects': sideEffects,
            'safetyAdvice': safetyAdvice,                   'alternateBrand': alternateBrand, 'expiry': expiryDate}
    return data


def scrapData(soup, header):

    flag = 0
    regexProductBox1 = re.compile(
        '.*style__product-box.*')  # for combiflam type UI
    regexProductBox2 = re.compile(
        '.*style__horizontal-card.*')  # for paracetamol type UI

    scrappedProducts = soup.find_all(
        'div', class_=regexProductBox1)   # all products on page
    if len(scrappedProducts) == 0:
        flag = 1
        scrappedProducts = soup.find_all('div', class_=regexProductBox2)

    threads = min(MAX_THREAD, len(scrappedProducts))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(scraperdata, scrappedProducts,
                     itertools.repeat(flag), itertools.repeat(header))

    return products
