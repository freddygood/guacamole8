#!/usr/bin/python 

import os
import sys
import numpy as np

def display_result(work_time, send_time, backends, incomplete):
	work_time_p95 = int(np.percentile(work_time, 95))

	send_time_sorted_list = sorted(send_time, key=lambda i: int(send_time[i]), reverse = True)

	if (len(send_time_sorted_list) >= 10):
		send_time_sorted_list = send_time_sorted_list[:9]

	print ("Event log file name: {}".format(file))
	print ("Backend groups involved: {}".format(len(backends)))
	print ("Working time's 95th percentile: {}".format(work_time_p95))
	print ("Top 10 of the longest sending requests: {}".format(', '.join(send_time_sorted_list)))
	print ("Requests with incomplete dataset: {}".format(incomplete))

	for gr in sorted(backends):
		print ("\nBackend group: {}".format(gr))
		print ("    Total backends involved: {}".format(len(backends[gr])))

		for n, b in enumerate(sorted(backends[gr]), 1):
			print ("    {}. {}".format(n, b))
			print ("        Requests: {}".format(backends[gr][b]['requests']))

			if (len(backends[gr][b]['errors'])):
				print "        Errors:"

				for e in sorted(backends[gr][b]['errors']):
					print "            {}: {}".format(e, backends[gr][b]['errors'][e])

def main_loop():

	work_time = []
	send_time = {}
	requests = {}
	backends = {}
	incomplete = 0

	with open(file, 'r') as f:
		for line in f:
			params = line.rstrip().split()

			time = params[0]
			request_id = params[1]
			state = params[2]

			if (len(params) > 3):
				backend_id = params[3]

			if (len(params) > 4):
				backend_param = ' '.join(params[4:]).replace("http://","")

			if (state == 'StartRequest'):
				requests[request_id] = {}
				requests[request_id]['backends'] = {}
				requests[request_id]['start'] = time
				requests[request_id]['state'] = 'Started'

			elif (state == 'StartMerge'):
				requests[request_id]['state'] = 'Merging'

				if (len(requests[request_id]['backends']) != 0):
					incomplete += 1

			elif (state == 'StartSendResult'):
				requests[request_id]['send'] = time
				requests[request_id]['state'] = 'Sending'

			elif (state == 'FinishRequest'):
				requests[request_id]['finish'] = time
				requests[request_id]['state'] = 'Finished'

				w_time = int(time) - int(requests[request_id]['start'])
				s_time = int(time) - int(requests[request_id]['send'])
				requests[request_id]['work_time'] = w_time
				requests[request_id]['send_time'] = s_time
				work_time.append(w_time)
				send_time[request_id] = s_time
				del requests[request_id]

			elif (state == 'BackendConnect'):
				requests[request_id]['backends'][backend_id] = { 'state': 'Connecting', 'name': backend_param }

				if (backend_id not in backends):
					backends[backend_id] = {}

				if (backend_param not in backends[backend_id]):
					backends[backend_id][backend_param] = { 'requests': '1', 'errors': {} }
				else:
					backends[backend_id][backend_param]['requests'] = int(backends[backend_id][backend_param]['requests']) + 1

			elif (state == 'BackendRequest'):
				requests[request_id]['backends'][backend_id]['state'] = 'Request'

			elif (state == 'BackendOk'):
				requests[request_id]['backends'][backend_id]['state'] = 'Finished'
				del requests[request_id]['backends'][backend_id]

				if (len(requests[request_id]['backends']) == 0):
					requests[request_id]['state'] = 'Complete'
				else:
					requests[request_id]['state'] = 'Incomplete'

			elif (state == 'BackendError'):
				requests[request_id]['backends'][backend_id]['state'] = 'Error'

				current_backend = requests[request_id]['backends'][backend_id]['name']

				if (backend_param not in backends[backend_id][current_backend]['errors']):
					backends[backend_id][current_backend]['errors'][backend_param] = 1
				else:
					backends[backend_id][current_backend]['errors'][backend_param] = int(backends[backend_id][current_backend]['errors'][backend_param]) + 1

	display_result(work_time, send_time, backends, incomplete)

##### main loop

if __name__ == '__main__':

	if (len(sys.argv) < 2):
		print ("No log file provided")
		sys.exit(1)

	file = sys.argv[1]
	if (not os.path.isfile(file)):
		print ("File {} not found".format(file))
		sys.exit(1)

	main_loop()
