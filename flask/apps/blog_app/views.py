import json
from markdown import markdown
from flask import Flask,Blueprint,redirect,jsonify,Markup
import os
import boto3
import os

s3_client = boto3.client('s3',
      aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
      aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
      region_name=os.getenv("S3_REGION")
      )

#ブループリントを作成
# url_prefixを追加したBlueprintオブジェクトを作成
blog_app = Blueprint("blog_app",__name__,url_prefix="/blog_app")

#--S3版-- Blogstopページの内容をS3のjsonファイルから取得してjsonデータを返す
@blog_app.route("/get_blogstopjson",methods=["GET"],endpoint="get_blogstopjson")
def get_blogstopjson():
  try:
    # S3からjsonファイルをダウンロード->ファイルのうち本文の記述内容のJSON型文字列->json.loadsで辞書へ変更しjson_dictに格納
    response = s3_client.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key="mdblog-content/md_contents.json")
    json_dict = json.loads(response['Body'].read().decode('utf-8'))
    # 辞書に新しいキーで要素を追加可能(ここでは記事の件数をcountキーで追加)
    json_dict["count"]=len(json_dict["md_contents"])

  except s3_client.exceptions.NoSuchKey:
    # ファイルが存在しない場合はスキップします
    pass
  # jsonify(辞書) -> JSON文字列として返す
  return jsonify(json_dict)


#--S3版 S3のjsonファイルと引数のタグ名から該当記事一覧を取得する
@blog_app.route("get_articles_by_tag/<tag_name>",methods=["GET"],endpoint="get_articles_by_tag")
def get_articles_by_tag(tag_name):
  try:
    
    # S3からjsonファイルをダウンロード->ファイルのうち本文の記述内容のJSON型文字列->json.loadsで辞書へ変更しjson_dictに格納
    response = s3_client.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key="mdblog-content/md_contents.json")
    json_dict = json.loads(response['Body'].read().decode('utf-8'))
    
    # 引数のtag_nameを含んだページのリストを取得
    # json_dict辞書からmd_contentsのキーに対応する要素でforを回し、要素を作成し直す
    # ただし、その要素のtagsキーに、引数tag_nameを含んでいるものだけが対象となる。
    searched_contents = [content for content in json_dict["md_contents"] if tag_name in content["tags"]]
    

  except s3_client.exceptions.NoSuchKey:
    # ファイルが存在しない場合はスキップします
    pass
  # jsonify(辞書) -> JSON文字列として返す
  return jsonify({"accessed --/get_articles_by_tag":"success","search_tag_name":tag_name, "searched_contents":searched_contents,"count":len(searched_contents)})

#--S3_md版 引数のファイル名に該当する記事を1つ取得----------------

@blog_app.route("/get_article_md/<filename>",methods=["GET"],endpoint="get_article_md")
def get_article_md(filename):
  
  try:
    # S3からmdファイルをダウンロードし、ファイルの内容をmd_contentに格納
    response = s3_client.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key="mdblog-content/testmd/"+filename+".md")
    
    md_content = response['Body'].read().decode('utf-8')
    
    md_content = md_content.replace('<img src="./',
                                    '<img src="https://imagecheckhandsonnanonets.s3.ap-northeast-1.amazonaws.com/mdblog-content/testmd/')
    
    codehilite_configs = {
        #python-markdownのcodehilite用の設定
        'codehilite':{
            #mdファイル内のコードブロック```領域に当てるスタイルをpygments_styleで指定
            'pygments_style': 'dracula',
            #noclassesはTrueにしないと、pygments_styleがコードブロックに当たらない
            'noclasses': True,
            #linenums=行番号をつける
            'linenums': True,
            # guess_lang=コードブロックで使われている言語に合わせてスタイルを変える
            'guess_lang': True
            # noclasses==True && linenums==Trueなら別途cssでpreタグにline-height: 125%;が必要。
            # ないと行番号とコードがずれる
        }
    }
    #拡張機能を使用してhtmlへ変換しつつ{{md_convert}}に使われる値へ変換
    #tab_lentgh=4は空白4つで、ネストリストや、コードブロックのインデントとする
    #他の拡張機能はmdファイルのテーブル記法変換、番号付きリストと箇条書きリストの混在可設定、codehiliteを使うためのfencedcode、[TOC]を記載しておけば目次を作成してくれるtoc
    mup=Markup(markdown(md_content,
                        extensions=['attr_list','tables','sane_lists','fenced_code','codehilite','toc'],
                        extension_configs=codehilite_configs,
                        tab_length=2))
    

  except s3_client.exceptions.NoSuchKey:
    # ファイルが存在しない場合はスキップします
    pass

  return jsonify({"filename":filename,"mup":mup})

#--S3_ipynbファイルからのhtml版 引数のファイル名に該当する記事を1つ取得----------------
@blog_app.route("/get_article_ipynb/<filename>",methods=["GET"],endpoint="get_article_ipynb")
def get_article_ipynb(filename):
  
  try:
    # S3からmdファイルをダウンロードし、ファイルの内容をhtml_contentに格納
    response = s3_client.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key="mdblog-content/testmd/"+filename+".html")
    
    html_content = response['Body'].read().decode('utf-8')
    
    html_content = html_content.replace(' alt="No description has been provided for this image"','')
    html_content = html_content.replace('<img src="./',
                                    '<img src="https://imagecheckhandsonnanonets.s3.ap-northeast-1.amazonaws.com/mdblog-content/testmd/')
    print("--------type(html_content)=",type(html_content))
    codehilite_configs = {
        #python-markdownのcodehilite用の設定
        'codehilite':{
            #mdファイル内のコードブロック```領域に当てるスタイルをpygments_styleで指定
            'pygments_style': 'dracula',
            #noclassesはTrueにしないと、pygments_styleがコードブロックに当たらない
            'noclasses': True,
            #linenums=行番号をつける
            'linenums': True,
            # guess_lang=コードブロックで使われている言語に合わせてスタイルを変える
            'guess_lang': True
            # noclasses==True && linenums==Trueなら別途cssでpreタグにline-height: 125%;が必要。
            # ないと行番号とコードがずれる
        }
    }
    #拡張機能を使用してhtmlへ変換しつつ{{md_convert}}に使われる値へ変換
    #tab_lentgh=4は空白4つで、ネストリストや、コードブロックのインデントとする
    #他の拡張機能はmdファイルのテーブル記法変換、番号付きリストと箇条書きリストの混在可設定、codehiliteを使うためのfencedcode、[TOC]を記載しておけば目次を作成してくれるtoc
    mup=Markup(markdown(html_content,
                        extensions=['attr_list','tables','sane_lists','fenced_code','codehilite','toc'],
                        extension_configs=codehilite_configs,
                        tab_length=2))
    print("--------type(mup)=",type(mup))
    print("---/get_article_ipynb--type(mup)=",type(mup))

  except s3_client.exceptions.NoSuchKey:
    # ファイルが存在しない場合はスキップします
    pass

  return jsonify({"filename":filename,"mup":mup})


