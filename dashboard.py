import streamlit as st
import requests
import base64
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Data Insight Dashboard", layout="wide")

st.title("📊 AI-Powered Data Insight Generator")
st.write("Upload your dataset and get instant analysis + AI-generated insights.")

uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        st.write("### 👀 Preview of Uploaded Data", df.head())
    except Exception:
        st.error("⚠️ Could not preview this file. Please upload a valid CSV/Excel file.")
        df = None

    if df is not None:
        # Column selections
        column = st.selectbox("📌 Select Category Column", options=df.columns)
        value_column = st.selectbox("💰 Select Value Column (for numerical analysis)", options=df.columns)
        chart_type = st.selectbox("📈 Select Chart Type", ["bar", "line", "pie"])

        if st.button("🚀 Run Analysis"):
            with st.spinner("Analyzing and generating insights..."):
                file_bytes = uploaded_file.getvalue()
                files = {"file": (uploaded_file.name, file_bytes, "text/csv")}
                data = {
                    "chart_type": chart_type,
                    "column": column,
                    "value_column": value_column
                }

                try:
                    response = requests.post("http://127.0.0.1:5000/analyze", files=files, data=data)
                    if response.status_code == 200:
                        res = response.json()
                        st.success("✅ Analysis Complete!")

                        # --- Display Summary and AI Insights ---
                        st.subheader("📄 Data Summary")
                        st.text(res["summary"])

                        st.subheader("🧠 AI Insight")
                        st.info(res["ai_insight"])
                        
                        # --- AI Caption for Chart ---
                        try:
                            top_category = df.loc[df[value_column].idxmax(), column]
                            top_value = df[value_column].max()
                            total = df[value_column].sum()
                            percentage = (top_value / total) * 100
                            insight_text = f"💬 The highest {value_column} is from '{top_category}' with value {top_value:.2f}, contributing {percentage:.1f}% of total."
                            st.caption(insight_text)
                        except Exception:
                            st.caption("💬 Unable to generate insight for this chart.")

                        # --- Display Chart ---
                        st.subheader("📊 Visualization")
                        try:
                            if chart_type == "bar":
                                fig, ax = plt.subplots()
                                ax.bar(df[column], df[value_column])
                                ax.set_xlabel(column)
                                ax.set_ylabel(value_column)
                                st.pyplot(fig)

                            elif chart_type == "line":
                                fig, ax = plt.subplots()
                                ax.plot(df[column], df[value_column], marker='o')
                                ax.set_xlabel(column)
                                ax.set_ylabel(value_column)
                                st.pyplot(fig)

                            elif chart_type == "pie":
                                pie_data = df.groupby(column)[value_column].sum()
                                fig, ax = plt.subplots()
                                ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%")
                                st.pyplot(fig)
                        except Exception as e:
                            st.error(f"⚠️ Chart could not be generated: {e}")

                        # --- Download Report Button ---
                        if "report_pdf" in res:
                            pdf_bytes = base64.b64decode(res["report_pdf"])
                            st.download_button(
                                label="📥 Download AI Insight Report (PDF)",
                                data=pdf_bytes,
                                file_name="AI_Insight_Report.pdf",
                                mime="application/pdf"
                            )
                            
                    else:
                        st.error(f"❌ Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Could not connect to backend: {e}")
