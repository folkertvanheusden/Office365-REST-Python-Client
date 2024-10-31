from office365.runtime.client_value import ClientValue


class SearchQuery(ClientValue):
    def __init__(self, query_string=None, query_template=None, row_limit=None, start_row=None):
        """
        Represents a search query that contains search terms and optional filters.

        :param str query_string: The search query containing the search terms.
        :param str query_template: Provides a way to decorate the query string. Supports both KQL and query variables.
        """
        super(SearchQuery, self).__init__()
        self.queryString = query_string
        self.queryTemplate = query_template
        self.rowLimit = row_limit
        self.startRow = start_row
