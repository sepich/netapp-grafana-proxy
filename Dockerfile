FROM python:2
COPY proxy.py .
CMD ["python", "proxy.py"]
