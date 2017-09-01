import requests, webbrowser, re, sys


def return_source_code(site):
    c = {"beget" : "begetok"}
    res = requests.get(site, cookies=c)
    res.encoding = "cp1250"
    return res.text


def find_acestream_link(source):
    begin = source.find("acestream://") #find beggining of acestream link
    end = source.find('\"', begin)      #find the end of acestream link
    return source[begin:end]


def open_stream(channel):
    if not 1 <= channel <= 35:
        return

    guide = return_source_code("http://arenavision.in/guide")     #site with urls to channels

    line = guide.find("ArenaVision " + str(channel))             #find the line with url to channel
    href_end = guide.rfind('\"', 0, line)                           #quotation mark ending href
    href_begin = guide.rfind('\"', 0, href_end)                     #quotation mark opening href

    href = guide[href_begin + 1 : href_end]
    src = return_source_code("http://arenavision.in" + href)

    link = find_acestream_link(src)
    webbrowser.open(link)


def find_channel(key):
    key = key.upper()
    page = return_source_code("http://arenavision.in/guide")    #get the source code
    page = page[page.find("EVENTS GUIDE"):]                     #cut everything prior to table
    page = page[page.find(key):]                                #cut everything prior to searched term
    page = page[page.find(r"</td>") + 5:]                       #cut out searched term
    page = page[:page.find(r"CEST")]                            #cut the page to beggining of the next row

    return re.findall(r"[1-3][0-9] \[...\]|[0-9] \[...\]|[1-3][0-9]-[1-3][0-9] \[...\]|[0-9]-[0-9] \[...\]", page) #find all channels steaming the event

team = ""
if len(sys.argv) > 1:
    team = sys.argv[1]

while len(find_channel(team)) == 0 and team != "*":         #repeat questioning, if term not found, * is wildcard
    team = input("Pass searched term\n")

if team != "*":                                                 #* is wildcard
    print(find_channel(team))

chnl = input("Pass index of the channel\n")
open_stream(int(chnl))