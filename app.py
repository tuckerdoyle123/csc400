from flask import Flask, render_template, request
import requests
import sys 
import crossref_commons.retrieval
from crossref_commons.retrieval import get_entity
from crossref_commons.types import EntityType, OutputType
from functions import *

{
  "User-Agent": "<<polite user Daniel Ramirez; including mailto:ramirezd16@southernct.edu>>",
  "Mailto": "<<ramirezd16@southernct.edu>>"
}

app = Flask(__name__)

@app.route('/user_input', methods =["GET", "POST"])
def user_input():
    error_message = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        department = request.form.get("department")
        doi = request.form.get("doi")
        title = request.form.get("title")
        coauthors = request.form.get("coauthor")
        citations = request.form.get("citation")
        itemtype = request.form.get("typeRadios")
        peer_review = request.form.get("peergridRadios")

        if "@southernct.edu" not in email:
            error_message = "Invalid email address! Please use a valis SCSU email address."
        else:

            #Dictionary containing data that will be sent to Formspree
            formspree_endpoint = "https://formspree.io/f/moqozqve"  
            data = {
                "Name": name,
                "Email": email,
                "Department": department,
                "DOI": doi,
                "Title": title,
                "Coauthor": coauthors,
                "Citation": citations,
                "Item Type": itemtype,
                "Peer Review?": peer_review, 
            }
            response = requests.post(formspree_endpoint, data=data)

            #Dictionary that will contain user data formatted for Zotero
            user_dictionary = {}
            name_list = []
            title_list = []
            title_list.append(title)
            #Dictionary for name to match formatting of Crossref name convention
            name_dictionary = {}
            #Try Except to add citations and coauthors together for Zotero submission
            try:
                if citations and coauthors:
                    extra = "Citations: " + citations + ', ' + 'Coauthors: ' + coauthors
            except:
                pass
            try:
                if citations and not coauthors:
                    extra = "Citations: " + citations  
            except:
                pass
            try:
                if coauthors and not citations:
                    extra = 'Coauthors: ' + coauthors 
            except:
                pass
            x = name.split()#split to get first and last name of author
            name_dictionary["family"] = x[1]
            name_dictionary["given"] = x[0]
            name_list.append(name_dictionary)
            user_dictionary["title"] = title_list
            user_dictionary["type"] = itemtype
            user_dictionary["author"] = name_list
            #Department will be used for library catalog within Zotero
            try:
                user_dictionary["libraryCatalog"] = department
            except:
                pass
            try:
                user_dictionary["extra"] = extra
            except:
                pass
            if response.status_code == 200:
                #if user does not submit DOI, send dictionary with user input to Zotero
                if not doi:
                    formatDict(user_dictionary)
            #If user does submit DOI
                else:
                #will attempt to pull crossref with given DOI with dictionary of data
                    try:
                        data = get_entity(doi, EntityType.PUBLICATION, OutputType.JSON)
                        formatDict(data)
                #if doi is not in crossref, will send dictionary with user input to Zotero
                    except:
                        formatDict(user_dictionary)
                   
                return render_template("thank_you.html")
            else:
                return "Form submission failed. Please try again later."

    return render_template("index.html",error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)
