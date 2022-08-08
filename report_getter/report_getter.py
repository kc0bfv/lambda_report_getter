#!/usr/bin/env python3

import os
import urllib.request
import urllib.error
import unittest

import boto3

SETTINGS = None
def get_settings():
    global SETTINGS
    if SETTINGS is None:
        SETTINGS = dict()
        SETTINGS["region"] = os.environ.get("region")
        SETTINGS["profile"] = os.environ.get("profile")
        SETTINGS["from_addr"] = os.environ["email_from"]
        SETTINGS["url"] = os.environ["monitor_url"]
        SETTINGS["subject"] = os.environ["subject"]

        to_addr_s = os.environ["email_to"]
        to_addr_list = [s.strip() for s in to_addr_s.split(";") if s.strip() != ""]
        SETTINGS["to_addrs"] = to_addr_list
        SETTINGS["timeout"] = int(os.environ.get("timeout", "10"))
    return SETTINGS

def send_email(subject_starter: str, content: str) -> None:
    settings = get_settings()
    subject = f"{ subject_starter }: { settings['subject'] }"
    body = f"URL: {settings['url']}\n\nContent:\n{ content }"

    sess = boto3.session.Session(region_name = settings["region"],
            profile_name = settings["profile"])
    ses = sess.client("ses")
    response = ses.send_email(
        Source = settings["from_addr"],
        Destination = {"ToAddresses": settings["to_addrs"]},
        Message = {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body} },
        }
    )

    print(f"SES Response: {response}")

def alert_failed(msg_txt: str = "Connection fail") -> None:
    return send_email("REPORT FAILURE", msg_txt)

def send_report(report: str) -> None:
    return send_email("REPORT", report)

def get_report():
    settings = get_settings()
    req = urllib.request.Request(settings["url"])

    with urllib.request.urlopen(req, timeout=settings["timeout"]) as urlf:
        data = urlf.read()

    print("Data received: {}".format(len(data)))
    send_report(data.decode())

def report_getter(event, context):
    try:
        get_report()
    except BaseException as e:
        alert_failed("Connection fail: {}".format(e))
        raise e
    except:
        alert_failed("Connection fail: non-BaseException?")
        raise

if __name__ == "__main__":
    report_getter((),())




def makeFakeBoto():
    class FakeBoto3:
        class session:
            class Session:
                all_sessions = list()
                def __init__(self, region_name, profile_name):
                    FakeBoto3.session.Session.all_sessions.append(self)
                    self.region_name = region_name
                    self.profile_name = profile_name
                def client(self, service):
                    self.service = service
                    return self
                def send_email(self, Source, Destination, Message):
                    self.send_email = {"src": Source, "dest": Destination,
                        "msg": Message}
                    return "Fake email sent"
    return FakeBoto3

class TestClass(unittest.TestCase):
    def test_with_200_expect_200(self):
        global boto3, SETTINGS

        fake_set = {
            "region": "fake_reg",
            "profile": "fake_prof",
            "from_addr": "from@from.com",
            "to_addrs": ["to@to.com"],
            "url": "https://google.com/",
            "expect": 200,
        }

        boto3 = makeFakeBoto()
        SETTINGS = fake_set

        service_monitor((),())

        self.assertEqual(len(boto3.session.Session.all_sessions), 0)

    def test_with_200_expect_400(self):
        global boto3, SETTINGS

        fake_set = {
            "region": "fake_reg",
            "profile": "fake_prof",
            "from_addr": "from@from.com",
            "to_addrs": ["to@to.com"],
            "url": "https://google.com/",
            "expect": 400,
        }

        boto3 = makeFakeBoto()
        SETTINGS = fake_set

        with self.assertRaises(RuntimeError):
            service_monitor((),())

        self.assertEqual(len(boto3.session.Session.all_sessions), 1)
        
        out_sess = boto3.session.Session.all_sessions[0]

        self.assertEqual(out_sess.region_name, fake_set["region"])
        self.assertEqual(out_sess.profile_name, fake_set["profile"])
        self.assertEqual(out_sess.service, "ses")
        self.assertEqual(out_sess.send_email["src"], fake_set["from_addr"])
        self.assertEqual(out_sess.send_email["dest"]["ToAddresses"], fake_set["to_addrs"])
        print(out_sess.send_email["msg"])

    def test_with_404_expect_404(self):
        global boto3, SETTINGS

        fake_set = {
            "region": "fake_reg",
            "profile": "fake_prof",
            "from_addr": "from@from.com",
            "to_addrs": ["to@to.com"],
            "url": "https://google.com/WEKNenWENWEweklj",
            "expect": 404,
        }

        boto3 = makeFakeBoto()
        SETTINGS = fake_set

        service_monitor((),())

        self.assertEqual(len(boto3.session.Session.all_sessions), 0)

    def test_with_404_expect_300(self):
        global boto3, SETTINGS

        fake_set = {
            "region": "fake_reg",
            "profile": "fake_prof",
            "from_addr": "from@from.com",
            "to_addrs": ["to@to.com"],
            "url": "https://google.com/WEKNenWENWEweklj",
            "expect": 300,
        }

        boto3 = makeFakeBoto()
        SETTINGS = fake_set

        with self.assertRaises(urllib.error.HTTPError):
            service_monitor((),())

        self.assertEqual(len(boto3.session.Session.all_sessions), 1)
        
        out_sess = boto3.session.Session.all_sessions[0]

        self.assertEqual(out_sess.region_name, fake_set["region"])
        self.assertEqual(out_sess.profile_name, fake_set["profile"])
        self.assertEqual(out_sess.service, "ses")
        self.assertEqual(out_sess.send_email["src"], fake_set["from_addr"])
        self.assertEqual(out_sess.send_email["dest"]["ToAddresses"], fake_set["to_addrs"])
        print(out_sess.send_email["msg"])
