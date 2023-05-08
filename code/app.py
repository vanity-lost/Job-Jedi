import requests
import streamlit as st
import base64
import os
from backend.resume_generation import ResumeGenerator
from backend.feedback import FeedbackBot
from backend import config


os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY
generator = ResumeGenerator()
chatbot = FeedbackBot()
#########################################################


# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="My Webpage", page_icon=":tada:", layout="wide")


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def read_initial_pdf_file(file):
    """
    Read the contents of a PDF file and return a base64-encoded string.
    """
    with open(file, "rb") as f:
        pdf_bytes = f.read()
        encoded = base64.b64encode(pdf_bytes).decode("utf-8")
        return encoded


def read_pdf_file(file):
    """
    Read the contents of a PDF file and return a base64-encoded string.
    """
    # with open(file.read(), "rb") as f:
    pdf_bytes = file.read()
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    return encoded


local_css("style/style.css")


# ---- HEADER SECTION ----
with st.container():
    st.title("Welcome, I'm Job Jedi")
    st.subheader("Let me help you with your Resume.")

with st.container():
    st.write("---")

    st.subheader("Your Background")
    st.write(
        """
            Please provide all your expirience and background, anything related to this job.
            """
    )
    background = st.file_uploader(
        "Please upload a word document", type=['doc', 'docx', 'pdf'])
    if background:
        with open(os.path.join("./", background.name), "wb") as f:
            f.write(background.getvalue())

    st.write("---")
    st.subheader("Job Descirption")
    description = st.text_area(
        label="Please past all job descriptions of the role this resume is for")

    st.write("---")
    st.subheader("Your Resume")
    st.write("##")
    if 'firstTime' not in st.session_state:
        st.session_state['firstTime'] = 'True'
with st.container():
    left_column, right_column = st.columns((3, 1))
    with left_column:
        if st.session_state['firstTime'] == 'True':
            pdf_data = read_initial_pdf_file("./placeholder.pdf")
        else:
            pdf_data = read_initial_pdf_file("./resume.pdf")
        pdf_iframe = st.empty()
        pdf_iframe.markdown(
            f'<iframe id="pdf" src="data:application/pdf;base64,{pdf_data}" width="1150" height="1495"></iframe>', unsafe_allow_html=True)

    with right_column:
        newRequirement = st.text_area(
            "Tell me what do you want your resume to focus on")
        if st.button("Generate"):
            print("clicked generate button\n")
            if st.session_state['firstTime'] == 'True':
                st.session_state['firstTime'] = 'False'
                if newRequirement == "":
                    newRequirement = "regenerate"
            print("requirement=" + newRequirement)
            isGenerate = chat(newRequirement)
            # isGenerate = True
            if isGenerate:
                generate_resume(os.path.join(
                    "./", background.name), description)
                st.experimental_rerun()
            # print(description)
            # print(newRequirement)
            if not isGenerate:
                st.text("Job Jedi: Generation failed")
