#!/usr/bin/env python

import csv, random, sys, pickle, os, json
from getopt import getopt

# ------------- functions --------------
def is_assigned_self(list1, list2):
    for i in range(len(list1)):
        if list1[i][0] == list2[i][0]:
            return True
    return False

def load_config():
    f = open('config.json', 'r')
    txt = f.read()
    return json.loads(txt)

def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
    except:
        sys.stderr.write("Unable to send mail to " + user + os.linesep)
# ---------------------------------
help = """
NAME
    gift.py

DESCRIPTION

OPTIONS
    --help     Return help text.

    --file=<input.csv>
               The input csv delimited with ',' file containing 2 fields name and email.

    --look-up=<name>
               If you want to know who someone is assigned, pass their name to this
               option, and it will print out who they were assigned. This is use for
               people who can't remember their email password or don't have an email.

    --send     Send an email to each person informing them who they should get a gift
               for in the gift exchange.

    --cached   If you want to load users and assignments from the cached previous
               assignment.pickle.
"""
pfile = 'assignment.pickle'
assignment = {};
config = load_config()

# -------- handle arguments ---------
# defaults
f = False
lookup = False
cached = False
send = False

opts, remainder = getopt(sys.argv[1:], '', ['cached', 'file=', 'look-up=', 'send', 'help'])

# override defaults
for key, val in opts:
    if key == '--help':
        print help
        sys.exit(0)
    if key == '--file':
        f = val
    if key == '--cached':
        cached = True
    if key == '--look-up':
        lookup = val
    if key == '--send':
        send = True

# --------- obvious errors ---------
if f and cached:
    sys.stderr.write("Use either csv file or log not both" + os.linesep)
    sys.exit(1)
if not f and not cached:
    sys.stderr.write("You should either use --file or use --cached" + os.linesep)
    sys.exit(1)

# --------- load from file or cache ------------
if f:
    # load names from the csv file
    name_email = []
    try:
        fh = open(f, "r")
    except:
        sys.stderr.write("Unable to open csv file" + os.linesep)
        sys.exit(1)

    reader = csv.reader(fh)
    first = True
    for row in reader:
        if len(row) != 2:
            continue
        if first:
            first = False
            continue

        name_email.append(row)

    if len(name_email) < 2:
        sys.stderr.write("You Can't have a gift exchange without at least 2 people" + os.linesep)
        sys.exit(1)

    assigned = list(name_email)

    while True:
        random.shuffle(assigned)
        if is_assigned_self(name_email, assigned):
            continue
        break

    for i in range(len(name_email)):
        gifter = name_email[i]
        assignment[gifter[0]] = {'email': gifter[1], 'assigned': assigned[i][0]};

    pickle.dump(assignment, open(pfile, 'wb'))
elif cached:
    try:
        assignment = pickle.load(open(pfile, 'rb'))
    except:
        sys.stderr.write("Unable to open " + pfile + os.linesep)
        sys.exit(1)

# ------- print lookup name ----------
if lookup:
    print assignment[lookup]
    sys.exit(0)

# -------- Send emails ------------
if send:
    for key, val in assignment.iteritems():
        if val['email'] == '':
            continue
        subject = "Gift exchange assignments"
        body = "You are assigned %s for the gift exchange." % val['assigned']
        send_email(config['email'], config['password'], val['email'], subject, body)

