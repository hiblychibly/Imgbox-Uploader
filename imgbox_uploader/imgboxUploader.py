#!/usr/bin/python

import requests
import re
import os
from PIL import Image
import imgbox_uploader.config as config


def isInvalidFile(file):
    if os.path.splitext(file)[1].lower() not in [".gif", ".jpeg", ".jpg", ".png"]:
        print(os.path.basename(file) + " is not a valid file, only gif/jpg/jpeg/png allowed")
        return True
    if os.path.getsize(file) > 10000000:
        print(os.path.basename(file) + " is too big, filesize limit is 10 MB")
        return True


def imgboxUpload(files):
    print("Starting imgbox upload...")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    imgbox_getAuthValues = session.get("https://imgbox.com/login")
    imgbox_authenticity_token = re.search('"authenticity_token" type="hidden" value="(.+?)" />', imgbox_getAuthValues.text).group(1)
    imgbox_login = session.post("https://imgbox.com/login", data={
        "utf8": "?",
        "authenticity_token": imgbox_authenticity_token,
        "user[login]": config.username,
        "user[password]": config.password})
    if "My Images" in imgbox_login.text:
        print("imgbox login successful!")
    else:
        print("imgbox login failed!")
        return
    imgbox_generate_tokens = session.get("https://imgbox.com/ajax/token/generate")
    if re.search('{"ok":(.+?),"token_id":(.+?),"token_secret":"(.+?)"}', imgbox_generate_tokens.text).group(1) == "true":
        print("Generating imgbox access tokens successful!")
        imgbox_token_id = re.search('{"ok":(.+?),"token_id":(.+?),"token_secret":"(.+?)"}', imgbox_generate_tokens.text).group(2)
        imgbox_token_secret = re.search('{"ok":(.+?),"token_id":(.+?),"token_secret":"(.+?)"}', imgbox_generate_tokens.text).group(3)
    else:
        print("Generating imgbox access tokens failed!")
        return
    images_bbcode = ""
    for file in files:
        if os.path.getsize(file) > 10000000:
            Image.open(file).save(file, "PNG")
        if isInvalidFile(file):
            continue
        print("Uploading " + os.path.basename(file))
        imgbox_image_post = session.post("https://imgbox.com/upload/process",
                                         data={
                                             "token_id": imgbox_token_id,
                                             "token_secret": imgbox_token_secret,
                                             "content_type": "1",
                                             "thumbnail_size": str(config.thumbnail_size_px) + "r" if config.resize_thumb else "c",
                                             "gallery_id": "null",
                                             "gallery_secret": "null",
                                             "comments_enabled": "0"},
                                         files={
                                             "files[]": open(file, "rb")})
        if imgbox_image_post.ok:
            image_full_url = re.search('"url":"(.+?)"', imgbox_image_post.text).group(1)
            image_thumb_url = re.search('"thumbnail_url":"(.+?)"', imgbox_image_post.text).group(1)
            images_bbcode += "[url=" + image_full_url + "][img]" + image_thumb_url + "[/img][/url] "
    print("Upload finished!")
    print(images_bbcode.strip())