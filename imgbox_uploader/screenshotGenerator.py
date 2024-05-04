# Description: Captures x number of screenshots from a video file
# Operating System: Linux
# Dependencies: MediaInfo, ffmpeg, python

import subprocess, math, os, sys

# CLASSES
###################################################
class StringHelper:
	@staticmethod
	def wrap(text): # in quotes
		return '"{}"'.format(text)

	@staticmethod
	def lead_with_zeroes(arg, num_zeroes):
		_arg = arg if isinstance(arg, str) else str(int(arg))
		return _arg.zfill(num_zeroes)

	@staticmethod
	def is_number(arg):
		return arg.isdigit()


class Time:
	def __init__(self):
		self.h = 0
		self.w = 0

	def from_minutes(self, minutes):
		self.h = math.floor(minutes / 60)
		self.m = minutes - (self.h * 60)

	def as_minutes(self):
		return self.h * 60 + self.m

	def as_string(self):
		return "{}h{}m".format(self.h, self.m)

	def set(self, duration_string):
		self.__init__()
		value = ''
		for char in duration_string:
			if char.isdigit():
				value += char
			elif char == 'h' or char == 'm':
				setattr(self, char, int(value))
				value = ''

def generateScreenshots(file, amount):
	cmd = ""
	time = Time()

	input_path = os.path.abspath(file)
	output_dir = os.path.dirname(input_path)

	raw_input_file = os.path.basename(input_path)				# without file extension
	print("Starting screenshot generation...")
	print("Input file: %s" % raw_input_file)
	print("Output path: %s" % output_dir)
	output_file = "{}/{}_{}.png".format(output_dir, raw_input_file, '{}')

	command = 'mediainfo {}'.format(StringHelper.wrap(input_path))
	info = subprocess.check_output(command, shell=True)
	duration = 'Not found'

	for line in info.decode().split('\n'):
		if 'Duration' in line:
			duration = line.split(':')[1]
			break

	if duration == 'Not found':
		exit(1)

	time.set(duration)
	screenshot_count = int(amount)

	interval_count = screenshot_count + 2
	interval = math.floor(time.as_minutes() / interval_count)
	digit_count = len(str(screenshot_count))
	screenshotList = []

	for i in range(screenshot_count):
		minute_stamp = interval * (i + 1)
		time.from_minutes(minute_stamp)

		splitter = ' && ' if i != 0 else ''
		cmd += splitter

		hour = StringHelper.lead_with_zeroes(time.h, 2)
		minute = StringHelper.lead_with_zeroes(time.m, 2)

		time_value = '{}:{}:00'.format(hour, minute)
		input_cmd = '-i {}'.format(StringHelper.wrap(input_path))
		output_value = output_file.format(StringHelper.lead_with_zeroes(i+1, digit_count))
		sub_cmd = "ffmpeg -ss {} {} -y -loglevel error -vframes 1 -vf \"scale='max(sar,1)*iw':'max(1/sar,1)*ih'\" {}"
		cmd += sub_cmd.format(time_value, input_cmd, StringHelper.wrap(output_value))
		screenshotList.append(output_file.format(StringHelper.lead_with_zeroes(i+1, digit_count)))

	print("Starting ffmeg...")
	subprocess.call(cmd, shell=True)
	print("Screenshot generation finished")
	return screenshotList
