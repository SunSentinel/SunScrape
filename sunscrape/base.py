# import os
import io
import csv
# import json
import requests
from datetime import datetime

from bs4 import BeautifulSoup
from collections import OrderedDict


class SunScraper(object):

    """ Base class for all the scrapers """

    date_format = '%m/%d/%Y'

    def request(self, url, payload):
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "referer": "https://www.google.com/"
        }
        r = requests.get(url, params=payload, headers=header)
        # r = requests.get(url, params=payload, allow_redirects=True)
        if r.status_code == 200:
            reader = csv.DictReader(io.StringIO(r.text),
                                    delimiter='\t',
                                    quoting=csv.QUOTE_NONE)
            return reader

        else:
            # print(r.text)
            print("====\nERROR: {0} response from server\n====".format(
                                                                r.status_code
                                                                ))


    @classmethod
    def get_election_ids(cls):
        """

        Returns an OrderedDict of available elections
        and the state's unique ID for that election.

        Florida's campaign finance website has custom ID's for each election.
        Pass one of these IDs in the scrapers for records for that election,
        or just get 'All' via "all_time=True"

        """

        elections = OrderedDict()

        url = cls.portal_url
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "referer": "https://www.google.com/"
        }
        r = requests.get(url, headers=header)
        soup = BeautifulSoup(r.content, "html.parser")
        elex_dropdown = soup.find("select", {"name": "election"})
        elections_list = elex_dropdown.findAll("option")
        for election in elections_list[1:]:
            elections.update({election.text: election['value']})

        return elections

    def _update_payload(self, kwargs):
        """
        Update the payload sent to the campaign finance site based on kwargs.
        """

        if "candidate_first" in kwargs.keys():
            self.payload["CanFName"] = kwargs["candidate_first"]
            self.payload["election"] = "All"

        if "candidate_last" in kwargs.keys():
            self.payload["CanLName"] = kwargs["candidate_last"]
            self.payload["election"] = "All"

        if "committee_name" in kwargs.keys():
            self.payload["ComName"] = kwargs["committee_name"]
            self.payload["ComNameSrch"] = 1
            self.payload["namesearch"] = 1
            self.payload["office"] = "All"
            self.payload["election"] = "All"

        if "from_date" in kwargs.keys():
            self.payload["cdatefrom"] = kwargs["from_date"]
            self.payload["election"] = "All"

        if "to_date" in kwargs.keys():
            self.payload["cdateto"] = kwargs["to_date"]
            self.payload["election"] = "All"

        if "all_time" in kwargs.keys() and kwargs["all_time"]:
            self.payload["election"] = "All"

        if "election_id" in kwargs.keys():
            self.payload["election"] = kwargs["election_id"]

        if "contributor_first" in kwargs.keys():
            self.payload["cfname"] = kwargs["contributor_first"]

        if "contributor_last" in kwargs.keys():
            self.payload["clname"] = kwargs["contributor_last"]
            self.payload["namesearch"] = 1


    @classmethod
    def toDate(cls, text):

        text = text.strip()

        try:
            dt = datetime.strptime(text, cls.date_format)
            return dt.date().isoformat()

        except ValueError:
            return ''

    # @classmethod
    # def save_to_file(cls):
    #     """
    #     Save results to disk.
    #     """

    #     date = datetime.now().strftime('%m%d%Y')
    #     file_path = os.getcwd() + '/{0}_{1}.json'.format(date,
    #                                                      cls.result_type)
    #     data = json.dumps(cls.results)

    #     with open(file_path, 'w') as f:
    #         f.write(data)