# encoding: utf-8
import cv2
from detector import Detector
from datetime import datetime
import socket
import numpy as np
from time import time, sleep
localIP = 108
W = 640
H = 480
address = ('192.168.1.109', 8000+localIP)
name = "192.168.1."+str(localIP)

cap = cv2.VideoCapture(0)
cap.set(3, W)
cap.set(4, H)
detector = Detector()

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


try:
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	# 开启连接
	sock.connect(address)
except socket.error as msg:
	print(msg)
	exit(1)

# 图像质量
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 50]

cv2.namedWindow(name, 0)
cv2.resizeWindow(name, W, H)
cv2.moveWindow(name, 0, 0)
# temp = recvall(sock, 64)
# dt = float(recvall(sock, 64)) - time()
# print(dt)
while True:
	ret, frame = cap.read()
	if not ret:
		break
	# 发送当前时间
	now = time()
	sock.send(str.encode(str(now).ljust(64)))

	center, _, _ = detector.apply(frame)
	# cv2.putText(frame, str(datetime.now())[0:-7], (0, frame.shape[0]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, 8)
	cv2.line(frame, (0, H//2), (W, H//2), (100, 100, 100), thickness=1)
	cv2.line(frame, (W//2, 0), (W//2, H), (100, 100, 100), thickness=1)
	cv2.imshow(name, frame)
	key = cv2.waitKey(1)
	if((key & 0xff) == 27):
		break
	
	# 发送坐标
	# print(center)
	if(center is None):
		sock.send(str.encode(str(-1).ljust(16)))
		sock.send(str.encode(str(-1).ljust(16)))
	else:
		sock.send(str.encode(str(center[0, 0]).ljust(16)))
		sock.send(str.encode(str(center[1, 0]).ljust(16)))
	
	# 发送图片
	# frame = cv2.resize(frame, (W//2, H//2), interpolation=cv2.INTER_CUBIC)
	result, imgencode = cv2.imencode('.jpg', frame, encode_param)
	data = np.array(imgencode)
	stringData = data.tostring()
	sock.send(str.encode(str(len(stringData)).ljust(64)))
	sock.send(stringData)
	# print((time()-now)*1000)

sock.close()
cv2.destroyAllWindows()
