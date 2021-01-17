from requests_html import HTML,HTMLSession
import csv

def getLinkInfo(url):
    session = HTMLSession()
    t = session.get(url)
    infoContainer = t.html.find(".bbWrapper")[0]

    try:
        try:
            location = infoContainer.search("Location: {}<br/>")[0]
        except TypeError:
            location = infoContainer.search("Location:{}<br/>")[0]

        try:
            age = infoContainer.search("Age: {}<br/>")[0]
        except TypeError:
            age = infoContainer.search("Age:{}<br/>")[0]

        try:
            price = infoContainer.search("Price: {}<br/>")[0]
        except TypeError:
            price = infoContainer.search("Price:{}<br/>")[0]
    except TypeError:
        return []

    return [price,age,location]

    # print(f"{age} for {price} in {location}")

def write_to_CSV(info):

    with open('carboniteDate.csv', mode='a') as dataFile:
        datafileWriter = csv.writer(dataFile, delimiter=';')
        datafileWriter.writerow(info)

session = HTMLSession()

urlParams = "&prefix_id=1&order=thread_fields_price&direction=desc"
url = "https://carbonite.co.za/index.php?forums/intel_cpu/" + urlParams
urlGlobal = "https://carbonite.co.za"
r = session.get(url)
# print(r.html.find("title")[0].text)

entriesContainer = r.html.find(".structItemContainer")
entries = entriesContainer[0].find(".structItem ")

for entry in entries:
    entryContainer = entry.find(".structItem-title")[0]
    title = entryContainer.find("a")[1].text
    typeOfSale = entryContainer.find("a")[0].text
    if typeOfSale == "[Reseller]" or typeOfSale == "[Wanted]" or typeOfSale == "[Feeler]"  :
        continue
    url = urlGlobal + str(entryContainer.find("a")[1].attrs["href"])
    # print(url)
    # print(typeOfSale)
    # print(f'{title} at {url}')

    info = [title] + getLinkInfo(url) + [url]

    print(info)

    write_to_CSV(info)

# print(r.html.find(".structItem structItem--thread is-prefix1 js-inlineModContainer js-threadListItem-339254"))

# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


