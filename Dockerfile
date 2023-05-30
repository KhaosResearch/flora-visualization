FROM python:3.10.7

WORKDIR .
COPY . .
RUN pip3 install python-dotenv
RUN pip3 install -r requirements.txt

EXPOSE 5025

ENTRYPOINT ["streamlit", "run", "main.py", "--server.baseUrlPath=/services/flora/visualization", "--server.port=8501", "--server.address=0.0.0.0"]