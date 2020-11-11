# Wikipedia page stored in MongoDB
import wikipedia
import json
import pymongo as pm
import PySimpleGUI as sg

# endpoint https://en.wikipedia.org/w/api.php
from bson import ObjectId


def get_wikipedia_page(name):
    print(name)
    try:
        page = wikipedia.page(name)
        print(page.title)
        print(page.content)
    except:
        page = None
    return page

def convert_to_json(page):
    page_json_style = {
        "_id": page.title,
        "data": [
            {
                # full page content as string
                "content": page.content,
                # internal links with page name
                "links": page.links,
                # url to images
                "images": page.images,
                # url to references
                "references": page.references
            }
        ]
    }
    return page_json_style
    # json_page = json.dumps(page_json_style)
    # return json_page

    # # returns entire text content of page
    # print(page.content)
    # # returns some form of categories?
    # print(page.categories)
    # # returns all internal links name = link
    # print(page.links)
    # # returns all links to images
    # print(page.images)
    # # returns references
    # print(page.references)
    # # seems to return empty array
    # print(page.sections)
    # # title
    # print(page.title)
    # # pageid
    # print(page.pageid)


def add_page_mongo(json, table):
    try:
        table.insert_one(json)
        return True
    except:
        return False



# to start serving mongod --noauth --dbpath /home/jeremy/mongodb/data/db
def connect_to_database():
    # local hosted mongodb
    myclient = pm.MongoClient("mongodb://localhost:27017/")
    # connect to database
    mydb = myclient["mydatabase"]
    # print(myclient.list_database_names())
    return mydb


def display_page(name, mongo):
    posts = mongo.posts
    # info = posts.find_one({"_id": name})
    print(name)
    info = mongo.pages.find_one({"_id": name})
    for item in info:
        print(item)
    print(info["data"])
    print("f")
    page_name = info["_id"]
    data = info["data"][0]
    content = str(data["content"])
    links = str(data["links"])
    images = str(data["images"])
    references = str(data["references"])
    return page_name, content, links, images, references



def main_window(mongo):
    layout = [[sg.Text("Choose an option")], [sg.Button("Add a page"), sg.InputText('Enter page name here', key='input')],
              [sg.Button("View all pages")], [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="_LISTBOX_")],
              [sg.Button("Exit")]]
    window = sg.Window(title="Wikipedia Pages", layout=layout)

    # event loop for window
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Add a page":
            # here we will allow users to add a page
            # get value from textbox
            name = window.Element("input").get()
            page = get_wikipedia_page(name)
            if page is not None:
                json = convert_to_json(page)
                if add_page_mongo(json, mongo["pages"]):
                    # set content of text box to page.title added successfully
                    # window.Element("textbox").set(name + " page was added successfully.")
                    print("success")
                else:
                    # window.Element("textbox").set(name + " page was not found.")
                    print("failed while adding page to mongo")
            else:
                # window.Element("textbox").set(name + " page was not found.")
                print("failed to find page")
        elif event == "View all pages":
            # here we will display a list of all pages
            # get values
            list_pages = get_all_pages(mongo["pages"])
            # populate listbox
            window.Element('_LISTBOX_').Update(values=list_pages)
        elif values['_LISTBOX_']:    # if something is highlighted in the list
            # grab values and pass
            print(values['_LISTBOX_'][0])
            page_name, content, links, images, references = display_page(values['_LISTBOX_'][0], mongo)
            # sg.popup(f"Your selected page is {values['_LISTBOX_'][0]}", no_titlebar=True)
            sg.popup_scrolled(page_name + "\n" + content + "\nInternal Links\n" + links + "\nLinks to Images\n" + images + "\nLinks to References\n" + references, no_titlebar=True)

    window.close()


def get_all_pages(pages):
    # use pages to return id of all elements
    id_list = pages.find().distinct('_id')
    return id_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mongo = connect_to_database()
    # create/connect to a collection called customers
    # page = get_wikipedia_page("Banana")
    # json = convert_to_json(page)
    main_window(mongo)
    # add_mongo(json, pages)


