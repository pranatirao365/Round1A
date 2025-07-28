# 🧾 PDF Processing Solution

## 👋 Introduction

Welcome! This project is designed to automatically extract meaningful information from PDF documents and convert it into a structured format. Whether you're dealing with resumes, reports, or other text-heavy files, this tool will help you process them efficiently — all wrapped inside a Docker container for smooth and consistent execution.

---

## 💡 What’s the Idea?

The approach is straightforward:

1. We grab all the PDF files from an input folder.
2. We use Python's `PyMuPDF` library to extract the raw text from each file.
3. Then, we clean and analyze the text to find the pieces of information we care about.
4. Finally, we save the results into structured output files (like JSON or CSV) in an output folder.

It’s a rule-based method, so it doesn’t rely on machine learning — instead, it uses good old pattern matching and layout analysis to get the job done.

---

## 🧰 Tools & Libraries Used

- **Python 3**
- [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/) (`fitz`) — to extract and work with PDF content
- **Docker** — so you can run everything without installing Python or any libraries

---

## ⚙️ How to Build & Run It

First things first — make sure you have [Docker installed](https://www.docker.com/get-started/) on your machine.

### 🛠️ Step 1: Build the Docker Image

In your terminal or command prompt, run:

```bash
docker build --platform linux/amd64 -t mysolutionname:hack .
