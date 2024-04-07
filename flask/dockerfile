#Dockerfile
#ベースイメージ
FROM python:3.9.4
#requirements.txtを、コンテナの/usr/src/appに置きます。
#cdを/usr/src/appに変えてからCOPYします。
WORKDIR /usr/src/app

COPY requirements.txt ./
#requirements.txtの内容をpip3でインストールします。
RUN pip3 install pip --upgrade 
RUN pip3 install -r requirements.txt
