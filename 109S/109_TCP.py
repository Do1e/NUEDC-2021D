import socket
from time import sleep, time
import cv2
import numpy as np
from datetime import datetime
import threading
# import RPi.GPIO as GPIO
from Calculator import *
import os
from time import sleep
W = 640
H = 480
KEY = 11
BEEP = 12
LED = 13
maxTime = 25

List1 = []
List2 = []
dataRead = False


def ReceiveVideo(PORT, name):
	address = ("0.0.0.0", PORT)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#将套接字绑定到地址, 在AF_INET下,以元组（host,port）的形式表示地址.
	sock.bind(address)
	#开始监听TCP传入连接。参数指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。
	sock.listen(2)

	def recvall(sock, count):
		buf = b''#buf是一个byte类型
		while count:
			#接受TCP套接字的数据。数据以字符串形式返回，count指定要接收的最大数据量.
			newbuf = sock.recv(count)
			if not newbuf: return None
			buf += newbuf
			count -= len(newbuf)
			# print(len(newbuf))
		return buf

	#接受TCP连接并返回（conn,address）,其中conn是新的套接字对象，可以用来接收和发送数据。addr是连接客户端的地址。
	#没有连接则等待有连接
	conn, addr = sock.accept()
	print('connect from:'+str(addr))
	print(str(datetime.now())[0:-7])
	
	cv2.namedWindow(name, 0)
	cv2.resizeWindow(name, W, H)
	if(name[-1] == '2'):
		cv2.moveWindow(name, 0, 0)
	else:
		cv2.moveWindow(name, 900, 0)
	# sock.send(str.encode((str(time())).ljust(64)))
	while 1:
		now = float(recvall(conn, 64))  # 获取当前图片的时间
		now = time()
		x = round(float(recvall(conn, 16)))
		y = round(float(recvall(conn, 16)))
		if((x != -1) and (y != -1) and dataRead):
			if(name[-1] == '2'):
				global List1
				# if(len(List1) >= 300):
				# 	del(List1[0])
				List1.append([now, x, y])
			else:
				global List2
				# if(len(List2) >= 300):
				# 	del(List2[0])
				List2.append([now, x, y])
		# print(len(List))
		length = int(recvall(conn, 64))  # 获得图片文件的长度,16代表获取长度
		# print(length)
		stringData = recvall(conn, length)  # 根据获得的文件长度，获取图片文件
		data = np.frombuffer(stringData, np.uint8)  # 将获取到的字符流数据转换成1维数组
		decimg=cv2.imdecode(data,cv2.IMREAD_COLOR)  # 将数组解码成图像
		cv2.imshow(name, decimg)
		# if(flag):
		# 	for i in range(1, len(npList)):
		# 		# print(List[i, 1], List[i, 2])
		# 		img = cv2.circle(decimg,(np.int(npList[i, 1]), np.int(npList[i, 2])), 3, (255, 255, 255), 2)
		# 	if(name[-1] == '2'):
		# 		cv2.imwrite("line1.jpg", img)
		# 	else:
		# 		cv2.imwrite("line2.jpg", img)
		k = cv2.waitKey(1) & 0xff
		if(k == 27):  # ESC
			sock.close()
			cv2.destroyAllWindows()
			# GPIO.cleanup()
			os._exit(0)

t1 = threading.Thread(target=ReceiveVideo, args=(8102, "192.168.1.102"))
t2 = threading.Thread(target=ReceiveVideo, args=(8108, "192.168.1.108"))
t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
t2.start()
while(0):
	print("ON")
	GPIO.cleanup()
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(KEY, GPIO.IN)
	GPIO.setup(BEEP, GPIO.OUT, initial=0)
	GPIO.setup(LED, GPIO.OUT, initial=0)
	GPIO.wait_for_edge(KEY, GPIO.RISING)
	print("Press time: " + str(datetime.now())[0:-7])

	List1.clear()
	List2.clear()
	sleep(20)
	dataRead = True
	startTime = time()
	while(1):
		if(time() - startTime >= maxTime):
			dataRead = False
			break
	l, th = calculate_angle_period(List1, List2)
	# print(l, th)
	print(len(List1), len(List2))
	print("\nlength = %.2fcm" % (float(l) * 100))
	print("theta = %.1f°" % th)
	# np.savetxt("~/EE/TCP/data1_" + str(th) + ".txt", List1, fmt="%.8f")
	# np.savetxt("~/EE/TCP/data2_" + str(th) + ".txt", List2, fmt="%.8f")


	GPIO.output(BEEP, 1)
	GPIO.output(LED, 1)
	print("time = %.4fs\n" % (time() - startTime))
	sleep(1)
	GPIO.output(BEEP, 0)
	GPIO.output(LED, 0)
	print("OFF")
t1.join()
t2.join()