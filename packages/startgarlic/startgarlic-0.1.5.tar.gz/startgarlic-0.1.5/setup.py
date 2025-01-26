from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

class BdistWheelCommand(bdist_wheel):
    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        self.root_is_pure = False

setup(
    name="startgarlic",
    version="0.1.5",
    author="Bogdan Ciolac, May Elshater",
    author_email="bogdan@startgarlic.com, may@startgarlic.com",
    description="A RAG-based company information retrieval system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/startgarlic/MVP",
    packages=find_packages(),
    # package_data={
    #     'garlic': ['companies/*.xlsx'],
    # },
    install_requires=[
         "numpy>=1.23.5,<2.0.0",
         "pandas>=2.0.0",
         "supabase-py",
         "python-dotenv",
         "sentence-transformers",
         "langchain>=0.0.200",
         "langchain-community", 
         "langchain-huggingface",
        #  "bcrypt",
        #  "faiss-cpu",  # For vector storage
        # "streamlit>=1.40.0"
    ],
    
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        
    python_requires=">=3.7",
    cmdclass={
        'bdist_wheel': BdistWheelCommand,
    },
    package_data={
        'startgarlic': ['.env'],
        'startgarlic.utils': ['config.py'],
    },
    include_package_data=True,
)
