from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import Scraper
from . import API
import logging
import re

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/feed', methods=['GET'])
def feed():
    return render_template('socialmedia.html', user=current_user)

@views.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        abstracts = Scraper.fetch_arxiv_abstracts(query)
        if abstracts:
            return render_template("results.html", abstracts=abstracts)
        else:
            return "No results found", 404
    return render_template('search.html')

@views.route('/grants')
def grants():
    return render_template('grants.html')

@views.route('/process', methods=['POST'])
def process_abstracts():
    try:
        query = request.form['query']
        abstracts = Scraper.fetch_arxiv_abstracts(query)
        if not abstracts:
            return "No abstracts found to process.", 404

        long_text = " ".join([abstract[1] for abstract in abstracts])
        logging.debug(f"Long text prepared: {long_text[:60]}...")

        API.configure_api()
        model = API.setup_model()
        summaries = [API.summarize_text(model, long_text)]
        processed_summaries = [process_summary_text(summary) for summary in summaries]
        return render_template("AI.html", summaries=processed_summaries)
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        return str(e), 500

@views.route('/qa', methods=['POST'])
def ask_summary_question():
    context = request.form.get('context')
    question = request.form.get('question')

    if not context or not question:
        return "Missing context or question", 400

    API.configure_api()
    model = API.setup_model()
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    answer = API.summarize_text(model, prompt)

    return render_template("AI.html", summaries=[context], answer=answer)

def process_summary_text(summary):
    summary = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", summary)
    summary = summary.replace("* ", "<br>")
    return summary
