import csv
import re
import const
import smtplib

from_add = input('From: ')

while True:
    temp_path = input('Template file path: ')
    try:
        with open(temp_path, 'r') as tp:
            if not re.match(r'.txt$', temp_path):
                print('Template must be a .txt file')
            break
    except FileNotFoundError:
        print('File not found')

while True:
    csv_path = input('CSV file path: ')
    try:
        with open(csv_path, 'r') as tp:
            if not re.match(r'.csv$', csv_path):
                print('Template must be a .csv file')
            break
    except FileNotFoundError:
        print('File not found')

def read_csv():
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            colnames = next(reader)[0].split(',')
            data = []

            while True:
                try:
                    rowdata = next(reader)[0].split(',')
                    rowdict = {}
                    for nocol in range(len(colnames)):
                        rowdict[colnames[nocol]] = rowdata[nocol]
                    data.append(rowdict)
                except StopIteration:
                    break

            return colnames, data

    except FileNotFoundError:
        print('File not found')
        return

def read_template():
    try:
        with open(temp_path, 'r') as tempfile:
            filestring = tempfile.readlines()
            indexes = [None]*4

            for i in range(len(filestring)):
                if const.SUBJECT_OPEN_TAG in filestring[i]:
                    indexes[0] = i
                if const.SUBJECT_CLOSE_TAG in filestring[i]:
                    indexes[1] = i
                if const.BODY_OPEN_TAG in filestring[i]:
                    indexes[2] = i
                if const.BODY_CLOSE_TAG in filestring[i]:
                    indexes[3] = i

            indexescopy = indexes.copy()
            indexescopy.sort()

            if indexes == indexescopy:
                subject = ''.join(filestring[indexes[0]+1:indexes[1]])
                body = ''.join(filestring[indexes[2]+1:indexes[3]])
                subvars = re.findall(r'\$<[A-z]+>',subject)
                bodyvars = re.findall(r'\$<[A-z]+>',body)
                return subject, subvars, body, bodyvars
            else:
                print('Template syntax error')
                return

    except FileNotFoundError:
        print('File not found')
        return

def write_emails():
    emails = []
    colnames, data= read_csv()
    subject, subvars, body, bodyvars = read_template()

    if not colnames[0] == 'emad':
        print('The first column of the csv must be named \'emad\' and must contain the email addresses')
        return

    for dt in data:
        add = dt[colnames[0]]
        sub = (subject + '.')[:-1]
        bod = (body + '.')[:-1]

        for col in colnames:

            for subvar in subvars:
                if col in subvar:
                    sub = sub.replace(subvar, dt[col])

            for bodyvar in bodyvars:
                if col in bodyvar:
                    bod = bod.replace(bodyvar, dt[col])

        emails.append({'address': add, 'subject': sub, 'body': bod})

    return emails

def send_email(email):
    server = smtplib.SMTP(const.HOST, const.PORT)
    server.login(const.API_KEY, const.SECRET_KEY)
    #YOUR AUTH METHODS
    server.sendmail(from_add, email['address'], 'Subject: {}\n\n{}'.format(email['subject'], email['body']))
    server.close()

emails = write_emails()
for email in emails:
    send_email(email)
