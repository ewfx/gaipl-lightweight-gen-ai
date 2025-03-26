"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server.
"""

import os
from typing import Dict, Union, Any
import json
import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.catalog import (
    CatalogCategoryListParams,
    CatalogListParams,
    CatalogResource,
)
from servicenow_mcp.resources.incidents import IncidentListParams, IncidentResource
from servicenow_mcp.resources.changesets import ChangesetListParams, ChangesetResource
from servicenow_mcp.resources.script_includes import ScriptIncludeListParams, ScriptIncludeResource
from servicenow_mcp.tools.catalog_tools import (
    GetCatalogItemParams,
    ListCatalogCategoriesParams,
    ListCatalogItemsParams,
    CreateCatalogCategoryParams,
    UpdateCatalogCategoryParams,
    MoveCatalogItemsParams,
)
from servicenow_mcp.tools.catalog_tools import (
    get_catalog_item as get_catalog_item_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    list_catalog_categories as list_catalog_categories_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    list_catalog_items as list_catalog_items_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    create_catalog_category as create_catalog_category_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    update_catalog_category as update_catalog_category_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    move_catalog_items as move_catalog_items_tool,
)
from servicenow_mcp.tools.catalog_optimization import (
    OptimizationRecommendationsParams,
    UpdateCatalogItemParams,
    get_optimization_recommendations as get_optimization_recommendations_tool,
    update_catalog_item as update_catalog_item_tool,
)
from servicenow_mcp.tools.catalog_variables import (
    CreateCatalogItemVariableParams,
    ListCatalogItemVariablesParams,
    UpdateCatalogItemVariableParams,
)
from servicenow_mcp.tools.catalog_variables import (
    create_catalog_item_variable as create_catalog_item_variable_tool,
)
from servicenow_mcp.tools.catalog_variables import (
    list_catalog_item_variables as list_catalog_item_variables_tool,
)
from servicenow_mcp.tools.catalog_variables import (
    update_catalog_item_variable as update_catalog_item_variable_tool,
)
from servicenow_mcp.tools.incident_tools import (
    AddCommentParams,
    CreateIncidentParams,
    ListIncidentsParams,
    ResolveIncidentParams,
    UpdateIncidentParams,
)
from servicenow_mcp.tools.incident_tools import (
    add_comment as add_comment_tool,
)
from servicenow_mcp.tools.incident_tools import (
    create_incident as create_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    list_incidents as list_incidents_tool,
)
from servicenow_mcp.tools.incident_tools import (
    resolve_incident as resolve_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    update_incident as update_incident_tool,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

from servicenow_mcp.tools.change_tools import (
    AddChangeTaskParams,
    ApproveChangeParams,
    CreateChangeRequestParams,
    GetChangeRequestDetailsParams,
    ListChangeRequestsParams,
    RejectChangeParams,
    SubmitChangeForApprovalParams,
    UpdateChangeRequestParams,
)
from servicenow_mcp.tools.change_tools import (
    add_change_task as add_change_task_tool,
)
from servicenow_mcp.tools.change_tools import (
    approve_change as approve_change_tool,
)
from servicenow_mcp.tools.change_tools import (
    create_change_request as create_change_request_tool,
)
from servicenow_mcp.tools.change_tools import (
    get_change_request_details as get_change_request_details_tool,
)
from servicenow_mcp.tools.change_tools import (
    list_change_requests as list_change_requests_tool,
)
from servicenow_mcp.tools.change_tools import (
    reject_change as reject_change_tool,
)
from servicenow_mcp.tools.change_tools import (
    submit_change_for_approval as submit_change_for_approval_tool,
)
from servicenow_mcp.tools.change_tools import (
    update_change_request as update_change_request_tool,
)

from servicenow_mcp.tools.workflow_tools import (
    GetWorkflowActivitiesParams,
    GetWorkflowDetailsParams,
    ListWorkflowsParams,
    ListWorkflowVersionsParams,
    CreateWorkflowParams,
    UpdateWorkflowParams,
    ActivateWorkflowParams,
    DeactivateWorkflowParams,
    AddWorkflowActivityParams,
    UpdateWorkflowActivityParams,
    DeleteWorkflowActivityParams,
    ReorderWorkflowActivitiesParams,
)
from servicenow_mcp.tools.workflow_tools import (
    get_workflow_activities as get_workflow_activities_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    get_workflow_details as get_workflow_details_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    list_workflows as list_workflows_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    list_workflow_versions as list_workflow_versions_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    create_workflow as create_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    update_workflow as update_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    activate_workflow as activate_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    deactivate_workflow as deactivate_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    add_workflow_activity as add_workflow_activity_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    update_workflow_activity as update_workflow_activity_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    delete_workflow_activity as delete_workflow_activity_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    reorder_workflow_activities as reorder_workflow_activities_tool,
)

from servicenow_mcp.tools.changeset_tools import (
    ListChangesetsParams,
    GetChangesetDetailsParams,
    CreateChangesetParams,
    UpdateChangesetParams,
    CommitChangesetParams,
    PublishChangesetParams,
    AddFileToChangesetParams,
)
from servicenow_mcp.tools.changeset_tools import (
    list_changesets as list_changesets_tool,
)
from servicenow_mcp.tools.changeset_tools import (
    get_changeset_details as get_changeset_details_tool,
)
from servicenow_mcp.tools.changeset_tools import (
    create_changeset as create_changeset_tool,
)
from servicenow_mcp.tools.changeset_tools import (
    update_changeset as update_changeset_tool,
)
from servicenow_mcp.tools.changeset_tools import (
    commit_changeset as commit_changeset_tool,
)
from servicenow_mcp.tools.changeset_tools import (
    publish_changeset as publish_changeset_tool,
)
from servicenow_mcp.tools.changeset_tools import (
    add_file_to_changeset as add_file_to_changeset_tool,
)

from servicenow_mcp.tools.script_include_tools import (
    ListScriptIncludesParams,
    GetScriptIncludeParams,
    CreateScriptIncludeParams,
    UpdateScriptIncludeParams,
    DeleteScriptIncludeParams,
    ScriptIncludeResponse,
    list_script_includes as list_script_includes_tool,
    get_script_include as get_script_include_tool,
    create_script_include as create_script_include_tool,
    update_script_include as update_script_include_tool,
    delete_script_include as delete_script_include_tool,
)

from servicenow_mcp.tools.knowledge_base import (
    CreateKnowledgeBaseParams,
    ListKnowledgeBasesParams,
    CreateCategoryParams,
    ListCategoriesParams,
    CreateArticleParams,
    UpdateArticleParams,
    PublishArticleParams,
    ListArticlesParams,
    GetArticleParams,
    KnowledgeBaseResponse,
    CategoryResponse,
    ArticleResponse,
)
from servicenow_mcp.tools.knowledge_base import (
    create_knowledge_base as create_knowledge_base_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    create_category as create_category_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    create_article as create_article_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    update_article as update_article_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    publish_article as publish_article_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    list_articles as list_articles_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    get_article as get_article_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    list_knowledge_bases as list_knowledge_bases_tool,
)
from servicenow_mcp.tools.knowledge_base import (
    list_categories as list_categories_tool,
)

from servicenow_mcp.tools.user_tools import (
    CreateUserParams,
    UpdateUserParams,
    GetUserParams,
    ListUsersParams,
    CreateGroupParams,
    UpdateGroupParams,
    AddGroupMembersParams,
    RemoveGroupMembersParams,
    ListGroupsParams,
)
from servicenow_mcp.tools.user_tools import (
    create_user as create_user_tool,
    update_user as update_user_tool,
    get_user as get_user_tool,
    list_users as list_users_tool,
    create_group as create_group_tool,
    update_group as update_group_tool,
    add_group_members as add_group_members_tool,
    remove_group_members as remove_group_members_tool,
    list_groups as list_groups_tool,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceNowMCP:
    """
    ServiceNow MCP Server implementation.

    This class provides a Model Context Protocol (MCP) server for ServiceNow,
    allowing LLMs to interact with ServiceNow data and functionality.
    """

    def __init__(self, config: Union[Dict, ServerConfig]):
        """
        Initialize the ServiceNow MCP server.

        Args:
            config: Server configuration, either as a dictionary or ServerConfig object.
        """
        if isinstance(config, dict):
            self.config = ServerConfig(**config)
        else:
            self.config = config

        self.auth_manager = AuthManager(self.config.auth)
        self.mcp_server = FastMCP("ServiceNow")
        # Add name attribute for MCP CLI
        self.name = "ServiceNow"

        # Register resources and tools
        self._register_resources()
        self._register_tools()

    def _register_resources(self):
        """Register all ServiceNow resources with the MCP server."""
        # Register incident resources
        incident_resource = IncidentResource(self.config, self.auth_manager)

        # Use decorator pattern for resources
        @self.mcp_server.resource("incidents://list")
        async def list_incidents() -> str:
            """List incidents from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            incidents = await incident_resource.list_incidents(IncidentListParams())
            return incidents

        @self.mcp_server.resource("incident://{incident_id}")
        def get_incident(incident_id: str) -> str:
            """Get a specific incident from ServiceNow by ID or number"""
            return incident_resource.get_incident(incident_id)
            
        # Register catalog resources
        catalog_resource = CatalogResource(self.config, self.auth_manager)
        
        @self.mcp_server.resource("catalog://items")
        async def list_catalog_items() -> str:
            """List catalog items from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            items = await catalog_resource.list_catalog_items(CatalogListParams())
            return items
            
        @self.mcp_server.resource("catalog://categories")
        async def list_catalog_categories() -> str:
            """List catalog categories from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            categories = await catalog_resource.list_catalog_categories(CatalogCategoryListParams())
            return categories
            
        @self.mcp_server.resource("catalog://{item_id}")
        async def get_catalog_item(item_id: str) -> str:
            """Get a specific catalog item from ServiceNow by ID or number"""
            return await catalog_resource.get_catalog_item(item_id)

        # Register changeset resources
        changeset_resource = ChangesetResource(self.config, self.auth_manager)
        
        @self.mcp_server.resource("changesets://list")
        async def list_changesets() -> str:
            """List changesets from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            changesets = await changeset_resource.list_changesets(ChangesetListParams())
            return changesets
            
        @self.mcp_server.resource("changeset://{changeset_id}")
        async def get_changeset(changeset_id: str) -> str:
            """Get a specific changeset from ServiceNow by ID"""
            return await changeset_resource.get_changeset(changeset_id)

        # Register script include resources
        script_include_resource = ScriptIncludeResource(self.config, self.auth_manager)
        
        @self.mcp_server.resource("scriptincludes://list")
        async def list_script_includes() -> str:
            """List script includes from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            script_includes = await script_include_resource.list_script_includes(ScriptIncludeListParams())
            return script_includes
            
        @self.mcp_server.resource("scriptinclude://{script_include_id}")
        async def get_script_include(script_include_id: str) -> str:
            """Get a specific script include from ServiceNow by ID or name"""
            return await script_include_resource.get_script_include(script_include_id)

    def _register_tools(self):
        """Register all ServiceNow tools with the MCP server."""

        # Register incident tools
        @self.mcp_server.tool()
        def create_incident(params: CreateIncidentParams) -> str:
            """Create a new incident in ServiceNow"""
            return create_incident_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def update_incident(params: UpdateIncidentParams) -> str:
            """Update an existing incident in ServiceNow"""
            return update_incident_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def add_comment(params: AddCommentParams) -> str:
            """Add a comment to an incident in ServiceNow"""
            return add_comment_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def resolve_incident(params: ResolveIncidentParams) -> str:
            """Resolve an incident in ServiceNow"""
            return resolve_incident_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def list_incidents(params: ListIncidentsParams) -> str:
            """List incidents from ServiceNow"""
            return list_incidents_tool(self.config, self.auth_manager, params)
            
        # Register catalog tools
        @self.mcp_server.tool()
        def list_catalog_items(params: ListCatalogItemsParams) -> str:
            """List service catalog items."""
            return json.dumps(
                list_catalog_items_tool(self.config, self.auth_manager, params)
            )

        @self.mcp_server.tool()
        def get_catalog_item(params: GetCatalogItemParams) -> str:
            """Get a specific service catalog item."""
            return json.dumps(
                get_catalog_item_tool(self.config, self.auth_manager, params).dict()
            )
            
        @self.mcp_server.tool()
        def list_catalog_categories(params: ListCatalogCategoriesParams) -> str:
            """List service catalog categories."""
            return json.dumps(
                list_catalog_categories_tool(self.config, self.auth_manager, params)
            )

        @self.mcp_server.tool()
        def create_catalog_category(params: CreateCatalogCategoryParams) -> str:
            """Create a new service catalog category."""
            return json.dumps(
                create_catalog_category_tool(self.config, self.auth_manager, params).dict()
            )

        @self.mcp_server.tool()
        def update_catalog_category(params: UpdateCatalogCategoryParams) -> str:
            """Update an existing service catalog category."""
            return json.dumps(
                update_catalog_category_tool(self.config, self.auth_manager, params).dict()
            )

        @self.mcp_server.tool()
        def move_catalog_items(params: MoveCatalogItemsParams) -> str:
            """Move catalog items to a different category."""
            return json.dumps(
                move_catalog_items_tool(self.config, self.auth_manager, params).dict()
            )

        @self.mcp_server.tool()
        def get_optimization_recommendations(params: OptimizationRecommendationsParams) -> str:
            """Get optimization recommendations for the service catalog."""
            return json.dumps(
                get_optimization_recommendations_tool(self.config, self.auth_manager, params)
            )
            
        @self.mcp_server.tool()
        def update_catalog_item(params: UpdateCatalogItemParams) -> str:
            """Update a service catalog item."""
            return json.dumps(
                update_catalog_item_tool(
                    self.config,
                    self.auth_manager,
                    params,
                )
            )

        @self.mcp_server.tool()
        def create_catalog_item_variable(params: CreateCatalogItemVariableParams) -> Dict[str, Any]:
            return create_catalog_item_variable_tool(
                self.config,
                self.auth_manager,
                params,
            ).__dict__
            
        @self.mcp_server.tool()
        def list_catalog_item_variables(params: ListCatalogItemVariablesParams) -> Dict[str, Any]:
            return list_catalog_item_variables_tool(
                self.config,
                self.auth_manager,
                params,
            ).__dict__
            
        @self.mcp_server.tool()
        def update_catalog_item_variable(params: UpdateCatalogItemVariableParams) -> Dict[str, Any]:
            return update_catalog_item_variable_tool(
                self.config,
                self.auth_manager,
                params,
            ).__dict__

        # Register change management tools
        @self.mcp_server.tool()
        def create_change_request(params: CreateChangeRequestParams) -> str:
            """Create a new change request in ServiceNow"""
            return create_change_request_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def update_change_request(params: UpdateChangeRequestParams) -> str:
            """Update an existing change request in ServiceNow"""
            return update_change_request_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def list_change_requests(params: ListChangeRequestsParams) -> str:
            """List change requests from ServiceNow"""
            return list_change_requests_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def get_change_request_details(params: GetChangeRequestDetailsParams) -> str:
            """Get detailed information about a specific change request"""
            return get_change_request_details_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def add_change_task(params: AddChangeTaskParams) -> str:
            """Add a task to a change request"""
            return add_change_task_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def submit_change_for_approval(params: SubmitChangeForApprovalParams) -> str:
            """Submit a change request for approval"""
            return submit_change_for_approval_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def approve_change(params: ApproveChangeParams) -> str:
            """Approve a change request"""
            return approve_change_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def reject_change(params: RejectChangeParams) -> str:
            """Reject a change request"""
            return reject_change_tool(self.config, self.auth_manager, params)

        # Register workflow management tools
        @self.mcp_server.tool()
        def list_workflows(params: ListWorkflowsParams) -> str:
            """List workflows from ServiceNow"""
            return list_workflows_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def get_workflow_details(params: GetWorkflowDetailsParams) -> str:
            """Get detailed information about a specific workflow"""
            return get_workflow_details_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def list_workflow_versions(params: ListWorkflowVersionsParams) -> str:
            """List workflow versions from ServiceNow"""
            return list_workflow_versions_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def get_workflow_activities(params: GetWorkflowActivitiesParams) -> str:
            """Get activities for a specific workflow"""
            return get_workflow_activities_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def create_workflow(params: CreateWorkflowParams) -> str:
            """Create a new workflow in ServiceNow"""
            return create_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_workflow(params: UpdateWorkflowParams) -> str:
            """Update an existing workflow in ServiceNow"""
            return update_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def activate_workflow(params: ActivateWorkflowParams) -> str:
            """Activate a workflow in ServiceNow"""
            return activate_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def deactivate_workflow(params: DeactivateWorkflowParams) -> str:
            """Deactivate a workflow in ServiceNow"""
            return deactivate_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def add_workflow_activity(params: AddWorkflowActivityParams) -> str:
            """Add a new activity to a workflow in ServiceNow"""
            return add_workflow_activity_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_workflow_activity(params: UpdateWorkflowActivityParams) -> str:
            """Update an existing activity in a workflow"""
            return update_workflow_activity_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def delete_workflow_activity(params: DeleteWorkflowActivityParams) -> str:
            """Delete an activity from a workflow"""
            return delete_workflow_activity_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def reorder_workflow_activities(params: ReorderWorkflowActivitiesParams) -> str:
            """Reorder activities in a workflow"""
            return reorder_workflow_activities_tool(self.config, self.auth_manager, params)

        # Register changeset management tools
        @self.mcp_server.tool()
        def list_changesets(params: ListChangesetsParams) -> str:
            """List changesets from ServiceNow"""
            return list_changesets_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def get_changeset_details(params: GetChangesetDetailsParams) -> str:
            """Get detailed information about a specific changeset"""
            return get_changeset_details_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def create_changeset(params: CreateChangesetParams) -> str:
            """Create a new changeset in ServiceNow"""
            return create_changeset_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_changeset(params: UpdateChangesetParams) -> str:
            """Update an existing changeset in ServiceNow"""
            return update_changeset_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def commit_changeset(params: CommitChangesetParams) -> str:
            """Commit a changeset in ServiceNow"""
            return commit_changeset_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def publish_changeset(params: PublishChangesetParams) -> str:
            """Publish a changeset in ServiceNow"""
            return publish_changeset_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def add_file_to_changeset(params: AddFileToChangesetParams) -> str:
            """Add a file to a changeset in ServiceNow"""
            return add_file_to_changeset_tool(self.config, self.auth_manager, params)

        # Register script include tools
        @self.mcp_server.tool()
        def list_script_includes(params: ListScriptIncludesParams) -> Dict[str, Any]:
            """List script includes from ServiceNow"""
            return list_script_includes_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def get_script_include(params: GetScriptIncludeParams) -> Dict[str, Any]:
            """Get a specific script include from ServiceNow"""
            return get_script_include_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def create_script_include(params: CreateScriptIncludeParams) -> ScriptIncludeResponse:
            """Create a new script include in ServiceNow"""
            return create_script_include_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_script_include(params: UpdateScriptIncludeParams) -> ScriptIncludeResponse:
            """Update an existing script include in ServiceNow"""
            return update_script_include_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def delete_script_include(params: DeleteScriptIncludeParams) -> str:
            return json.dumps(delete_script_include_tool(self.config, self.auth_manager, params).dict())
        
        # Knowledge Base tools
        @self.mcp_server.tool()
        def create_knowledge_base(params: CreateKnowledgeBaseParams) -> str:
            """Create a new knowledge base in ServiceNow"""
            return json.dumps(
                create_knowledge_base_tool(self.config, self.auth_manager, params).dict()
            )
        
        @self.mcp_server.tool()
        def list_knowledge_bases(params: ListKnowledgeBasesParams) -> Dict[str, Any]:
            """List knowledge bases from ServiceNow"""
            logger.info("list_knowledge_bases called with params: %s", params)
            try:
                result = list_knowledge_bases_tool(self.config, self.auth_manager, params)
                logger.info("list_knowledge_bases_tool returned: %s", result)
                
                # Third approach - match script_include tools exactly by returning raw dictionary
                logger.info("Using approach: Return raw dictionary (matching script_include tools)")
                return result
            except Exception as e:
                logger.error("Error in list_knowledge_bases: %s", str(e), exc_info=True)
                return {"success": False, "message": f"Error: {str(e)}"}
        
        @self.mcp_server.tool()
        def create_category(params: CreateCategoryParams) -> str:
            """Create a new category in a knowledge base"""
            return json.dumps(
                create_category_tool(self.config, self.auth_manager, params).dict()
            )
        
        @self.mcp_server.tool()
        def create_article(params: CreateArticleParams) -> str:
            """Create a new knowledge article"""
            return json.dumps(
                create_article_tool(self.config, self.auth_manager, params).dict()
            )
        
        @self.mcp_server.tool()
        def update_article(params: UpdateArticleParams) -> str:
            """Update an existing knowledge article"""
            return json.dumps(
                update_article_tool(self.config, self.auth_manager, params).dict()
            )
        
        @self.mcp_server.tool()
        def publish_article(params: PublishArticleParams) -> str:
            """Publish a knowledge article"""
            return json.dumps(
                publish_article_tool(self.config, self.auth_manager, params).dict()
            )
        
        @self.mcp_server.tool()
        def list_articles(params: ListArticlesParams) -> Dict[str, Any]:
            """List knowledge articles"""
            logger.info("list_articles called with params: %s", params)
            try:
                result = list_articles_tool(self.config, self.auth_manager, params)
                logger.info("list_articles_tool returned type: %s", type(result))
                return result
            except Exception as e:
                logger.error("Error in list_articles: %s", str(e), exc_info=True)
                return {"success": False, "message": f"Error: {str(e)}"}
        
        @self.mcp_server.tool()
        def get_article(params: GetArticleParams) -> Dict[str, Any]:
            """Get a specific knowledge article by ID"""
            logger.info("get_article called with params: %s", params)
            try:
                result = get_article_tool(self.config, self.auth_manager, params)
                logger.info("get_article_tool returned type: %s", type(result))
                return result
            except Exception as e:
                logger.error("Error in get_article: %s", str(e), exc_info=True)
                return {"success": False, "message": f"Error: {str(e)}"}

        @self.mcp_server.tool()
        def list_categories(params: ListCategoriesParams) -> Dict[str, Any]:
            """List categories in a knowledge base"""
            logger.info("list_categories called with params: %s", params)
            try:
                result = list_categories_tool(self.config, self.auth_manager, params)
                logger.info("list_categories_tool returned type: %s", type(result))
                return result
            except Exception as e:
                logger.error("Error in list_categories: %s", str(e), exc_info=True)
                return {"success": False, "message": f"Error: {str(e)}"}

        # User management tools
        @self.mcp_server.tool()
        def create_user(params: CreateUserParams) -> Dict[str, Any]:
            return create_user_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def update_user(params: UpdateUserParams) -> Dict[str, Any]:
            return update_user_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def get_user(params: GetUserParams) -> Dict[str, Any]:
            return get_user_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def list_users(params: ListUsersParams) -> Dict[str, Any]:
            return list_users_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def create_group(params: CreateGroupParams) -> Dict[str, Any]:
            return create_group_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def update_group(params: UpdateGroupParams) -> Dict[str, Any]:
            return update_group_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def add_group_members(params: AddGroupMembersParams) -> Dict[str, Any]:
            return add_group_members_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def remove_group_members(params: RemoveGroupMembersParams) -> Dict[str, Any]:
            return remove_group_members_tool(
                self.config,
                self.auth_manager,
                params,
            )
            
        @self.mcp_server.tool()
        def list_groups(params: ListGroupsParams) -> Dict[str, Any]:
            """List groups from ServiceNow with optional filtering"""
            return list_groups_tool(
                self.config,
                self.auth_manager,
                params,
            )

    def start(self):
        """Start the MCP server."""
        self.mcp_server.run()

    def stop(self):
        """Stop the MCP server."""
        # Cleanup resources if needed
        pass


def create_servicenow_mcp(instance_url: str, username: str, password: str):
    """
    Create a ServiceNow MCP server with minimal configuration.

    This is a simplified factory function that creates a pre-configured
    ServiceNow MCP server with basic authentication.

    Args:
        instance_url: ServiceNow instance URL
        username: ServiceNow username
        password: ServiceNow password

    Returns:
        A configured ServiceNowMCP instance ready to use

    Example:
        ```python
        from servicenow_mcp.server import create_servicenow_mcp

        # Create an MCP server for ServiceNow
        mcp = create_servicenow_mcp(
            instance_url="https://instance.service-now.com",
            username="admin",
            password="password"
        )

        # Start the server
        mcp.start()
        ```
    """

    # Create basic auth config
    auth_config = AuthConfig(
        type=AuthType.BASIC, basic=BasicAuthConfig(username=username, password=password)
    )

    # Create server config
    config = ServerConfig(instance_url=instance_url, auth=auth_config)

    # Create and return server
    return ServiceNowMCP(config)


# Create a standard variable that MCP CLI can recognize
# This will be used when running `mcp install src/servicenow_mcp/server.py`
# The actual configuration will be loaded from environment variables

# Load environment variables
load_dotenv()

# Get configuration from environment variables
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
username = os.getenv("SERVICENOW_USERNAME")
password = os.getenv("SERVICENOW_PASSWORD")

# Create the server instance with a standard variable name
# This is the variable that MCP CLI will look for
if instance_url and username and password:
    server = create_servicenow_mcp(instance_url=instance_url, username=username, password=password)
else:
    # Create a dummy server with default values for MCP CLI to discover
    # The actual configuration will be loaded from environment variables when run
    server = ServiceNowMCP(
        {
            "instance_url": "https://example.service-now.com",
            "auth": {"type": "basic", "basic": {"username": "admin", "password": "password"}},
        }
    )
