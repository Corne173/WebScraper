from requests_html import HTML,HTMLSession
import concurrent.futures
import csv
import re
import time

# Tutorial help on multithreading
# https://www.youtube.com/watch?v=IEEhzQoKtQU&ab_channel=CoreySchafer

def get_link_info(threadinfo):
    session = HTMLSession()
    url = threadinfo["url"]
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

    info = [title] + results + [ threadinfo["views"],threadinfo["replies"] ,lockedStatus , datetimePosted , url]
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
    data = []

    # within each post
    for entry in entries:
        entryContainer = entry.find(".structItem-title")[0]
        metaData = entry.find(".structItem-cell--meta")[0].find(".pairs")

        a = {}
        a["replies"] = metaData[0].text.replace("Replies\n","")
        a["views"]   = metaData[1].text.replace("Views\n","")


        title = entryContainer.find("a")[1].text
        typeOfSale = entryContainer.find("a")[0].text
        if typeOfSale == "[Reseller]" or typeOfSale == "[Wanted]" or typeOfSale == "[Feeler]":
            continue

        a["url"] = urlGlobal + str(entryContainer.find("a")[1].attrs["href"])
        data.append(a)

    return data




urlGlobal = "https://carbonite.co.za"
urlThreads = "?forums/nvidia_gpu/"
params = "&prefix_id=1&order=thread_fields_price&direction=desc"

# Script starts
session = HTMLSession()
r = session.get(urlGlobal + urlThreads + params)
# Gets the total number of pages
numberOfPages = int(r.html.find(".pageNav-page ")[-1].text)
print(f"Scraping {numberOfPages} pages")

# loops over total pages
for page in range(1,numberOfPages+1):
    url = f"{urlGlobal+urlThreads}page-{str(page)}{params}"

    print("Scraping: ",url)
    # gets all the links to each thread
    threads = scape_threads_for_links(url)

    with concurrent.futures.ThreadPoolExecutor() as executor:

        results = []
        for thread in threads:
            url = thread["url"]
            print("Scraping thread: ",url)
            # multi threading happens here
            results.append(executor.submit(get_link_info, thread))
            # sleep for 10ms. Dont want to punish their servers with 30 requests all at once (might get my your IP addr banned)
            time.sleep(0.1)
            break
        for f in concurrent.futures.as_completed(results):
            print(f.result())
            break
