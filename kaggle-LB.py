import time
import json
import requests
import subprocess
import smtplib, ssl


def get_leaderboard_status():

    URL = 'https://www.kaggle.com/c/3d-object-detection-for-autonomous-vehicles/leaderboard'
    client = requests.session() # create a session
    client.get(URL)  # sets cookie

    # prepare cookie string for headers
    str_cookies = ''
    for k, v in client.cookies.get_dict().items():
        str_cookies += f'{k}={v}; '

    # prepare headers
    headers = {
        'sec-fetch-mode': 'cors',
        'origin': 'https://www.kaggle.com',
        'x-xsrf-token': client.cookies['XSRF-TOKEN'],
        'accept-language': 'en,hi;q=0.9',
        'accept-encoding': 'gzip, deflate',
        'cookie': str_cookies,
        'content-type': 'application/json',
        'accept': 'application/json',
        'referer': URL,
        'authority': 'www.kaggle.com',
        'sec-fetch-site': 'same-origin',
        'dnt': '1',
    }

    # payload
    data = {
        "competitionId":0,
        "competitionName":"3d-object-detection-for-autonomous-vehicles"
    }

    # this url is used by kaggle to check competition status
    api_url = 'https://www.kaggle.com/requests/CompetitionService/GetCompetition'

    # get response from api url
    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    data = json.loads(response.text.strip())

    status = data['result']['finalLeaderboardHasBeenVerified']

    return status


def send_email(credentials):

    URL = 'https://www.kaggle.com/c/3d-object-detection-for-autonomous-vehicles/leaderboard'
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    sender_email = credentials["sender_email"]
    password = credentials["password"]
    receiver_email = credentials["receiver_email"]

    message = f"""\
    Hi there,

    THE LEADERBOARD HAS BEEN FINALIZED!, check it out: {URL}"""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


if __name__ == "__main__":

    interval = 30 # interval between to checks, in minutes
    message = "THE LEADERBOARD HAS BEEN FINALIZED 🎉🎉🎉"

    # credentials to be used for email notification
    credentials = {
            "sender_email": "",
            "password": "",
            "receiver_email": ""
    }

    while True:
        # check if LB is finalized
        status = get_leaderboard_status()
        if status:
            print(message)
            # send system notification
            subprocess.Popen(['notify-send', message])
            # send email
            send_email(credentials)
            break

        # sleep for `interval` minutes
        clock = time.strftime('%H:%M%p %Z on %b %d, %Y')
        print(f'{clock} | Still not finalized :(')
        time.sleep(interval * 60)

        
