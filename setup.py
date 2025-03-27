"""
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whatsapp-chatgpt-python",
    version="1.0.0",
    author="GREEN-API",
    author_email="support@green-api.com",
    description="A modern WhatsApp bot library with OpenAI GPT integration on Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/green-api/whatsapp-chatgpt-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.7",
    install_requires=[
        "whatsapp-chatbot-python>=0.9.6",
        "openai>=1.66.3",
        "requests>=2.32.3"
    ],
)
