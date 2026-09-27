
from typing import Callable
from typing import cast
from typing import TypeAlias

from dataclasses import dataclass

from logging import Logger
from logging import getLogger

from wx import CheckBox
from wx import Choice
from wx import CommandEvent
from wx import EVT_CHECKBOX
from wx import EVT_CHOICE
from wx import EVT_SPINCTRL
from wx import EVT_TEXT
from wx import ID_ANY
from wx import Size
from wx import SpinCtrl
from wx import StaticText
from wx import Window

from wx.lib.sized_controls import SizedStaticBox

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlFontFamily import UmlFontFamily

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ui.preferences.BaseExtPreferencesPanel import BaseExtPreferencesPanel

ColorChoices:       TypeAlias = list[str]
FontFamilyChoices:  TypeAlias = list[str]
ChangeEventHandler: TypeAlias = Callable[[CommandEvent], None]


@dataclass
class FontGroupSpec:
    """
    Configuration choices and event callbacks for creating a font control group.
    """
    colorChoices:      ColorChoices
    fontFamilyChoices: FontFamilyChoices
    onSizeChange:      ChangeEventHandler
    onBoldChange:      ChangeEventHandler
    onItalicChange:    ChangeEventHandler
    onFamilyChange:    ChangeEventHandler
    onColorChange:     ChangeEventHandler


@dataclass
class FontGroupControls:
    """
    Widgets created for a font control group.
    """
    fontSizeCtrl: SpinCtrl
    boldCheck:    CheckBox
    italicCheck:  CheckBox
    familyChoice: Choice
    colorChoice:  Choice


FONT_SIZE_MIN: int = 6
FONT_SIZE_MAX: int = 72


class TooltipSectionPanel(BaseExtPreferencesPanel):
    """
    Preferences panel for the 'ArrangerTooltip' INI section.

    Covers:
        balloonColor              - Choice (UmlColor)

        Tip Title group:
            balloonTipTitleFontSize   - SpinCtrl
            balloonTipTitleBold       - CheckBox
            balloonTipTitleItalicize  - CheckBox
            balloonTipTitleFontFamily - Choice (UmlFontFamily)
            balloonTipTitleColor      - Choice (UmlColor)

        Tip Text group:
            balloonTipTextFontSize    - SpinCtrl
            balloonTipTextBold        - CheckBox
            balloonTipTextItalicize   - CheckBox
            balloonTipTextFontFamily  - Choice (UmlFontFamily)
            balloonTipTextColor       - Choice (UmlColor)
    """

    PANEL_NAME: str = 'Tooltip'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        # Balloon
        self._balloonColorChoice: Choice = cast(Choice, None)       # noqa

        # Title
        self._titleFontSizeCtrl:   SpinCtrl = cast(SpinCtrl, None)  # noqa
        self._titleBoldCheck:      CheckBox = cast(CheckBox, None)  # noqa
        self._titleItalicCheck:    CheckBox = cast(CheckBox, None)  # noqa
        self._titleFontFamilyChoice: Choice = cast(Choice,   None)  # noqa
        self._titleColorChoice:    Choice   = cast(Choice,   None)  # noqa

        # Text
        self._textFontSizeCtrl:    SpinCtrl = cast(SpinCtrl, None)  # noqa
        self._textBoldCheck:       CheckBox = cast(CheckBox, None)  # noqa
        self._textItalicCheck:     CheckBox = cast(CheckBox, None)  # noqa
        self._textFontFamilyChoice: Choice  = cast(Choice,   None)  # noqa
        self._textColorChoice:     Choice   = cast(Choice,   None)  # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return TooltipSectionPanel.PANEL_NAME

    def _layoutControls(self):
        """
        Builds and lays out the preference controls for the tooltip section.
        """
        colorChoices:      ColorChoices      = [e.value for e in UmlColor]
        fontFamilyChoices: FontFamilyChoices = [e.value for e in UmlFontFamily]

        self._layoutBalloonColor(colorChoices=colorChoices)
        self._layoutTipTitle(colorChoices=colorChoices, fontFamilyChoices=fontFamilyChoices)
        self._layoutTipText(colorChoices=colorChoices, fontFamilyChoices=fontFamilyChoices)

    def _layoutBalloonColor(self, colorChoices: ColorChoices):
        """
        Lays out the balloon background color selection box.

        Args:
            colorChoices: Available color names
        """
        balloonBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Balloon')
        balloonBox.SetSizerType('form')
        balloonBox.SetMinSize(Size(-1, 60))
        balloonBox.SetSizerProps(expand=True)

        balloonColorLabel: StaticText = StaticText(balloonBox, ID_ANY, 'Balloon Color')
        balloonColorLabel.SetSizerProps(valign='center')
        self._balloonColorChoice = Choice(balloonBox, ID_ANY, choices=colorChoices)
        self._balloonColorChoice.SetSizerProps(valign='center')
        self._balloonColorChoice.SetToolTip('Background color of the balloon tooltip')
        self.Bind(EVT_CHOICE, self._onBalloonColorChanged, self._balloonColorChoice)

    def _layoutTipTitle(self, colorChoices: ColorChoices, fontFamilyChoices: FontFamilyChoices):
        """
        Lays out the title font controls static box.

        Args:
            colorChoices:      Available color names
            fontFamilyChoices: Available font family names
        """
        titleBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Tip Title')
        titleBox.SetSizerType('form')
        titleBox.SetMinSize(Size(-1, 185))
        titleBox.SetSizerProps(expand=True)

        titleSpec: FontGroupSpec = FontGroupSpec(
            colorChoices=colorChoices,
            fontFamilyChoices=fontFamilyChoices,
            onSizeChange=self._onTitleFontSizeChanged,
            onBoldChange=self._onTitleBoldChanged,
            onItalicChange=self._onTitleItalicChanged,
            onFamilyChange=self._onTitleFontFamilyChanged,
            onColorChange=self._onTitleColorChanged,
        )

        titleControls: FontGroupControls = self._layoutFontGroup(parent=titleBox, spec=titleSpec)
        self._titleFontSizeCtrl     = titleControls.fontSizeCtrl
        self._titleBoldCheck        = titleControls.boldCheck
        self._titleItalicCheck      = titleControls.italicCheck
        self._titleFontFamilyChoice = titleControls.familyChoice
        self._titleColorChoice      = titleControls.colorChoice

    def _layoutTipText(self, colorChoices: ColorChoices, fontFamilyChoices: FontFamilyChoices):
        """
        Lays out the tip text font controls static box.

        Args:
            colorChoices:      Available color names
            fontFamilyChoices: Available font family names
        """
        textBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Tip Text')
        textBox.SetSizerType('form')
        textBox.SetMinSize(Size(-1, 185))
        textBox.SetSizerProps(expand=True)

        textSpec: FontGroupSpec = FontGroupSpec(
            colorChoices=colorChoices,
            fontFamilyChoices=fontFamilyChoices,
            onSizeChange=self._onTextFontSizeChanged,
            onBoldChange=self._onTextBoldChanged,
            onItalicChange=self._onTextItalicChanged,
            onFamilyChange=self._onTextFontFamilyChanged,
            onColorChange=self._onTextColorChanged,
        )

        textControls: FontGroupControls = self._layoutFontGroup(parent=textBox, spec=textSpec)
        self._textFontSizeCtrl     = textControls.fontSizeCtrl
        self._textBoldCheck        = textControls.boldCheck
        self._textItalicCheck      = textControls.italicCheck
        self._textFontFamilyChoice = textControls.familyChoice
        self._textColorChoice      = textControls.colorChoice

    def _layoutFontGroup(self, parent: SizedStaticBox, spec: FontGroupSpec) -> FontGroupControls:
        """
        Creates and lays out a standard set of font-control widgets in a form panel.

        Returns:
            FontGroupControls containing the created widgets
        """
        fontSizeCtrl: SpinCtrl = self._createFontSizeCtrl(parent, spec.onSizeChange)
        boldCheck:    CheckBox = self._createBoldCheck(parent, spec.onBoldChange)
        italicCheck:  CheckBox = self._createItalicCheck(parent, spec.onItalicChange)
        familyChoice: Choice   = self._createFamilyChoice(parent, spec.fontFamilyChoices, spec.onFamilyChange)
        colorChoice:  Choice   = self._createColorChoice(parent, spec.colorChoices, spec.onColorChange)

        return FontGroupControls(
            fontSizeCtrl=fontSizeCtrl,
            boldCheck=boldCheck,
            italicCheck=italicCheck,
            familyChoice=familyChoice,
            colorChoice=colorChoice,
        )

    def _createFontSizeCtrl(self, parent: SizedStaticBox, onSizeChange: ChangeEventHandler) -> SpinCtrl:

        fontSizeLabel: StaticText = StaticText(parent, ID_ANY, 'Font Size')
        fontSizeLabel.SetSizerProps(valign='center')

        sizeCtrl: SpinCtrl = SpinCtrl(parent, ID_ANY, min=FONT_SIZE_MIN, max=FONT_SIZE_MAX)
        sizeCtrl.SetSizerProps(valign='center')

        self.Bind(EVT_SPINCTRL, onSizeChange, sizeCtrl)
        self.Bind(EVT_TEXT,     onSizeChange, sizeCtrl)
        return sizeCtrl

    def _createBoldCheck(self, parent: SizedStaticBox, onBoldChange: ChangeEventHandler) -> CheckBox:

        boldLabel: StaticText = StaticText(parent, ID_ANY, 'Bold')
        boldLabel.SetSizerProps(valign='center')

        boldCheck: CheckBox = CheckBox(parent, ID_ANY, '')
        boldCheck.SetSizerProps(valign='center')

        self.Bind(EVT_CHECKBOX, onBoldChange, boldCheck)
        return boldCheck

    def _createItalicCheck(self, parent: SizedStaticBox, onItalicChange: ChangeEventHandler) -> CheckBox:

        italicLabel: StaticText = StaticText(parent, ID_ANY, 'Italic')
        italicLabel.SetSizerProps(valign='center')

        italicCheck: CheckBox = CheckBox(parent, ID_ANY, '')
        italicCheck.SetSizerProps(valign='center')

        self.Bind(EVT_CHECKBOX, onItalicChange, italicCheck)
        return italicCheck

    def _createFamilyChoice(self,
                            parent:            SizedStaticBox,
                            fontFamilyChoices: FontFamilyChoices,
                            onFamilyChange:    ChangeEventHandler,
    ) -> Choice:
        """
        Creates and binds the font family dropdown choice control.

        Args:
            parent:            The parent sized static box
            fontFamilyChoices: Available font family names
            onFamilyChange:    Callback invoked when font family selection changes

        Returns:
            The configured font family Choice control
        """
        fontFamilyLabel: StaticText = StaticText(parent, ID_ANY, 'Font Family')
        fontFamilyLabel.SetSizerProps(valign='center')

        familyChoice: Choice = Choice(parent, ID_ANY, choices=fontFamilyChoices)
        familyChoice.SetSizerProps(valign='center')

        self.Bind(EVT_CHOICE, onFamilyChange, familyChoice)
        return familyChoice

    def _createColorChoice(self,
                           parent:        SizedStaticBox,
                           colorChoices:  ColorChoices,
                           onColorChange: ChangeEventHandler,
    ) -> Choice:
        """
        Creates and binds the color dropdown choice control.

        Args:
            parent:        The parent sized static box
            colorChoices:  Available color names
            onColorChange: Callback invoked when color selection changes

        Returns:
            The configured color Choice control
        """
        colorLabel: StaticText = StaticText(parent, ID_ANY, 'Color')
        colorLabel.SetSizerProps(valign='center')

        colorChoice: Choice = Choice(parent, ID_ANY, choices=colorChoices)
        colorChoice.SetSizerProps(valign='center')

        self.Bind(EVT_CHOICE, onColorChange, colorChoice)
        return colorChoice

    def _setControlValues(self):

        p: ExtensionsPreferences = self._preferences

        # Balloon
        self._balloonColorChoice.SetSelection(self._balloonColorChoice.FindString(p.balloonColor.value))

        # Title
        self._titleFontSizeCtrl.SetValue(p.balloonTipTitleFontSize)
        self._titleBoldCheck.SetValue(p.balloonTipTitleBold)
        self._titleItalicCheck.SetValue(p.balloonTipTitleItalicize)
        self._titleFontFamilyChoice.SetSelection(
            self._titleFontFamilyChoice.FindString(p.balloonTipTitleFontFamily.value)
        )
        self._titleColorChoice.SetSelection(
            self._titleColorChoice.FindString(p.balloonTipTitleColor.value)
        )

        # Text
        self._textFontSizeCtrl.SetValue(p.balloonTipTextFontSize)
        self._textBoldCheck.SetValue(p.balloonTipTextBold)
        self._textItalicCheck.SetValue(p.balloonTipTextItalicize)
        self._textFontFamilyChoice.SetSelection(
            self._textFontFamilyChoice.FindString(p.balloonTipTextFontFamily.value)
        )
        self._textColorChoice.SetSelection(
            self._textColorChoice.FindString(p.balloonTipTextColor.value)
        )

    def _onBalloonColorChanged(self, event: CommandEvent):
        self._preferences.balloonColor = UmlColor(event.GetString())

    def _onTitleFontSizeChanged(self, event: CommandEvent):
        self._preferences.balloonTipTitleFontSize = event.GetInt()

    def _onTitleBoldChanged(self, event: CommandEvent):
        self._preferences.balloonTipTitleBold = event.IsChecked()

    def _onTitleItalicChanged(self, event: CommandEvent):
        self._preferences.balloonTipTitleItalicize = event.IsChecked()

    def _onTitleFontFamilyChanged(self, event: CommandEvent):
        self._preferences.balloonTipTitleFontFamily = UmlFontFamily.deSerialize(event.GetString())

    def _onTitleColorChanged(self, event: CommandEvent):
        self._preferences.balloonTipTitleColor = UmlColor(event.GetString())

    def _onTextFontSizeChanged(self, event: CommandEvent):
        self._preferences.balloonTipTextFontSize = event.GetInt()

    def _onTextBoldChanged(self, event: CommandEvent):
        self._preferences.balloonTipTextBold = event.IsChecked()

    def _onTextItalicChanged(self, event: CommandEvent):
        self._preferences.balloonTipTextItalicize = event.IsChecked()

    def _onTextFontFamilyChanged(self, event: CommandEvent):
        self._preferences.balloonTipTextFontFamily = UmlFontFamily.deSerialize(event.GetString())

    def _onTextColorChanged(self, event: CommandEvent):
        self._preferences.balloonTipTextColor = UmlColor(event.GetString())
