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

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

import json
import os

from faction.models import *
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):

        factions = Faction.objects.all()
        for i, faction in enumerate(factions):
            newss = faction.news_set.filter(member="?")
            for j, news in enumerate(newss):
                print("{} ({:04d}/{:04d}): {:05d}/{:05d} {}".format(faction, i + 1, len(factions), j + 1, len(newss), news.setMember()))
