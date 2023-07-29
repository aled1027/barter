import requests


class Linear:
    def __init__(self, api_key: str) -> None:
        self.url = "https://api.linear.app/graphql"
        self.headers = {"Authorization": api_key}

    def query_grapql(self, query: str) -> requests.Response:
        data = {"query": query}
        resp = requests.post(self.url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp

    def query_basic_resource(self, resource: str):
        query = (
            """
            query Resource {"""
            + resource
            + """{nodes{id,name}}}
        """
        )
        resp = self.query_grapql(query)

        return resp.json()["data"][resource]["nodes"]

    def create_issue(
        self,
        title: str,
        description: str,
        team_id: str,
    ):
        query = f"""
            mutation IssueCreate {{
              issueCreate(
                input: {{
                    title: "{title}"
                    description: "{description}"
                    teamId: "{team_id}"
                }}
              ) {{
                success
                issue {{
                  id
                  title
                }}
              }}
            }}
            """
        resp = self.query_grapql(query)
        return resp.json()["data"]["issueCreate"]

    def get_teams(self):
        return self.query_basic_resource("teams")

    def get_states(self):
        return self.query_basic_resource("workflowStates")

    def get_projects(self):
        return self.query_basic_resource("projects")
