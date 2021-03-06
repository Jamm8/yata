"""
Copyright 2019 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from django.utils import timezone

import random
import string


HISTORY_TIMES = {
    "one_day": 86400,
    "one_week": 604800,
    "two_weeks": 1209600,
    "one_month": 2678400,
    "two_months": 5356800,
    "three_months": 8035200,
    "six_months": 16070400,
    "one_year": 32140800,
    "two_years": 64281600,
}


def histTime(key):
    return " ".join([k for k in key.split("_")])


def tsnow():
    return int(timezone.now().timestamp())


def apiCall(section, id, selections, key, sub=None, verbose=True):
    import requests

    key = str(key)

    # DEBUG live chain
    # if selections in ["chain", "chain,timestamp"] and section == "faction":
    #     from django.utils import timezone
    #     print("[yata.function.apiCall] DEBUG chain/faction")
    #     chain = dict({"timestamp": int(timezone.now().timestamp())-4,
    #                   "chain": {"current": 76,
    #                             "timeout": 8,
    #                             "max": 100,
    #                             "modifier": 0.75,
    #                             "cooldown": 0,
    #                             "start": 1555211268
    #                             }})
    #     if sub is None:
    #         return chain
    #     else:
    #         return chain.get(sub)

    # DEBUG API error
    # return dict({"apiError": "API error code 42: debug error."})

    try:
        url = "https://api.torn.com/{}/{}?selections={}&key={}".format(section, id, selections, key)
        if verbose:
            print("[yata.function.apiCall] {}".format(url.replace("&key=" + key, "")))
        # print("[yata.function.apiCall] {}".format(url))
        r = requests.get(url)
        r.raise_for_status()

        rjson = r.json()

        if "error" in rjson:  # standard api error
            err = rjson
        else:
            if sub is not None:
                if sub in rjson:
                    return rjson[sub]
                else:  # key not found
                    err = dict({"error": {"code": "", "error": "key not found... something went wrong..."}})
            else:
                return rjson

    except requests.exceptions.HTTPError as e:
        print("[yata.function.apiCall] API HTTPError {}".format(e))
        err = dict({"error": {"code": r.status_code, "error": "{} #blameched".format(r.reason)}})

    return dict({"apiError": "API error code {}: {}.".format(err["error"]["code"], err["error"]["error"]),
                 "apiErrorString": err["error"]["error"],
                 "apiErrorCode": int(err["error"]["code"])})


def timestampToDate(timestamp, fmt=False):
    import datetime
    import pytz
    d = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    if fmt is False:
        return d
    elif type(fmt) == bool and fmt:
        return d.strftime("%Y/%m/%d %H:%M TCT")
    else:
        return d.strftime(fmt)


def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def returnError(type=500, msg=None, home=True):
    import traceback
    from django.utils import timezone
    from django.http import HttpResponseServerError
    from django.http import HttpResponseForbidden
    from django.http import HttpResponseNotFound
    from django.template.loader import render_to_string

    if type == 403:
        msg = "Permission Denied" if msg is None else msg
        return HttpResponseForbidden(render_to_string('403.html', {'exception': msg, 'home': home}))
    if type == 404:
        msg = "Not Found" if msg is None else msg
        return HttpResponseNotFound(render_to_string('404.html', {'exception': msg, 'home': home}))
    else:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip(), 'home': home}))


def getPlayer(tId):
    from player.models import Player

    player, _ = Player.objects.get_or_create(tId=tId)
    player.lastActionTS = tsnow()
    player.active = True
    player.save()
    return player


def randomSlug(length=32):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
