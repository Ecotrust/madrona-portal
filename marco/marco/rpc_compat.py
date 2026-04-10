"""JSON-RPC 2.0 compatibility shim — POST /rpc/

Accepts JSON-RPC 2.0 requests from the legacy jsonrpc.js frontend and
dispatches them to the same business logic as the new DRF REST API views.

This shim allows the frontend JavaScript to keep using $.jsonrpc() without
modification while the backend has moved to REST endpoints at /api/.

rpc4django required @csrf_exempt on the /rpc/ view; this shim preserves
that behaviour so the JS can send application/json without a CSRF token.
"""
from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 response helpers
# ---------------------------------------------------------------------------

def _ok(result: Any, rpc_id: Any) -> JsonResponse:
    return JsonResponse({'jsonrpc': '2.0', 'id': rpc_id, 'result': result})


def _err(message: str, rpc_id: Any, code: int = -32000) -> JsonResponse:
    return JsonResponse({'jsonrpc': '2.0', 'id': rpc_id, 'error': {'code': code, 'message': message}})


# ---------------------------------------------------------------------------
# Bookmark handlers
# ---------------------------------------------------------------------------

def _get_bookmarks(request: Any) -> list:
    from visualize.models import Bookmark

    content: list[dict] = []
    bookmark_list = Bookmark.objects.filter(user=request.user)

    for bookmark in bookmark_list:
        sharing_groups = [
            g.mapgroup_set.get().name for g in bookmark.sharing_groups.all()
        ]
        content.append({
            'uid': bookmark.uid,
            'name': bookmark.name,
            'description': bookmark.description,
            'hash': bookmark.url_hash,
            'sharing_groups': sharing_groups,
            'json': bookmark.json,
        })

    shared_bookmarks = Bookmark.objects.shared_with_user(request.user)
    for bookmark in shared_bookmarks:
        if bookmark not in bookmark_list:
            groups = bookmark.sharing_groups.filter(user__in=[request.user])
            shared_groups = [g.mapgroup_set.get().name for g in groups]
            content.append({
                'uid': bookmark.uid,
                'name': bookmark.name,
                'description': bookmark.description,
                'hash': bookmark.url_hash,
                'shared': True,
                'shared_by_user': bookmark.user.id,
                'shared_to_groups': shared_groups,
                'shared_by_name': bookmark.user.get_short_name(),
                'json': bookmark.json,
            })

    return content


def _add_bookmark(request: Any, params: list) -> bool:
    from visualize.models import Bookmark

    name, description, url_hash, json_str = params[0], params[1], params[2], params[3]
    bookmark = Bookmark(
        user=request.user,
        name=name,
        description=description,
        url_hash=url_hash,
        json=json_str,
    )
    bookmark.save()
    return True


def _load_bookmark(params: list) -> list:
    from visualize.models import Bookmark

    bookmark = Bookmark.objects.get(pk=int(params[0]))
    return [{'uid': bookmark.uid, 'hash': bookmark.url_hash, 'json': bookmark.json}]


def _remove_bookmark(request: Any, params: list) -> bool:
    from features.registry import get_feature_by_uid

    bookmark = get_feature_by_uid(params[0])
    viewable, _ = bookmark.is_viewable(request.user)
    if viewable:
        bookmark.delete()
    return True


def _share_bookmark(request: Any, params: list) -> bool:
    from features.registry import get_feature_by_uid

    uid, group_names = params[0], params[1]
    bookmark = get_feature_by_uid(uid)
    viewable, _ = bookmark.is_viewable(request.user)
    if not viewable:
        return False
    bookmark.share_with(None)
    groups = [Group.objects.get(mapgroup__name=gname) for gname in group_names]
    bookmark.share_with(groups, append=False)
    return True


# ---------------------------------------------------------------------------
# User Layer handlers
# ---------------------------------------------------------------------------

def _get_user_layers(request: Any) -> list:
    from visualize.models import UserLayer

    content: list[dict] = []

    try:
        user_layer_list = UserLayer.objects.filter(user=request.user)
    except TypeError:
        user_layer_list = []

    for ul in user_layer_list:
        sharing_groups = [
            g.mapgroup_set.get().name
            for g in ul.sharing_groups.all()
            if g.mapgroup_set.exists()
        ]
        public_groups = [
            g.name
            for g in Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
            if g in ul.sharing_groups.all()
        ]
        content.append({
            'id': ul.id,
            'uid': ul.uid,
            'name': ul.name,
            'description': ul.description,
            'url': ul.url,
            'layer_type': ul.layer_type,
            'password_protected': ul.password_protected,
            'arcgis_layers': ul.arcgis_layers,
            'sharing_groups': sharing_groups + public_groups,
            'shared_to_groups': sharing_groups,
            'owned_by_user': True,
            'wms_slug': ul.wms_slug,
            'wms_srs': ul.wms_srs,
            'wms_params': ul.wms_params,
            'wms_version': ul.wms_version,
            'wms_format': ul.wms_format,
            'wms_styles': ul.wms_styles,
        })

    try:
        shared_layers = UserLayer.objects.shared_with_user(request.user)
    except TypeError:
        shared_layers = UserLayer.objects.filter(pk=-1)

    for ul in shared_layers:
        if ul not in user_layer_list:
            try:
                permission_groups = [
                    x.map_group.permission_group
                    for x in request.user.mapgroupmember_set.all()
                ]
            except TypeError:
                permission_groups = []

            sharing_groups = [
                g.mapgroup_set.get().name
                for g in ul.sharing_groups.all()
                if g.mapgroup_set.exists() and g in permission_groups
            ]
            public_groups = [
                g.name
                for g in Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
                if g in ul.sharing_groups.all()
            ]
            content.append({
                'id': ul.id,
                'uid': ul.uid,
                'name': ul.name,
                'description': ul.description,
                'url': ul.url,
                'layer_type': ul.layer_type,
                'password_protected': ul.password_protected,
                'arcgis_layers': ul.arcgis_layers,
                'shared': True,
                'shared_by_user': ul.user.id,
                'sharing_groups': sharing_groups + public_groups,
                'shared_to_groups': sharing_groups,
                'shared_by_name': ul.user.get_short_name(),
                'owned_by_user': len(sharing_groups) > 0,
                'wms_slug': ul.wms_slug,
                'wms_srs': ul.wms_srs,
                'wms_params': ul.wms_params,
                'wms_version': ul.wms_version,
                'wms_format': ul.wms_format,
                'wms_styles': ul.wms_styles,
            })

    return content


def _add_user_layer(request: Any, params: list) -> bool:
    from visualize.models import UserLayer

    (name, description, layer_type, url, arcgis_layers,
     wms_slug, wms_srs, wms_params, wms_version, wms_format, wms_styles) = params

    ul = UserLayer(
        user=request.user,
        name=name,
        description=description or '',
        url=url,
        layer_type=layer_type,
        arcgis_layers=arcgis_layers or '',
        wms_slug=wms_slug,
        wms_srs=wms_srs,
        wms_params=wms_params,
        wms_version=wms_version,
        wms_format=wms_format,
        wms_styles=wms_styles,
    )
    ul.save()
    return True


def _remove_user_layer(request: Any, params: list) -> bool:
    from features.registry import get_feature_by_uid

    ul = get_feature_by_uid(params[0])
    viewable, _ = ul.is_viewable(request.user)
    if viewable:
        ul.delete()
    return True


def _share_user_layer(request: Any, params: list) -> bool:
    from features.registry import get_feature_by_uid

    uid, group_names = params[0], params[1]
    ul = get_feature_by_uid(uid)
    viewable, _ = ul.is_viewable(request.user)
    if not viewable:
        return False
    ul.share_with(None)
    groups = [Group.objects.get(mapgroup__name=gname) for gname in group_names]
    ul.share_with(groups, append=False)
    return True


# ---------------------------------------------------------------------------
# Sharing Groups handler
# ---------------------------------------------------------------------------

def _get_sharing_groups(request: Any) -> list:
    data: list[dict] = []

    for membership in request.user.mapgroupmember_set.all():
        group = membership.map_group
        members = sorted(
            member.user_name_for_group()
            for member in group.mapgroupmember_set.all()
        )
        data.append({
            'group_name': group.name,
            'group_slug': group.permission_group.name,
            'members': members,
            'is_mapgroup': True,
        })

    for public_group in Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS):
        data.append({
            'group_name': public_group.name,
            'group_slug': public_group.name,
            'members': [],
            'is_mapgroup': False,
        })

    return data


# ---------------------------------------------------------------------------
# Drawing handler
# ---------------------------------------------------------------------------

def _delete_drawing(request: Any, params: list) -> bool:
    from features.registry import get_feature_by_uid

    drawing = get_feature_by_uid(params[0])
    viewable, _ = drawing.is_viewable(request.user)
    if viewable:
        drawing.delete()
    return True


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_AUTH_REQUIRED = frozenset({
    'get_bookmarks', 'add_bookmark', 'remove_bookmark', 'share_bookmark',
    'add_user_layer', 'remove_user_layer', 'share_user_layer',
    'get_sharing_groups', 'delete_drawing',
})


def _dispatch(request: Any, method: str, params: list, rpc_id: Any) -> JsonResponse:
    if method in _AUTH_REQUIRED and not request.user.is_authenticated:
        return _err('Authentication required.', rpc_id, code=-32001)

    try:
        if method == 'get_bookmarks':
            return _ok(_get_bookmarks(request), rpc_id)
        elif method == 'add_bookmark':
            return _ok(_add_bookmark(request, params), rpc_id)
        elif method == 'load_bookmark':
            return _ok(_load_bookmark(params), rpc_id)
        elif method == 'remove_bookmark':
            return _ok(_remove_bookmark(request, params), rpc_id)
        elif method == 'share_bookmark':
            return _ok(_share_bookmark(request, params), rpc_id)
        elif method == 'get_user_layers':
            return _ok(_get_user_layers(request), rpc_id)
        elif method == 'add_user_layer':
            return _ok(_add_user_layer(request, params), rpc_id)
        elif method == 'remove_user_layer':
            return _ok(_remove_user_layer(request, params), rpc_id)
        elif method == 'share_user_layer':
            return _ok(_share_user_layer(request, params), rpc_id)
        elif method == 'get_sharing_groups':
            return _ok(_get_sharing_groups(request), rpc_id)
        elif method == 'delete_drawing':
            return _ok(_delete_drawing(request, params), rpc_id)
        else:
            return _err(f'Method not found: {method}', rpc_id, code=-32601)
    except Exception as exc:
        return _err(str(exc), rpc_id)


@csrf_exempt
@require_POST
def rpc_view(request):
    """JSON-RPC 2.0 endpoint — POST /rpc/

    Accepts legacy jsonrpc.js requests and dispatches them to the same
    business logic as the REST API views at /api/.
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _err('Parse error.', None, code=-32700)

    method = body.get('method', '')
    params = body.get('params', [])
    rpc_id = body.get('id', 7)

    return _dispatch(request, method, params, rpc_id)
