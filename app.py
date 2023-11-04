from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        doi = request.form['doi']
        title = request.form['title']
        coauthor = request.form['coauthor']
        studentauthor = request.form['studentauthor']
        citation = request.form['citation']
        gridRadios = request.form['gridRadios']

        formspree_endpoint = "https://formspree.io/f/mrgwdgbk"
        
        data = {
            "name": name,
            "email": email,
            "department": department,
            "doi": doi,
            "title": title,
            "coauthor": coauthor,
            "studentauthor": studentauthor,
            "citation": citation,
            "gridRadios": gridRadios, 
        }
        response = requests.post(formspree_endpoint, data=data)

        if response.status_code == 200:
            return render_template("thank_you.html")
        else:
            return "Form submission failed. Please try again later."
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)