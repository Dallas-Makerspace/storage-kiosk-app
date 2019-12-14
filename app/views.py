from flask import render_template, flash, redirect, request, url_for, session
from app import app
import os
import requests
import json
from wtforms import TextField
from .forms import IndexForm
from .forms import StorageForm
from .forms import MemberNotFoundForm
from .forms import ServerErrorForm
from .forms import RegisterToVoteForm
from .emails import send_email
from .emails import send_email_request_voting_rights
from datetime import *
from escpos.printer import Usb
import csv

serverError = ''

@app.before_request
def session_management():
	    # make the session last indefinitely until it is cleared
    session.permanent = True

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # reset the session data
    session.clear()

    form  = IndexForm()
    if request.method == 'POST':
        member_id = str(form.member_id)
        member_id = member_id[:-2]                             # remove '">'
        member_id = member_id[member_id.find('value="') + 7:]  # Keep only ID
        # Get member information from Active Directory
        url = "http://192.168.200.32:8080/api/v1/lookupByRfid"
        payload = "rfid=" + member_id
        headers = {
                  'content-type': "application/x-www-form-urlencoded",
                  }
        try:
            details = payload
            response = requests.request("POST", url, data=payload, headers=headers)
            details = json.loads(response.text)

            if not 'user' in details['result']:
                return redirect(url_for('member_not_found'))

            # Use new API to get firstName and lastName
            url = "http://192.168.200.32:8080/api/v1/users/lookupByFields"
            payload = "username=" + details['result']['user']['username']
            headers = {
                'cache-control': "no-cache",
                'postman-token': "e6948c06-3b31-f48b-1f06-11e1b5226175",
                'content-type': "application/x-www-form-urlencoded"
                }
            response = requests.request("POST", url, data=payload, headers=headers)

            details = json.loads(response.text)

        except:
            serverError = str(details)
            return redirect(url_for('server_error'))

        session['member_id'] = member_id
        session['start'] = None
        session['slotID'] = None
        session['userName'] = details['result'][0]['username']
        session['fullName'] = details['result'][0]['firstName'] + ' ' + details['result'][0]['lastName']
        session['email'] = details['result'][0]['email']
        session['phone'] = details['result'][0]['phone']
        session['description'] = None
        session['expire'] = None
        session['storageType'] = None

        return redirect('/storage/'+ str(form.member_id))

    return render_template('index.html',
                           title='Home',
                           form=form)


@app.route('/storage/<member_id>', methods=['GET', 'POST'])
def storage(member_id):

    global serverError

    error = False
    form  = StorageForm()

    if request.method == 'GET':
        print('GET')
        # Get values from Active Directory (session) or the form
        if session['member_id'] != None:
            member_id = session['member_id']
            session['member_id'] = None
        else:
            member_id = ''

        if session['start'] != None:
            start = session['start']
            session['start'] = None
        else:
            start = ''

        if session['slotID'] != None:
            slotID = session['slotID']
            session['slotID'] = None
        else:
            slotID = ''

        if session['userName'] != None:
            userName = session['userName']
            session['userName'] = None
        else:
            userName = ''

        if session['fullName'] != None:
            fullName = session['fullName']
            session['fullName'] = None
        else:
            fullName = ''

        if session['email'] != None:
            email = session['email']
            session['email'] = None
        else:
            email = ''

        if session['phone'] != None:
            phone = session['phone']
            session['phone'] = None
        else:
            phone = ''

        if session['description'] != None:
            description = session['description']
            session['description'] = None
        else:
            description = ''

        if session['expire'] != None:
            expire = session['expire']
            session['expire'] = None
        else:
            expire = ''

        if session['storageType'] != None:
            storageType = session['storageType']
            session['storageType'] = None
        else:
            storageType = ''

        # Log times are in UTC
        utcTime = datetime.now(timezone.utc)

        # Determine expiration date using local time
        localTime= utcTime.astimezone()
        if start == '':
            start = localTime.strftime('%Y-%m-%d')
        if expire == '':
            expire = expiration(localTime.year,
                localTime.month, localTime.day)

            # Format date and time
            #expire = expire.strftime('%B') + ' ' + str(expire.day)

    else:
        if request.method == 'POST':
            print('POST')
            # Save values from the form
            member_id = session['member_id'] = request.form.get('memberID')
            start = session['start'] = request.form.get('start')
            slotID = session['slotID'] = request.form.get('slotID')
            userName = session['userName'] = request.form.get('userName')
            fullName = session['fullName'] = request.form.get('fullName')
            email = session['email'] = request.form.get('email')
            phone = session['phone'] = request.form.get('phone')
            description = session['description'] = request.form.get('description')
            expire = session['expire'] = request.form.get('expire')
            storageType = session['storageType'] = request.form.get('storageType')

            if request.form['submit'] == 'print':
                try:
                    createTicket(member_id)
                except:
                    error = True
                    return render_template('storage.html', form=form, error = error,
                        memberID=member_id, start=start, slotID=slotID, userName=userName,
                        fullName=fullName, email=email, phone=phone, description=description,
                        expire=expire, setStorageType=storageType)

            return redirect(url_for('index'))

    return render_template('storage.html', form=form,
        memberID=member_id, start=start, slotID=slotID, userName=userName,
        fullName=fullName, email=email, phone=phone, description=description,
        expire=expire, setStorageType=storageType)


def createTicket(member_id):
    """ Create and print a storage ticket
    """

    # Log times are in UTC
    utcTime = datetime.now(timezone.utc)

    # Determine expiration date using local time
    localTime= utcTime.astimezone()
    expire = expiration(localTime.year,
        localTime.month, localTime.day)

    # Format date and time
    expire = expire.strftime('%B') + ' ' + str(expire.day)
    localTime = localTime.strftime('%Y-%m-%d %H:%M')

    printTicket(member_id,
        request.form['slotID'],
        expire,
        request.form.get('userName'),
        request.form.get('name'),
        request.form.get('email'),
        request.form.get('phone'),
        request.form.get('storageType'),
        request.form.get('description'),
        localTime,
        request.form.get('completion'))

    # Write log
    outputFile = open('storage.log', 'a', newline='')
    outputWriter = csv.writer(outputFile)
    outputWriter.writerow([member_id, localTime,
        expire,
        request.form['slotID'],
        request.form.get('storageType'),
        request.form.get('userName'),
        request.form.get('name'),
        request.form.get('email'),
        request.form.get('phone')])
    outputFile.close()
    print("after write log")

def firstSunday(year, month):
    """ Determine the date of the first Sunday of the month.
    """

    for i in range(1, 8):
        if date(year, month, i).weekday() == 6:
            break

    return date(year, month, i)

def expiration(year, month, day):
    """ Determine the expiration date.
    """

    today = date(year, month, day)

    # If less than 7 days to the next First Sunday, give an extra month
    today = today + timedelta(days=7)

    expire = firstSunday(year, month)
    if expire <= today:
        # Expire next month
        month = month + 1
        if month > 12:
            # Happy New Year!
            year = year + 1
            month = 1
        expire = firstSunday(year,month)

    return expire

def printTicket(member_id, slot, expirationDate, username, name, email, phone, storageType, description, printTime, completion):
    """ Print a storage ticket and receipt.
    """

    p = Usb(0x04b8, 0x0e15, 0)

    p.set(align='center', text_type='B', width=4, height=4)
    p.text(expirationDate)
    p.text("\n")

    p.set(align='center', width=1, height=1)
    p.text("storage expiration date\n\n")

    p.set(align='center', width=2, height=2)
    p.text("DMS Storage Ticket\n")
    p.text(str.format("Slot:\t{}\n\n", slot))
    p.text(str.format("Name:\t{}\n\n", name))

    p.set(align='left')
    p.text("Ticket required on any items left at DMS.\n")
    p.text("Place ticket in holder or on project.\n\n")

    p.set(align='left')
    p.text(str.format("User:\t{}\n", username))
    p.text(str.format("Email:\t{}\n", email))
    p.text(str.format("Phone:\t{}\n", phone))
    p.text(str.format("Type:\t{}\n", storageType))
    p.text(str.format("Desc:\t{}\n", description))
    p.text(str.format("Start:\t{}\n", printTime))
    p.text(str.format("Compl:\t{}\n", completion))

    p.text("\n\n")
    p.text("Signature: ____________________________________\n")
    p.text("By signing you agree to follow the posted rules and remove your item before the expiration date.\n")
    p.text("Failure to remove items will result in loss of\nstorage privileges.")

    p.set(align='center')
    p.text("\n")
    qrDataString = str.format("{};{};{};{}", member_id, slot, storageType, expirationDate)
    p.qr(qrDataString, 1, 6, 2)

    p.cut()

    p.set(align='center', width=2, height=2)
    p.text("DMS Storage Receipt\n\n")

    p.set(align='left', width=1, height=1)
    p.text("Keep this receipt as a reminder that you\n")
    p.text("agreed to remove your item before:\n")
    p.set(align='center', text_type='B', width=2, height=2)
    p.text(expirationDate)
    p.text("\n\n")

    p.set(align='left')
    p.text(str.format("User:\t{}\n", username))
    p.text(str.format("Name:\t{}\n", name))
    p.text(str.format("Email:\t{}\n", email))
    p.text(str.format("Phone:\t{}\n", phone))
    p.text(str.format("Type:\t{}\n", storageType))
    p.text(str.format("Desc:\t{}\n", description))
    p.text(str.format("Start:\t{}\n", printTime))
    p.text(str.format("Compl:\t{}\n", completion))
    p.cut()

@app.route('/member-not-found', methods=['GET', 'POST'])
def member_not_found():
    form=MemberNotFoundForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))

    return render_template('member-not-found.html',
                                        form=form)

@app.route('/server-error', methods=['GET', 'POST'])
def server_error():

    global serverError

    form=ServerErrorForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))

    if serverError:
        flash(serverError)
        serverError = ''

    return render_template('server-error.html',
                                        form=form)
