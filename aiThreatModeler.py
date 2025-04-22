import streamlit as st
import google.generativeai as genai
import os
import tempfile
from dotenv import load_dotenv
import fitz 
import git
import shutil

# Load Gemini API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)

# === Streamlit UI ===
st.set_page_config(page_title="STRIDE Threat Modeling", page_icon="🔐")
st.title("🔐 STRIDE Threat Modeling")
st.markdown("Upload a PRD/System PDF and optionally provide a GitHub repo URL. This app uses Gemini to analyze and generate a STRIDE-based threat model.")

uploaded_file = st.file_uploader("📄 Upload PRD or System Document (PDF)", type=["pdf"])
github_url = st.text_input("🔗 Optional GitHub Repository URL")
github_pat = st.text_input("🔑 GitHub Personal Access Token (for private repos)", type="password")

def clone_and_extract_github(url, pat=None):
    """Clone GitHub repo (public or private) and extract relevant content."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            # Inject PAT for private repo support
            if pat:
                # Convert https://github.com/owner/repo -> https://<PAT>@github.com/owner/repo
                url_parts = url.split("https://")
                if len(url_parts) == 2:
                    authenticated_url = f"https://{pat}@{url_parts[1]}"
                else:
                    return "❌ Invalid GitHub URL format."
            else:
                authenticated_url = url

            repo = git.Repo.clone_from(authenticated_url, tmp_dir)
            file_contents = []

            for root, _, files in os.walk(tmp_dir):
                for file in files:
                    if file.lower() in {"readme.md", "app.py", "main.py", "server.py", "dockerfile"}:
                        full_path = os.path.join(root, file)
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            file_contents.append(f"\n\n---\n### 📄 {file}\n```python\n{content}\n```")

            return "\n".join(file_contents) if file_contents else "⚠️ No key files (README, app.py, etc.) found."

        except Exception as e:
            return f"❌ Error cloning GitHub repo: {str(e)}"

if uploaded_file:
    if uploaded_file.size > 5 * 1024 * 1024:
        st.warning("⚠️ PDF is larger than 5MB. Consider uploading a smaller document.")
    else:
        with st.spinner("📤 Uploading and analyzing PDF with Gemini..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            try:
                with fitz.open(tmp_file_path) as doc:
                    extracted_text = "\n".join(page.get_text() for page in doc[:2]).strip()

                if not extracted_text:
                    st.error("❌ Could not extract text from the PDF. Please ensure it's not a scanned document.")
                else:
                    with st.expander("📖 Preview Extracted PDF Text"):
                        st.write(extracted_text)

                    gemini_file = genai.upload_file(tmp_file_path, mime_type="application/pdf")
                    st.success(f"✅ Uploaded: {uploaded_file.name}")

                    github_context = ""
                    if github_url:
                        with st.spinner("🔍 Cloning and extracting GitHub content..."):
                            github_context = clone_and_extract_github(github_url, github_pat)
                            if github_context.startswith("❌"):
                                st.error(github_context)
                            else:
                                with st.expander("🧾 GitHub Repo Context Preview"):
                                    st.markdown(github_context[:3000] + "..." if len(github_context) > 3000 else github_context)

                    # Final Gemini prompt
                    prompt = f"""You are a senior security architect. You are tasked with performing a comprehensive security threat modeling assessment.

1. You will be provided with a PDF product/system document.
2. Optionally, you may also have a GitHub repo with code or infrastructure.
3. Goal: Perform a threat model based on the content of the provided PDF document and GitHub repo.

Your steps:
- Analyze the document to understand the features and architecture.
- Analyze the GitHub repo to build context around the system.
- Identify key components in the system and data flow. 
- Identify potential attacker entry points and vulnerabilities for each component.
- Create a STRIDE threat model (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privileges).
- Create a PASTA threat model (Process for Attack Simulation and Threat Analysis).
- Be very specific and contextual, no generic risks like injection attacks. You have the code so you should be able to validate all risks. 

GitHub Context (if provided):
{github_context if github_context else "[No GitHub context provided]"}

Now, analyze the following uploaded PDF and generate a threat model report:
"""

                    response = model.generate_content([prompt, gemini_file])
                    threat_model = response.text

                    st.subheader("📋 STRIDE Threat Modeling Report")
                    st.markdown(threat_model)

                    st.download_button(
                        label="📥 Download Report",
                        data=threat_model,
                        file_name="stride_threat_model.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error("❌ Error processing the file. Make sure it’s a valid PDF and try again.")
                st.text(f"Details: {e}")
