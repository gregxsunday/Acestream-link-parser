import requests, webbrowser, re, sys, pyperclip

the_url = 'http://arenavision.us'

def return_source_code(site):
    c = {"beget" : "begetok"}       #required on all sites on this domain
    res = requests.get(site, cookies=c)
    res.encoding = "cp1250"
    return res.text


def find_acestream_link(source):
    begin = source.find("acestream://") #find beggining of acestream link
    end = source.find('\"', begin)      #find the end of acestream link
    return source[begin:end]


def find_site_with_link(channel, guide_url):
    if not 1 <= channel <= 42:
        return

    guide = return_source_code(guide_url)     #site with urls to channels

    line = guide.find("ArenaVision " + str(channel))             #find the line with url to channel
    href_begin = guide.rfind(r'href="', 0, line) + 6                   #href beggining
    href_end = guide.find('\"', href_begin)  # quotation mark ending href

    href = guide[href_begin : href_end]

    if 'http://' in href:       #distinguishing relative and absolute hrefs
        src = return_source_code(href)
    else:
        src = return_source_code(the_url + href)

    #src is source code of the chosen channel's site

    return find_acestream_link(src)


def find_channel(key, guide_url):
    key = key.upper()
    page = return_source_code(guide_url)    #get the source code

    page = page[page.find("EVENTS GUIDE"):]                     #cut everything prior to table

    #getting the part between the first column and the keyword
    prior_to_key = page[:page.find(key)]
    prior_to_key = prior_to_key[prior_to_key.rfind(r"CEST") - 6:]        #CET timezone is the begging of the row

    #getting the part behind the keyword up to the hour of next evet
    past_key = page[page.find(key):]
    past_key = past_key[:past_key.find(r"CEST")]

    hour = prior_to_key[:5]
    page = prior_to_key + past_key        #concatinating the whole row with the proper event

    # find all channels steaming the event
    ch = re.findall(r"[1-3][0-9] \[...\]|[0-9] \[...\]|[1-3][0-9]-[1-3][0-9] \[...\]|[0-9]-[0-9] \[...\]", page)
    if len(ch) == 0:
        return ''

    page = page[:page.find(ch[0])]

    lines = page.split('\n') #divide properties of the event
    lines = lines[1:-1]  #cut out hour and channel, as they are separate variables

    #cut out </td> at the end of each line and then the rest of html
    for idx, line in enumerate(lines):
        lines[idx] = line[:-5]
        lines[idx] = lines[idx][lines[idx].rfind('>') + 1:]

    return 'Event: ' + str(lines)[1:-1] + '\nHour: ' + hour + '\nChannels: ' + str(ch)[1:-1] + '\n'


def find_guide_site():
    #first check the path found previously
    # with open(r"D:\Program Files\Ace\Acestream-link-parser\acestream\prv_guide_url.txt", 'r') as prv_guide_url_file:
    #     prv_guide_url = prv_guide_url_file.read()
    #     if len(prv_guide_url) != 0:
    #         req = requests.head(prv_guide_url)
    #         if req.status_code == 200:
    #             print(prv_guide_url)
    #             return prv_guide_url

    #previous url is invalid, let's find the proper one

    #working on raw html, to cut out url to the guide
    main_source = return_source_code(the_url)
    main_source = main_source[ : main_source.find('EVENTS GUIDE') - 2]
    href = main_source[main_source.rfind(r'href="') + 6 :]

    #distinguishing between relative and absolute urls
    if 'http://' in href:
        cr_guide_url = href
    else:
        cr_guide_url = the_url + href

    #overwrite url in the file
    with open(r"D:\Program Files\Ace\Acestream-link-parser\acestream\prv_guide_url.txt", 'w') as prv_guide_url_file:
        prv_guide_url_file.write(cr_guide_url)

    return cr_guide_url


if __name__ == "__main__":
    team = ""
    if len(sys.argv) > 1:
        team = sys.argv[1]

    guide_url = find_guide_site()

    while team == '' or (team != "*" and len(find_channel(team, guide_url)) == 0):         #repeat questioning, if term not found; * is wildcard
        team = input("Pass searched term\n")

    if team != "*":                                                 #* is wildcard
        print(find_channel(team, guide_url))

    inp = input("Pass index of the channel\n").split(' ') #if 'number' open channel, if 'number C' copy link

    chnl = inp[0]
    link = find_site_with_link(int(chnl), guide_url)

    if len(inp) > 1 and inp[1].upper() == 'C':
        pyperclip.copy(link)
        print("Link: " + link + ", copied.")
    else:
        print('Link: ' + link + ', opened.')
        webbrowser.open(link)