from django.db import models

import math

from player.models import Player
from faction.models import Faction
from yata.handy import *

ATTACK_LOST = ["Lost", "Assist", "Timeout", "Escape"]


class Revive(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    timestamp = models.IntegerField(default=0)
    reviver_id = models.IntegerField(default=0)
    reviver_name = models.CharField(default="reviver_name", max_length=32)
    reviver_faction = models.IntegerField(default=0)
    reviver_factionname = models.CharField(default="reviver_factionname", null=True, blank=True, max_length=64)
    target_id = models.IntegerField(default=0)
    target_name = models.CharField(default="target_name", max_length=32)
    target_faction = models.IntegerField(default=0)
    target_factionname = models.CharField(default="target_factionname", null=True, blank=True, max_length=64)
    target_last_action_status = models.CharField(default="Unkown", null=True, blank=True, max_length=16)
    target_last_action_timestamp = models.IntegerField(default=0)
    target_hospital_reason = models.CharField(default="Unkown", null=True, blank=True, max_length=128)

    paid = models.BooleanField(default=False)


class Attack(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    # API Fields
    tId = models.IntegerField(default=0)
    timestamp_started = models.IntegerField(default=0)
    timestamp_ended = models.IntegerField(default=0)
    attacker_id = models.IntegerField(default=0)
    attacker_name = models.CharField(default="attacker_name", max_length=16, null=True, blank=True)
    attacker_faction = models.IntegerField(default=0)
    attacker_factionname = models.CharField(default="attacker_factionname", max_length=64, null=True, blank=True)
    defender_id = models.IntegerField(default=0)
    defender_name = models.CharField(default="defender_name", max_length=16, null=True, blank=True)
    defender_faction = models.IntegerField(default=0)
    defender_factionname = models.CharField(default="defender_factionname", max_length=64, null=True, blank=True)
    result = models.CharField(default="result", max_length=64)
    stealthed = models.IntegerField(default=0)
    respect_gain = models.FloatField(default=0.0)
    chain = models.IntegerField(default=0)
    code = models.SlugField(default="0", max_length=32)

    # mofifiers
    fairFight = models.FloatField(default=0.0)
    war = models.FloatField(default=1.0)
    retaliation = models.FloatField(default=1.0)
    groupAttack = models.FloatField(default=1.0)
    overseas = models.FloatField(default=1.0)
    chainBonus = models.FloatField(default=1.0)

    # perso fields
    attacker = models.BooleanField(default=False)
    targetId = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    baseRespect = models.FloatField(default=0.0)
    flatRespect = models.FloatField(default=0.0)
    level = models.FloatField(default=0.0)

    def __str__(self):
        return "Attack [{}]: {} [{}] -> {} [{}]".format(self.timestamp_started, self.attacker_name, self.attacker_id, self.defender_name, self.defender_id)


class Target(models.Model):
    # target general info
    target_id = models.IntegerField(default=0)
    name = models.CharField(default="target_name", max_length=16)
    rank = models.CharField(default="rank", max_length=128)
    level = models.IntegerField(default=0)
    age = models.IntegerField(default=0)

    # last update
    update_timestamp = models.IntegerField(default=0)

    # life
    life_current = models.IntegerField(default=0)
    life_maximum = models.IntegerField(default=1)

    # last action (ts)
    last_action_timestamp = models.IntegerField(default=0)
    last_action_relative = models.CharField(default="last_action_relative", max_length=32, null=True, blank=True)
    last_action_status = models.CharField(default="Offline", max_length=16)

    # status
    status_description = models.CharField(default="status_description", max_length=64, null=True, blank=True)
    status_details = models.CharField(default="status_details", max_length=128, null=True, blank=True)
    status_state = models.CharField(default="status_state", max_length=32, null=True, blank=True)
    status_color = models.CharField(default="green", max_length=16, null=True, blank=True)
    status_until = models.IntegerField(default=0)

    # faction
    faction_position = models.CharField(default="faction_position", max_length=16)
    faction_name = models.CharField(default="faction_name", max_length=32)
    faction_faction_id = models.IntegerField(default=0)
    faction_faction_dif = models.IntegerField(default=0)

    # link with faction
    faction = models.ManyToManyField(Faction, blank=True)

    def __str__(self):
        return "{} [{}]".format(self.name, self.target_id)

    def updateFromApi(self, req):
        if 'apiError' in req:
            return True, self

        self.name = req.get("name", "?")
        self.rank = req.get("rank", "?")
        self.level = int(req.get("level", 0))
        self.age = int(req.get("age", 1))

        if req.get("life") is None:
            self.life_current = 0
            self.life_maximum = 1
        else:
            self.life_current = req["life"].get("current", 0)
            self.life_maximum = req["life"].get("maximum", 1)

        if req.get("status") is None:
            self.status_description = "?"
            self.status_details = "?"
            self.status_state = "?"
            self.status_color = "?"
            self.status_until = 0
        else:
            self.status_description = req["status"].get("description", "?")
            self.status_details = req["status"].get("details", "?")
            self.status_state = req["status"].get("state", "?")
            self.status_color = req["status"].get("color", "?")
            self.status_until = req["status"].get("until", 0)

        if req.get("faction") is None:
            self.faction_position = "?"
            self.faction_name = "?"
            self.faction_id = 0
            self.faction_dif = 0
        else:
            self.faction_position = req["faction"].get("position", "?")
            self.faction_name = req["faction"].get("faction_name", "?")
            self.faction_id = req["faction"].get("faction_id", 0)
            self.faction_dif = req["faction"].get("days_in_faction", 0)

        if req.get("last_action") is None:
            self.last_action_timestamp = 0
            self.last_action_relative = "?"
            self.last_action_status = "Offline"
        else:
            self.last_action_timestamp = req["last_action"].get("timestamp", 0)
            self.last_action_relative = req["last_action"].get("relative", "?")
            self.last_action_status = req["last_action"].get("status", "Offline")

        self.update_timestamp = req.get("timestamp", 0)
        self.save()
        return False, self

    def customDescription(self):
        if self.status_state == "Hospital":
            # return "H for {}".format(self.status_until - tsnow())
            return self.status_description.replace("In hospital", "H")
        elif self.status_state == "Jail":
            return self.status_description.replace("In jail", "J")
        else:
            return self.status_description


class TargetInfo(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    # link with target
    target_id = models.IntegerField(default=0)

    # last update (for personnal info, can be different than target.update_timestamp)
    update_timestamp = models.IntegerField(default=0)
    last_attack_timestamp = models.IntegerField(default=0)
    last_attack_attacker = models.BooleanField(default=True)
    fairFight = models.FloatField(default=1.0)
    baseRespect = models.FloatField(default=0)
    flatRespect = models.FloatField(default=0)
    result = models.CharField(default="", max_length=16, null=True, blank=True)
    note = models.CharField(default="", max_length=128, null=True, blank=True)

    def __str__(self):
        return "Target [{}] of {}".format(self.target_id, self.player)

    def getTarget(self, update=False):
        target, _ = Target.objects.get_or_create(target_id=self.target_id)
        if update:
            req = apiCall("user", target.target_id, "profile,timestamp", self.player.getKey())

            # update common part of the target
            error, target = target.updateFromApi(req)
            if error:
                return req, target.target_id, target

            # update player part of the target
            last_attack = self.player.attack_set.filter(targetId=target.target_id, bonus=False).order_by("timestamp_ended").last()

            if last_attack is not None:
                isWar = last_attack.war - 1.0 > 0.001
                attacker = last_attack.attacker_id == self.player.tId
                respect = last_attack.flatRespect > 0.001
                if not isWar and attacker and respect:
                    # if not war, not problem we know FF
                    self.fairFight = last_attack.fairFight
                    self.flatRespect = last_attack.flatRespect
                    self.baseRespect = last_attack.baseRespect

                elif not respect:
                    # we update flat respect to be base respect if unknown
                    self.baseRespect = 0.25 * (math.log(float(target.level)) + 1.0) if target.level else 0.0
                    self.fairFight = max(last_attack.fairFight, self.fairFight)
                    self.flatRespect = self.baseRespect * self.fairFight

                self.last_attack_timestamp = last_attack.timestamp_ended
                self.result = last_attack.result
                self.last_attack_attacker = last_attack.attacker
                self.update_timestamp = target.update_timestamp
                self.save()

            if self.flatRespect < 0.001:
                # we update flat respect to be base respect if unknown
                self.baseRespect = 0.25 * (math.log(float(target.level)) + 1.0) if target.level else 0.0
                self.flatRespect = self.baseRespect * self.fairFight
                self.update_timestamp = target.update_timestamp
                self.save()

        target_dic = {
            # global target information
            "name": target.name,
            "life_current": target.life_current,
            "life_maximum": target.life_maximum,
            "status_description": target.customDescription(),
            "status_details": target.status_details,
            "status_color": target.status_color,
            "status_state": target.status_state,
            "status_until": target.status_until,
            "level": target.level,
            "last_action_relative": target.last_action_relative,
            "last_action_timestamp": target.last_action_timestamp,
            "last_action_status": target.last_action_status,
            "update_timestamp": min(target.update_timestamp, tsnow()),

            # player target information
            "last_attack_attacker": self.last_attack_attacker,
            "last_attack_timestamp": self.last_attack_timestamp,
            "note": self.note,
            "result": self.result,
            "fairFight": self.fairFight,
            "flatRespect": self.flatRespect,
            "baseRespect": self.baseRespect,

            # additional fields for rendering
            "win": 0 if self.result in ATTACK_LOST else 1,
            }

        return False, target.target_id, target_dic
