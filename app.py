from transformers import pipeline
import re
import spacy
from flask import Flask, request, render_template_string

# Load summarizer and NLP
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

def summarize_text(text):
    return summarizer(text, max_length=60, min_length=20, do_sample=False)[0]['summary_text']

def tag_priorities(text):
    priorities = []
    if re.search(r'\bdeadline\b|\bby Monday\b', text, re.I):
        priorities.append("[Urgent 🔴] Deadline mentioned")
    if re.search(r'\bapprove\b|\bagreed\b', text, re.I):
        priorities.append("[Decision 🟡] Decision made")
    if re.search(r'@\w+', text):
        priorities.append("[Mention 🟢] Someone tagged")
    return priorities

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    if request.method == "POST":
        convo = request.form["conversation"]
        summary = summarize_text(convo)
        priorities = tag_priorities(convo)
        output = f"<h3>Summary:</h3><p>{summary}</p><h3>Priorities:</h3><ul>"
        for p in priorities:
            output += f"<li>{p}</li>"
        output += "</ul>"
    return render_template_string("""
        <form method="post">
            <textarea name="conversation" rows="10" cols="50"></textarea><br>
            <button type="submit">Summarize</button>
        </form>
        {{output|safe}}
    """, output=output)

if __name__ == "__main__":
    app.run(debug=True)
