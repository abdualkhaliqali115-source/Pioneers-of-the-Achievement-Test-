from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
import random

app = Flask(__name__)
app.secret_key = "your-secret-key"  # مهم لحماية جلسة المستخدم

# ----- ضع هنا رابط الـ API الخاص بجدول بيانات جوجل (Google Sheets JSON API) -----
GOOGLE_SHEET_API_URL = "https://your-sheet-link.com"  # ← عدّل هذا الرابط إلى رابط الـ Google Sheets الخاص بك

def fetch_questions():
    """جلب الأسئلة من Google Sheets عبر API (JSON).
    يجب أن تكون البيانات بصيغة [{السؤال, خيار أ, خيار ب, خيار ج, خيار د, الإجابة الصحيحة, التفسير}, ...]
    """
    try:
        resp = requests.get(GOOGLE_SHEET_API_URL)
        questions = resp.json()
        return questions
    except Exception as e:
        print("خطأ في جلب الأسئلة:", e)
        return []

def get_random_questions(n=10):
    """جلب n أسئلة عشوائية من الأسئلة المتاحة"""
    questions = fetch_questions()
    if len(questions) > n:
        return random.sample(questions, n)
    return questions

@app.route("/")
def home():
    # بدء الاختبار ب10 أسئلة عشوائية
    questions = get_random_questions(10)
    session['questions'] = questions
    session['current'] = 0
    session['score'] = 0
    session['answers'] = []
    return render_template("index.html", question=questions[0], qnum=1)

@app.route("/next", methods=["POST"])
def next_question():
    user_answer = request.form.get("answer")
    qnum = session.get("current", 0)
    questions = session.get("questions", [])
    score = session.get("score", 0)
    answers = session.get("answers", [])

    # تحقق من الإجابة الصحيحة
    correct = False
    explanation = ""
    if questions and qnum < len(questions):
        correct_answer = questions[qnum]["الإجابة الصحيحة"].strip()
        explanation = questions[qnum].get("التفسير", "")
        if user_answer == correct_answer:
            score += 1
            correct = True
        answers.append({"user_answer": user_answer, "correct_answer": correct_answer, "correct": correct, "explanation": explanation})

    session['score'] = score
    session['answers'] = answers
    session['current'] = qnum + 1

    if qnum + 1 >= len(questions):
        # انتهاء الاختبار
        percent = int((score / len(questions)) * 100) if questions else 0
        return render_template("result.html",
                               score=score,
                               total=len(questions),
                               percent=percent,
                               answers=answers)
    else:
        # سؤال جديد
        return render_template("index.html", question=questions[qnum+1], qnum=qnum+2)

@app.route("/restart")
def restart():
    return redirect(url_for('home'))

# واجهة API لجلب أسئلة عشوائية (تجربة أو توصيل مع الواجهة الأمامية JS)
@app.route("/api/questions")
def api_questions():
    questions = get_random_questions(10)
    return jsonify(questions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)