import requests
import streamlit as st
import base64
import os
from backend import config
from streamlit_chat import message
from backend.mainbot import CustomAgent

#########################################################


# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="My Webpage", page_icon=":tada:", layout="wide")


# load CSS file for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# read and display the generated Resume or the place holder at the start
def read_initial_pdf_file(file):
    """
    Read the contents of a PDF file and return a base64-encoded string.
    """
    with open(file, "rb") as f:
        pdf_bytes = f.read()
        encoded = base64.b64encode(pdf_bytes).decode("utf-8")
        return encoded
    
# Deprecated, originally used to read user uploaded pdf files
def read_pdf_file(file):
    """
    Read the contents of a PDF file and return a base64-encoded string.
    """
    #with open(file.read(), "rb") as f:
    pdf_bytes = file.read()
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    return encoded



local_css("style/style.css")

if 'firstTime' not in st.session_state:
    st.session_state['firstTime'] = 'True'
if 'newInput' not in st.session_state:
    st.session_state['newInput'] = ''
if 'agent' not in st.session_state:
    st.session_state.agent = CustomAgent()
if 'isNewInput' not in st.session_state:
    st.session_state.isNewInput = 'False'


# ---- HEADER SECTION ----
with st.container():
    st.title("Welcome, I'm Job Jedi")
    st.subheader("Let me help you with your Resume.")

#---Background expirience and Job descirption input--#
with st.container():
    st.write("---")

    st.subheader("Your Background")
    st.write(
        """
            Please provide all your expirience and background, anything related to this job.
            """
    )
    background = st.file_uploader(
        "Please upload a word document", type=['doc', 'docx','pdf'])
    if background:
        with open(os.path.join("./",background.name),"wb") as f: 
            f.write(background.getvalue())         

    st.write("---")
    st.subheader("Job Descirption")
    description = st.text_area(label="Please past all job descriptions of the role this resume is for")

    st.write("---")
    st.subheader("Your Resume")
    st.write("##")
    
#---Display generated PDF on the left, Customization input and Generate button on the right---#
def render_pdf(left_column):
    with left_column:
        if st.session_state['firstTime']=='True':
            pdf_data = read_initial_pdf_file("./placeholder.pdf")
        else:
            pdf_data = read_initial_pdf_file("./resume.pdf")
        pdf_iframe = st.empty()
        pdf_iframe.markdown(
            f'<iframe id="pdf" src="data:application/pdf;base64,{pdf_data}" width="1150" height="1495"></iframe>', unsafe_allow_html=True)

with st.container():
    left_column, right_column = st.columns((3, 1))
    render_pdf(left_column)
    
    with right_column:
        
        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["Tell me what do you want your resume to focus on"]

        if 'past' not in st.session_state:
            st.session_state['past'] = []

        def get_text():
            input_text = st.text_input("You: ",key="input")
            return input_text 
        def clearUserInput():
            st.session_state["input"] = ""

        def submit():
            st.session_state.newInput = st.session_state.input
            st.session_state.input = ''
            st.session_state.isNewInput = 'True'

        st.text_input("You: ", key="input", on_change=submit)
        
        if len(st.session_state.newInput)>0 and st.session_state.isNewInput == 'True':
            user_input = st.session_state.newInput
            config.job_description = description
            config.background_path = os.path.join("./",background.name)

            with st.spinner('Job Jedi is working on it...'):
                agentOutput = st.session_state.agent.run(user_input)
            render_pdf(left_column)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(agentOutput)
            st.session_state.isNewInput = 'False'
            st.session_state['firstTime'] = 'False'
            st.experimental_rerun()


        if st.session_state['generated']:
            if st.session_state['past']:
                for i in range(len(st.session_state['past'])-1, -1, -1):
                    message(st.session_state["generated"][i+1], key=str(i+1))
                    message(st.session_state['past'][i], is_user=True, key=str(i+1) + '_user')
            message(st.session_state["generated"][0], key='0')
        



