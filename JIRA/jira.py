import time
from datetime import datetime, timedelta

import suds

def re_make_pattern(projects):
    keys = r"(%s)" % "|".join(projects)
    # A project key followed by some numbers, e.g. FL-1234.
    pattern = r"(^|\s)(%s-\d+)(?=$|\s)" % keys
    return pattern

def re_get_issue(match):
    issue_id = match.group(2).upper()
    return issue_id

class JiraClient:
    def __init__(self, soap_url, username, password):
        self._client = suds.client.Client(soap_url)

        self._auth = None
        self._status_map = None
        self._resolution_map = None
        self._projects_keys = None

        self._username = username
        self._password = password

    def login(self):
        self._login()
        self._get_status_map()
        self._get_resolution_map()

    def _login(self):
        self._auth = self._client.service.login(self._username, self._password)

    def _get_status_map(self):
        statuses = self._client.service.getStatuses()
        self._status_map = dict([(s.id, s.name) for s in statuses])

    def _get_resolution_map(self):
        resolutions = self._client.service.getResolutions()
        self._resolution_map = dict([(s.id, s.name) for s in resolutions])

    def get_projects_keys(self):
        # projects-keys are the keywords of the projects in a JIRA install,
        # e.g. FL, KDE, XFCE.
        if not self._projects_keys:
            projects = self._client.service.getProjectsNoSchemes(self._auth)
            self._projects_keys = [p.key for p in projects]

        return self._projects_keys

    def get_user_fullname(self, username):
        user = self._client.service.getUser(self._auth, username)
        ret = user.fullname
        return ret

    def get_status_string(self, status):
        return self._status_map[status]

    def get_resolution_string(self, resolution):
        # Resolution can be None
        if not resolution:
            ret = "None"
        else:
            ret = self._resolution_map[resolution]
        return ret

    def query_issue(self, number):

        def get_issue(number):
            return self._client.service.getIssue(self._auth, number)

        try:
            issue = get_issue(number)
        except suds.WebFault as excp:
            # If the session timed out, re-login and try again.
            if excp.args[0] == ("Server raised fault: "
                    "'com.atlassian.jira.rpc.exception.RemoteAuthenticationException: "
                    "User not authenticated yet, or session timed out.'"):
                self._login()
                issue = get_issue(number)
            else:
                raise

        return issue

    def _server_time_to_local(self, server_time):
        # format of server_time ==> 2011-11-11T04:45:23.471-0500
        # in ISO8601 format: yyyy-MM-dd'T'HH:mm:ss.SSSZ
        date = datetime.strptime(server_time[:-5], '%Y-%m-%dT%H:%M:%S.%f')
        timezone = int(server_time[-5:]) / 100.0
        local_tz = -time.timezone / 3600.0 + time.daylight
        timezone_delta = timedelta(hours=local_tz - timezone)

        return date + timezone_delta

    def get_server_time(self):
        '''Return current time on the server, converted to local timezone
        '''
        info = self._client.service.getServerInfo()
        server_time = info.serverTime.serverTime
        return self._server_time_to_local(server_time)
