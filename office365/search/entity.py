from typing import List, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.search.acronym import Acronym
from office365.search.entity_type import EntityType
from office365.search.query import SearchQuery
from office365.search.request import SearchRequest
from office365.search.response import SearchResponse


class SearchEntity(Entity):
    """
    A top level object representing the Microsoft Search API endpoint. It does not behave as any other resource
    in Graph, but serves as an anchor to the query action.
    """

    def query(self, query_string, entity_types=None, row_limit=None, start_row=None):
        # type: (str, Optional[List[str]]) -> ClientResult[ClientValueCollection[SearchResponse]]
        """
        Runs the query specified in the request body. Search results are provided in the response.

        :param str query_string: Contains the query terms.
        :param list[str] entity_types: One or more types of resources expected in the response.
            Possible values are: list, site, listItem, message, event, drive, driveItem, externalItem.
        """
        search_request = SearchRequest(
            query=SearchQuery(query_string), entity_types=entity_types,
            row_limit=row_limit, start_row=start_row
        )
        payload = {"requests": ClientValueCollection(SearchRequest, [search_request])}
        return_type = ClientResult(self.context, ClientValueCollection(SearchResponse))
        qry = ServiceOperationQuery(self, "query", None, payload, None, return_type)

        def _patch_hit(search_hit):
            pass
            # resource = Entity(self.context)
            # self.context.pending_request().map_json(search_hit.resource, resource)
            # search_hit.set_property("resource", resource)

        def _process_response(result):
            # type: (ClientResult[ClientValueCollection[SearchResponse]]) -> None
            for item in result.value:
                for hcs in item.hitsContainers:
                    [_patch_hit(hit) for hit in hcs.hits]

        self.context.add_query(qry).after_query_execute(_process_response)
        return return_type

    def query_messages(self, query_string, row_limit=None, start_row=None):
        """Searches Outlook messages. Alias to query method
        :param str query_string: Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.message], row_limit=row_limit, start_row=start_row)

    def query_events(self, query_string, row_limit=None, start_row=None):
        """Searches Outlook calendar events. Alias to query method
        :param str query_string: Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.event], row_limit=row_limit, start_row=start_row)

    def query_drive_items(self, query_string, row_limit=None, start_row=None):
        """Searches OneDrive items. Alias to query method
        :param str query_string: Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.driveItem], row_limit=row_limit, start_row=start_row)

    @property
    def acronyms(self):
        """Administrative answer in Microsoft Search results to define common acronyms in an organization."""
        return self.properties.get(
            "acronyms",
            EntityCollection(
                self.context,
                Acronym,
                ResourcePath("acronyms", self.resource_path),
            ),
        )
