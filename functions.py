import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import Docx2txtLoader
from langchain.callbacks import get_openai_callback

os.environ['OPENAI_API_KEY'] = "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"

def generate_resume(background_path, job_description, output_path='./results/resume.tex'):
    with open('./prompts/rephrase_template.txt') as f:
        REPHRASE_PROMPT_TEMPLATE = f.read()
    with open('./prompts/latex_template_1.txt') as f:
        LATEX_PROMPT_TEMPLAT_1 = f.read()
    with open('./prompts/latex_template_2.txt') as f:
        LATEX_PROMPT_TEMPLAT_2 = f.read()

    with open('./latex_template/header.tex') as f:
        latex_header = f.read()

    with open('./latex_template/part1.tex') as f:
        part1 = f.read()

    with open('./latex_template/part2.tex') as f:
        part2 = f.read()

    llm = OpenAI(model_name='text-davinci-003', max_tokens=1200)

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
                            verbose=False)

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
                            verbose=False)
    res = reformat_chain.run(background=background_info_generated, template=part1)
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
                            verbose=False)

    res = reformat_chain.run(background=background_info_generated, template=part2)
    results.append(bytes(res, 'utf-8').decode('utf-8', 'ignore').strip())

    generated_resume = latex_header + '\n' + results[0] + '\n' + results[1] + '\n\n \end{document}'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(generated_resume)

    os.system(f"pdflatex {output_path}")


def chat(user_query):
    with open('./prompts/chat_template.txt') as f:
        CHAT_PROMPT_TEMPLAT = f.read()

    chat_template = PromptTemplate(
        input_variables=["query"],
        template=CHAT_PROMPT_TEMPLAT,
    )

    chat_memory = ConversationBufferMemory(input_key='query', memory_key='query_history')

    conversation = LLMChain(llm=OpenAI(temperature=0), memory=chat_memory, prompt=chat_template)

    res = conversation.run(query=user_query).strip()

    if res != 'YES':
        return False
    
    with open('./prompts/revision_template.txt') as f:
        REVISE_PROMPT_TEMPLAT = f.read()

    revise_template = PromptTemplate(
        input_variables=["old_template", "user_request"],
        template=REVISE_PROMPT_TEMPLAT,
    )

    with open('./prompts/rephrase_template.txt') as f:
        REPHRASE_PROMPT_TEMPLATE = f.read().replace('{', '#(#').replace('}', '#)#')
    with open('./prompts/latex_template_1.txt') as f:
        LATEX_PROMPT_TEMPLAT_1 = f.read().replace('{', '#(#').replace('}', '#)#')
    with open('./prompts/latex_template_2.txt') as f:
        LATEX_PROMPT_TEMPLAT_2 = f.read().replace('{', '#(#').replace('}', '#)#')

    revision_chain = LLMChain(llm=OpenAI(temperature=0.7), 
                            prompt=revise_template,
                            verbose=False)

    REPHRASE_PROMPT_TEMPLATE = revision_chain.run(old_template=REPHRASE_PROMPT_TEMPLATE, user_request=user_query)
    LATEX_PROMPT_TEMPLAT_1 = revision_chain.run(old_template=LATEX_PROMPT_TEMPLAT_1, user_request=user_query)
    LATEX_PROMPT_TEMPLAT_2 = revision_chain.run(old_template=LATEX_PROMPT_TEMPLAT_2, user_request=user_query)

    with open('./prompts/rephrase_template.txt', 'w') as f:
        f.write(REPHRASE_PROMPT_TEMPLATE.replace('#(#', '{').replace('#)#', '}'))
    with open('./prompts/latex_template_1.txt', 'w') as f:
        f.write(LATEX_PROMPT_TEMPLAT_1.replace('#(#', '{').replace('#)#', '}'))
    with open('./prompts/latex_template_2.txt', 'w') as f:
        f.write(LATEX_PROMPT_TEMPLAT_2.replace('#(#', '{').replace('#)#', '}'))
    
    return True