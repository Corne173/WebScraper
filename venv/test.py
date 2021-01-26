from requests_html import HTML,HTMLSession
import concurrent.futures
import csv
import re
import time


def get_link_info(url):
    session = HTMLSession()
    t = session.get(url)

    # get the title. Bit of a messy way but it works
    titleData = t.html.find(".p-title-value")[0].text
    title = re.match(r'\[\w+\] ?(.+)',titleData).group(1).strip()

    # get the container containing the info of interest
    infoContainer = t.html.find(".bbWrapper")[0]
    # get the datetime it was posted
    datetimePosted = t.html.find("time")[0].attrs["datetime"]

    lockedStatusData = t.html.find("blockStatus-message blockStatus-message--locked")
    if len(lockedStatusData) == 0:
        lockedStatus = "Open"
    else:
        lockedStatus = "Closed"

    infoContainerText = infoContainer.text

    locationPtn = re.compile(r'Location: ?([^\n]+)')
    agePtn = re.compile(r'Age: ?([^\n]+)')
    pricePtn = re.compile(r'Price: ?([^\n]+)')
    conditionPtn = re.compile(r'Condition: ?([^\n]+)')

    infosOfInterest = [locationPtn, agePtn, pricePtn, conditionPtn]
    results = []

    for field in infosOfInterest:
        try:
            data = field.finditer(infoContainerText).__next__().group(1)
            results.append(data)
        except StopIteration:
            print(infoContainerText)
            return

    # print(location,age,price)

    info = [title] + results + [lockedStatus] + [datetimePosted]
    print(info)
    write_to_CSV(info)
    return f"Done scraping {url}"


def write_to_CSV(info):
    try:
        with open('carboniteDate.csv', mode='a',newline='') as dataFile:
            datafileWriter = csv.writer(dataFile, delimiter=';')
            datafileWriter.writerow(info)
    except UnicodeEncodeError:
        print("UnicodeEncodeError due to emojies. Entry ignored")

def scape_threads_for_links(url):
    session = HTMLSession()
    r = session.get(url)

    # Looks for all posts/threads on forum
    entriesContainer = r.html.find(".structItemContainer")
    entries = entriesContainer[0].find(".structItem ")
    threadLinks = []
    # within each post
    for entry in entries:
        entryContainer = entry.find(".structItem-title")[0]
        title = entryContainer.find("a")[1].text
        typeOfSale = entryContainer.find("a")[0].text
        if typeOfSale == "[Reseller]" or typeOfSale == "[Wanted]" or typeOfSale == "[Feeler]":
            continue

        url = urlGlobal + str(entryContainer.find("a")[1].attrs["href"])
        threadLinks.append(url)

    return threadLinks






urlParams = "&prefix_id=1&order=thread_fields_price&direction=desc"
urlThreads = "https://carbonite.co.za/index.php?forums/intel_cpu/"
urlGlobal = "https://carbonite.co.za"


# Script starts
session = HTMLSession()
r = session.get(urlThreads+urlParams)
# Gets the total number of pages
numberOfPages = int(r.html.find(".pageNav-page ")[-1].text)
print(f"Scraping {numberOfPages} pages")

# loops over total pages
for page in range(1,numberOfPages+1):
    url = f"{urlThreads}page-{str(page)}{urlParams}"

    print("Scraping: ",url)
    # gets all the links to each thread
    threadLinks = scape_threads_for_links(url)

    with concurrent.futures.ThreadPoolExecutor() as executor:

        results = []
        for url in threadLinks:
            print("Scraping thread: ",url)
            # multi threading happens here
            results.append(executor.submit(get_link_info, url))
            # sleep for 10ms. Dont want to punish their servers with 30 requests all at once (might get my your IP addr banned)
            time.sleep(0.01)

        for f in concurrent.futures.as_completed(results):
            print(f.result())





            # scape_threads_for_links(url)

