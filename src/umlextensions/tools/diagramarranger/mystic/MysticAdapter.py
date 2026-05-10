from typing import Dict
from typing import NewType
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import Bitmap
from wx import Window

from codeallyadvanced.ui.mystic.Mystic import Mystic
from codeallyadvanced.ui.mystic.Mystic import MYSTIC_CANCELLED
from codeallyadvanced.ui.mystic.Mystic import MYSTIC_FINISHED

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType

from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import BaseConfigStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import LayoutCallback
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import UndoCallback

from umlextensions.tools.diagramarranger.mystic.arrangersteps.ARFConfigStep import ARFConfigStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.ForceAtlas2ConfigStep import ForceAtlas2ConfigStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.GoodByeStep import GoodByeStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.PlanarConfigStep import PlanarConfigStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.IntroductionStep import IntroductionStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.LayoutSelectionStep import LayoutSelectionStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.SpringConfigStep import SpringConfigStep

from umlextensions.tools.diagramarranger.mystic.resources.ArrangerMystic import embeddedImage as mysticLogo

CompleteCallback = Callable[[], None]
CancelCallback   = Callable[[], None]

ConfigStepMap = NewType('ConfigStepMap', Dict[ArrangerType, BaseConfigStep])

class MysticAdapter:
    """
    Moves all the details of handling the Mystic to a separate class
    """
    def __init__(self, parent: Window,
                 completeCallback: CompleteCallback,
                 cancelCallback: CancelCallback,
                 layoutCallback: LayoutCallback,
                 undoCallback:   UndoCallback
                 ):
        """

        Args:
            parent:                 parent window for dialog
            completeCallback:       Method to call when Mystic is complete
            cancelCallback:         Method to call when Mystic is canceled
            layoutCallback:         Method to call to re-arrange UML Diagram
            undoCallback:           Method to call to undo last arrangement
        """
        self._frame:            Window           = parent
        self._completeCallback: CompleteCallback = completeCallback
        self._cancelCallback:   CancelCallback   = cancelCallback
        self._layoutCallback:   LayoutCallback   = layoutCallback
        self._undoCallback:     UndoCallback     = undoCallback

        self.logger: Logger = getLogger(__name__)

        self.extensionPreferences: ExtensionsPreferences = ExtensionsPreferences()

        logo:   Bitmap = mysticLogo.GetBitmap()
        mystic: Mystic  = Mystic(parent=self._frame, title='', bitmap=logo, nextCallback=self._getNextStep, backCallback=self._getBackStep)

        introductionStep:    IntroductionStep    = IntroductionStep(parent=mystic.pageContainer)
        layoutSelectionStep: LayoutSelectionStep = LayoutSelectionStep(parent=mystic.pageContainer)

        springConfigStep: SpringConfigStep = SpringConfigStep(
            parent=mystic.pageContainer,
            configuresArranger=ArrangerType.SPRING,
            layoutCallback=self._layoutCallback,
            undoCallback=self._undoCallback
        )
        forceAtlas2ConfigStep: ForceAtlas2ConfigStep = ForceAtlas2ConfigStep(
            parent=mystic.pageContainer,
            configuresArranger=ArrangerType.FORCE_ATLAS2,
            layoutCallback=self._layoutCallback,
            undoCallback=self._undoCallback
        )

        planarConfigStep: PlanarConfigStep = PlanarConfigStep(
            parent=mystic.pageContainer,
            configuresArranger=ArrangerType.PLANAR,
            layoutCallback=self._layoutCallback,
            undoCallback=self._undoCallback
        )
        aRFConfigStep: ARFConfigStep = ARFConfigStep(
            parent=mystic.pageContainer,
            configuresArranger=ArrangerType.ARF,
            layoutCallback=self._layoutCallback,
            undoCallback=self._undoCallback
        )
        goodByeStep: GoodByeStep = GoodByeStep(parent=mystic.pageContainer)

        mystic.addMysticStep(mysticStep=introductionStep)
        mystic.addMysticStep(mysticStep=layoutSelectionStep)
        mystic.addMysticStep(mysticStep=springConfigStep)
        mystic.addMysticStep(mysticStep=forceAtlas2ConfigStep)
        mystic.addMysticStep(mysticStep=planarConfigStep)
        mystic.addMysticStep(mysticStep=aRFConfigStep)
        mystic.addMysticStep(mysticStep=goodByeStep)

        self._mystic:           Mystic              = mystic

        self._introductionStep: IntroductionStep    = introductionStep
        self._layoutSelection:  LayoutSelectionStep = layoutSelectionStep

        self._springConfigStep: SpringConfigStep      = springConfigStep
        self._forceAtlas2Step:  ForceAtlas2ConfigStep = forceAtlas2ConfigStep
        self._planarConfigStep: PlanarConfigStep      = planarConfigStep
        self._aRFConfigStep:    ARFConfigStep         = aRFConfigStep
        self._goodByeStep:      GoodByeStep           = goodByeStep

        self._configStepMap: ConfigStepMap = ConfigStepMap(
            {
                ArrangerType.SPRING:        springConfigStep,
                ArrangerType.FORCE_ATLAS2:  forceAtlas2ConfigStep,
                ArrangerType.PLANAR:        planarConfigStep,
                ArrangerType.ARF:           aRFConfigStep
            }
        )

    def _getNextStep(self, currentStep: MysticStepBase) -> int:

        if isinstance(currentStep, IntroductionStep):
            return currentStep.stepNumber + 1
        elif isinstance(currentStep, LayoutSelectionStep):
            arrangerType: ArrangerType = self._layoutSelection.arrangerType
            return self._configStepMap[arrangerType].stepNumber
        elif isinstance(currentStep, BaseConfigStep):
            return self._goodByeStep.stepNumber
        elif isinstance(currentStep, GoodByeStep):
            return self._goodByeStep.stepNumber + 1
        else:
            assert False, 'Developer error'

    def _getBackStep(self, currentStep: MysticStepBase) -> int:

        if isinstance(currentStep, LayoutSelectionStep):
            return self._introductionStep.stepNumber

        return self._layoutSelection.stepNumber


    def run(self):

        status: int = self._mystic.runMystic()

        if status == MYSTIC_CANCELLED:
            self.logger.info(f'Mystic Canceled')
            self._cancelCallback()
        elif status == MYSTIC_FINISHED:
            self.logger.info(f'Things are cool')
            self.logger.info(f'ArrangerType: {self._layoutSelection.arrangerType}')
            self._completeCallback()
