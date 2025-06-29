from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load Excel data once when the app starts
students_df = pd.read_excel('students.xlsx')
teachers_df = pd.read_excel('teachers.xlsx')

# Correct headers
students_df.columns = students_df.iloc[0].fillna("Unnamed")
students_df = students_df[1:].reset_index(drop=True)
teachers_df.columns = teachers_df.columns.str.strip()

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    user_type = request.form['user_type']
    email = request.form['email'].strip().lower()
    password = request.form['password'].strip()

    if user_type == 'student':
        students_df["Official mail id"] = students_df["Official mail id"].astype(str).str.strip().str.lower()
        students_df["Register Number"] = students_df["Register Number"].astype(str).str.strip()
        match = students_df[students_df["Official mail id"] == email]

        if not match.empty and match["Register Number"].values[0] == password:
            session['user'] = match.to_dict(orient='records')[0]
            return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid student credentials!")

    elif user_type == 'teacher':
        teachers_df["email id"] = teachers_df["email id"].astype(str).str.strip().str.lower()
        match = teachers_df[teachers_df["email id"] == email]

        if not match.empty and str(match["Phone Number"].values[0]).strip() == password:
            session['user'] = match.iloc[0].to_dict()
            return redirect(url_for('teacher_dashboard'))
        else:
            flash("Invalid teacher credentials!")

    return redirect(url_for('home'))

@app.route('/student_dashboard')
def student_dashboard():
    user = session.get('user', {})
    if not user:
        return redirect(url_for('home'))
    return render_template("student_dashboard.html", user=user)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    user = session.get('user', {})
    return render_template("teacher_dashboard.html", user=user)

@app.route('/search_student', methods=['POST'])
def search_student():
    register_number = request.form['register_number'].strip()
    user = session.get('user', {})

    result = students_df[students_df['Register Number'] == register_number]
    if not result.empty:
        student = result.to_dict(orient='records')[0]
        return render_template("teacher_dashboard.html", user=user, student=student, searched=True)
    else:
        return render_template("teacher_dashboard.html", user=user, student=None, searched=True)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
