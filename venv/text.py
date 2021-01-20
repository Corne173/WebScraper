from requests_html import HTML,HTMLSession
import csv
import re


def get_link_info(url):
    session = HTMLSession()
    t = session.get(url)
    infoContainer = t.html.find(".bbWrapper")[0]


    infoContainerText = infoContainer.text

    locationPtn = re.compile(r'Location: ?[^\n]+')
    agePtn = re.compile(r'Age: ?[^\n]+')
    pricePtn = re.compile(r'Price: ?[^\n]+')

    infosOfInterest = [locationPtn, agePtn, pricePtn]
    results = []

    for field in infosOfInterest:
        try:
            results.append(field.finditer(infoContainerText).__next__().group())
        except StopIteration:
            print(infoContainerText)
            return

    # print(location,age,price)


    return results

    # print(f"{age} for {price} in {location}")

def write_to_CSV(info):

    with open('carboniteDate.csv', mode='a') as dataFile:
        datafileWriter = csv.writer(dataFile, delimiter=';')
        datafileWriter.writerow(info)


a = "A string     \n with       newline chars"
print(a.replace('\n',''))

url = "https://carbonite.co.za/index.php?threads/gaming-pc.325796/"
url = "https://carbonite.co.za/index.php?threads/i5-9400f-r2000.339774/"
# print(url)
# print(typeOfSale)

linkInfo = get_link_info(url)
if linkInfo == None:
    pass

else:

    info  = linkInfo + [url]

    print(info)
# break
    write_to_CSV(info)

# print(r.html.find(".structItem structItem--thread is-prefix1 js-inlineModContainer js-threadListItem-339254"))

# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


