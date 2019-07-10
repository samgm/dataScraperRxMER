import requests
import re
import numpy as np 
import math 

#Does a http GET on our behalf
r = requests.get('http://10.70.35.120:10001/getCmRxMerData/?cm_mac=6038E0583F87&duration=86400')

values_str = []
values_float = []
flagged_once = []
flagged_twice = []

mer_hit_index = 0 

data = r.text

if data == {} :
	#Grabs generic timestamp tags using regex and returns a list of matched items
	x = re.findall(r'["]\w+["]:\s\d+.\d' ,data)
	lenx = len(x)

	#Grabs MerData tags corresponding to every timestamp generated and returns a list of matched items
	y = re.findall(r'["]mer_data["]:\s+"(.*?)"', data) 
	leny = len(y)

	if lenx == leny: #Just a safety check if every timestamp yields a corresponding fresh batch of MER data
		for p in range(0,lenx):
			values_str = y[p].split(',') #y[lenx-1] because we need the most recent fresh batch of MER data to work upon
			values_float = [float(i) for i in values_str] #Converts the MER values form str to individual floats for processing.

			#This calculates the 3 sigma limit for the RxMer values
			#Reference: https://www.investopedia.com/terms/t/three-sigma-limits.asp

			mean = np.sum(values_float)/len(values_float)
			variance = np.var(values_float)
			std_dev = math.sqrt(variance)

			upper_ctrl_limit = mean + (3*std_dev)
			lower_ctrl_limit = mean - (3*std_dev)

			print("Details for " + str(p) + " timestamp: " + str(x[p]))
			c = 0

			for k in range(0,len(values_float)):
				if values_float[k] < upper_ctrl_limit and values_float[k] > lower_ctrl_limit:
					continue
				else:
					print("Problem with slice number: " + str(k)) #Prints the value violating 3 sigma limit
					flagged_once.append(k)
					c = c+1

			print("Done with scan !")
			if c == 0:
				print("No anomalies for "+ str(p) + " timestamp: " + str(x[p]))

			if len(flagged_once) > 0 :
				for i in range(0,len(flagged_once)):
					if i != len(flagged_once) - 1:  				#To dodge the case of comparing last value of the set with its immediate non existent successor
						if flagged_once[i+1] - flagged_once[i] == 1:
							flagged_twice.append(flagged_once[i]) #Include the first one of the 2 consecutive values to a flagged set
						else:
							continue
					else:
						break

				if len(flagged_twice) > 0:
					flagged_twice = list(set(flagged_twice)) #To have only unique entries in our flagged twice set
					print(flagged_twice)

					for t in range(0,len(flagged_twice)):
						mer_hit_index+=1

			else:
				print("No violations, all test results within 3 sigma limit !")

			flagged_once.clear()
			flagged_twice.clear()

		print("The MER hit index value is: " + str(mer_hit_index))

	else:
		print("Something's fishy ! Not as many value sets received as timestamps. Exiting the program.")
		exit()
else:
	print("No data captured for the given duration value. Exiting the program.")

exit()





