from flask import Flask, request, jsonify
import pandas as pd
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    chart_type = request.form.get("chart_type", "bar")
    column = request.form.get("column")
    value_column = request.form.get("value_column")

    # --- File parsing ---
    try:
        filename = file.filename.lower()
        if filename.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(io.BytesIO(file.read()))
        file.seek(0)
    except Exception as e:
        return jsonify({"error": f"Could not parse file: {str(e)}"}), 400

    if df is None or df.empty:
        return jsonify({"error": "Uploaded file is empty or invalid"}), 400

    # --- Basic Data Summary ---
    summary = df.describe(include="all").to_string()

    # --- Simple AI Insight (simulated) ---
    if value_column and column in df.columns and value_column in df.columns:
        mean_val = df[value_column].mean()
        ai_insight = f"📊 The average {value_column} is {mean_val:.2f}, and key category is '{df[column].mode()[0]}'."
    else:
        ai_insight = "💡 The dataset looks clean and ready for deeper analysis."

    # --- Generate Report PDF ---
    pdf_path = "AI_Insight_Report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("AI Data Insight Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Summary:", styles["Heading2"]),
        Paragraph(summary.replace("\n", "<br/>"), styles["Normal"]),
        Spacer(1, 12),
        Paragraph("AI Insight:", styles["Heading2"]),
        Paragraph(ai_insight, styles["Normal"])
    ]
    doc.build(story)

    # Convert PDF to base64
    with open(pdf_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

    return jsonify({
        "summary": summary,
        "ai_insight": ai_insight,
        "report_pdf": encoded_pdf
    })

if __name__ == "__main__":
    app.run(debug=True)
