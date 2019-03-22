FROM reg.xiaoneng.cn/library/python:3.6-alpine-utc8

COPY . /chattbot/
WORKDIR /chattbot

RUN  pip3 install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

ENV TZ "Asia/Shanghai"

ENTRYPOINT ["/bin/sh", "/chattbot/docker-entrypoint.sh"]
CMD ["gunicorn", "demo.wsgi", "--workers=5", "--bind=0.0.0.0:8000", "--reload"]
