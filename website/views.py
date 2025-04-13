from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from sqlalchemy import desc

from .models import ViewedPaperHistory, SearchHistory, ConferenceSearchHistory
from . import Scraper
from . import API
from website import db
import logging
import re

import pytz
from datetime import datetime

views = Blueprint('views', __name__)

@views.route("/conferences", methods=['GET', 'POST'])
@login_required
def conferences_page():
    if request.method == 'POST':
        query = request.form.get("query")
        if query:
            history = ConferenceSearchHistory(query=query, user_id=current_user.id)
            db.session.add(history)
            db.session.commit()
    return render_template('conferences.html')

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/feed', methods=['GET'])
def feed():
    return render_template('socialmedia.html', user=current_user)

@views.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form['query']
        abstracts = Scraper.fetch_arxiv_abstracts(query)
        if abstracts:
            history = SearchHistory(query=query, user_id=current_user.id)
            db.session.add(history)
            db.session.commit()
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

@views.route("/history")
@login_required
def history():
    india = pytz.timezone('Asia/Kolkata')

    viewed_papers = db.session.query(ViewedPaperHistory)\
        .filter(ViewedPaperHistory.user_id == current_user.id)\
        .order_by(desc(ViewedPaperHistory.timestamp)).limit(10).all()

    recent_queries = db.session.query(SearchHistory)\
        .filter(SearchHistory.user_id == current_user.id)\
        .order_by(desc(SearchHistory.timestamp)).limit(10).all()

    conference_queries = db.session.query(ConferenceSearchHistory)\
        .filter(ConferenceSearchHistory.user_id == current_user.id)\
        .order_by(desc(ConferenceSearchHistory.timestamp)).limit(10).all()

    grants_viewed = db.session.query(GrantViewHistory)\
        .filter(GrantViewHistory.user_id == current_user.id)\
        .order_by(desc(GrantViewHistory.timestamp)).limit(10).all()

    # ⏰ Convert all timestamps to IST
    for item in viewed_papers + recent_queries + conference_queries + grants_viewed:
        item.timestamp = item.timestamp.astimezone(india)

    return render_template("history.html", 
        viewed_papers=viewed_papers, 
        recent_queries=recent_queries, 
        conference_queries=conference_queries,
        grants_viewed=grants_viewed)
        
@views.route("/view_paper")
@login_required
def view_paper():
    title = request.args.get("title")
    url = request.args.get("url")
    if title and url:
        history = ViewedPaperHistory(title=title, url=url, user_id=current_user.id)
        db.session.add(history)
        db.session.commit()
        return redirect(url)
    return "Invalid request", 400

from .models import GrantViewHistory

@views.route('/view_grant')
@login_required
def view_grant():
    title = request.args.get("title")
    url = request.args.get("url")
    if title and url:
        history = GrantViewHistory(title=title, url=url, user_id=current_user.id)
        db.session.add(history)
        db.session.commit()
        return redirect(url)
    return "Invalid grant", 400
