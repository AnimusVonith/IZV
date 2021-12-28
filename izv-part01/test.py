import csv

with open('test.csv', 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=";", quotechar='"')
	for row in reader:
		print(len(row))