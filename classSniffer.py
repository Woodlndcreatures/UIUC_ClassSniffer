#! /usr/bin/env python3
courses = []

########################################################################################
# This is a script to detect open sections of classes at UIUC. For every course and CRN
# given, it will check to see if that course is open, and let you know if it is.
# It is meant to be run once by the user, and then every so often it will check again.
#
# You can set how long it waits between each check.
# Please go through the following section and set everything to how you like.
#
# You can choose to have this email you if a section opens up, or just write this fact
# to a file. The former will require some setup (like setting up Thunderbird or Outlook)
# while the latter is perhaps harder to check, or not much better than just doing it
# manually. The default is configured for your illinois.edu address (but others, like
# Gmail, can also be setup as well).
########################################################################################
#
# Fill this in to suit your needs
# One line per course, multiple CRNs per course is okay
# Copy the format here (including the double parentheses)
# The department and course title must be EXACTLY as displayed at courses.illinois.edu
# They ARE case sensitive
courses.append(('Mathematics', 'Probability Theory', 38063, 40671))
courses.append(('Psychology', 'Intro to Social Psych', 37034, 37040, 37032))

# How long to wait between each check
# The more you check, the more likely you'll catch an open section
# But then the people controlling the website might get suspicious
# I recommend 6-12 hour intervals, or absolutely no less than 3 hours
wait_time = 6

# Set to False to put results in the file below
# Otherwise results will be emailed
use_email = True 

# Used if use_email is False
file = 'C:\\Users\\Public\\opencourses.txt' 

# The email setup
email_domain = 'smtp.illinois.edu'
email_port = 587  # For other emails, this might be 25
email_acct = 'NetID'
email_addr = 'NetID@illinois.edu'
email_pswd = 'ADPassword'

# Set this to true if you want the script to send a test email
# This would only happen on the first run, to both make sure the
# script is running and that your email info is setup correctly
send_test_email = True

# You should be able to safely ignore everything below here
########################################################################################
########################################################################################

import re
from time import sleep
from urllib import request, parse, error
from http.cookiejar import CookieJar

def main():
     good = []
     for course in courses:
          dpmt, title = course[:2]
          for crn in course[2:]:
               print(dpmt, title, crn)
               request.install_opener(request.build_opener(request.HTTPCookieProcessor(CookieJar())))
               # In my testing, checking two courses wouldn't work on the same cookie *shrug*
               result = is_open(dpmt, title, crn)
               if result > 0:
                    good.append((title, crn))
               elif result < 0:
                    print('Error: something went wrong for {} section {}'.format(title, str(crn)))
     msg = ''
     for title, crn in good:
          msg += '{} section {} is open!\n'.format(title, crn)
     if msg: email('Good news, everyone!', msg)

def blogotubes(url):
     req = request.Request(url, 
          headers={'User-Agent': 'Open the courses I want!'})
          # Confuse UIUC sysadmins (and make our point clear)
     try:
          contents = request.urlopen(req).read().decode('utf-8')
     except error.URLError as u:
          print(u)
     except error.HTTPError as e:
          print(e)
     else:
          return contents
     return None

def geturl(txt, title):
     # Parse the link out of an <a> tag holding "title"
     m = re.search(r'<a href="(.*?)">\s*?{}</a>'.format(title), txt)
     if m: return m.group(1)
     else: return None

def parse(page, crn):
     page = page[page.find(str(crn)):] # Shorten the text to everything after the crn
     result = re.search(r'Availability:</div>\s*?<div.*?>(.*?)</div>', page).group(1) # Matches the first occurence
     print(result)
     return 'Open' in result # (Could be restricted)

def is_open(dpmt, course, crn):
     base = "http://my.illinois.edu"
     page = blogotubes('http://www.courses.illinois.edu')
     if not page:
          print(page); return -1
     url = geturl(page, 'Class Schedule')
     if not url: 
          print(url); return -1
     page = blogotubes(base+url)
     if not page: 
          print('lol'+page); return -1
     url = geturl(page, dpmt)
     if not url:
          print(url); return -1
     page = blogotubes(base+url) # Get list of courses in dpmt
     if not page:
          print(page); return -1
     url = geturl(page, course)
     if not url:
          print(url); return -1
     page = blogotubes(base+url) # Get list of sections in course
     if not page:
          print(page); return -1
     result = parse(page, crn) # Parse openness of section
     if result:
          return 1
     else:
          return 0

########################################################################################
# Email stuff
import smtplib
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to, sbjct, txt, host, port, acct, pswd, sndr):
	msg = MIMEMultipart()

	if isinstance(to, list):
		to = ', '.join(to)

	msg['To'] = to
	msg['Subject'] = sbjct
	msg['From'] = sndr
	msg['Date'] = formatdate(localtime=True)

	msg.attach(MIMEText(txt))

	server = smtplib.SMTP(host, port)
	server.starttls()
	server.login(acct, pswd)
	server.send_message(msg)

def email(sbjct, text):
     if use_email:
          send_email(email_addr, sbjct, text, email_domain, email_port, email_acct, email_pswd, email_addr)
     else:
          with open(file, 'a') as f:
               f.write(sjbct+'\n'+text+'\n\n')


# Now we start actually doing things
if send_test_email:
     email("Open course detector is working", "It appears you've setup the course detecting script fine!")
while True: # Never stop
     main()
     print("Sleeping")
     sleep(wait_time * 3600)
