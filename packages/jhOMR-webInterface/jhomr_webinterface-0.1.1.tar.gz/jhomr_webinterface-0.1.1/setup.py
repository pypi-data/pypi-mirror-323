from setuptools import setup, find_packages

setup(
    name='jhOMR_webInterface',
    version='0.1.1',
    author='Md Nur Kutubul Alam',
    author_email='alamjhilam@gmail.com',
    description='OMR format to be used in KUET. This program supports using of Web Interface making use of fastAPI',
    
    packages=find_packages(),  # Automatically find the 'jhOMR_webInterface' package
    
    install_requires=[
        'numpy',
        'pandas',
        'opencv-python',
        'openpyxl',
        'fastapi',
        'uvicorn',
        'requests',
        'Jinja2',
        'python-multipart'
    ],
    python_requires='>=3.7',
)
