# license

import sys
import os
import random
import anki

from aqt.qt import *
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.deckconf import DeckConf
from aqt.forms import dconf
from aqt.utils import tooltip

from anki.sched import Scheduler
from anki.schedv2 import Scheduler

from anki.hooks import addHook, wrap
from . import sortconfig


def setup_ui(self, Dialog):
    self.maxTaken.setMinimum(3)

    grid = QGridLayout()
    self.toggleAddon = QCheckBox("Enable Anki Ultimate")
    # self.toggleAddon.stateChanged.connect(checked)
    grid.addWidget(self.toggleAddon, 0, 0, 1, 1)
    self.verticalLayout_6.insertLayout(4, grid)


def fill_review(self, recursing=False) -> bool:
    "True if a review card can be fetched."
    if self._revQueue:
        return True
    if not self.revCount:
        return False

    anki_ultimate = 1
    if not anki_ultimate:
        return False

    while self._revDids:
        did = self._revDids[0]
        lim = min(self.queueLimit, self._deckRevLimit(did))
        if lim:
            # fill the queue with the current did

            selected: int = 2
            sort_by: str = sortconfig.SORT_OPTIONS.get(selected)[1]

            # working
            self._revQueue = self.col.db.list(
                f"""select id from cards where
                did = {did} and queue = 2 and due <= {self.today}
                order by {sort_by}
                limit {lim}"""
            )

            # THIS ONE WORKS
            # self._revQueue = self.col.db.list(
            #     f"""select id from cards where
            #     did = ? and queue = 2 and due <= ?
            #     order by lapses asc, ivl desc
            #     limit ?""", did, self.today, lim,
            # )

            if self._revQueue:
                # ordering
                if self.col.decks.get(did)["dyn"]:
                    # dynamic decks need due order preserved
                    self._revQueue.reverse()
                else:
                    # random order for regular reviews
                    # r = random.Random()
                    # r.seed(self.today)
                    # r.shuffle(self._revQueue)

                    # CANNOT SORT AFTER DB BECAUSE  self._revQueue
                    # is full of cid not card objects.
                    pass

                # is the current did empty?
                if len(self._revQueue) < lim:
                    self._revDids.pop(0)
                return True
        # nothing left in the deck; move to next
        self._revDids.pop(0)

    # if we didn't get a card but the count is non-zero,
    # we need to check again for any cards that were
    # removed from the queue but not buried
    if recursing:
        print("bug: fillRev()")
        return False
    self._resetRev()
    return self._fillRev(recursing=True)


def load_config(self):
    f = self.form
    addon_config = self.conf
    f.toggleAddon.setChecked(addon_config.get('toggleAddon', 0))
    # f.toggleAddon.setEnabled(addon_config.get('toggleAddon', 0))


def save_config(self):
    f = self.form
    addon_config = self.conf
    addon_config['toggleAddon'] = f.toggleAddon.isChecked()


# # Hooks
dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setup_ui)
DeckConf.loadConf = wrap(DeckConf.loadConf, load_config)
DeckConf.saveConf = wrap(DeckConf.saveConf, save_config, 'before')

# anki.sched.Scheduler._fillRev = fill_review
anki.sched.Scheduler._fillRev = wrap(anki.sched.Scheduler._fillRev, fill_review, 'before')
