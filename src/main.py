# license

import sys
import os

import anki

from aqt.qt import *
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.deckconf import DeckConf
from aqt.forms import dconf
from aqt.utils import tooltip

from anki.sched import Scheduler
from anki.schedv2 import Scheduler
from anki.utils import ids2str

from anki.hooks import addHook, wrap


# from anki.sound import play
# from anki.lang import _


def setup_ui(self, Dialog):
    self.maxTaken.setMinimum(3)

    grid = QGridLayout()
    self.toggleAddon = QCheckBox("Enable Anki Ultimate")
    self.toggleAddon.stateChanged.connect(checked)
    grid.addWidget(self.toggleAddon, 0, 0, 1, 1)
    self.verticalLayout_6.insertLayout(4, grid)


def fill_review(self, _old):
    if self._revQueue:
        return True
    if not self.revCount:
        return False
    self._revQueue = self.col.db.list("""select id from cards order by ivl and queue = 2""")
    # if self.col.decks.current()['dyn']:
    #     run_tests.state = 3
    #     return _old(self)
    # did = self._revDids[0]
    # d = self.col.decks.get(self.col.decks.selected(), default=False)
    # lim = min(self.queueLimit, currentRevLimit(self))
    # lim = min(self.queueLimit, currentRevLimit(self))
    # lim = 200
    # if lim:
        # sort_by = SORT_CHOICE
        # sort_by = "lapses asc, " \
        #           "(select max(revlog.ease) from revlog where revlog.cid = cards.id) desc," \
        #           "(select max(revlog.time) from revlog where revlog.cid = cards.id) asc "
        # sort_by1 = "order by lapses asc"
        # sql = """
        # select id from cards where did in ?
        # order by %s and queue = 2 and due <= ? limit ?
        # """
        # perDeckLimit ?
        # prioritize today?

        # deck_list = ids2str(self.col.decks.active())

        # self._revQueue = self.col.db.list(sql, did, sort_by1, self.today, lim)
        # self._revQueue = self.col.db.list("""select id from cards where did in %s
        # and queue = 2 limit ?""" % ((deck_list, sort_by1), lim))

        # self._revQueue = self.col.db.list("""
        # select id from cards order by ivl and queue = 2""")
    # if self.revCount:
    #     self._resetRev()
    #     return self._fillRev()


# From: anki.schedv2.py
def currentRevLimit(sched):
    d = sched.col.decks.get(sched.col.decks.selected(), default=False)
    return deckRevLimitSingle(sched, d)


# From: anki.schedv2.py
def deckRevLimitSingle(sched, d, parentLimit=None):
    if not d: return 0  # invalid deck selected?
    if d['dyn']: return 99999

    c = sched.col.decks.confForDid(d['id'])
    lim = max(0, c['rev']['perDay'] - d['revToday'][1])
    if parentLimit is not None:
        return min(parentLimit, lim)
    elif '::' not in d['name']:
        return lim
    else:
        for parent in sched.col.decks.parents(d['id']):
            # pass in dummy parentLimit so we don't do parent lookup again
            lim = min(lim, deckRevLimitSingle(sched, parent, parentLimit=lim))
        return lim


def checked(self):
    pass


def load_config(self):
    f = self.form
    addon_config = self.conf
    f.toggleAddon.setChecked(addon_config.get('toggleAddon', 0))
    # f.toggleAddon.setEnabled(addon_config.get('toggleAddon', 0))


def save_config(self):
    f = self.form
    addon_config = self.conf
    addon_config['toggleAddon'] = f.toggleAddon.isChecked()


# Hooks
dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setup_ui)
DeckConf.loadConf = wrap(DeckConf.loadConf, load_config)
DeckConf.saveConf = wrap(DeckConf.saveConf, save_config, 'before')

anki.sched.Scheduler._fillRev = wrap(
    anki.sched.Scheduler._fillRev, fill_review, 'around'
)
# anki.sched.Scheduler._resetRevCount = wrap(
#     anki.sched.Scheduler._resetRevCount, resetRevCount, 'around'
# )
