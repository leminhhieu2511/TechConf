import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    SENDGRID_API_KEY = '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'
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # Get connection to database
    connection = psycopg2.connect(host="techconf-db-server15.postgres.database.azure.com", user="azureuser@techconf-db-server15", 
                                password="P@ssword123456", database="techconfdb")
    cur = connection.cursor()
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    try:
        # Get notification message and subject from database using the notification_id
        cur.execute("Select subject, message from notification where id = {}".format(notification_id))
        notification = cur.fetchone()

        # Get attendees email and name
        cur.execute("Select email, last_name, first_name from attendee")
        attendees = cur.fetchall()

        # Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            mail = Mail(from_email='haitt.dev15@gmail.com', to_emails= attendee[0], subject= notification[0], 
            plain_text_content= "Hi {}, \n {}".format(attendee[2], attendee[1], notification[1]))
            sg.send(mail)
        
        status = "Notified {} attendees".format(len(attendees))
        # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cur.execute("Update notification set status = '{}', completed_date = '{}' where id = {}".format(status, datetime.utcnow(), notification_id))
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        connection.rollback()
    finally:
        # Close connection
        cur.close()
        connection.close()