# from flask import Flask, jsonify, render_template
# from live_monitor import get_live_changes
# from ai_explainer import explain_system_change
# import time

# app = Flask(__name__)

# last_ai_result = None        # ❗ IMPORTANT CHANGE
# last_ai_time = 0
# AI_INTERVAL = 30             # seconds
# ai_initialized = False       # ❗ NEW FLAG

# @app.route("/")
# def dashboard():
#     return render_template("dashboard.html")

# @app.route("/api/live")
# def live_api():
#     global last_ai_result, last_ai_time, ai_initialized

#     data = get_live_changes()

#     # If no data yet, return safely
#     if not data or "cpu_now" not in data:
#         return jsonify({
#             "status": "initializing",
#             "ai_explanation": "Initializing system monitoring..."
#         })

#     now = time.time()

#     # 🔥 FORCE AI ON FIRST VALID DATA
#     if not ai_initialized:
#         try:
#             last_ai_result = explain_system_change(data)
#             last_ai_time = now
#             ai_initialized = True
#         except Exception as e:
#             last_ai_result = f"AI initialization error: {e}"

#     # 🔁 NORMAL AI TRIGGERS AFTER INIT
#     elif (abs(data.get("cpu_change", 0)) > 2) or (now - last_ai_time > AI_INTERVAL):
#         try:
#             last_ai_result = explain_system_change(data)
#             last_ai_time = now
#         except Exception:
#             pass  # Never break live data

#     data["ai_explanation"] = last_ai_result
#     return jsonify(data)

# if __name__ == "__main__":
#     app.run(debug=True)

#----------------------------------------------------------------------


# from flask import Flask, jsonify, render_template, request
# from live_monitor import get_live_changes
# from ai_explainer import explain_system_change

# app = Flask(__name__)

# last_snapshot = None
# last_ai_result = "Click 'Analyze with AI' to generate system explanation."

# @app.route("/")
# def dashboard():
#     return render_template("dashboard.html")

# @app.route("/api/live")
# def live_api():
#     global last_snapshot
#     data = get_live_changes()
#     last_snapshot = data
#     return jsonify(data or {})

# @app.route("/api/analyze", methods=["POST"])
# def analyze():
#     global last_ai_result, last_snapshot

#     if not last_snapshot:
#         return jsonify({
#             "ai_explanation": "System data not ready yet. Please wait a moment."
#         })

#     try:
#         last_ai_result = explain_system_change(last_snapshot)
#     except Exception as e:
#         last_ai_result = f"AI analysis failed due to rate limits. Try again later.\n\nDetails: {str(e)}"

#     return jsonify({
#         "ai_explanation": last_ai_result
#     })

# if __name__ == "__main__":
#     app.run(debug=True)


# from datetime import datetime
# from flask import send_file
# import io

# @app.route("/api/export")
# def export_report():
#     global last_snapshot, last_ai_result

#     if not last_snapshot:
#         return "System data not available yet.", 400

#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     report = f"""
# ==============================
#  ExplainMySystem Report
# ==============================

# Generated At: {now}

# --- System Metrics ---
# CPU Usage    : {last_snapshot.get("cpu_now")}%
# Memory Usage : {last_snapshot.get("memory_now")}%
# Disk Usage   : {last_snapshot.get("disk_now")}%

# --- Top Processes ---
# """

#     for p in last_snapshot.get("top_processes", []):
#         report += f"- {p['name']} | CPU {p['cpu_percent']}% | RAM {p['memory_percent']}%\n"

#     report += f"""

# --- AI System Analysis ---
# {last_ai_result or "No AI analysis available."}

# ==============================
# """

#     buffer = io.BytesIO()
#     buffer.write(report.encode("utf-8"))
#     buffer.seek(0)

#     return send_file(
#         buffer,
#         as_attachment=True,
#         download_name="ExplainMySystem_Report.txt",
#         mimetype="text/plain"
#     )



from flask import Flask, jsonify, render_template, request, send_file
from datetime import datetime
import io

from live_monitor import get_live_changes
from ai_explainer import explain_system_change

# PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

app = Flask(__name__)

# ---------------- GLOBAL STATE ----------------
last_snapshot = None
last_ai_result = "Click 'Analyze with AI' to generate system explanation."

# ---------------- ROUTES ----------------

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/live")
def live_api():
    global last_snapshot
    data = get_live_changes()
    last_snapshot = data
    return jsonify(data or {})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    global last_ai_result, last_snapshot

    if not last_snapshot:
        return jsonify({
            "ai_explanation": "System data not ready yet. Please wait a moment."
        })

    try:
        last_ai_result = explain_system_change(last_snapshot)
    except Exception as e:
        last_ai_result = (
            "AI analysis failed due to rate limits or configuration issues.\n\n"
            f"Details:\n{str(e)}"
        )

    return jsonify({
        "ai_explanation": last_ai_result
    })


@app.route("/api/export")
def export_report():
    global last_snapshot, last_ai_result

    if not last_snapshot:
        return "System data not available yet.", 400

    buffer = io.BytesIO()

    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(
        "<b>ExplainMySystem – System Health Report</b>",
        styles["Title"]
    ))
    story.append(Spacer(1, 12))

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(
        f"<b>Generated At:</b> {timestamp}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    # System Metrics
    story.append(Paragraph("<b>System Metrics</b>", styles["Heading2"]))
    story.append(Paragraph(
        f"CPU Usage: {last_snapshot.get('cpu_now')}%",
        styles["Normal"]
    ))
    story.append(Paragraph(
        f"Memory Usage: {last_snapshot.get('memory_now')}%",
        styles["Normal"]
    ))
    story.append(Paragraph(
        f"Disk Usage: {last_snapshot.get('disk_now')}%",
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    # Top Processes
    story.append(Paragraph("<b>Top Processes</b>", styles["Heading2"]))
    for p in last_snapshot.get("top_processes", []):
        story.append(Paragraph(
            f"- {p['name']} | CPU {p['cpu_percent']}% | RAM {p['memory_percent']}%",
            styles["Normal"]
        ))
    story.append(Spacer(1, 12))

    # AI Analysis
    story.append(Paragraph("<b>AI System Analysis</b>", styles["Heading2"]))
    analysis_text = last_ai_result or "AI analysis not generated yet."

    for line in analysis_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="ExplainMySystem_Report.pdf",
        mimetype="application/pdf"
    )


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
