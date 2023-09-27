import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import smtplib
from socket import gaierror

def main(msg: func.ServiceBusMessage):
    print('msg.getBody:', msg.get_body())
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # Get connection to database
    connection = psycopg2.connect(host="maitp1-server.postgres.database.azure.com", user="adminadmin@maitp1-server", 
                                password="Hieule~~2511", database="techconfdb")
    cur = connection.cursor()

    try:
        # Get notification message and subject from database using the notification_id
        cur.execute("Select subject, message from notification where id = {}".format(notification_id))
        notification = cur.fetchone()

        # Get attendees email and name
        cur.execute("Select email, last_name, first_name from attendee")
        attendees = cur.fetchall()

        ##client = mt.MailtrapClient(token="e1e4a588a0278984b34c47d578eef84a")
        sender = "nhoxkho25111998@gmail.com"
        # Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            text="Hi {} {}, \n {}".format(attendee[2], attendee[1], notification[1])
                                       
            message = f"""\
            Subject: {notification[0]}
            To: {attendee[0]}
            From: {sender}
            {text}"""

            with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
                server.login("00b4c8b6d56518", "067dd2b67c4da3")
                server.sendmail(sender, attendee[0], message)
        
        status = "Notified {} attendees".format(len(attendees))
        # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cur.execute("Update notification set status = '{}', completed_date = '{}' where id = {}".format(status, datetime.utcnow(), notification_id))
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        connection.rollback()
        print('Sent')
    finally:
        # Close connection
        cur.close()
        connection.close()