from langchain_community.document_loaders import PyPDFLoader, CSVLoader, UnstructuredMarkdownLoader, UnstructuredExcelLoader,Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

if(not os.getenv("OPENAI_API_KEY")):
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")


# #loading .md files
# benefits_md = UnstructuredMarkdownLoader("data/raw/benefits.md").load()
# company_wiki_md = UnstructuredMarkdownLoader("data/raw/company_wiki.md").load()
# employee_handbook_md = UnstructuredMarkdownLoader("data/raw/employee_handbook.md").load()
# expenses_policy_md = UnstructuredMarkdownLoader("data/raw/expense_policy.md").load()
# hr_policies_md = UnstructuredMarkdownLoader("data/raw/hr_policies.md").load()
# it__support_guide_md = UnstructuredMarkdownLoader("data/raw/it_support_guide.md").load()
# onboarding_guide_md = UnstructuredMarkdownLoader("data/raw/onboarding_guide.md").load()
# remote_work_policy_md = UnstructuredMarkdownLoader("data/raw/remote_work_policy.md").load()
# security_policy_md = UnstructuredMarkdownLoader("data/raw/security_policy.md").load()
# training_material_md = UnstructuredMarkdownLoader("data/raw/training_materials.md").load()


# # loading pdf files
# benefits_overview_pdf = PyPDFLoader("ddata/raw/Benefits_Overview.pdf").load()
# hr_policies_pdf = PyPDFLoader("data/raw/HR_Policies.pdf").load()
# security_policy_pdf = PyPDFLoader("data/raw/Security_Policy.pdf").load()

# # loading excel files
# benefits_comparison_excel = UnstructuredExcelLoader("data/raw/Benefits_Comparison.xlsx").load()
# company_directory_excel = UnstructuredExcelLoader("data/raw/Company_Directory.xlsx").load()
# pto_tracker_excel = UnstructuredExcelLoader("data/raw/PTO_Tracker.xlsx").load()

# # loading docx files
# employee_handbook_docx = Docx2txtLoader("data/raw/Employee_Handbook.docx").load()
# onboarding_guide_docx = Docx2txtLoader("data/raw/Onboarding_Guide.docx").load()
# training_material_docx = Docx2txtLoader("data/raw/Training_Materials.docx").load()

# # loading csv files
# benefits_comparison_csv = CSVLoader("data/raw/Benefits_Comparison.csv").load()
# company_directory_csv = CSVLoader("data/raw/Company_Directory.csv").load()