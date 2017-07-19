import codecs
import pydoc
import re
import sys
import imp

from bs4 import BeautifulSoup

# TODO : Use rootdir, Make code pretty again

def load_html_file(dir):
    f = codecs.open(dir, 'r')
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def is_module_link(link):
    if link is None:
        return False
    if "group" not in link:
        return False
    if "#" in link:
        return False

    return True


def get_links_list(soup):
    href_list = []
    for link in soup.findAll('a'):
        tmp_href = link.get('href')
        if is_module_link(tmp_href):
            href_list.append(tmp_href)

    return href_list


def output_help_to_file(file_path, request):
    f = file(file_path, 'w')
    sys.stdout = f
    pydoc.help(request)
    f.close()
    sys.stdout = sys.__stdout__
    return

def get_signature_to_string(file_path, function_name):
    with open(file_path, 'r') as fin:
        for i, line in enumerate(fin):
            if function_name+"(" and "," in line:
                return line

    return ""

try:
    imp.find_module('cv2')
except ImportError:
    print 'You have not installed the cv2 module'
    sys.exit(-1)

root_dir = sys.argv[1]

# use index.html to get modules
soup = load_html_file(root_dir + "index.html")
href_list = get_links_list(soup)

for link in href_list:
    if "group__imgproc" in link:

        # get the sub-modules
        soup = load_html_file(root_dir + link)
        sub_href_list = get_links_list(soup)

        # get the right link to a sub-module html file
        link = re.sub(r"group__.+html","",link)
        for sub_link in sub_href_list:
            if "group__imgproc__filter" in sub_link:
                soup = load_html_file(root_dir + link + sub_link)
                for function in soup.findAll("h2", {"class": "memtitle"}):
                    # get function_name from html element
                    function_name = function.getText()

                    if "()" not in function_name:
                        continue
                    else:
                        function_name = function_name.replace(' ', '')[2:-2]
                        print function_name

                        output_help_to_file(r'tmp_file.txt', str("cv2." + function_name + ""))
                        signature = get_signature_to_string('tmp_file.txt', function_name)

                        if signature != "":
                            print signature
                            cpp_table = function.findNext('table')

                            new_table = soup.new_tag('table')
                            new_row = soup.new_tag('tr')

                            ## Add elements
                            new_item = soup.new_tag('th')
                            new_item.append('Python:')
                            new_row.append(new_item)

                            if "->" in signature:
                                new_item = soup.new_tag('td')
                                new_item.append('dst =') # what's after ->
                                new_row.append(new_item)

                            new_item = soup.new_tag('td')
                            new_item.append('cv2.'+function_name+'(')
                            new_row.append(new_item)

                            new_item = soup.new_tag('td', ** {'class': 'paramname'})
                            new_item.append('src, d, sigmaColor, sigmaSpace[, dst[, borderType]]') # what's inside
                            new_row.append(new_item)

                            new_item = soup.new_tag('td')
                            new_item.append(')')
                            new_row.append(new_item)

                            new_table.append(new_row)

                            # insert the new table after the current table
                            cpp_table.insert_after(new_table)

                        #print quote2.text

with open("output1.html", "w") as file:
    file.write(str(soup))