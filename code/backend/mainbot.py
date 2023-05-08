import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import Docx2txtLoader
from langchain.agents import initialize_agent, AgentType, Tool

from backend import config
from backend.feedback import FeedbackBot
from backend.resume_generation import ResumeGenerator

class CustomAgent():
    def __init__(self):
        os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY
        self.feedback_bot = FeedbackBot()
        self.resume_generator = ResumeGenerator()
        self.llm = OpenAI(temperature=0)
        tools = [
            Tool(
                name = "Update Prompts",
                func=self.feedback_bot.run,
                description="useful for when you need to re-generate the resume based on user request. Users may have special requirements and preferences and you will need to use this function to update the resume. For example, `more project experience` will be the input if you want to have more project experiences."
            ),
            Tool(
                name = "Generate Resume",
                func=self.resume_generator.run,
                description="useful for when you need to generate resume and the user does not have specific requirements. If the user have no new instructions, you will need to use this function to generate a new resume. For example, `` be will the input if you want to generate a resume."
            )
        ]

        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = initialize_agent(tools, self.llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=self.memory)
    
    def run(self, query):
        return self.agent.run(query)