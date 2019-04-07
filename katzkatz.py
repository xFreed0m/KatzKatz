# A simple python script to parse text files containing output from mimikatz sekurlsa::logonpasswords
# create by @x_Freed0m


import argparse
import sys
from colorlog import ColoredFormatter
import logging
import csv
import os
import re
import magic


def my_args():
	args_parser = argparse.ArgumentParser()
	input_group = args_parser.add_mutually_exclusive_group(required=True)  # get at least file or folder
	input_group.add_argument('-F', '--folder', help="Folder containing multiple text files to parse")
	input_group.add_argument('-f', '--file', help="Single text file to parse")
	args_parser.add_argument('-o', '--output', help="Output csv file to save the creds", default="katzkatz")
	return args_parser.parse_args()


def configure_logger():
	"""
		This function is responsible to configure logging object.
	"""

	global LOGGER
	LOGGER = logging.getLogger("KatzKatz")
	# Set logging level
	LOGGER.setLevel(logging.INFO)

	# Create console handler
	log_colors = {
		'DEBUG': 'bold_red',
		'INFO': 'green',
		'WARNING': 'yellow',
		'ERROR': 'red',
		'CRITICAL': 'red',
	}
	formatter = "%(log_color)s[%(asctime)s] - %(message)s%(reset)s"
	formatter = ColoredFormatter(formatter, datefmt='%d-%m-%Y %H:%M', log_colors=log_colors)
	ch = logging.StreamHandler(sys.stdout)
	ch.setFormatter(formatter)
	LOGGER.addHandler(ch)


def excptn(e):
	LOGGER.critical("[!]Exception: " + str(e))
	exit(1)


def output(filename, db):
	try:
		with open(filename + ".csv", mode='a') as output_csv:
			fieldnames = ['Domain', 'Username', 'Password', 'NTLM-Hash']
			creds_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
			creds_writer.writeheader()  # adding the 1st line for the csv for filtering
			duplicate_rows = []
			total_unique = 0

			for row in db:
				if row in duplicate_rows:  # removing the same sets of creds
					continue
				creds_writer.writerow(row)
				duplicate_rows.append(row)
				total_unique += 1
			return total_unique
	except KeyboardInterrupt:
		LOGGER.critical("[CTRL+C] Stopping the tool")
		exit(1)
	except Exception as e:
		excptn(e)


def folder(path):
	return [os.path.join(path, f) for f in os.listdir(path)]


def is_valid_input(file_location):  # checking if file is txt or not (when running over a folder)
	mime = magic.Magic(mime=True)
	return os.path.isfile(file_location) and mime.from_file(file_location) == 'text/plain'


def parser(input_file):
	if not is_valid_input(input_file):
		LOGGER.error("File isn't text or doesn't exist, please recheck (moving forward to the next one)")
		return [], 0
	try:
		paragraph_regex = re.compile("\t((msv|tspkg|wdigest|kerberos|ssp|credman) :\t)\n((\t .*\n)+)", re.M)
		username_regex = re.compile("\s*\*\s+Username\s+:\s+((?!\(null\)).+)\s*(?!\$)", re.M)
		password_regex = re.compile("\s*\*\s+Password\s+:\s+((?!\(null\)).+)\s*(?!\$)", re.M)
		domain_regex = re.compile("\s*\*\s+Domain\s+:\s+((?!\(null\)).+)\s*(?!\$)", re.M)
		ntlm_regex = re.compile("\s*\*\s+NTLM\s+:\s+((?!\(null\)).+)\s*(?!\$)", re.M)
		db = []
		with open(input_file) as i:
			mimikatz_content = i.read()
			para = paragraph_regex.findall(mimikatz_content)
			cred_counter = 0
			for grp in para:
				user_dict = {}
				grp_content = grp[2]
				cred_counter += 1
				username = username_regex.findall(grp_content)
				if not username:
					continue
				user_dict['Username'] = username[0]
				password = password_regex.findall(grp_content)
				if password:
					if len(password[0]) < 255:
						user_dict['Password'] = password[0]
				domain_name = domain_regex.findall(grp_content)
				if domain_name:
					user_dict['Domain'] = domain_name[0]
				ntlm_hash = ntlm_regex.findall(grp_content)
				if ntlm_hash:
					user_dict['NTLM-Hash'] = ntlm_hash[0]
				if user_dict and not user_dict['Username'].endswith('$') and (
						'NTLM-Hash' in user_dict.keys() or 'Password' in user_dict.keys()):
					if user_dict not in db:
						db.append(user_dict)
		return db, cred_counter
	except KeyboardInterrupt:
		LOGGER.critical("[CTRL+C] Stopping the tool")
		exit(1)
	except Exception as e:
		excptn(e)


def logo():
	print("""
	/$$   /$$             /$$              /$$   /$$             /$$             
	| $$  /$$/            | $$             | $$  /$$/            | $$             
	| $$ /$$/   /$$$$$$  /$$$$$$  /$$$$$$$$| $$ /$$/   /$$$$$$  /$$$$$$  /$$$$$$$$
	| $$$$$/   |____  $$|_  $$_/ |____ /$$/| $$$$$/   |____  $$|_  $$_/ |____ /$$/
	| $$  $$    /$$$$$$$  | $$      /$$$$/ | $$  $$    /$$$$$$$  | $$      /$$$$/ 
	| $$\  $$  /$$__  $$  | $$ /$$ /$$__/  | $$\  $$  /$$__  $$  | $$ /$$ /$$__/  
	| $$ \  $$|  $$$$$$$  |  $$$$//$$$$$$$$| $$ \  $$|  $$$$$$$  |  $$$$//$$$$$$$$
	|__/  \__/ \_______/   \___/ |________/|__/  \__/ \_______/   \___/ |________/
	""")
	print('\nKatzKatz By @x_Freed0m\n')


def main():
	logo()
	args = my_args()
	configure_logger()
	total_creds = 0
	total_unique = 0
	db = []
	try:
		if args.file:
			db, cred_counter = parser(args.file)
			total_unique = output(args.output, db)
			total_creds += cred_counter
		elif args.folder:
			if not os.path.exists(args.folder):
				LOGGER.error("Path doesn't exist, please recheck")
			file_list = folder(args.folder)
			for current_file in file_list:
				new_db, cred_counter = parser(current_file)
				total_creds += cred_counter
				db += new_db
			total_unique = output(args.output, db)
		else:
			LOGGER.warning('Could not find it! Did you specify existing file or folder?')
		LOGGER.info('All done! parsed %s sets credentials, found %s valid creds\nUnique sets: %s.' % (
			total_creds, len(db), total_unique))
	except KeyboardInterrupt:
		LOGGER.critical("[CTRL+C] Stopping the tool")
		exit(1)
	except Exception as e:
		excptn(e)


if __name__ == '__main__':
	main()

# TODO: verify variables names are fine (beautify the code)
# TODO: add keytab generation
# TODO: add support for pin-codes
# TODO: print progress bar