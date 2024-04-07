#app.py
from flask import Flask
from flask_cors import CORS
import os

#ブループリントblog_appのviews.pyをインポート
from apps.blog_app import views

def create_app(config_key):
  app=Flask(__name__)
  app.register_blueprint(views.blog_app,url_prefix="/blog_app")

  print("create_app----config_key=",config_key)
  if config_key == "dev":
    app.debug = True  # デバッグモードを有効にする
  elif config_key == "prod":
    app.debug = False  # デバッグモードを無効にする
  else:
    app.debug = False  # デバッグモードを無効にする
  #環境変数を読み込む(docker-composeのenv-fileを使っていることを前提)
  app.config["TESTING"] = os.getenv("TESTING")
  app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
  app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY")  
  

  CORS(app, resources={"/blog_app/*":{"origins":"http://flask:5000"}})

  return app
if __name__=="__main__":
    app=create_app()