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

    forumName = t.html.find(".p-breadcrumbs")[0].text.replace("\n","-")

    lockedStatusData = t.html.find(".blockStatus-message")
    print(len(lockedStatusData))

    if len(lockedStatusData) < 2:
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
    write_to_CSV(info,forumName)
    return f"Done scraping {url}"


def write_to_CSV(info,fileName):
    try:
        with open(f'{fileName}.csv', mode='a',newline='') as dataFile:
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






url ="https://carbonite.co.za/index.php?threads/intel-9th-gen-core-i3-9100f-3-60-ghz.343752/"
# url ="https://carbonite.co.za/index.php?threads/intel-core-i3-8100-3-6ghz.344219/"
# Script starts
get_link_info( url)


