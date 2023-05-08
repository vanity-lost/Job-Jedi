import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import Docx2txtLoader
from backend import config


class ResumeGenerator():
    def __init__(self):
        pass

    def run(self, background_path, job_description, output_path=config.output_path, verbose=False):
        config.background_path = background_path
        config.job_description = job_description

        with open(config.REPHRASE_PROMPT_TEMPLATE_PATH) as f:
            REPHRASE_PROMPT_TEMPLATE = f.read()
        with open(config.LATEX_PROMPT_TEMPLATE_1_PATH) as f:
            LATEX_PROMPT_TEMPLAT_1 = f.read()
        with open(config.LATEX_PROMPT_TEMPLATE_2_PATH) as f:
            LATEX_PROMPT_TEMPLAT_2 = f.read()

        with open(config.LATEX_HEADER_PATH) as f:
            latex_header = f.read()

        with open(config.LATEX_PART1_PATH) as f:
            part1 = f.read()

        with open(config.LATEX_PART2_PATH) as f:
            part2 = f.read()

        llm = OpenAI(max_tokens=1200)

        loader = Docx2txtLoader(background_path)
        background_info = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=4000, chunk_overlap=0)
        background_info_doc = text_splitter.split_documents(background_info)

        rephrase_template = PromptTemplate(
            input_variables=[
                "background",
                "job",
            ],
            template=REPHRASE_PROMPT_TEMPLATE,
        )

        rephrase_chain = LLMChain(llm=llm,
                                  prompt=rephrase_template,
                                  verbose=verbose)

        results = []
        for part in background_info_doc:
            res = rephrase_chain.run(background=part, job=job_description)
            results.append(res)

        background_info_generated = '\n\n'.join(results)

        results = []

        reformat_template = PromptTemplate(
            input_variables=[
                "template",
                "background",
            ],
            template=LATEX_PROMPT_TEMPLAT_1,
        )

        reformat_chain = LLMChain(llm=llm,
                                  prompt=reformat_template,
                                  verbose=verbose)
        res = reformat_chain.run(
            background=background_info_generated, template=part1)
        results.append(bytes(res, 'utf-8').decode('utf-8', 'ignore').strip())

        reformat_template = PromptTemplate(
            input_variables=[
                "template",
                "background",
            ],
            template=LATEX_PROMPT_TEMPLAT_2,
        )

        reformat_chain = LLMChain(llm=llm,
                                  prompt=reformat_template,
                                  verbose=verbose)

        res = reformat_chain.run(
            background=background_info_generated, template=part2)
        results.append(bytes(res, 'utf-8').decode('utf-8', 'ignore').strip())

        generated_resume = latex_header + '\n' + \
            results[0] + '\n' + results[1] + '\n\n \end{document}'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_resume)

        os.system(f"pdflatex {output_path}")
