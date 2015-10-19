'''
Created on Oct 16, 2015

@author: django
'''
from xml.dom import minidom
 
doc = minidom.Document()
doc.appendChild(doc.createComment("base_component must be compatible with basecore type so basecore_ID should be specified here"))
booklist = doc.createElement("base_component")
doc.appendChild(booklist)
 
def addBook(newbook):
    book = doc.createElement("book")
    book.setAttribute("id", newbook["id"])
     
    title = doc.createElement("title")
    title.appendChild(doc.createTextNode(newbook["title"]))
    book.appendChild(title)
     
    author = doc.createElement("author")
    name = doc.createElement("name")
    firstname = doc.createElement("firstname")
    firstname.appendChild(doc.createTextNode(newbook["firstname"]))
    lastname = doc.createElement("lastname")
    lastname.appendChild(doc.createTextNode(newbook["lastname"]))
    name.appendChild(firstname)
    name.appendChild(lastname)
    author.appendChild(name)
    book.appendChild(author)
     
    pubdate = doc.createElement("pubdate")
    pubdate.appendChild(doc.createTextNode(newbook["pubdate"]))
    book.appendChild(pubdate)
     
    booklist.appendChild(book)
 
addBook({"id":"1001","title":"An apple","firstname":"Peter","lastname":"Zhang","pubdate":"2012-1-12"})
addBook({"id":"1002","title":"Love","firstname":"Mike","lastname":"Li","pubdate":"2012-1-10"})
addBook({"id":"1003","title":"Steve.Jobs","firstname":"Tom","lastname":"Wang","pubdate":"2012-1-19"})
addBook({"id":"1004","title":"Harry Potter","firstname":"Peter","lastname":"Chen","pubdate":"2012-11-11"})
 
f = open(r"C:\Users\zh\Desktop\book.xml","w")
doc.writexml(f)
f.close()
print('finished')
