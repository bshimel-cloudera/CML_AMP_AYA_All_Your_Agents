from crewai_tools import BaseTool
import os
import requests
import json

from sample_external_applications.accounts_knowledge_graph_app.client import KGClient

kg = KGClient()

class ToolAccountsKnowledgeGraph(BaseTool):
    name: str = "AccountsKnowledgeGraphTool"
    description: str = "Handles queries that can be answered by a knowledgegraph containing information about customer accounts and the field teams supporting them."

    def _query_kg(self, question):
        response = kg.query(question)
        return json.dumps(response, indent=4)

    def _run(self, request_id: str, question: str) -> str:
        with open('/tmp/%s' % request_id, 'w') as tools_log:
          tools_log.write('Accounts Knowledge Graph Query Agent')
        response = self._query_kg(question)
        return response