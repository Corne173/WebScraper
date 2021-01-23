from requests_html import HTML,HTMLSession
import csv
import re


def get_link_info(url):
    session = HTMLSession()
    t = session.get(url)
    infoContainer = t.html.find(".bbWrapper")[0]

    datetimePosted = t.html.find("time")[0].attrs["datetime"]
    lockedStatusData = t.html.find("blockStatus-message blockStatus-message--locked")
    print(lockedStatusData)
    if len(lockedStatusData) == 0:
        lockedStatus = "Open"
    else:
        lockedStatus = "Closed"

    infoContainerText = infoContainer.text

    locationPtn = re.compile(r'Location: ?([^\n]+)')
    agePtn = re.compile(r'Age: ?([^\n]+)')
    pricePtn = re.compile(r'Price: ?([^\n]+)')
    conditionPtn = re.compile(r'Condition: ?([^\n]+)')

    infosOfInterest = [locationPtn, agePtn, pricePtn,conditionPtn]
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

    # print(f"{age} for {price} in {location}")

def write_to_CSV(info):

    with open('carboniteDate.csv', mode='a') as dataFile:
        datafileWriter = csv.writer(dataFile, delimiter=';')
        datafileWriter.writerow(info)

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)


url = "https://carbonite.co.za/index.php?threads/intel-9th-gen-core-i5-9400f-2-90ghz-turbo-boost-4-10ghz.334419/"
# url = "https://carbonite.co.za/index.php?threads/i7-7700-3-60-ghz-r3000-shipping-included.318718//"
# print(url)
# print(typeOfSale)

linkInfo = get_link_info(url)
if linkInfo == None:
    pass

else:

    info  = linkInfo + [url]

    print(info)
# break
    try:
        write_to_CSV(info)
    except UnicodeEncodeError:
        print("UnicodeEncodeError. Entry ignored")

# print(r.html.find(".structItem structItem--thread is-prefix1 js-inlineModContainer js-threadListItem-339254"))

# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


