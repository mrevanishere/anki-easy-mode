# license
import anki

from aqt.qt import *
from aqt.deckconf import DeckConf
from aqt.forms import dconf

from anki.sched import Scheduler
# from anki.schedv2 import Scheduler

from anki.hooks import wrap
from . import sortconfig


def setup_ui(self, Dialog):
    self.maxTaken.setMinimum(3)

    grid = QGridLayout()
    self.toggleAddon = QCheckBox("Enable Anki Ultimate")
    # self.toggleAddon.stateChanged.connect(checked)
    grid.addWidget(self.toggleAddon, 0, 0, 1, 1)
    self.verticalLayout_6.insertLayout(10, grid)

    grid = QGridLayout()
    label1 = QLabel(self.tab_5)
    label1.setText("Special Queue Type")
    grid.addWidget(label1, 0, 0, 1, 1)
    self.choicesDropDown = QComboBox()
    for i in sortconfig.SORT_OPTIONS:
        self.choicesDropDown.addItem(sortconfig.SORT_OPTIONS.get(i)[0])
    grid.addWidget(self.choicesDropDown, 0, 1, 1, 1)
    self.verticalLayout_6.insertLayout(10, grid)


def fill_review(self, recursing=False) -> bool:
    "True if a review card can be fetched."
    if self._revQueue:
        return True
    if not self.revCount:
        return False

    # check if special queue is enabled
    # needsdeckself = DeckManager.confForDid(self._revDids[0]).get('toggleAddon', 0)
    deck_conf = self.col.decks.confForDid(self._revDids[0])
    enabled = deck_conf.get('toggleAddon', 0)
    if not enabled:
        return False

    while self._revDids:
        did = self._revDids[0]

        lim = min(self.queueLimit, self._deckRevLimit(did))
        if lim:
            # fill the queue with the current did

            selected: int = deck_conf.get('choicesDropDown')
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
    f.choicesDropDown.setCurrentIndex(addon_config.get('choicesDropDown', 0))


def save_config(self):
    f = self.form
    addon_config = self.conf
    addon_config['toggleAddon'] = f.toggleAddon.isChecked()
    addon_config['choicesDropDown'] = f.choicesDropDown.currentIndex()


# Hooks
dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setup_ui)
DeckConf.loadConf = wrap(DeckConf.loadConf, load_config)
DeckConf.saveConf = wrap(DeckConf.saveConf, save_config, 'before')

# anki.sched.Scheduler._fillRev = fill_review
anki.sched.Scheduler._fillRev = wrap(
    anki.sched.Scheduler._fillRev, fill_review, 'before'
)
