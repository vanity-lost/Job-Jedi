from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from backend.resume_generation import ResumeGenerator
from backend import config


class FeedbackBot():
    def __init__(self):
        pass

    def run(self, user_query, verbose=False):
        with open(config.REVISE_PROMPT_TEMPLATE_PATH) as f:
            REVISE_PROMPT_TEMPLAT = f.read()

        with open(config.REPHRASE_PROMPT_TEMPLATE_PATH) as f:
            REPHRASE_PROMPT_TEMPLATE = f.read().replace(
                '{', '#(#').replace('}', '#)#')
        with open(config.LATEX_PROMPT_TEMPLATE_1_PATH) as f:
            LATEX_PROMPT_TEMPLAT_1 = f.read().replace(
                '{', '#(#').replace('}', '#)#')
        with open(config.LATEX_PROMPT_TEMPLATE_2_PATH) as f:
            LATEX_PROMPT_TEMPLAT_2 = f.read().replace(
                '{', '#(#').replace('}', '#)#')

        revise_template = PromptTemplate(
            input_variables=["old_template", "user_request"],
            template=REVISE_PROMPT_TEMPLAT,
        )

        feedback_memory = ConversationBufferMemory(
            input_key='user_request', memory_key='query_history')

        revision_chain = LLMChain(llm=OpenAI(temperature=0.7),
                                  memory=feedback_memory,
                                  prompt=revise_template,
                                  verbose=verbose)

        REPHRASE_PROMPT_TEMPLATE = revision_chain.run(
            old_template=REPHRASE_PROMPT_TEMPLATE, user_request=user_query)
        LATEX_PROMPT_TEMPLAT_1 = revision_chain.run(
            old_template=LATEX_PROMPT_TEMPLAT_1, user_request=user_query)
        LATEX_PROMPT_TEMPLAT_2 = revision_chain.run(
            old_template=LATEX_PROMPT_TEMPLAT_2, user_request=user_query)

        with open(config.REVISE_PROMPT_TEMPLATE_PATH, 'w') as f:
            f.write(REPHRASE_PROMPT_TEMPLATE.replace(
                '#(#', '{').replace('#)#', '}'))
        with open(config.LATEX_PROMPT_TEMPLATE_1_PATH, 'w') as f:
            f.write(LATEX_PROMPT_TEMPLAT_1.replace(
                '#(#', '{').replace('#)#', '}'))
        with open(config.LATEX_PROMPT_TEMPLATE_2_PATH, 'w') as f:
            f.write(LATEX_PROMPT_TEMPLAT_2.replace(
                '#(#', '{').replace('#)#', '}'))

        generator = ResumeGenerator()
        generator.run(config.background_path, config.job_description)
