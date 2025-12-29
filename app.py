from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-me"  # troque depois

DB = "database.db"
REPORT_PATH = os.path.join("reports", "sessions.csv")

EMAILS = [
    {
        "id": 1,
        "subject": "Atualização obrigatória de senha (TI)",
        "from": "suporte-ti@empresa-seguranca.com",
        "body": "Olá! Identificamos atividade incomum. Atualize sua senha em até 2 horas: http://seguranca-empresa-login.com",
        "is_phishing": True,
        "clues": [
            "Link com domínio estranho (não é o domínio oficial).",
            "Urgência artificial (2 horas).",
            "Pedido de credenciais via link."
        ]
    },
    {
        "id": 2,
        "subject": "Comprovante de pagamento - RH",
        "from": "rh@empresa.com",
        "body": "Seu comprovante mensal está disponível no portal interno. Acesse pelo intranet normalmente.",
        "is_phishing": False,
        "clues": [
            "Não há link suspeito.",
            "Orientação para acessar por canal oficial (intranet)."
        ]
    },
    {
        "id": 3,
        "subject": "Entrega pendente - confirme seu endereço",
        "from": "logistica@entregas-suporte.com",
        "body": "Sua entrega está retida. Confirme o endereço aqui: http://bit.ly/confirmar-endereco",
        "is_phishing": True,
        "clues": [
            "Link encurtado (bit.ly) oculta destino real.",
            "Remetente genérico e não relacionado.",
            "Mensagem vaga e sem referência de pedido."
        ]
    },
    {
        "id": 4,
        "subject": "Convite: reunião de alinhamento (Segunda 10h)",
        "from": "gestao@empresa.com",
        "body": "Pessoal, segue o convite da reunião no calendário. Qualquer dúvida me chamem no Teams.",
        "is_phishing": False,
        "clues": [
            "Sem pedidos de dados sensíveis.",
            "Canal corporativo mencionado (Teams/Calendário)."
        ]
    },
    {
        "id": 5,
        "subject": "Microsoft 365: sua conta será desativada",
        "from": "microsoft-security@support-alerts.com",
        "body": "Detectamos violação. Para evitar bloqueio, valide agora: http://microsoft-validacao-conta.com",
        "is_phishing": True,
        "clues": [
            "Domínio não oficial da Microsoft.",
            "Ameaça de desativação imediata.",
            "Solicita validação via link externo."
        ]
    },
    {
        "id": 6,
        "subject": "Atualização do manual de conduta",
        "from": "compliance@empresa.com",
        "body": "O manual de conduta foi atualizado. Acesse na pasta oficial do SharePoint corporativo.",
        "is_phishing": False,
        "clues": [
            "Direciona para repositório oficial (SharePoint).",
            "Conteúdo alinhado ao time (Compliance)."
        ]
    },
]

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_name TEXT,
            email_id INTEGER,
            action TEXT,
            correct INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_email(email_id: int):
    for e in EMAILS:
        if e["id"] == email_id:
            return e
    return None

def compute_score(session_id: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT action, correct FROM actions WHERE session_id=?", (session_id,))
    rows = cur.fetchall()
    conn.close()

    score = 0
    # regra simples (ajustável)
    for action, correct in rows:
        if action == "report":
            score += 10 if correct else -5
        elif action == "click":
            score += -15 if not correct else 5
    return score, len(rows)

def ensure_reports():
    os.makedirs("reports", exist_ok=True)
    if not os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "session_id", "user_name", "score", "total_actions"])

def append_report(session_id: str, user_name: str, score: int, total_actions: int):
    ensure_reports()
    with open(REPORT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), session_id, user_name, score, total_actions])

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("login.html", error="Preencha seu nome.")
        session["user_name"] = name
        session["session_id"] = f"{name}-{int(datetime.utcnow().timestamp())}"
        return redirect(url_for("inbox"))
    return render_template("login.html")

@app.route("/inbox")
def inbox():
    if "user_name" not in session:
        return redirect(url_for("login"))
    return render_template("inbox.html", emails=EMAILS)

@app.route("/email/<int:email_id>")
def view_email(email_id):
    if "user_name" not in session:
        return redirect(url_for("login"))
    email = get_email(email_id)
    if not email:
        return "Email não encontrado", 404
    return render_template("email.html", email=email)

@app.route("/action/<int:email_id>/<string:action>", methods=["POST"])
def take_action(email_id, action):
    if "user_name" not in session:
        return redirect(url_for("login"))

    email = get_email(email_id)
    if not email:
        return "Email não encontrado", 404

    if action not in ("report", "click"):
        return "Ação inválida", 400

    # correto se: reporta phishing OU não clica em legit
    if action == "report":
        correct = 1 if email["is_phishing"] else 0
    else:  # click
        correct = 1 if not email["is_phishing"] else 0

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO actions (session_id, user_name, email_id, action, correct, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["session_id"],
        session["user_name"],
        email_id,
        action,
        correct,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

    return redirect(url_for("results"))

@app.route("/results")
def results():
    if "user_name" not in session:
        return redirect(url_for("login"))

    session_id = session["session_id"]
    user_name = session["user_name"]

    score, total = compute_score(session_id)

    # puxa histórico pra mostrar
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT email_id, action, correct, created_at
        FROM actions
        WHERE session_id=?
        ORDER BY id DESC
        LIMIT 20
    """, (session_id,))
    actions = cur.fetchall()
    conn.close()

    # salva linha no CSV a cada visita do results (simples pro MVP)
    append_report(session_id, user_name, score, total)

    return render_template("results.html", score=score, total=total, actions=actions, emails=EMAILS)

@app.route("/export")
def export_csv():
    # export global (do arquivo de report)
    ensure_reports()
    return send_file(REPORT_PATH, as_attachment=True)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    os.makedirs("reports", exist_ok=True)
    app.run(debug=True)
