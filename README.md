## 🚨 About the Project

Awareness Lab is an educational anti-phishing simulator that recreates a corporate email inbox where users must analyze messages and decide whether to report phishing attempts or interact with malicious content.

The project was designed to demonstrate security awareness, engineering social analysis, and Blue Team mindset in a safe, controlled environment.

⚠️ No real emails are sent and no sensitive data is collected.

## 🎯 Goals

Simulate phishing awareness campaigns

Train users to identify social engineering indicators

Demonstrate SOC / Blue Team skills

Generate awareness metrics and reports

Provide a portfolio-ready cybersecurity project

## 🧪 Features

Simulated user login (session-based)

Corporate-style inbox with phishing & legitimate emails

Manual email analysis

User actions:

✅ Report phishing

❌ Click on links

Awareness score system

Session history tracking

CSV report export

Dark Hacker Lab UI

## 📊 Awareness Scoring Logic
Action	Result	Score

Correct phishing report	✅	+10

Incorrect phishing report	❌	-5

Clicking phishing link	❌	-15

Clicking legitimate email	⚠️	+5

## 🧱 Project Structure
   awareness-lab/
   
   ├── app.py   
   ├── requirements.txt   
   ├── README.md   
   ├── reports/   
   │   └── sessions.csv  
   ├── templates/   
   │   ├── login.html   
   │   ├── inbox.html   
   │   ├── email.html   
   │   └── results.html
   └── static/
   └── style.css

## 🛠️ Tech Stack

Python 3

Flask

SQLite

HTML5

CSS3 (Dark UI / Glassmorphism)

CSV reporting

## 🚀 Running Locally
git clone https://github.com/SEU-USUARIO/awareness-lab.git
cd awareness-lab

python -m venv .venv
.venv\Scripts\activate   # Windows

pip install -r requirements.txt
python app.py

## 🧠 Security Concepts Covered

Phishing Awareness

Social Engineering

User Behavior Analysis (basic)

Blue Team fundamentals

SOC mindset

Defensive security education

## 🔮 Future Improvements

Email-by-email feedback explaining phishing indicators

Dashboard with charts (Chart.js)

Department-based metrics

Multiple campaigns

SIEM integration (simulated)

Incident response playbook

## ⚠️ Disclaimer

This project is for educational and demonstration purposes only.
It must not be used for real phishing campaigns or malicious activities.

## 👨‍💻 Author

Matheus Costa Silva
Cybersecurity • Blue Team • Security Awareness
