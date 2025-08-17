from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd

app = Flask(__name__)
CORS(app)  

# Initialize database
def init_db():
    conn = sqlite3.connect('emails.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 content TEXT,
                 is_spam BOOLEAN)''')
    conn.close()

# Train or load ML model
def get_model():
    try:
        return joblib.load('spam_model.joblib')
    except:
        df = pd.DataFrame({
            'text': [
                "Win a free iPhone now!", 
                "Meeting at 3pm tomorrow",
                "Limited time offer!", 
                "Your account statement"
            ],
            'label': [1, 0, 1, 0] 
        })
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        model.fit(df['text'], df['label'])
        joblib.dump(model, 'spam_model.joblib')
        return model

model = get_model()
init_db()

@app.route('/analyze', methods=['POST'])
@app.route('/analyze', methods=['POST'])
def analyze():
    email_text = request.json.get('emailText', '')
    proba = model.predict_proba([email_text])[0]
    is_spam = bool(proba[1] > 0.6)  
    
    return jsonify({
        "is_spam": is_spam,  
        "confidence": float(proba[1]),  
        "keywords": ["free", "win"] if is_spam else []  
    })

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('emails.db')
    cursor = conn.execute("SELECT content, is_spam FROM emails")
    emails = [{"text": row[0], "is_spam": bool(row[1])} for row in cursor]
    conn.close()
    return jsonify(emails)

if __name__ == '__main__':
    app.run(debug=True, port=5000)