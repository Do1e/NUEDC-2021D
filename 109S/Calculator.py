from math import pi, atan, ceil
import numpy as np
from scipy.linalg import lstsq
g = 9.7949
min_ms = 50


def calculate_angle_period(List1, List2):
	List1 = np.array(List1, dtype=np.float64)
	List2 = np.array(List2, dtype=np.float64)
	print(List1)
	print(List2)
	t1 = (List1[:, 0] - List1[0, 0]) * 1000
	t2 = (List2[:, 0] - List1[0, 0]) * 1000
	x1 = List1[:, 1]
	x2 = List2[:, 1]
	y1 = List1[:, 2]
	y2 = List2[:, 2]
	errorP = []
	for i in range(1, x1.shape[0] - 1):
		if (np.abs(x1[i]-x1[i-1]) >= 55 and np.abs(x1[i]-x1[i+1]) >= 55) or (np.abs(y1[i]-y1[i-1]) >= 30 and np.abs(y1[i]-y1[i+1]) >= 30):
			errorP.append(i)
	x1 = np.delete(x1, errorP)
	y1 = np.delete(y1, errorP)
	t1 = np.delete(t1, errorP)
	errorP.clear()
	for i in range(1, x2.shape[0] - 1):
		if (np.abs(x2[i]-x2[i-1]) >= 55 and np.abs(x2[i]-x2[i+1]) >= 55) or (np.abs(y2[i]-y2[i-1]) >= 30 and np.abs(y2[i]-y2[i+1]) >= 30):
			errorP.append(i)
	x2 = np.delete(x2, errorP)
	y2 = np.delete(y2, errorP)
	t2 = np.delete(t2, errorP)
	
	minj = 0
	matchList = []
	for i in range(0, len(t1)):
		for j in range(minj, len(t2)):
			if(abs(t1[i] - t2[j]) < min_ms):
				minj = min(j + 1, len(t2) - 1)
				matchList.append([t1[i], t2[j], -x2[j], x1[i]])
				break
	matchList = np.array(matchList, dtype=np.float64)
	# print(matchList)
	# f = open("test.txt", "w")
	# for i in range(matchList.shape[0]):
	# 	f.write(str(matchList[i, 2])  + " " + str(matchList[i, 3])  + " " + str(matchList[i, 0])  + " " + str(matchList[i, 1]) + "\n")
	# f.close()
	if(max(x1) < max(x2)):
		A = np.vstack([(matchList[:, 2])**0, (matchList[:, 2])**1])
		sol, _, _, _ = lstsq(A.T, matchList[:, 3])
		theta = atan(sol[1]) * 180 / pi
	else:
		A = np.vstack([(matchList[:, 3])**0, (matchList[:, 3])**1])
		sol, _, _, _ = lstsq(A.T, matchList[:, 2])
		theta = atan(1 / sol[1]) * 180 / pi


	def getAvaT(x, t):
		max_t = []
		min_t = []
		for i in range(2, x.shape[0] - 2):
			if (x[i-1] <= x[i] and x[i+1] < x[i] and x[i-2] <= x[i] and x[i+2] < x[i]):
				max_t.append(t[i])
			if (x[i-1] >= x[i] and x[i+1] > x[i] and x[i-2] >= x[i] and x[i+2] > x[i]):
				min_t.append(t[i])
		max_t = np.array(max_t)
		min_t = np.array(min_t)
		max_mean = np.mean(np.abs(max_t[0:len(max_t)//2] - max_t[-(len(max_t)//2):])) / ceil(len(max_t)/2)
		min_mean = np.mean(np.abs(min_t[0:len(min_t)//2] - min_t[-(len(min_t)//2):])) / ceil(len(min_t)/2)
		Ava_t = (min_mean * (len(min_t)//2) + max_mean * (len(max_t)//2)) / ((len(min_t)//2) + (len(max_t)//2))
		return Ava_t

	Ava_t1 = getAvaT(x1, t1) / 1000
	Ava_t2 = getAvaT(x2, t2) / 1000

	if(abs(theta) < 30):
		Weight1 = 0
		Weight2 = 1
	elif(abs(theta) > 60):
		Weight1 = 1
		Weight2 = 0
	else:
		Weight1 = (abs(theta) - 30) / 30
		Weight2 = 1 - Weight1
	ansL1 = g * (Ava_t1 / (2 * pi)) * (Ava_t1 / (2 * pi)) - 0.078
	ansL2 = g * (Ava_t2 / (2 * pi)) * (Ava_t2 / (2 * pi)) - 0.078
	LengthRe = ansL1 * Weight1 + ansL2 * Weight2
	return LengthRe, theta
	

# List1 = []
# List2 = []
# with open("data1_59.txt") as f:
# 	for line in f.readlines():
# 		List1.append(line.split())
# with open("data2_59.txt") as f:
# 	for line in f.readlines():
# 		List2.append(line.split())

# # print(List2, "\n\n", List2)
# L, T = calculate_angle_period(List1, List2)
# print(L, T)