"""Public blueprint"""

from app.model import DynamicData, OrgDetail, OrgDetailBanner, Organization, SectoralGroup, User
from flask import Blueprint, abort, current_app, jsonify, request, send_from_directory
from app.helper.csrf import paranoid_mode

import mongoengine
import os

api_endpoint = Blueprint('public_api', __name__)


@api_endpoint.app_errorhandler(400)
def errorhandler(error):
    return jsonify({"status": error.code, "message": error.description}), error.code


@api_endpoint.after_app_request
def after_request(response):
    return paranoid_mode(response)


@api_endpoint.route('/api/public/sectoral')
def general_sect():
    carrier = []
    sector = SectoralGroup.objects()

    for x in sector:
        payload = {
            "sector_id": str(x.id),
            "sector_name": x.sector_name
        }
        carrier.append(payload)
    return jsonify(carrier)


@api_endpoint.route('/api/public/org')
def general_org():
    query = request.args.get('q')

    if query:
        group_by = request.args.get('group_by')
        display = request.args.get('display')
        sector = request.args.get('sector')
        org = request.args.get('org')

        if group_by == 'sector':
            if sector:
                banner = []
                detail = []
                carrier = []

                sector = SectoralGroup.objects(sector_name__iexact=sector)
                org = Organization.objects(sector_group__in=sector).all()
                org_detail = OrgDetail.objects(org__in=org)
                org_banner = OrgDetailBanner.objects(org_detail__in=org_detail)

                for x in org_banner:
                    banner.append({
                        "id": x.org_public_id,
                        "banner": x.org_banner_name,
                        "url": x.org_banner_url,
                        "path": x.org_banner_path
                    })

                for y in org_detail:
                    detail.append({
                        "id": y.public_id,
                        "phone": y.org_phone,
                        "email": y.org_email,
                        "notif": y.org_notification,
                        "address": y.org_address,
                        "admin": {
                            "username": y.creator.username,
                            "email": y.creator.email,
                            "lvl": y.creator.lvl,
                            "status": y.creator.is_active
                        }
                    })

                for z in org:
                    payload = {
                        "org_id": str(z.id),
                        "org_name": z.org_name,
                        "org_detail": detail,
                        "banner": banner,
                        "sector": {
                            "sector_id": str(z.sector_group.id),
                            "sector_name": z.sector_group.sector_name
                        }
                    }
                    carrier.append(payload)

                carrier.sort(key=lambda k: k['org_name'])
                return jsonify(carrier)

            else:
                banner = []
                detail = []
                carrier = []

                org = Organization.objects().order_by('+org_name')
                org_detail = OrgDetail.objects(org__in=org)
                org_banner = OrgDetailBanner.objects(org_detail__in=org_detail)

                for x in org_banner:
                    banner.append({
                        "id": x.org_public_id,
                        "banner": x.org_banner_name,
                        "url": x.org_banner_url,
                        "path": x.org_banner_path
                    })

                for y in org_detail:
                    detail.append({
                        "id": y.public_id,
                        "phone": y.org_phone,
                        "email": y.org_email,
                        "notif": y.org_notification,
                        "address": y.org_address,
                        "admin": {
                            "username": y.creator.username,
                            "email": y.creator.email,
                            "lvl": y.creator.lvl,
                            "status": y.creator.is_active
                        }
                    })

                for z in org:
                    payload = {
                        "org_id": str(z.id),
                        "org_name": z.org_name,
                        "org_detail": detail,
                        "banner": banner,
                        "sector": {
                            "sector_id": str(z.sector_group.id),
                            "sector_name": z.sector_group.sector_name
                        }
                    }
                    carrier.append(payload)

                carrier.sort(key=lambda k: k['org_name'])
                return jsonify(carrier)

        elif group_by == 'org':
            if org:
                banner = []
                detail = []

                data = Organization.objects(org_name__iexact=org).first()

                org_detail = OrgDetail.objects(org=data)
                org_banner = OrgDetailBanner.objects(org_detail__in=org_detail)

                for x in org_banner:
                    banner.append({
                        "id": x.org_public_id,
                        "banner": x.org_banner_name,
                        "url": x.org_banner_url,
                        "path": x.org_banner_path
                    })

                for y in org_detail:
                    detail.append({
                        "id": y.public_id,
                        "phone": y.org_phone,
                        "email": y.org_email,
                        "notif": y.org_notification,
                        "address": y.org_address,
                        "admin": {
                            "username": y.creator.username,
                            "email": y.creator.email,
                            "lvl": y.creator.lvl,
                            "status": y.creator.is_active
                        }
                    })

                if data:
                    return jsonify({
                        "org_id": str(data.id),
                        "org_name": data.org_name,
                        "org_detail": detail,
                        "banner": banner,
                        "sector": {
                            "sector_id": str(data.sector_group.id),
                            "sector_name": data.sector_group.sector_name
                        }
                    })

                else:
                    return jsonify([])

            else:
                banner = []
                detail = []
                carrier = []

                org = Organization.objects().order_by('+org_name')
                org_detail = OrgDetail.objects(org__in=org)
                org_banner = OrgDetailBanner.objects(org_detail__in=org_detail)

                for x in org_banner:
                    banner.append({
                        "id": x.org_public_id,
                        "banner": x.org_banner_name,
                        "url": x.org_banner_url,
                        "path": x.org_banner_path
                    })

                for y in org_detail:
                    detail.append({
                        "id": y.public_id,
                        "phone": y.org_phone,
                        "email": y.org_email,
                        "notif": y.org_notification,
                        "address": y.org_address,
                        "admin": {
                            "username": y.creator.username,
                            "email": y.creator.email,
                            "lvl": y.creator.lvl,
                            "status": y.creator.is_active
                        }
                    })

                for z in org:
                    payload = {
                        "org_id": str(z.id),
                        "org_name": z.org_name,
                        "org_detail": detail,
                        "banner": banner,
                        "sector": {
                            "sector_id": str(z.sector_group.id),
                            "sector_name": z.sector_group.sector_name
                        }
                    }
                    carrier.append(payload)
                carrier.sort(key=lambda k: k['org_name'], reverse=True)
                return jsonify(carrier)

        else:
            banner = []
            detail = []
            carrier = []

            org = Organization.objects().order_by('+org_name')
            org_detail = OrgDetail.objects(org__in=org)
            org_banner = OrgDetailBanner.objects(org_detail__in=org_detail)

            for x in org_banner:
                banner.append({
                    "id": x.org_public_id,
                    "banner": x.org_banner_name,
                    "url": x.org_banner_url,
                    "path": x.org_banner_path
                })

            for y in org_detail:
                detail.append({
                    "id": y.public_id,
                    "phone": y.org_phone,
                    "email": y.org_email,
                    "notif": y.org_notification,
                    "address": y.org_address,
                    "admin": {
                        "username": y.creator.username,
                        "email": y.creator.email,
                        "lvl": y.creator.lvl,
                        "status": y.creator.is_active
                    }
                })

            for z in org:
                payload = {
                    "org_id": str(z.id),
                    "org_name": z.org_name,
                    "org_detail": detail,
                    "banner": banner,
                    "sector": {
                        "sector_id": str(z.sector_group.id),
                        "sector_name": z.sector_group.sector_name
                    }
                }
                carrier.append(payload)

            carrier.sort(key=lambda k: k['org_name'])
            return jsonify(carrier)

    else:
        banner = []
        detail = []
        carrier = []

        org = Organization.objects().order_by('+org_name')
        org_detail = OrgDetail.objects(org__in=org)
        org_banner = OrgDetailBanner.objects(org_detail__in=org_detail)

        for x in org_banner:
            banner.append({
                "id": x.org_public_id,
                "banner": x.org_banner_name,
                "url": x.org_banner_url,
                "path": x.org_banner_path
            })

        for y in org_detail:
            detail.append({
                "id": y.public_id,
                "phone": y.org_phone,
                "email": y.org_email,
                "notif": y.org_notification,
                "address": y.org_address,
                "admin": {
                    "username": y.creator.username,
                    "email": y.creator.email,
                    "lvl": y.creator.lvl,
                    "status": y.creator.is_active
                }
            })

        for z in org:
            payload = {
                "org_id": str(z.id),
                "org_name": z.org_name,
                "org_detail": detail,
                "banner": banner,
                "sector": {
                    "sector_id": str(z.sector_group.id),
                    "sector_name": z.sector_group.sector_name
                }
            }
            carrier.append(payload)

        carrier.sort(key=lambda k: k['org_name'], reverse=True)
        return jsonify(carrier)


@api_endpoint.route('/api/public/resource')
def general_res():
    query = request.args.get('q')

    if not query:
        limit = request.args.get('l')
        skip = request.args.get('s')

        if skip and limit:
            carrier = []
            table = DynamicData.objects().limit(int(limit)).skip(
                int(skip)).order_by('-created_on')

            for x in table:
                payload = {
                    "table_id": x.public_id,
                    "table_name": x.table_name,
                    "created_on": x.created_on,
                    "table_content": x.table_content,
                    "display": x.display,
                    "table_owner": {
                        "username": x.owner.username,
                        "organization": x.owner.org.org_name,
                        "sector": x.owner.org.sector_group.sector_name
                    }
                }
                carrier.append(payload)

            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif skip and not limit:
            carrier = []
            table = DynamicData.objects().skip(int(skip)).order_by('-created_on')

            for x in table:
                payload = {
                    "table_id": x.public_id,
                    "table_name": x.table_name,
                    "created_on": x.created_on,
                    "table_content": x.table_content,
                    "display": x.display,
                    "table_owner": {
                        "username": x.owner.username,
                        "organization": x.owner.org.org_name,
                        "sector": x.owner.org.sector_group.sector_name
                    }
                }
                carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif not skip and limit:
            carrier = []
            table = DynamicData.objects().limit(int(limit)).order_by('-created_on')

            for x in table:
                payload = {
                    "table_id": x.public_id,
                    "table_name": x.table_name,
                    "created_on": x.created_on,
                    "table_content": x.table_content,
                    "display": x.display,
                    "table_owner": {
                        "username": x.owner.username,
                        "organization": x.owner.org.org_name,
                        "sector": x.owner.org.sector_group.sector_name
                    }
                }
                carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
            carrier = []
            table = DynamicData.objects().order_by('-created_on')

            for x in table:
                payload = {
                    "table_id": x.public_id,
                    "table_name": x.table_name,
                    "created_on": x.created_on,
                    "table_content": x.table_content,
                    "display": x.display,
                    "table_owner": {
                        "username": x.owner.username,
                        "organization": x.owner.org.org_name,
                        "sector": x.owner.org.sector_group.sector_name
                    }
                }
                carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

    elif query:
        group_by = request.args.get('group_by')
        limit = request.args.get('l')
        skip = request.args.get('s')

        if group_by == "sector":
            sector_name = request.args.get('sector')
            display = request.args.get('display')

            if display == 'chart':
                if limit and skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(
                            owner__in=owner, display=display).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(
                            display=display).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

            elif display == 'table':
                if limit and skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(
                            owner__in=owner, display=display).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(
                            display=display).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

            else:
                if limit and skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().limit(int(limit)).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if sector_name:
                        carrier = []
                        sector = SectoralGroup.objects(
                            sector_name__iexact=sector_name)
                        org = Organization.objects(
                            sector_group__in=sector).all()
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(
                            owner__in=owner).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

        elif group_by == 'display':
            display = request.args.get('display_by')

            if limit and skip:
                if display == 'chart':
                    carrier = []
                    data = DynamicData.objects(display=display).limit(
                        int(limit)).skip(int(skip)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                elif display == 'table':
                    carrier = []
                    data = DynamicData.objects(display=display).limit(
                        int(limit)).skip(int(skip)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                else:
                    carrier = []
                    data = DynamicData.objects().limit(int(limit)).skip(
                        int(skip)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

            elif skip and not limit:
                if display == 'chart':
                    carrier = []
                    data = DynamicData.objects(display=display).skip(
                        int(skip)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                elif display == 'table':
                    carrier = []
                    data = DynamicData.objects(display=display).skip(
                        int(skip)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                else:
                    carrier = []
                    data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

            elif not skip and limit:
                if display == 'chart':
                    carrier = []
                    data = DynamicData.objects(display=display).order_by(
                        '-created_on').limit(int(limit))

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                elif display == 'table':
                    carrier = []
                    data = DynamicData.objects(display=display).limit(
                        int(limit)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                else:
                    carrier = []
                    data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

            else:
                if display == 'chart':
                    carrier = []
                    data = DynamicData.objects(display=display)

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                elif display == 'table':
                    carrier = []
                    data = DynamicData.objects(
                        display=display).order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

                else:
                    carrier = []
                    data = DynamicData.objects().order_by('-created_on')

                    for x in data:
                        payload = {
                            "table_id": x.public_id,
                            "table_name": x.table_name,
                            "created_on": x.created_on,
                            "table_content": x.table_content,
                            "display": x.display,
                            "table_owner": {
                                "username": x.owner.username,
                                "organization": x.owner.org.org_name,
                                "sector": x.owner.org.sector_group.sector_name
                            }
                        }
                        carrier.append(payload)
                    carrier.sort(key=lambda k: k['created_on'], reverse=True)
                    return jsonify(carrier)

        elif group_by == 'organization':
            org_name = request.args.get('org')
            display = request.args.get('display')

            if display == 'chart':
                if limit and skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(
                            owner__in=owner, display=display).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(
                            display=display).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

            elif display == 'table':
                if limit and skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(
                            owner__in=owner, display=display).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(
                            display=display).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

            else:
                if limit and skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().limit(int(limit)).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(owner__in=owner).limit(
                            int(limit)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if org_name:
                        carrier = []
                        org = Organization.objects(org_name__iexact=org_name)
                        owner = User.objects(org__in=org).all()
                        data = DynamicData.objects(
                            owner__in=owner).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

        elif group_by == "user":
            username = request.args.get('user')
            display = request.args.get('display')

            if display == 'chart':
                if limit and skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner, display=display).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(
                            owner__in=owner, display=display).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(
                            display=display).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

            elif display == 'table':
                if limit and skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner, display=display).limit(
                            int(limit)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).limit(
                            int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner, display=display).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(display=display).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(
                            owner__in=owner, display=display).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects(
                            display=display).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

            else:
                if limit and skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner).limit(
                            int(limit)).skip(int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().limit(int(limit)).skip(
                            int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif limit and not skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner).limit(
                            int(limit)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                elif not limit and skip:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(owner__in=owner).skip(
                            int(skip)).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                else:
                    if username:
                        carrier = []
                        owner = User.objects(username__iexact=username)
                        data = DynamicData.objects(
                            owner__in=owner).all().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)

                    else:
                        carrier = []
                        data = DynamicData.objects().order_by('-created_on')

                        for x in data:
                            payload = {
                                "table_id": x.public_id,
                                "table_name": x.table_name,
                                "created_on": x.created_on,
                                "table_content": x.table_content,
                                "display": x.display,
                                "table_owner": {
                                    "username": x.owner.username,
                                    "organization": x.owner.org.org_name,
                                    "sector": x.owner.org.sector_group.sector_name
                                }
                            }
                            carrier.append(payload)
                        carrier.sort(
                            key=lambda k: k['created_on'], reverse=True)
                        return jsonify(carrier)


@api_endpoint.route('/api/public/resource/table/<table>')
def table_detail(table):
    try:
        content = DynamicData.objects(public_id__iexact=table).get()
        return jsonify({
            "table_id": content.public_id,
            "table_name": content.table_name,
            "created_on": content.created_on,
            "table_content": content.table_content,
            "display": content.display,
            "table_owner": {
                "username": content.owner.username,
                "organization": content.owner.org.org_name,
                "sector": content.owner.org.sector_group.sector_name
            }
        })

    except mongoengine.errors.DoesNotExist:
        return jsonify([])


@api_endpoint.route('/api/public/resource/file/<filename>')
def file_serve(filename):
    return send_from_directory(current_app.config.get('UPLOAD_FOLDER'), filename)


@api_endpoint.route('/api/public/org/file/<filename>')
def org_file_serve(filename):
    folder = os.path.join(current_app.config.get(
        'UPLOAD_FOLDER'), 'organization/')
    return send_from_directory(folder, filename)


@api_endpoint.route('/api/public/search')
def general_search():
    carrier = []
    query = request.args.get('query')
    table = DynamicData.objects.search_text(
        query).all().order_by('-created_on')
    for x in table:
        payload = {
            "table_id": x.public_id,
            "table_name": x.table_name,
            "created_on": x.created_on,
            "table_content": x.table_content,
            "display": x.display,
            "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
            }
        }
        carrier.append(payload)

    carrier.sort(key=lambda k: k['created_on'], reverse=True)
    return jsonify(carrier)


@api_endpoint.route('/api/public/count/<item>')
def general_count(item):
    if item == 'resource':
        group_by = request.args.get('group_by')

        if group_by == 'display':
            display_by = request.args.get('display_by')

            if display_by == 'chart':
                resource = DynamicData.objects(display=display_by).count()
                return jsonify({"item": resource})

            elif display_by == 'table':
                resource = DynamicData.objects(display=display_by).count()
                return jsonify({"item": resource})

            else:
                resource = DynamicData.objects().count()
                return jsonify({"item": resource})

        elif group_by == 'sector':
            sector = request.args.get('sector')
            display = request.args.get('display')

            if display == 'chart':
                if sector:
                    sector = SectoralGroup.objects(sector_name__iexact=sector)
                    org = Organization.objects(sector_group__in=sector).all()
                    owner = User.objects(org__in=org).all()
                    resource = DynamicData.objects(
                        owner__in=owner, display=display).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects(display=display).count()
                    return jsonify({"item": resource})

            elif display == 'table':
                if sector:
                    sector = SectoralGroup.objects(sector_name__iexact=sector)
                    org = Organization.objects(sector_group__in=sector).all()
                    owner = User.objects(org__in=org).all()
                    resource = DynamicData.objects(
                        owner__in=owner, display=display).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects(display=display).count()
                    return jsonify({"item": resource})

            else:
                if sector:
                    sector = SectoralGroup.objects(sector_name__iexact=sector)
                    org = Organization.objects(sector_group__in=sector).all()
                    owner = User.objects(org__in=org).all()
                    resource = DynamicData.objects(owner__in=owner).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects().count()
                    return jsonify({"item": resource})

        elif group_by == 'organization':
            org_name = request.args.get('org')
            display = request.args.get('display')

            if display == 'chart':
                if org_name:
                    org = Organization.objects(org_name__iexact=org_name)
                    owner = User.objects(org__in=org).all()
                    resource = DynamicData.objects(
                        owner__in=owner, display=display).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects(display=display).count()
                    return jsonify({"item": resource})

            elif display == 'table':
                if org_name:
                    org = Organization.objects(org_name__iexact=org_name)
                    owner = User.objects(org__in=org).all()
                    resource = DynamicData.objects(
                        owner__in=owner, display=display).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects(display=display).count()
                    return jsonify({"item": resource})

            else:
                if org_name:
                    org = Organization.objects(org_name__iexact=org_name)
                    owner = User.objects(org__in=org).all()
                    resource = DynamicData.objects(owner__in=owner).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects().count()
                    return jsonify({"item": resource})

        elif group_by == 'user':
            username = request.args.get('user')
            display = request.args.get('display')

            if display == 'chart':
                if username:
                    owner = User.objects(username__iexact=username)
                    resource = DynamicData.objects(
                        owner__in=owner, display=display).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects(display=display).count()
                    return jsonify({"item": resource})

            elif display == 'table':
                if username:
                    owner = User.objects(username__iexact=username)
                    resource = DynamicData.objects(
                        owner__in=owner, display=display).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects(display=display).count()
                    return jsonify({"item": resource})

            else:
                if username:
                    owner = User.objects(username__iexact=username)
                    resource = DynamicData.objects(owner__in=owner).count()
                    return jsonify({"item": resource})

                else:
                    resource = DynamicData.objects().count()
                    return jsonify({"item": resource})

        else:
            resource = DynamicData.objects().count()
            return jsonify({"item": resource})

    else:
        abort(400, {"CountError": "Missing direction on what to count"})
