from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from src.prompt import *
import os
from dotenv import load_dotenv

# OPENAI authentication
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def file_processor(file_path):

    # Load the file
    loader = PyPDFLoader(file_path)
    data = loader.load()

    question_gen = ""

    for page in data:
        question_gen = page.page_content

    splitter_que_gen = TokenTextSplitter(
        model_name= "gpt-3.5-turbo",
        chunk_size= 10000,
        chunk_overlap= 200
    )

    chunck_ques_gen = splitter_que_gen.split_text(question_gen)
    
    document_que_gen = [Document(page_content=i) for i in chunck_ques_gen]

    splitter_ans_gen = TokenTextSplitter(
        model_name= "gpt-3.5-turbo",
        chunk_size= 1000,
        chunk_overlap= 100
    )

    chunck_ans_gen = splitter_ans_gen.split_documents(document_que_gen)
    
    document_ans_gen = [Document(page_content=i) for i in chunck_ans_gen]

    return document_que_gen, document_ans_gen

def llm_pipeline(file_path):

    document_que_gen, document_ans_gen = file_processor(file_path)
    
    # Load the LLM
    llm_ques_gen_pipeline = ChatOpenAI(
        # openai_api_key= OPENAI_KEY,
        temperature=0.3, #cretivity index 0.1 to 1
        model_name= "gpt-3.5-turbo")
    
    PROMPT_QUESTIONS = PromptTemplate(
        template=prompt_template, 
        input_variables=["text"])
    
    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        input_variables= ["existing_answer","text"],
        template= refine_template)
    
    chain_ques_gen = load_summarize_chain(
        llm= llm_ques_gen_pipeline,
        chain_type= "refine",
        question_prompt= PROMPT_QUESTIONS,
        refine_prompt= REFINE_PROMPT_QUESTIONS
        verbose=True)
    
    ques= chain_ques_gen.run(
        document_que_gen)
    
    embeddings = OpenAIEmbeddings()

    vector_store = FAISS.from_documents(
        document_ans_gen,
        embeddings)
    
    llm_ans_gen = ChatOpenAI(
        temperature= 0.1,
        model= "gpt-3.5-turbo")
    
    ques_list = ques.split("\n")
    
    filtered_ques_list = [i for i in ques_list if i.endswith("?")]

    ans_gen_chain = RetrievalQA.from_chain_type(
        llm= llm_ans_gen,
        chain_type= "stuff",
        retriever= vector_store.as_retriever())

    return ans_gen_chain, filtered_ques_list