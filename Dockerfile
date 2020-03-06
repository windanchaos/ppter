FROM python:3.6
WORKDIR /root/
COPY *.py requirement /root/
RUN pip install -r requirement -i  http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
ENTRYPOINT ["python","Jobs.py"]