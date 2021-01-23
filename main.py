from requests_html import HTML,HTMLSession
import csv
import re


def get_link_info(url):
    session = HTMLSession()
    t = session.get(url)
    infoContainer = t.html.find(".bbWrapper")[0]

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

    return results + [lockedStatus] + [datetimePosted]


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
    # print(r.html.find("title")[0].text)
    numberOfPages = r.html.find(".pageNav-page ")[-1].text

    entriesContainer = r.html.find(".structItemContainer")
    entries = entriesContainer[0].find(".structItem ")


    for entry in entries:
        entryContainer = entry.find(".structItem-title")[0]
        title = entryContainer.find("a")[1].text
        typeOfSale = entryContainer.find("a")[0].text
        if typeOfSale == "[Reseller]" or typeOfSale == "[Wanted]" or typeOfSale == "[Feeler]":
            continue

        url = urlGlobal + str(entryContainer.find("a")[1].attrs["href"])


        linkInfo = get_link_info(url)
        if linkInfo == None:
            continue

        info = [title] + linkInfo + [url]

        print(info)
        # break
        write_to_CSV(info)





urlParams = "&prefix_id=1&order=thread_fields_price&direction=desc"
urlThreads = "https://carbonite.co.za/index.php?forums/intel_cpu/"
urlGlobal = "https://carbonite.co.za"


session = HTMLSession()
r = session.get(urlThreads+urlParams)
numberOfPages = int(r.html.find(".pageNav-page ")[-1].text)
print(f"Scraping {numberOfPages} pages")

for page in range(1,numberOfPages+1):
    url = f"{urlThreads}page-{str(page)}{urlParams}"

    print("Scraping: ",url)
    scape_threads_for_links(url)

# scape_threads_for_links(url)

