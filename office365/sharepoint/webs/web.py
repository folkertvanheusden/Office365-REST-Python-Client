# coding=utf-8
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.alerts.collection import AlertCollection
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.clientsidecomponent.storage_entity import StorageEntity
from office365.sharepoint.clientsidecomponent.query_result import SPClientSideComponentQueryResult
from office365.sharepoint.clientsidecomponent.identifier import SPClientSideComponentIdentifier
from office365.sharepoint.contenttypes.collection import ContentTypeCollection
from office365.sharepoint.eventreceivers.definition import EventReceiverDefinitionCollection
from office365.sharepoint.fields.collection import FieldCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.flows.synchronization_result import FlowSynchronizationResult
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.folders.collection import FolderCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.document_library_information import DocumentLibraryInformation
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_collection import ListCollection
from office365.sharepoint.lists.list_template_collection import ListTemplateCollection
from office365.sharepoint.navigation.navigation import Navigation
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.role_definition_collection import RoleDefinitionCollection
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.group import Group
from office365.sharepoint.principal.group_collection import GroupCollection
from office365.sharepoint.principal.user import User
from office365.sharepoint.principal.user_collection import UserCollection
from office365.sharepoint.pushnotifications.subscriber import PushNotificationSubscriber
from office365.sharepoint.recyclebin.item_collection import RecycleBinItemCollection
from office365.sharepoint.sharing.externalSharingSiteOption import ExternalSharingSiteOption
from office365.sharepoint.sharing.object_sharing_settings import ObjectSharingSettings
from office365.sharepoint.sharing.sharing_link_data import SharingLinkData
from office365.sharepoint.sharing.sharing_result import SharingResult
from office365.sharepoint.sitescripts.utility import SiteScriptUtility
from office365.sharepoint.marketplace.sitecollection.appcatalog.accessor import SiteCollectionCorporateCatalogAccessor
from office365.sharepoint.marketplace.tenant.appcatalog.accessor import TenantCorporateCatalogAccessor
from office365.sharepoint.ui.applicationpages.client_people_picker import (
    ClientPeoplePickerWebServiceInterface, ClientPeoplePickerQueryParameters
)
from office365.sharepoint.usercustomactions.collection import UserCustomActionCollection
from office365.sharepoint.views.view import View
from office365.sharepoint.webparts.client.collection import ClientWebPartCollection
from office365.sharepoint.webs.calendar_type import CalendarType
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.datetime_field_format_type import DateTimeFieldFormatType
from office365.sharepoint.webs.multilingual_settings import MultilingualSettings
from office365.sharepoint.webs.regional_settings import RegionalSettings
from office365.sharepoint.sitescripts.types import SiteScriptSerializationResult, SiteScriptSerializationInfo
from office365.sharepoint.webs.web_information_collection import WebInformationCollection
from office365.sharepoint.webs.web_template_collection import WebTemplateCollection
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class Web(SecurableObject):
    """Represents a SharePoint site. A site is a type of SP.SecurableObject.
    Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self, context, resource_path=None):
        """
        Specifies the push notification subscriber over the site for the specified device app instance identifier.

        :type resource_path: ResourcePath or None
        :type context: office365.sharepoint.client_context.ClientContext
        """
        if resource_path is None:
            resource_path = ResourcePath("Web")
        super(Web, self).__init__(context, resource_path)
        self._web_url = None

    def get_site_script(self, include_branding=True, included_lists=None, include_links_to_exported_items=True,
                        include_regional_settings=True):
        """
        Creates site script syntax from current SharePoint site.

        :param bool include_branding: Extracts the configuration of the site's branding.
        :param list[str] or None included_lists: A list of one or more lists. Each is identified by the list url.
        :param bool include_links_to_exported_items: Extracts navigation links. In order to export navigation links
            pointing to lists, the list needs to be included in the request as well.
        :param bool include_regional_settings: Extracts the site's regional settings.
        """
        result = ClientResult(self.context, SiteScriptSerializationResult())
        info = SiteScriptSerializationInfo(include_branding, included_lists, include_links_to_exported_items,
                                           include_regional_settings)

        def _web_loaded():
            SiteScriptUtility.get_site_script_from_web(self.context, self.url, info, return_type=result)

        self.ensure_property("Url", _web_loaded)
        return result

    def consent_to_power_platform(self):
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "ConsentToPowerPlatform", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_push_notification_subscriber(self, device_app_instance_id):
        """
        Specifies the push notification subscriber over the site for the specified device app instance identifier.

        :param str device_app_instance_id: Device application instance identifier.
        """
        return_type = PushNotificationSubscriber(self.context)
        qry = ServiceOperationQuery(self, "GetPushNotificationSubscriber", [device_app_instance_id], None,
                                    None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_client_side_components(self, components):
        """
        Returns the client side components for the requested components.
        Client components include data necessary to render Client Side Web Parts and Client Side Applications.

        :param list components: array of requested components, defined by id and version.
        """
        return_type = ClientResult(self.context, ClientValueCollection(SPClientSideComponentIdentifier))
        payload = {
            "components": components
        }
        qry = ServiceOperationQuery(self, "GetClientSideComponents", None, payload,
                                    None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_push_notification_subscribers_by_user(self, user_or_username):
        """
        Queries for the push notification subscribers for the site  for the specified user.

        :param str or User user_or_username:
        """
        return_type = BaseEntityCollection(self.context, PushNotificationSubscriber)

        if isinstance(user_or_username, User):
            def _user_loaded():
                next_qry = ServiceOperationQuery(self, "GetPushNotificationSubscribersByUser",
                                                 [user_or_username.login_name], None, None, return_type)
                self.context.add_query(next_qry)

            user_or_username.ensure_property("LoginName", _user_loaded)
        else:
            qry = ServiceOperationQuery(self, "GetPushNotificationSubscribersByUser", [user_or_username], None,
                                        None, return_type)
            self.context.add_query(qry)
        return return_type

    @staticmethod
    def create_organization_sharing_link(context, url, is_edit_link):
        """ Creates and returns an organization-internal link that can be used to access a document and gain permissions
           to it.

        :param office365.sharepoint.client_context.ClientContext context:
        :param str url: he URL of the site, with the path of the object in SharePoint that is represented as query
            string parameters, forSharing set to 1 if sharing, and bypass set to 1 to bypass any mobile logic.
        :param bool is_edit_link: If true, the link will allow the logged in user to edit privileges on the item.
        """
        result = ClientResult(context)
        params = {"url": url, "isEditLink": is_edit_link}
        qry = ServiceOperationQuery(context.web, "CreateOrganizationSharingLink", None, params, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def destroy_organization_sharing_link(context, url, is_edit_link, remove_associated_sharing_link_group):
        """ Removes an existing organization link for an object.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param str url: the URL of the site, with the path of the object in SharePoint that is represented as query
            string parameters, forSharing set to 1 if sharing, and bypass set to 1 to bypass any mobile logic.
        :param bool is_edit_link: If true, the link will allow the logged in user to edit privileges on the item.
        :param bool remove_associated_sharing_link_group: Indicates whether to remove the groups that contain the users
            who have been given access to the shared object via the sharing link
        """
        payload = {
            "url": url,
            "isEditLink": is_edit_link,
            "removeAssociatedSharingLinkGroup": remove_associated_sharing_link_group
        }
        qry = ServiceOperationQuery(context.web, "DestroyOrganizationSharingLink", None, payload, None, None)
        qry.static = True
        context.add_query(qry)
        return context.web

    @staticmethod
    def get_context_web_information(context):
        """
        Returns an object that specifies metadata about the site

        :type context: office365.sharepoint.client_context.ClientContext
        """
        result = ClientResult(context, ContextWebInformation())
        qry = ServiceOperationQuery(context.web, "GetContextWebInformation", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_web_url_from_page_url(context, page_full_url):
        """Returns the URL of the root folder for the site containing the specified URL

        :type context: office365.sharepoint.client_context.ClientContext
        :param str page_full_url: Specifies the URL from which to return the site URL.
        """
        result = ClientResult(context)
        payload = {
            "pageFullUrl": page_full_url
        }
        qry = ServiceOperationQuery(context.web, "GetWebUrlFromPageUrl", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    def create_default_associated_groups(self, user_login, user_login2, group_name_seed):
        """
        Creates the default Owners, Members and Visitors SPGroups on the web.

        :param str user_login: The user logon name of the group owner.
        :param str user_login2: The secondary contact for the group.
        :param str group_name_seed: The name seed to use when creating of the full names of the default groups.
            For example, if the name seed is Contoso then the default groups will be created with the names:
            Contoso Owners, Contoso Members and Contoso Visitors. If the value of this parameter is null then the
            web title is used instead.
        """
        payload = {
            "userLogin": user_login,
            "userLogin2": user_login2,
            "groupNameSeed": group_name_seed
        }
        qry = ServiceOperationQuery(self, "CreateDefaultAssociatedGroups", None, payload)
        qry.static = True
        self.context.add_query(qry)
        return self

    def create_group_based_environment(self):
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "CreateGroupBasedEnvironment", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_group_based_environment(self):
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "GetGroupBasedEnvironment", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_instances(self, target_web_url):
        """
        :param str target_web_url:
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"targetWebUrl": target_web_url}
        qry = ServiceOperationQuery(self, "SyncFlowInstances", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_templates(self, category):
        """
        :param str category:
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"category": category}
        qry = ServiceOperationQuery(self, "SyncFlowTemplates", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_client_side_components(self):
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "getAllClientSideComponents", None, None, None, result)
        self.context.add_query(qry)
        return result

    def get_client_side_web_parts(self, project, include_errors=False):
        """
        :param str project:
        :param bool include_errors: If true, webparts with errors MUST be included in the results of the request.
           If false, webparts with errors MUST be excluded in the results of the request.
        """
        result = ClientValueCollection(SPClientSideComponentQueryResult)
        params = {
            "includeErrors": include_errors,
            "project": project
        }
        qry = ServiceOperationQuery(self, "getClientSideWebParts", None, params, None, result)
        self.context.add_query(qry)
        return result

    def add_supported_ui_language(self, lcid):
        """
        Adds a supported UI language by its language identifier.

        :param int lcid: Specifies the language identifier to be added.
        """
        qry = ServiceOperationQuery(self, "AddSupportedUILanguage", {"lcid": lcid})
        self.context.add_query(qry)
        return self

    def get_sub_webs_filtered_for_current_user(self, query):
        """Returns a collection of objects that contain metadata about subsites of the current site (2) in which the
        current user is a member.

        :type query: office365.sharepoint.webs.subweb_query.SubwebQuery
        """
        users = WebInformationCollection(self.context)
        qry = ServiceOperationQuery(self, "getSubWebsFilteredForCurrentUser", {
            "nWebTemplateFilter": query.WebTemplateFilter,
            "nConfigurationFilter": query.ConfigurationFilter
        }, None, None, users)
        self.context.add_query(qry)
        return users

    def get_recycle_bin_items(self, paging_info=None, row_limit=100, is_ascending=True, order_by=None, item_state=None):
        """
        Gets the recycle bin items that are based on the specified query.

        :param str paging_info: an Object that is used to obtain the next set of rows in a paged view of the Recycle Bin
        :param int row_limit: a limit for the number of items returned in the query per page.
        :param bool is_ascending: a Boolean value that specifies whether to sort in ascending order.
        :param int order_by: the column by which to order the Recycle Bin query.
        :param int item_state: Recycle Bin stage of items to return in the query.
        """
        result = RecycleBinItemCollection(self.context)
        payload = {
            "rowLimit": row_limit,
            "isAscending": is_ascending,
            "pagingInfo": paging_info,
            "orderBy": order_by,
            "itemState": item_state
        }
        qry = ServiceOperationQuery(self, "GetRecycleBinItems", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_all_webs(self):
        """Returns a collection containing a flat list of all Web objects in the Web."""
        from office365.sharepoint.webs.web_collection import WebCollection
        return_type = WebCollection(self.context, self.webs.resource_path)

        def _webs_loaded():
            self._load_sub_webs_inner(self.webs, return_type)

        self.ensure_property("Webs", _webs_loaded)
        return return_type

    def _load_sub_webs_inner(self, webs, all_webs):
        """
        :type webs: office365.sharepoint.webs.web_collection.WebCollection
        :type all_webs: office365.sharepoint.webs.web_collection.WebCollection
        """
        for cur_web in webs:  # type: Web
            all_webs.add_child(cur_web)

            def _webs_loaded(web):
                if len(web.webs) > 0:
                    self._load_sub_webs_inner(web.webs, all_webs)

            cur_web.ensure_property("Webs", _webs_loaded, cur_web)

    def get_list_using_path(self, decoded_url):
        """
        Returns the list that is associated with the specified server-relative path.

        :param str decoded_url: Contains the site-relative path for a list, for example, /Lists/Announcements.
        """
        safe_decoded_url = self.context.create_safe_url(decoded_url)
        return_type = List(self.context)
        self.lists.add_child(return_type)
        qry = ServiceOperationQuery(self, "GetListUsingPath", SPResPath(safe_decoded_url), None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_news_list(self, allow_create=False):
        """
        Returns the News List on this web, if it exists. If the list does not exist, the list will be created and
        then returned if allowCreate is set to true. The News List is a hidden SP.List in which News Posts are stored.

        :param bool allow_create: Indicates whether to create the list if it does not exist on this web.
            "true" means yes.
        """
        return_type = List(self.context)
        self.lists.add_child(return_type)
        payload = {"allowCreate": allow_create}
        qry = ServiceOperationQuery(self, "GetNewsList", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_view_from_url(self, list_url):
        """Returns a view of a list within the site based on the specified URL.

        :param str list_url: Contains either an absolute URL or a site-relative URL of a view.
        """
        return View(self.context, ServiceOperationPath("GetViewFromUrl", [list_url], self.resource_path))

    def get_view_from_path(self, decoded_url):
        """Returns a view of a list within the site based on the specified path.

        :param str decoded_url: Contains either an absolute path or a site-relative path of a view.
        """
        return View(self.context, ServiceOperationPath("GetViewFromPath", [decoded_url], self.resource_path))

    def get_regional_datetime_schema(self):
        """Get DateTime Schema based on regional settings"""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetRegionalDateTimeSchema", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sharing_link_data(self, link_url):
        """
        This method determines basic information about the supplied link URL, including limited data about the object
        the link URL refers to and any additional sharing link data if the link URL is a tokenized sharing link

        :param str link_url: A URL that is either a tokenized sharing link or a canonical URL for a document
        """
        return_type = ClientResult(self.context, SharingLinkData())
        payload = {"linkUrl": link_url}
        qry = ServiceOperationQuery(self, "GetSharingLinkData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_context_web_theme_data(context):
        """
        Get ThemeData for the context web.

        :type context: office365.sharepoint.client_context.ClientContext
        """
        result = ClientResult(context)
        qry = ServiceOperationQuery(context.web, "GetContextWebThemeData", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def create_anonymous_link(context, url, is_edit_link):
        """Create an anonymous link which can be used to access a document without needing to authenticate.

        :param bool is_edit_link: If true, the link will allow the guest user edit privileges on the item.
        :param str url: The URL of the site, with the path of the object in SharePoint represented as query
        string parameters
        :param office365.sharepoint.client_context.ClientContext context: client context
        """
        result = ClientResult(context)
        payload = {
            "url": context.create_safe_url(url, False),
            "isEditLink": is_edit_link
        }
        qry = ServiceOperationQuery(context.web, "CreateAnonymousLink", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_object_sharing_settings(context, object_url, group_id, use_simplified_roles):
        """Given a path to an object in SharePoint, this will generate a sharing settings object which contains
        necessary information for rendering sharing information

        :param office365.sharepoint.client_context.ClientContext context: SharePoint client
        :param str object_url: A URL with one of two possible formats.
              The two possible URL formats are:
              1) The URL of the site, with the path of the object in SharePoint represented as query string parameters,
              forSharing set to 1 if sharing, and mbypass set to 1 to bypass any mobile logic
              e.g. https://contoso.com/?forSharing=1&mbypass=1&List=%7BCF908473%2D72D4%2D449D%2D8A53%2D4BD01EC54B84%7D&
              obj={CF908473-72D4-449D-8A53-4BD01EC54B84},1,DOCUMENT
              2) The URL of the SharePoint object (web, list, item) intended for sharing
              e.g. https://contoso.com/Documents/SampleFile.docx
        :param int group_id: The id value of the permissions group if adding to a group, 0 otherwise.
        :param bool use_simplified_roles: A Boolean value indicating whether to use the SharePoint
        simplified roles (Edit, View) or not.
        """
        return_type = ObjectSharingSettings(context)
        payload = {
            "objectUrl": object_url,
            "groupId": group_id,
            "useSimplifiedRoles": use_simplified_roles
        }
        qry = ServiceOperationQuery(context.web, "GetObjectSharingSettings", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def get_file_by_server_relative_url(self, url):
        """Returns the file object located at the specified server-relative URL.
        :type url: str
        """
        return File(self.context, ServiceOperationPath("getFileByServerRelativeUrl", [url], self.resource_path))

    def get_file_by_server_relative_path(self, url_or_path):
        """Returns the file object located at the specified server-relative path.
        Prefer this method over get_folder_by_server_relative_url since it supports % and # symbols in names

        :type url_or_path: str or SPResPath
        """
        path = url_or_path if isinstance(url_or_path, SPResPath) else SPResPath(url_or_path)
        return File(self.context,
                    ServiceOperationPath("getFileByServerRelativePath", path.to_json(), self.resource_path))

    def get_folder_by_server_relative_url(self, url):
        """Returns the folder object located at the specified server-relative URL.

        :type url: str
        """
        return Folder(self.context, ServiceOperationPath("getFolderByServerRelativeUrl", [url], self.resource_path))

    def get_folder_by_server_relative_path(self, decoded_url):
        """Returns the folder object located at the specified server-relative URL.
        Prefer this method over get_folder_by_server_relative_url since it supports % and # symbols

        :type decoded_url: str
        """
        path = SPResPath(decoded_url)
        return Folder(self.context,
                      ServiceOperationPath("getFolderByServerRelativePath", path.to_json(), self.resource_path))

    def ensure_folder_path(self, path):
        """
        Ensures a nested folder hierarchy exist

        :param str path: relative server URL (path) to a folder
        """
        return self.root_folder.folders.ensure_folder_path(path)

    def ensure_user(self, login_name):
        """Checks whether the specified logon name belongs to a valid user of the website, and if the logon name does
        not already exist, adds it to the website.

        :param str login_name: Specifies a string that contains the login name.
        """
        return_type = User(self.context)
        self.site_users.add_child(return_type)
        qry = ServiceOperationQuery(self, "EnsureUser", [login_name], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_user_effective_permissions(self, user_name):
        """Gets the effective permissions that the specified user has within the current application scope.

        :param str user_name: Specifies the user login name.
        """
        result = ClientResult(self.context, BasePermissions())
        qry = ServiceOperationQuery(self, "GetUserEffectivePermissions", [user_name], None, None, result)
        self.context.add_query(qry)
        return result

    def does_user_have_permissions(self, permission_mask):
        """Returns whether the current user has the given set of permissions.

        :type permission_mask: BasePermissions
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "DoesUserHavePermissions", permission_mask, None, None, result)
        self.context.add_query(qry)
        return result

    def does_push_notification_subscriber_exist(self, device_app_instance_id):
        """
        Specifies whether the push notification subscriber exists for the current user
            with the given device  app instance identifier.

        :param str device_app_instance_id: Device application instance identifier.
        """
        result = ClientResult(self.context)
        params = {"deviceAppInstanceId": device_app_instance_id}
        qry = ServiceOperationQuery(self, "DoesPushNotificationSubscriberExist", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_folder_by_id(self, unique_id):
        """
        Returns the folder object with the specified GUID.

        :param str unique_id: A GUID that identifies the folder.
        """
        return Folder(self.context, ServiceOperationPath("GetFolderById", [unique_id], self.resource_path))

    def get_user_by_id(self, user_id):
        """Returns the user corresponding to the specified member identifier for the current site.

        :param int user_id: Specifies the member identifier.
        """
        return User(self.context, ServiceOperationPath("getUserById", [user_id], self.resource_path))

    def default_document_library(self):
        """Retrieves the default document library."""
        return List(self.context, ServiceOperationPath("defaultDocumentLibrary", None, self.resource_path))

    def get_list(self, path):
        """Get list by path

        :type path: str
        """
        safe_path = self.context.create_safe_url(path)
        return List(self.context, ServiceOperationPath("getList", [safe_path], self.resource_path))

    def get_changes(self, query):
        """Returns the collection of all changes from the change log that have occurred within the scope of the site,
        based on the specified query.

        :param office365.sharepoint.changes.query.ChangeQuery query: Specifies which changes to return
        """
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def get_available_web_templates(self, lcid=1033, do_include_cross_language=False):
        """
        Returns a collection of site templates available for the site.

        :param int lcid: Specifies the LCID of the site templates to be retrieved.
        :param bool do_include_cross_language: Specifies whether to include language-neutral site templates.
        :return:
        """
        params = {
            "lcid": lcid,
            "doIncludeCrossLanguage": do_include_cross_language
        }
        return_type = WebTemplateCollection(self.context,
                                            ServiceOperationPath("GetAvailableWebTemplates ", params,
                                                                 self.resource_path))

        qry = ServiceOperationQuery(self, "GetAvailableWebTemplates", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def hub_site_data(self, force_refresh=False):
        """Retrieves data describing a SharePoint hub site.

        :param bool force_refresh: Default value is false. When false, the data is returned from the server's cache.
            When true, the cache is refreshed with the latest updates and then returned. Use this if you just made
            changes and need to see those changes right away.
        """
        return_type = ClientResult(self.context)
        payload = {"forceRefresh": force_refresh}
        qry = ServiceOperationQuery(self, "HubSiteData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def increment_site_client_tag(self):
        """
        Increments the client cache control number for this site collection.
        """
        qry = ServiceOperationQuery(self, "IncrementSiteClientTag")
        self.context.add_query(qry)
        return self

    def apply_web_template(self, web_template):
        """
        Applies the specified site definition or site template to the website that has no template applied to it.

        :param str web_template: The name of the site definition or the file name of the site template to be applied.
        :return:
        """
        qry = ServiceOperationQuery(self, "ApplyWebTemplate", {"webTemplate": web_template})
        self.context.add_query(qry)
        return self

    def get_custom_list_templates(self):
        """
        Specifies the collection of custom list templates for a given site.

        """
        return_type = ListTemplateCollection(self.context)
        qry = ServiceOperationQuery(self, "GetCustomListTemplates", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_guest_url(self, guest_url):
        """
        Returns the file object from the guest access URL.

        :param str guest_url: The guest access URL to get the file with.
        """
        return_type = File(self.context)
        payload = {"guestUrl": guest_url}
        qry = ServiceOperationQuery(self, "GetFileByGuestUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_linking_url(self, linking_url):
        """
        Returns the file object from the linking URL.

        :param str linking_url: The linking URL to return the file object for.
            A linking URL can be obtained from LinkingUrl.
        """
        return_type = File(self.context)
        payload = {"linkingUrl": linking_url}
        qry = ServiceOperationQuery(self, "GetFileByLinkingUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_wopi_frame_url(self, wopi_frame_url):
        """
        Returns the file object from the WOPI frame URL.

        :param str wopi_frame_url:  The WOPI frame URL used to get the file object.
        """
        return_type = File(self.context)
        qry = ServiceOperationQuery(self, "GetFileByWOPIFrameUrl", [wopi_frame_url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_folder_by_guest_url(self, guest_url):
        """
        Returns the folder object from the tokenized sharing link URL.

        :param str guest_url: The tokenized sharing link URL for the folder.
        """
        return_type = File(self.context)
        qry = ServiceOperationQuery(self, "GetFolderByGuestUrl", [guest_url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def parse_datetime(self, value, display_format=DateTimeFieldFormatType.DateTime, calendar_type=CalendarType.None_):
        """
        Returns parsed DateTime value.

        :param str value: The input is the string of a datetime that's in web's local time and in web's calendar.
           For example, the input "09/08/1430" when web's calendar was set to Hijri, the actual datetime is 07/31/2009
           in Gregorian calendar.
        :param int display_format: Int value representing SP.DateTimeFieldFormatType
        :param int calendar_type: Int value representing SP.CalendarType
        """
        return_type = ClientResult(self.context)
        payload = {
            "value": value,
            "displayFormat": display_format,
            "calendarType": calendar_type
        }
        qry = ServiceOperationQuery(self, "ParseDateTime", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def share(self, user_principal_name,
              share_option=ExternalSharingSiteOption.View,
              send_email=True, email_subject=None, email_body=None):
        """
        Share a Web with user

        :param str user_principal_name: User identifier
        :param ExternalSharingSiteOption share_option: The sharing type of permission to grant on the object.
        :param bool send_email: A flag to determine if an email notification SHOULD be sent (if email is configured).
        :param str email_subject: The email subject.
        :param str email_body: The email subject.
        :rtype: SharingResult
        """

        picker_result = ClientResult(self.context)
        sharing_result = SharingResult(self.context)

        def _picker_value_resolved(picker_value):
            picker_result.value = picker_value

        def _grp_resolved(role_value):
            def _web_loaded():
                Web.share_object(self.context, self.url, picker_result.value, role_value, 0,
                                 False, send_email, False, email_subject, email_body, return_type=sharing_result)

            self.ensure_property("Url", _web_loaded)

        params = ClientPeoplePickerQueryParameters(user_principal_name)
        ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.context, params,
                                                                                _picker_value_resolved)
        Web._resolve_group_value(self.context, share_option, _grp_resolved)
        return sharing_result

    def unshare(self):
        """
        Removes Sharing permissions on a Web

        :rtype: SharingResult
        """
        result = SharingResult(self.context)

        def _web_initialized():
            Web.unshare_object(self.context, self.url, return_type=result)

        self.ensure_property("Url", _web_initialized)
        return result

    @staticmethod
    def get_document_libraries(context, web_full_url):
        """
        Returns the document libraries of a SharePoint site, specifically a list of objects that represents
        document library information. Document libraries that are private—picture library, catalog library,
        asset library, application list, form template or libraries—for whom the user does not have permission to view
        the items are not included.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str web_full_url: The URL of the web.
        """
        result = ClientResult(context, ClientValueCollection(DocumentLibraryInformation))
        payload = {
            "webFullUrl": web_full_url
        }
        qry = ServiceOperationQuery(context.web, "GetDocumentLibraries", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def default_document_library_url(context, web_url):
        """
        Returns the default document library URL.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str web_url:  URL of the web.
        """
        result = ClientResult(context, DocumentLibraryInformation())
        payload = {
            "webUrl": web_url,
        }
        qry = ServiceOperationQuery(context.web, "DefaultDocumentLibraryUrl", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def delete_all_anonymous_links_for_object(context, url):
        """
        Removes all existing anonymous links for an object.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url:  The URL of the object being shared, with the path of the object in SharePoint that is
             represented as query string parameters.
        """
        payload = {
            "url": url
        }
        qry = ServiceOperationQuery(context.web, "DeleteAllAnonymousLinksForObject", None, payload)
        qry.static = True
        context.add_query(qry)
        return context.web

    @staticmethod
    def get_document_and_media_libraries(context, web_full_url, include_page_libraries):
        """
        Returns the document libraries of a SharePoint site, including picture, asset, and site assets libraries.
        Document libraries that are private, catalog library, application list, form template, or libraries that user
        does not have permission to view items are not inlcuded.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str web_full_url:  URL of the web.
        :param bool include_page_libraries: Indicates whether to include page libraries. A value of "true" means yes.
        """
        result = ClientResult(context, ClientValueCollection(DocumentLibraryInformation))
        payload = {
            "webFullUrl": web_full_url,
            "includePageLibraries": include_page_libraries
        }
        qry = ServiceOperationQuery(context.web, "GetDocumentAndMediaLibraries", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def _resolve_group_value(context, share_option, on_resolved):
        """

        :param office365.sharepoint.client_context.ClientContext context:
        :param ExternalSharingSiteOption share_option:
        :param (str) -> None on_resolved:
        """
        options = {
            ExternalSharingSiteOption.View: context.web.associated_visitor_group,
            ExternalSharingSiteOption.Edit: context.web.associated_member_group,
            ExternalSharingSiteOption.Owner: context.web.associated_owner_group,
        }
        grp = options[share_option]
        context.load(grp)

        def _group_resolved(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            role_value = "group:{groupId}".format(groupId=grp.properties["Id"])
            on_resolved(role_value)

        context.after_execute(_group_resolved)

    @staticmethod
    def get_sharing_link_kind(context, file_url, return_type=None):
        """
        This method determines the kind of tokenized sharing link represented by the supplied file URL.

        :param office365.sharepoint.client_context.ClientContext context:
        :param str file_url: A URL that is a tokenized sharing link for a document
        :param ClientResult or None return_type: Return object
        """
        if return_type is None:
            return_type = ClientResult(context)
        qry = ServiceOperationQuery(context.web, "GetSharingLinkKind", None, {"fileUrl": file_url}, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def forward_object_link(context, url, people_picker_input, email_subject=None, email_body=None):
        """
        Shares an object in SharePoint, such as a list item or a site with no Acl changes, by sending the link.
        This is used when the user has no permission to share and cannot send access request.
        The user can use this method to send the link of the object to site members who already have permission
        to view the object.
        Returns a SharingResult object that contains completion script and page for redirection if desired.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url: The URL of the website with the path of an object in SharePoint query string parameters.
        :param str people_picker_input: A string of JSON representing users in people picker format.
        :param str email_subject: The email subject.
        :param str email_body: The email subject.
        """
        result = SharingResult(context)
        payload = {
            "url": url,
            "peoplePickerInput": people_picker_input,
            "emailSubject": email_subject,
            "emailBody": email_body,
        }
        qry = ServiceOperationQuery(context.web, "ForwardObjectLink", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def share_object(context, url, people_picker_input,
                     role_value=None,
                     group_id=0, propagate_acl=False,
                     send_email=True, include_anonymous_link_in_email=False, email_subject=None, email_body=None,
                     use_simplified_roles=True, return_type=None):
        """
        This method shares an object in SharePoint such as a list item or site. It returns a SharingResult object
        which contains the completion script and a page to redirect to if desired.


        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url: The URL of the website with the path of an object in SharePoint query string parameters.
        :param str role_value: The sharing role value for the type of permission to grant on the object.
        :param str people_picker_input: A string of JSON representing users in people picker format.
        :param int group_id: The ID of the group to be added. Zero if not adding to a permissions group.
        :param bool propagate_acl:  A flag to determine if permissions SHOULD be pushed to items with unique permissions
        :param bool send_email: A flag to determine if an email notification SHOULD be sent (if email is configured).
        :param bool include_anonymous_link_in_email: If an email is being sent, this determines if an anonymous link
        SHOULD be added to the message.
        :param str email_subject: The email subject.
        :param str email_body: The email subject.
        :param bool use_simplified_roles: A Boolean value indicating whether to use the SharePoint simplified roles
        (Edit, View) or not.
        :param SharingResult or None return_type: Return type
        """
        if return_type is None:
            return_type = SharingResult(context)
        payload = {
            "url": url,
            "groupId": group_id,
            "peoplePickerInput": people_picker_input,
            "roleValue": role_value,
            "includeAnonymousLinkInEmail": include_anonymous_link_in_email,
            "propagateAcl": propagate_acl,
            "sendEmail": send_email,
            "emailSubject": email_subject,
            "emailBody": email_body,
            "useSimplifiedRoles": use_simplified_roles
        }
        qry = ServiceOperationQuery(context.web, "ShareObject", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def unshare_object(context, url, return_type=None):
        """
        Removes Sharing permissions on an object.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url: A SharingResult object which contains status codes pertaining to the completion of the operation
        :param SharingResult return_type: Return type
        """
        if return_type is None:
            return_type = SharingResult(context)
        payload = {
            "url": url
        }
        qry = ServiceOperationQuery(context.web, "UnshareObject", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def get_file_by_id(self, unique_id):
        """Returns the file object with the specified GUID.

        :param str unique_id: A GUID that identifies the file object.
        """
        return File(self.context, ServiceOperationPath("GetFileById", [unique_id], self.resource_path))

    def get_list_item(self, str_url):
        """
        Returns the list item that is associated with the specified server-relative URL.

        :param str str_url: A string that contains the server-relative URL,
        for example, "/sites/MySite/Shared Documents/MyDocument.docx".
        :return: ListItem
        """
        return ListItem(self.context, ServiceOperationPath("GetListItem", [str_url], self.resource_path))

    def get_list_item_using_path(self, decoded_url):
        """
        Returns the list item that is associated with the specified server-relative path.

        :param str decoded_url: A string that contains the server-relative path,
        for example, "/sites/MySite/Shared Documents/MyDocument.docx".
        :return: ListItem
        """
        path = SPResPath(self.context.create_safe_url(decoded_url))
        return ListItem(self.context,
                        ServiceOperationPath("GetListItemUsingPath", path, self.resource_path))

    def get_catalog(self, type_catalog):
        """Gets the list template gallery, site template gallery, or Web Part gallery for the Web site.

        :param int type_catalog: The type of the gallery.
        """
        return List(self.context, ServiceOperationPath("getCatalog", [type_catalog], self.resource_path))

    def page_context_info(self, include_odb_settings, emit_navigation_info):
        """
        Return Page context info for the current list being rendered.

        :param bool include_odb_settings:
        :param bool emit_navigation_info:
        """
        return_type = ClientResult(self.context)
        payload = {
            "includeODBSettings": include_odb_settings,
            "emitNavigationInfo": emit_navigation_info
        }
        qry = ServiceOperationQuery(self, "PageContextInfo", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_storage_entity(self, key):
        """
        This will return the storage entity identified by the given key

        :param str key: ID of storage entity to be returned.
        """
        return_type = StorageEntity(self.context)
        params = {
            "key": key,
        }
        qry = ServiceOperationQuery(self, "GetStorageEntity", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_storage_entity(self, key, value, description=None, comments=None):
        """
        This will set the storage entity identified by the given key

        :param str key: Id of the storage entity to be set.
        :param str value: Value of the storage entity to be set.
        :param str description: Description of the storage entity to be set.
        :param str comments: Comments of the storage entity to be set.
        """
        payload = {
            "key": key,
            "value": value,
            "description": description,
            "comments": comments
        }
        qry = ServiceOperationQuery(self, "SetStorageEntity", None, payload, None)
        self.context.add_query(qry)
        return self

    def remove_storage_entity(self, key):
        """
        This will remove the storage entity identified by the given key

        :param str key: Id of the storage entity to be removed.
        """
        params = {
            "key": key,
        }
        qry = ServiceOperationQuery(self, "RemoveStorageEntity", params, None, None, None)
        self.context.add_query(qry)
        return self

    @property
    def allow_rss_feeds(self):
        """Gets a Boolean value that specifies whether the site collection allows RSS feeds.

        :rtype: str
        """
        return self.properties.get("AllowRssFeeds", None)

    @property
    def alternate_css_url(self):
        """Gets the URL for an alternate cascading style sheet (CSS) to use in the website.

        :rtype: str
        """
        return self.properties.get("AlternateCssUrl", None)

    @property
    def author(self):
        """
        Gets a user object that represents the user who created the Web site.
        """
        return self.properties.get("Author", User(self.context, ResourcePath("Author", self.resource_path)))

    @property
    def created(self):
        """Specifies when the site was created.

        :rtype: datetime or None
        """
        return self.properties.get("Created", None)

    @property
    def custom_master_url(self):
        """Gets the URL for a custom master page to apply to the Web site

        :rtype: str or None
        """
        return self.properties.get("CustomMasterUrl", None)

    @property
    def id(self):
        """
        Specifies the site identifier for the site

        :rtype: str
        """
        return self.properties.get("Id", None)

    @property
    def access_requests_list(self):
        return self.properties.get('AccessRequestsList',
                                   List(self.context, ResourcePath("AccessRequestsList", self.resource_path)))

    @property
    def access_request_list_url(self):
        """
        :rtype: str or None
        """
        return self.properties.get("AccessRequestListUrl", None)

    @property
    def webs(self):
        """Get child webs"""
        from office365.sharepoint.webs.web_collection import WebCollection
        return self.properties.get("Webs",
                                   WebCollection(self.context, ResourcePath("webs", self.resource_path), self))

    @property
    def folders(self):
        """Get folder resources"""
        return self.properties.get('Folders',
                                   FolderCollection(self.context, ResourcePath("folders", self.resource_path), self))

    @property
    def lists(self):
        """Get web list collection"""
        return self.properties.get('Lists',
                                   ListCollection(self.context, ResourcePath("lists", self.resource_path)))

    @property
    def site_users(self):
        """
        Specifies the collection of users in the site collection that contains the site
        """
        return self.properties.get('SiteUsers',
                                   UserCollection(self.context, ResourcePath("siteUsers", self.resource_path)))

    @property
    def site_groups(self):
        """Gets the collection of groups for the site collection."""
        return self.properties.get('SiteGroups',
                                   GroupCollection(self.context, ResourcePath("siteGroups", self.resource_path)))

    @property
    def current_user(self):
        """Gets the current user."""
        return self.properties.get('CurrentUser',
                                   User(self.context, ResourcePath("CurrentUser", self.resource_path)))

    @property
    def parent_web(self):
        """Gets the parent website of the specified website."""
        return self.properties.get('ParentWeb',
                                   Web(self.context, ResourcePath("ParentWeb", self.resource_path)))

    @property
    def associated_visitor_group(self):
        """Gets or sets the associated visitor group of the Web site."""
        return self.properties.get('AssociatedVisitorGroup',
                                   Group(self.context, ResourcePath("AssociatedVisitorGroup", self.resource_path)))

    @property
    def associated_owner_group(self):
        """Gets or sets the associated owner group of the Web site."""
        return self.properties.get('AssociatedOwnerGroup',
                                   Group(self.context, ResourcePath("AssociatedOwnerGroup", self.resource_path)))

    @property
    def associated_member_group(self):
        """Gets or sets the group of users who have been given contribute permissions to the Web site."""
        return self.properties.get('AssociatedMemberGroup',
                                   Group(self.context, ResourcePath("AssociatedMemberGroup", self.resource_path)))

    @property
    def fields(self):
        """Specifies the collection of all the fields (2) in the site (2)."""
        return self.properties.get('Fields',
                                   FieldCollection(self.context, ResourcePath("Fields", self.resource_path)))

    @property
    def content_types(self):
        """Gets the collection of content types for the Web site."""
        return self.properties.get('ContentTypes',
                                   ContentTypeCollection(self.context,
                                                         ResourcePath("ContentTypes", self.resource_path), self))

    @property
    def role_definitions(self):
        """Gets the collection of role definitions for the Web site."""
        return self.properties.get("RoleDefinitions",
                                   RoleDefinitionCollection(self.context,
                                                            ResourcePath("RoleDefinitions", self.resource_path)))

    @property
    def event_receivers(self):
        """Specifies the collection of event receiver definitions that are currently available on the Web site"""
        return self.properties.get('EventReceivers',
                                   EventReceiverDefinitionCollection(self.context,
                                                                     ResourcePath("eventReceivers", self.resource_path),
                                                                     self))

    @property
    def client_web_parts(self):
        """
        Gets a collection of the ClientWebParts installed in this SP.Web. It can be used to get metadata of the
        ClientWebParts or render them. It is a read-only collection as ClientWebParts need to be installed in
        an app package."""
        return self.properties.get('ClientWebParts',
                                   ClientWebPartCollection(self.context,
                                                           ResourcePath("ClientWebParts", self.resource_path)))

    @property
    def tenant_app_catalog(self):
        """Returns the tenant app catalog for the given tenant if it exists."""
        return self.properties.get('TenantAppCatalog',
                                   TenantCorporateCatalogAccessor(self.context,
                                                                  ResourcePath("TenantAppCatalog", self.resource_path)))

    @property
    def site_collection_app_catalog(self):
        """Returns the site collection app catalog for the given web if it exists."""
        return self.properties.get('SiteCollectionAppCatalog',
                                   SiteCollectionCorporateCatalogAccessor(self.context,
                                                                          ResourcePath("SiteCollectionAppCatalog",
                                                                                       self.resource_path)))

    @property
    def web_infos(self):
        """Specifies the collection of all child sites for the site"""
        return self.properties.get('WebInfos',
                                   WebInformationCollection(self.context, ResourcePath("WebInfos", self.resource_path)))

    @property
    def url(self):
        """Gets the absolute URL for the website.

        :rtype: str or None
        """
        return self.properties.get('Url', None)

    @property
    def quick_launch_enabled(self):
        """Gets a value that specifies whether the Quick Launch area is enabled on the site.

        :rtype: bool or None
        """
        return self.properties.get('QuickLaunchEnabled', None)

    @quick_launch_enabled.setter
    def quick_launch_enabled(self, value):
        """Sets a value that specifies whether the Quick Launch area is enabled on the site.

        :type value: bool
        """
        self.set_property('QuickLaunchEnabled', value)

    @property
    def site_logo_url(self):
        """Gets a value that specifies Site logo url.

        :rtype: str or None
        """
        return self.properties.get('SiteLogoUrl', None)

    @property
    def list_templates(self):
        """Gets a value that specifies the collection of list definitions and list templates available for creating
            lists on the site."""
        return self.properties.get('ListTemplates',
                                   ListTemplateCollection(self.context,
                                                          ResourcePath("ListTemplates", self.resource_path)))

    @property
    def multilingual_settings(self):
        """Gets a value that specifies the collection of list definitions and list templates available for creating
            lists on the site."""
        return self.properties.get('MultilingualSettings',
                                   MultilingualSettings(self.context,
                                                        ResourcePath("MultilingualSettings", self.resource_path)))

    @property
    def web_template(self):
        """Gets the name of the site definition or site template that was used to create the site.

        :rtype: str or None
        """
        return self.properties.get('WebTemplate', None)

    @property
    def regional_settings(self):
        """Gets the regional settings that are currently implemented on the website."""
        return self.properties.get('RegionalSettings',
                                   RegionalSettings(self.context, ResourcePath("RegionalSettings", self.resource_path)))

    @property
    def recycle_bin(self):
        """Specifies the collection of Recycle Bin items of the Recycle Bin of the site"""
        return self.properties.get('RecycleBin',
                                   RecycleBinItemCollection(self.context,
                                                            ResourcePath("RecycleBin", self.resource_path)))

    @property
    def navigation(self):
        """Specifies the navigation structure on the site (2), including the Quick Launch area and the link bar."""
        return self.properties.get('Navigation',
                                   Navigation(self.context,
                                              ResourcePath("Navigation", self.resource_path)))

    @property
    def push_notification_subscribers(self):
        """Specifies the collection of push notification subscribers for the site"""
        return self.properties.get('PushNotificationSubscribers',
                                   BaseEntityCollection(self.context, PushNotificationSubscriber,
                                                        ResourcePath("PushNotificationSubscribers",
                                                                     self.resource_path)))

    @property
    def root_folder(self):
        """Get a root folder"""
        return self.properties.get("RootFolder", Folder(self.context, ResourcePath("RootFolder", self.resource_path)))

    @property
    def alerts(self):
        """Gets the collection of alerts for the site or subsite."""
        return self.properties.get('Alerts',
                                   AlertCollection(self.context,
                                                   ResourcePath("Alerts", self.resource_path)))

    @property
    def available_fields(self):
        """
        Specifies the collection of all fields available for the current scope, including those of the
        current site, as well as any parent sites.
        """
        return self.properties.get('AvailableFields',
                                   FieldCollection(self.context, ResourcePath("AvailableFields", self.resource_path)))

    @property
    def available_content_types(self):
        """
        Specifies the collection of all site content types that apply to the current scope,
        including those of the current site (2), as well as any parent sites.
        """
        return self.properties.get('AvailableContentTypes',
                                   ContentTypeCollection(self.context, ResourcePath("AvailableContentTypes",
                                                                                    self.resource_path)))

    @property
    def site_user_info_list(self):
        """
        Specifies the user information list for the site collection that contains the site
        """
        return self.properties.get('SiteUserInfoList',
                                   List(self.context, ResourcePath("SiteUserInfoList", self.resource_path)))

    @property
    def welcome_page(self):
        """
        Specifies the URL of the Welcome page for the site

        :rtype: str or None
        """
        return self.properties.get('WelcomePage', None)

    @property
    def supported_ui_language_ids(self):
        """Specifies the language code identifiers (LCIDs) of the languages that are enabled for the site."""
        return self.properties.get('SupportedUILanguageIds', ClientValueCollection(int))

    @property
    def ui_version(self):
        """
        Gets or sets the user interface (UI) version of the Web site.

        :rtype: int or None
        """
        return self.properties.get('UIVersion', None)

    @property
    def user_custom_actions(self):
        """Specifies the collection of user custom actions for the site"""
        return self.properties.get('UserCustomActions',
                                   UserCustomActionCollection(self.context,
                                                              ResourcePath("UserCustomActions", self.resource_path)))

    @property
    def server_relative_path(self):
        """
        Gets the server-relative Path of the Web.
        """
        return self.properties.get("ServerRelativePath", SPResPath())

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "AccessRequestsList": self.access_requests_list,
                "AvailableFields": self.available_fields,
                "AvailableContentTypes": self.available_content_types,
                "AssociatedOwnerGroup": self.associated_owner_group,
                "AssociatedMemberGroup": self.associated_member_group,
                "AssociatedVisitorGroup": self.associated_visitor_group,
                "ContentTypes": self.content_types,
                "ClientWebParts": self.client_web_parts,
                "CurrentUser": self.current_user,
                "EventReceivers": self.event_receivers,
                "ListTemplates": self.list_templates,
                "MultilingualSettings": self.multilingual_settings,
                "ParentWeb": self.parent_web,
                "PushNotificationSubscribers": self.push_notification_subscribers,
                "RootFolder": self.root_folder,
                "RegionalSettings": self.regional_settings,
                "RoleDefinitions": self.role_definitions,
                "RecycleBin": self.recycle_bin,
                "SiteCollectionAppCatalog": self.site_collection_app_catalog,
                "SiteGroups": self.site_groups,
                "SiteUsers": self.site_users,
                "SiteUserInfoList": self.site_user_info_list,
                "TenantAppCatalog": self.tenant_app_catalog,
                "UserCustomActions": self.user_custom_actions,
                "WebInfos": self.web_infos
            }
            default_value = property_mapping.get(name, None)
        return super(Web, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(Web, self).set_property(name, value, persist_changes)
        if name == "Url":
            self._web_url = value
        return self

    @property
    def resource_url(self):
        """Returns Web url"""
        val = super(Web, self).resource_url
        if self._web_url is not None:
            val = val.replace(self.context.service_root_url(), self._web_url + '/_api')
        return val
