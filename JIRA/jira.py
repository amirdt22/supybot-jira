import suds

class JiraClient:
    def __init__(self, soap_url, username, password):
        self._client = suds.client.Client(soap_url)

        self._auth = None
        self._status_map = None
        self._resolution_map = None
        self._projects_keys = None

        self._username = username
        self._password = password

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
