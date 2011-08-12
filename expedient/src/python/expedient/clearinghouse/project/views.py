'''
@author: jnaous
'''

from django.views.generic import list_detail, create_update, simple
from models import Project
from forms import ProjectCreateForm
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.aggregate.models import Aggregate
import logging
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage
from django.db.models import Q
from expedient.common.permissions.decorators import require_objs_permissions_for_view
from expedient.common.permissions.utils import get_queryset, get_user_from_req,\
    get_queryset_from_class
from expedient.clearinghouse.roles.models import ProjectRole,\
    ProjectRoleRequest
from expedient.common.permissions.models import ObjectPermission,\
    PermissionOwnership, Permittee
from expedient.clearinghouse.project.forms import AddMemberForm, MemberForm
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import uuid   
 
logger = logging.getLogger("project.views")

TEMPLATE_PATH = "project"

DEFAULT_OWNER_PERMISSIONS = [
    "can_edit_project", "can_delete_project", "can_view_project",
    "can_add_members", "can_remove_members",
    "can_create_slices", "can_edit_slices", "can_delete_slices",
    "can_start_slices", "can_stop_slices",
    "can_add_aggregates", "can_remove_aggregates",
    "can_create_roles", "can_edit_roles",
]

DEFAULT_RESEARCHER_PERMISSIONS = [
    "can_view_project",
    "can_create_slices", "can_edit_slices", "can_delete_slices",
    "can_start_slices", "can_stop_slices",
]

def list(request):
    '''Show list of projects'''
    
    qs = Project.objects.get_for_user(request.user)
    
    return list_detail.object_list(
        request,
        queryset=qs,
        template_name=TEMPLATE_PATH+"/list.html",
        template_object_name="project",
    )

@require_objs_permissions_for_view(
    perm_names=["can_delete_slices"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
    methods=["GET", "POST"],
)
@require_objs_permissions_for_view(
    perm_names=["can_delete_project"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
    methods=["GET", "POST"],
)
def delete(request, proj_id):
    '''Delete the project'''
    project = get_object_or_404(Project, id=proj_id)
    if request.method == "POST":
        try:
            for s in project.slice_set.all():
                s.stop(request.user)
            project.delete()
            DatedMessage.objects.post_message_to_user(
                "Successfully deleted project %s" % project.name,
               request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        except Exception as e:
            print "LEODEBUG ERROR EN EL VIEW"
            print e
            DatedMessage.objects.post_message_to_user(
            "Problems ocurred while trying to delete project %s: %s" % (project.name,str(e)),
            request.user, msg_type=DatedMessage.TYPE_ERROR)
        return HttpResponseRedirect(reverse("home"))
    else:
        return simple.direct_to_template(
            request,
            template=TEMPLATE_PATH+"/confirm_delete.html",
            extra_context={"object": project},
        )

@require_objs_permissions_for_view(
    perm_names=["can_view_project"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def detail(request, proj_id):
    '''Show information about the project'''
    project = get_object_or_404(Project, id=proj_id)
    role_reqs = ProjectRoleRequest.objects.filter(
        giver=request.user, requested_role__project=project)
    return list_detail.object_detail(
        request,
        Project.objects.all(),
        object_id=proj_id,
        template_name=TEMPLATE_PATH+"/detail.html",
        template_object_name="project",
        extra_context={
            "role_requests": role_reqs,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
            )
        }
    )

def create_project_roles(project, user):
    """Create the default roles in a project."""
    owner_role = ProjectRole.objects.create(
        name="owner",
        description=\
            "The 'owner' role is a special role that has permission to "
            "do everything "
            "in the project and can give the permissions to everyone. "
            "In addition every time a slice is created, users with "
            "the 'owner' role get full permissions over those.",
        project=project,
    )
    for permission in DEFAULT_OWNER_PERMISSIONS:
        obj_perm = ObjectPermission.objects.\
            get_or_create_for_object_or_class(
                permission, project)[0]
        owner_role.obj_permissions.add(obj_perm)
        
    researcher_role = ProjectRole.objects.create(
        name="researcher",
        description=\
            "By default users with the 'researcher' role can only "
            "create slices and "
            "delete slices they created. They have full permissions over "
            "their created slices.",
            project=project,
    )
    for permission in DEFAULT_RESEARCHER_PERMISSIONS:
        obj_perm = ObjectPermission.objects.\
            get_or_create_for_object_or_class(
                permission, project)[0]
        researcher_role.obj_permissions.add(obj_perm)
    
    # give the creator of the project an owner role
    owner_role.give_to_permittee(
        user,
        can_delegate=True,
    )

@require_objs_permissions_for_view(
    perm_names=["can_create_project"],
    permittee_func=get_user_from_req,
    target_func=get_queryset_from_class(Project),
)
def create(request):
    '''Create a new project'''
   
    def post_save(instance, created):
        # Create default roles in the project
	#Generate UUID: fixes caching problem on model default value
	instance.uuid = uuid.uuid4()
	instance.save()
        create_project_roles(instance, request.user)
        
    def redirect(instance):
        return reverse("project_detail", args=[instance.id])
    
    try:
        return generic_crud(
            request, None,
            model=Project,
            form_class=ProjectCreateForm,
            template=TEMPLATE_PATH+"/create_update.html",
            post_save=post_save,
            redirect=redirect,
            template_object_name="project",
            extra_context={
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Create Project", request.path),
                ),
            },
            success_msg = lambda instance: "Successfully created project %s." % instance.name,
        )
    except Exception as e:
        DatedMessage.objects.post_message_to_user(
            "Project may have been created, but some problem ocurred: %s" % str(e),
            request.user, msg_type=DatedMessage.TYPE_ERROR)
        return HttpResponseRedirect(reverse("home"))


 
@require_objs_permissions_for_view(
    perm_names=["can_view_project"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
@require_objs_permissions_for_view(
    perm_names=["can_edit_project"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
    methods=["POST"],
)
def update(request, proj_id, iframe=False):
    '''Update information about a project'''
    
    project = get_object_or_404(Project, id=proj_id)
    
    def redirect(instance):
        if iframe:
            return reverse("project_list")
        else:
            return reverse("project_detail", args=[instance.id])
    
    return generic_crud(
        request, proj_id,
        model=Project,
        form_class=ProjectCreateForm,
        template=TEMPLATE_PATH+"/create_update.html",
        redirect=redirect,
        template_object_name="project",
        extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
                ("Update Info", request.path),
            ),
        },
        success_msg = lambda instance: "Successfully updated project %s." % instance.name,
    )

@require_objs_permissions_for_view(
    perm_names=["can_add_aggregates"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def add_aggregate(request, proj_id):
    '''Add/remove aggregates to/from a project'''
    
    project = get_object_or_404(Project, id=proj_id)
    aggregate_list = Aggregate.objects.exclude(
        id__in=project.aggregates.all().values_list("id", flat=True))
    
    if request.method == "GET":
        return simple.direct_to_template(
            request, template=TEMPLATE_PATH+"/add_aggregates.html",
            extra_context={
                "aggregate_list": aggregate_list,
                "project": project,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
                    ("Add Project Aggregates", request.path),
                ),
            }
        )
    
    elif request.method == "POST":
        # check which submit button was pressed
        try:
            agg_id = int(request.POST.get("id", 0))
        except ValueError:
            raise Http404

        if agg_id not in aggregate_list.values_list("id", flat=True):
            raise Http404

        aggregate = get_object_or_404(Aggregate, id=agg_id).as_leaf_class()
        return HttpResponseRedirect(aggregate.add_to_project(
            project, reverse("project_add_agg", args=[proj_id])))
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
@require_objs_permissions_for_view(
    perm_names=["can_add_aggregates"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def update_aggregate(request, proj_id, agg_id):
    '''Update any info stored at the aggregate'''
    project = get_object_or_404(Project, id=proj_id)
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=project.aggregates.values_list(
            "id", flat=True)).as_leaf_class()

    if request.method == "POST":
        return HttpResponseRedirect(aggregate.add_to_project(
            project, reverse("project_detail", args=[proj_id])))
    else:
        return HttpResponseNotAllowed(["POST"])

@require_objs_permissions_for_view(
    perm_names=["can_remove_aggregates"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def remove_aggregate(request, proj_id, agg_id):
    """Remove the aggregate from the project"""
    project = get_object_or_404(Project, id=proj_id)
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=project.aggregates.values_list(
            "id", flat=True)).as_leaf_class()

    if request.method == "POST":
        return HttpResponseRedirect(aggregate.remove_from_project(
            project, reverse("project_detail", args=[proj_id])))
    else:
        return HttpResponseNotAllowed(["POST"])

@require_objs_permissions_for_view(
    perm_names=["can_add_members"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def add_member(request, proj_id):
    """Add a member to the project"""
    
    project = get_object_or_404(Project, id=proj_id)
    
    if request.method == "POST":
        form = AddMemberForm(project=project, giver=request.user, data=request.POST)
        if form.is_valid():
            form.save()
	    #Sync LDAP
	    project.save()
            return HttpResponseRedirect(reverse("project_detail", args=[proj_id]))

    else:
        form = AddMemberForm(project=project, giver=request.user)
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/add_member.html",
        extra_context={
            "form": form,
            "project": project,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
                ("Add Member", request.path),
            ),
        },
    )
    
@require_objs_permissions_for_view(
    perm_names=["can_add_members"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def update_member(request, proj_id, user_id):
    """Update a member's roles"""
    
    project = get_object_or_404(Project, id=proj_id)
    member = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = MemberForm(
            project=project, user=member,
            giver=request.user, data=request.POST)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("project_detail", args=[proj_id]))

    else:
        form = MemberForm(
            project=project, user=member,
            giver=request.user)
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/update_member.html",
        extra_context={
            "form": form,
            "project": project,
            "member": member,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
                ("Update Member %s" % member.username, request.path),
            ),
        },
    )
    
@require_objs_permissions_for_view(
    perm_names=["can_remove_members"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(Project, "proj_id"),
)
def remove_member(request, proj_id, user_id):
    """Kick a member out by stripping his roles"""
    
    project = get_object_or_404(Project, id=proj_id)
    member = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        member = Permittee.objects.get_as_permittee(member)
        # Remove the roles
        for role in ProjectRole.objects.filter(project=project):
            role.remove_from_permittee(member)
        # Remove other permissions
        PermissionOwnership.objects.delete_all_for_target(project, member)
	#Sync LDAP
    	project.save()

        return HttpResponseRedirect(
            reverse("project_detail", args=[proj_id]))
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/remove_member.html",
        extra_context={
            "project": project,
            "member": member,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
                ("Remove Member %s" % member.username, request.path),
            ),
        },
    )
