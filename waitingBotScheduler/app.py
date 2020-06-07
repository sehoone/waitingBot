from flask import Flask, url_for, render_template, request, redirect, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from sqlalchemy.orm import relationship
import cv2
import numpy as np
import pyautogui
import random
import time
import platform
import subprocess
import schedule
import serial
from PIL import ImageGrab
import pytesseract

import time
import json
import datetime
import re

is_retina = False
if platform.system() == "Darwin":
    is_retina = subprocess.call("system_profiler SPDisplaysDataType | grep 'retina'", shell=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dgwyneth:Gwy@neth!1@221.139.81.198:3306/D_SEHOON_DB?charset=utf8'
db = SQLAlchemy(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

###Models####
class WaitingBotInfo(db.Model):
	__tablename__ = "waiting_bot_info"
	__table_args__ = {"mysql_collate":"utf8_general_ci"}
	bot_info_seq = db.Column(db.BIGINT, primary_key=True)
	game_name = db.Column(db.String(50))
	create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

	def create(self):
	  db.session.add(self)
	  db.session.commit()
	  return self
	def __init__(self,game_name,create_date):
		self.game_name = game_name
		self.create_date = create_date

class WaitingBotDetail(db.Model):
	__tablename__ = "waiting_bot_detail"
	__table_args__ = {"mysql_collate":"utf8_general_ci"}
	bot_detail_seq = db.Column(db.BIGINT, primary_key=True)
	bot_info_seq = db.Column(db.Integer, db.ForeignKey('waiting_bot_info.bot_info_seq'),nullable=False)
	server_name = db.Column(db.String(50))
	wait_cnt = db.Column(db.Integer)
	create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

	def create(self):
	  db.session.add(self)
	  db.session.commit()
	  return self
	def __init__(self,bot_info_seq,server_name,wait_cnt,create_date):
		self.bot_info_seq = bot_info_seq
		self.server_name = server_name
		self.wait_cnt = wait_cnt
		self.create_date = create_date
		
#db.create_all()
class WaitingBotInfoSchema(ModelSchema):
	class Meta(ModelSchema.Meta):
		model = WaitingBotInfo
		sqla_session = db.session
	bot_info_seq = fields.Number(dump_only=True)
	game_name = fields.String(required=True)
	create_date = fields.DateTime(required=True)

class WaitingBotDetailSchema(ModelSchema):
	class Meta(ModelSchema.Meta):
		model = WaitingBotDetail
		sqla_session = db.session
	bot_detail_seq = fields.Number(dump_only=True)	
	bot_info_seq = fields.Number(required=True)
	server_name = fields.String(required=True)
	wait_cnt = fields.Integer(required=True)
	create_date = fields.DateTime(required=True)

@app.route('/run-tasks')
def run_tasks():
	app.apscheduler.add_job(func=waitBotJob, trigger='interval', seconds=30, id='waitBotJob')
	#app.apscheduler.add_job(func=waitBotJob, trigger='interval', minutes=10, id='waitBotJob')
	#for i in range(2):
		#app.apscheduler.add_job(func=scheduled_task, trigger='interval', seconds=10, args=[i], id='j'+str(i))
		#app.apscheduler.add_job(func=job, trigger='interval', seconds=10, args=[i], id='j'+str(i))
	return 'Scheduled several long running tasks.', 200

@app.route('/run-ocrtasks')
def run_ocr_tasks():
	print("run-ocrtasks start")
	#ocrTestJob()
	return pytesseract.image_to_string("image/waitCnt1.png",lang='kor')

def scheduled_task(task_id):
	for i in range(5):
		time.sleep(1)
		print('Task {} running iteration {}'.format(task_id, i))

@app.route('/products', methods = ['GET'])
def index():
	get_products = Product.query.all()
	product_schema = ProductSchema(many=True)
	products = product_schema.dump(get_products)
	print(make_response(jsonify({"product": products})))
	return make_response(jsonify({"product": products}))

@app.route('/products', methods = ['POST'])
def create_product():
	testVal = '{ "price": "222", "productBrand": "ㄷㄷ", "productDescription": "ㅂㅂ", "title": "ㄷㄷ" }'
	#data = request.get_json()
	data = json.loads(testVal)
	product_schema = ProductSchema()
	product = product_schema.load(data)
	result = product_schema.dump(product.create())
	return make_response(jsonify({"product": result}),200)

def r(num, rand):
    return num + rand * random.random()
    
def imagesearch(image, precision=0.8):
    im = pyautogui.screenshot()
    if is_retina:
        im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
    # im.save('testarea.png') useful for debugging purposes, this will save the captured region as "testarea.png"
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc

def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    height, width, channels = img.shape
    searchX = pos[0] + round(r(width / 2, 5))
    searchY = pos[1] + round(r(height / 2, 5))
    print("searchX : ",searchX)
    print("searchY : ",searchY)
    pyautogui.moveTo(searchX, searchY,
                     timestamp)
    pyautogui.click(button=action)

def selectImage(image):
    isExist = True
    pos = imagesearch(image)
    if pos[0] != -1:
        img2 = cv2.imread(image)
        height, width, channels = img2.shape
        searchX = pos[0] + round(r(width / 2, 5))
        searchY = pos[1] + round(r(height / 2, 5))
        print("searchX : ",searchX)
        print("searchY : ",searchY)
        sumXY = str(searchX) + "," + str(searchY) + ";"
        print("sumXY : ",sumXY)
        ser = serial.Serial('COM7', 9600, timeout=10)
        ser.write(str.encode(sumXY))
        ser.close()
    else:
        print("image not found")
        isExist = False
    return isExist

def screenCapture():
	pyautogui.screenshot("image/captureWaitImg.png", region=(197, 436, 35, 21))
	time.sleep(1)
	waitCnt = pytesseract.image_to_string("image/captureWaitImg.png", lang='kor')
	result = re.sub('[^0-9]', '', waitCnt)
	return result

def botWorker():
	botInfo = WaitingBotInfo(game_name='거상', create_date=datetime.datetime.now())
	db.session.add(botInfo)
	db.session.commit()
	print("insertId", botInfo.bot_info_seq)

	serverNames = ['백호','청룡','주작','현무']
	serverImages = ['image/selectServerWhiteLion.png','image/selectServerBlueDragon.png','image/selectServerJuJak.png','image/selectServerHyunmu.png']

	for index, value in enumerate(serverNames):
		selectImage(serverImages[index])
		time.sleep(2)
		selectImage("image/loginBtn.png")
		time.sleep(2)
		pos2 = imagesearch("image/loginGoBack.png")
		waitCnt = 0
		if pos2[0] != -1:
			print("대기중아님")
			time.sleep(3)
			selectImage("image/loginGoBack.png")
		else:
			print("대기중임.캡처로직추가")
			time.sleep(3)
			waitCnt = screenCapture()
			selectImage("image/waitCancel.png")

		botDetail = WaitingBotDetail(bot_info_seq=botInfo.bot_info_seq, server_name=value, wait_cnt=waitCnt, create_date=datetime.datetime.now())
		db.session.add(botDetail)
		db.session.commit()
		time.sleep(4)

def gameAliveWorker():
	serverNames = ['태황']
	serverImages = ['image/selectServerTaeHawang.png']

	for index, value in enumerate(serverNames):
		selectImage(serverImages[index])
		time.sleep(2)
		selectImage("image/loginBtn.png")
		time.sleep(2)
		pos2 = imagesearch("image/loginGoBack.png")
		waitCnt = 0
		if pos2[0] != -1:
			print("대기중아님")
			time.sleep(3)
			selectImage("image/loginGoBack.png")
		else:
			print("대기중임.캡처로직추가")
			time.sleep(3)
			selectImage("image/waitCancel.png")

		time.sleep(4)		

def ocrTestJob():
	screenCapture()

def waitBotJob():
	botWorker()

def gameAlive():
	gameAliveWorker()

app.apscheduler.add_job(func=waitBotJob, trigger='interval', minutes=10, id='waitBotJob')	
app.apscheduler.add_job(func=gameAlive, trigger='interval', minutes=2, id='gameAlive')

if __name__ == '__main__':
	app.debug = True
	#db.create_all()
	app.secret_key = "123"
	app.run(host='0.0.0.0', port=8000)
	
	