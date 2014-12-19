import sys, os, json
from datetime import datetime


def find_tag_content(string, start, end, tagname):
	tag_start = string.find("<%s>" %tagname, start)
	if tag_start < 0 or tag_start > end:
		return None

	tag_end   = string.find("</%s>" %tagname, tag_start)

	if not (tag_end > tag_start and tag_end < end):
		print start, end
		print tag_start, tag_end, tagname
		# print string[start: end]
		sys.exit(-1)

	tag_string = string[tag_start + len(tagname) + 2: tag_end]

	return tag_string.strip()


def collect_articles(string):
	"""
	Parse the given string and return a list of {"title": ..., "time": datetime obj, "content": ..., "author": ...}
	"""
	start_pos, end_pos = 0, None

	result = []
	while True:
		start_pos = string.find("<REUTERS", start_pos)

		if start_pos < 0:
			break

		end_pos = string.find("</REUTERS>", start_pos)

		date_string = find_tag_content(string, start_pos, end_pos, "DATE")
		title_string = find_tag_content(string, start_pos, end_pos, "TITLE")
		body_string = find_tag_content(string, start_pos, end_pos, "BODY")

		author_string = find_tag_content(string, start_pos, end_pos, "AUTHOR")
		if date_string is None:
			print string[start_pos: end_pos]

		if author_string is not None:
			author_string = author_string.lower()
			if author_string.startswith("by "):
				author_string = author_string[2: ]

			idx = author_string.rfind(",")
			if idx > 0:
				author_string = author_string[: idx]

			author_string = author_string.strip()

		try:
			time = datetime.strptime(date_string[: date_string.rfind(".")], "%d-%b-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
			result.append({"title": title_string, "content": body_string, "author": author_string, \
			               "time": time})
		except ValueError as e:
			pass

		start_pos = end_pos + 1

	return result

def save_result(data, output_file):
	fs = open(output_file, 'w')

	for item in data:
		if item['content'] is None:
			continue
			
		try:
			fs.write("%s\n" %(json.dumps(item)))
		except Exception as e:
			continue

	fs.close()

def main():
	inputdir = sys.argv[1]
	output_file = sys.argv[2]

	articles = []
	for filename in os.listdir(inputdir):
		if not os.path.splitext(filename)[1] in ('.sgm'):
			continue

		filename = os.path.join(inputdir, filename)

		articles += collect_articles(open(filename, 'r').read())

	print "Parsing DONE"

	save_result(articles, output_file)


if __name__ == '__main__':
	main()