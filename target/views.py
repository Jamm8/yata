from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.utils import timezone

import json
import math

from yata.handy import apiCall
from player.models import Player
from chain.functions import BONUS_HITS
from target.functions import updateAttacks


def index(request):
    if request.session.get('player'):
        print('[view.awards.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()

        error = updateAttacks(player)

        targets = json.loads(player.targetJson).get("targets", dict({}))
        context = {"player": player, "targetcat": True, "targets": targets, "view": {"targets": True}}
        if error:
            context.update(error)
        return render(request, 'target.html', context)

    else:
        raise PermissionDenied("You might want to log in.")


def attacks(request):
    if request.session.get('player'):
        print('[view.awards.attacks] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        targetJson = json.loads(player.targetJson)
        attacks = targetJson.get("attacks") if "attacks" in targetJson else dict({})
        targets = targetJson.get("targets") if "targets" in targetJson else dict({})

        error = updateAttacks(player)

        context = {"player": player, "targetcat": True, "attacks": attacks, "targets": targets, "view": {"attacks": True}}
        if error:
            context.update(error)

        page = 'target/content-reload.html' if request.method == "POST" else 'target.html'
        return render(request, page, context)

    else:
        raise PermissionDenied("You might want to log in.")


def targets(request):
    if request.session.get('player'):
        print('[view.awards.attacks] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        targetJson = json.loads(player.targetJson)
        targets = targetJson.get("targets") if "targets" in targetJson else dict({})

        context = {"player": player, "targetcat": True, "targets": targets, "view": {"targets": True}}
        page = 'target/content-reload.html' if request.method == "POST" else 'target.html'
        return render(request, page, context)

    else:
        raise PermissionDenied("You might want to log in.")


def toggleTarget(request, targetId):
    if request.session.get('player') and request.method == "POST":
        print('[view.target.toggleTarget] get player id from session and check POST')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        targetJson = json.loads(player.targetJson)
        attacks = targetJson.get("attacks") if "attacks" in targetJson else dict({})
        targets = targetJson.get("targets") if "targets" in targetJson else dict({})

        # call for target info
        targetInfo = apiCall('user', targetId, '', key)
        if 'apiError' in targetInfo:
            level = "?"
            lifeMax = 1
            life = 0
            status = "?"
            statusFull = "?"
            lastAction = "?"
            lastUpdate = 0

        else:
            level = targetInfo["level"]
            lifeMax = int(targetInfo["life"]["maximum"])
            life = int(targetInfo["life"]["current"])
            status = targetInfo["status"][0].replace("In hospital", "Hosp")
            statusFull = " ".join(targetInfo["status"])
            lastAction = targetInfo["last_action"]["relative"]
            lastUpdate = int(timezone.now().timestamp())

        if targetId not in targets:
            print('[view.target.toggleTarget] create target {}'.format(targetId))
            for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
                if int(v["defender_id"]) == int(targetId):
                    respect = float(v['modifiers']['fairFight']) * 0.25 * (math.log(level) + 1) if level else 0
                    targets[targetId] = {"targetName": v["defender_name"],
                                         "result": v["result"],
                                         "endTS": int(v["timestamp_ended"]),
                                         "fairFight": float(v['modifiers']['fairFight']),
                                         "respect": respect,
                                         "level": level,
                                         "lifeMax": lifeMax,
                                         "life": life,
                                         "status": status,
                                         "statusFull": statusFull,
                                         "lastAction": lastAction,
                                         "lastUpdate": lastUpdate,
                                         "note": ""
                                         }
                    break
        else:
            print('[view.target.toggleTarget] delete target {}'.format(targetId))
            del targets[targetId]

        targetJson["targets"] = targets
        player.targetJson = json.dumps(targetJson)
        player.save()

        targets = targetJson.get("targets") if "targets" in targetJson else dict({})

        context = {"target": {"defender_id": targetId}, "targets": targets}
        return render(request, 'target/attacks-buttons.html', context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def refresh(request, targetId):
    if request.session.get('player') and request.method == "POST":
        print('[view.target.refresh] get player id from session and check POST')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        targetJson = json.loads(player.targetJson)
        attacks = targetJson.get("attacks") if "attacks" in targetJson else dict({})
        targets = targetJson.get("targets") if "targets" in targetJson else dict({})

        # call for target info
        error = False
        targetInfo = apiCall('user', targetId, '', key)
        if 'apiError' in targetInfo:
            error = targetInfo

        else:
            # get latest attack to target id
            target = targets.get(targetId)
            target["life"] = int(targetInfo["life"]["current"])
            target["lifeMax"] = int(targetInfo["life"]["maximum"])
            target["status"] = targetInfo["status"][0].replace("In hospital", "Hosp")
            target["statusFull"] = " ".join(targetInfo["status"])
            target["lastAction"] = targetInfo["last_action"]["relative"]
            target["lastUpdate"] = int(timezone.now().timestamp())
            level = targetInfo["level"]
            target["level"] = level
            target["respect"] = 0.25 * (math.log(level) + 1) if level else 0
            for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
                if int(v["defender_id"]) == int(targetId) and int(v["chain"]) not in BONUS_HITS:
                    print('[view.target.refresh] refresh traget last attack info')
                    target["targetName"] = v["defender_name"]
                    target["result"] = v["result"]
                    target["endTS"] = int(v["timestamp_ended"])
                    target["fairFight"] = float(v['modifiers']['fairFight'])
                    target["respect"] = float(v['modifiers']['fairFight']) * target["respect"]

                    break

            targetJson["targets"][targetId] = target
            player.targetJson = json.dumps(targetJson)
            player.save()

        if error:
            context = {"apiErrorLine": error["apiError"]}
        else:
            context = {"targetId": targetId, "target": target}
        return render(request, 'target/targets-line.html', context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def updateNote(request):
    if request.session.get('player') and request.method == "POST":
        print('[view.target.updateNote] get player id from session and check POST')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        targetId = request.POST.get("targetId")
        note = request.POST.get("note")
        print('[view.target.updateNote] {}: {}'.format(targetId, note))

        targetJson = json.loads(player.targetJson)
        targetJson["targets"][targetId]["note"] = note
        player.targetJson = json.dumps(targetJson)
        player.save()

        context = {"target": {"note": note}, "targetId": targetId}
        return render(request, 'target/targets-line-note.html', context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def delete(request, targetId):
    if request.session.get('player') and request.method == "POST":
        print('[view.target.delete] get player id from session and check POST')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        targetJson = json.loads(player.targetJson)

        del targetJson["targets"][targetId]
        player.targetJson = json.dumps(targetJson)
        player.save()

        return render(request, 'target/targets-line.html')

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def add(request):
    if request.session.get('player') and request.method == "POST":
        print('[view.target.add] get player id from session and check POST')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        targetJson = json.loads(player.targetJson)

        targetId = request.POST.get("targetId")
        print('[view.target.add] target id {}'.format(targetId))

        # call for target info
        error = False
        targetInfo = apiCall('user', targetId, '', key)
        if 'apiError' in targetInfo:
            error = targetInfo

        else:
            attacks = targetJson.get("attacks") if "attacks" in targetJson else dict({})
            targets = targetJson.get("targets") if "targets" in targetJson else dict({})

            if targetId not in targets:
                added = False
                for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
                    if v["defender_id"] == targetId:
                        print('[view.target.add] create target {} from attacks'.format(targetId))
                        level = targetInfo["level"]
                        respect = float(v['modifiers']['fairFight']) * 0.25 * (math.log(level) + 1) if level else 0
                        targets[targetId] = {"targetName": targetInfo["name"],
                                             "result": v["result"],
                                             "endTS": int(v["timestamp_ended"]),
                                             "fairFight": float(v['modifiers']['fairFight']),
                                             "respect": respect,
                                             "level": level,
                                             "lifeMax": int(targetInfo["life"]["maximum"]),
                                             "life": int(targetInfo["life"]["current"]),
                                             "status": targetInfo["status"][0].replace("In hospital", "Hosp"),
                                             "statusFull": " ".join(targetInfo["status"]),
                                             "lastAction": targetInfo["last_action"]["relative"],
                                             "lastUpdate": int(timezone.now().timestamp()),
                                             "note": ""
                                             }
                        added = True
                        break

                if not added:
                    print('[view.target.add] create target {} from nothing'.format(targetId))
                    level = targetInfo["level"]
                    respect = float(v['modifiers']['fairFight']) * 0.25 * (math.log(level) + 1) if level else 0

                    targets[targetId] = {"targetName": targetInfo["name"],
                                         "result": "No recent attack",
                                         "endTS": int(v["timestamp_ended"]),
                                         "fairFight": 1,
                                         "respect": respect,
                                         "level": level,
                                         "lifeMax": int(targetInfo["life"]["maximum"]),
                                         "life": int(targetInfo["life"]["current"]),
                                         "status": targetInfo["status"][0].replace("In hospital", "Hosp"),
                                         "statusFull": " ".join(targetInfo["status"]),
                                         "lastAction": targetInfo["last_action"]["relative"],
                                         "lastUpdate": int(timezone.now().timestamp()),
                                         "note": ""}

                targetJson["targets"] = targets
                player.targetJson = json.dumps(targetJson)
                player.save()
            else:
                print('[view.target.add] target {} already exists'.format(targetId))

        context = {"targets": targetJson["targets"], "view": {"targets": True}}
        if error:
            context.update({"apiErrorAdd": error["apiError"]})
        return render(request, 'target/content-reload.html', context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)