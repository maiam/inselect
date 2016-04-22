import humanize
import locale
import platform
import subprocess
import sys

from PySide.QtCore import Qt, QProcessEnvironment
from PySide.QtGui import QWidget, QFormLayout, QLabel, QGroupBox, QVBoxLayout

from inselect.lib.utils import format_dt_display

from .toggle_widget_label import ToggleWidgetLabel
from .utils import report_to_user


def reveal_path(path):
    """Shows path in Finder (on Mac) or in Explorer (on Windows)
    """
    # http://stackoverflow.com/a/3546503
    if sys.platform.startswith("win"):
        explorer = QProcessEnvironment.systemEnvironment().searchInPath("explorer.exe")
        if not explorer:
            # Handle gracefully
            pass
        else:
            if not path.is_dir():
                arg = u"/select,{0}".format(path)
            else:
                arg = unicode(path)
        subprocess.check_call([explorer, arg])
    elif 'Darwin' == platform.system():
        reveal = u'tell application "Finder" to reveal POSIX file "{0}"'
        activate = u'tell application "Finder" to activate "{0}"'
        args = ['/usr/bin/osascript', '-e']
        subprocess.check_call(args + [reveal.format(path)])
        subprocess.check_call(args + [activate.format(path)])
    else:
        # What to do on Linux?
        pass


class RevealPathLabel(QLabel):
    """A QLabel that, when clicked, reveals a path in Finder / Explorer
    """
    def __init__(self, parent=None, flags=0):
        super(RevealPathLabel, self).__init__('', parent, flags)
        self.path = None
        self.setCursor(Qt.PointingHandCursor)

    def set_label_and_path(self, path):
        if path:
            self.setText(path.name)
            self.path = path
        else:
            self.setText('')
            self.path = None

    @report_to_user
    def mouseReleaseEvent(self, event):
        """QLabel virtual
        """
        if self.path:
            reveal_path(self.path)


class BoldLabel(QLabel):
    """A label in a bold font
    """
    pass


class InfoWidget(QGroupBox):
    """Shows information about the document and the scanned image
    """

    STYLESHEET = """
    ToggleWidgetLabel {
        text-decoration: none;
        font-weight: bold;
        color: black;
    }

    BoldLabel {
        font-weight: bold;
    }

    RevealPathLabel {
        text-decoration: underline;
    }
    """


    def __init__(self, parent=None):
        super(InfoWidget, self).__init__(parent)

        self.setStyleSheet(self.STYLESHEET)

        layout = QFormLayout()

        self._document_path = RevealPathLabel()
        layout.addRow('Name', self._document_path)

        self._created_by = QLabel()
        layout.addRow('Created by', self._created_by)

        self._created_on = QLabel()
        layout.addRow('Created on', self._created_on)

        self._last_saved_by = QLabel()
        layout.addRow('Last saved by', self._last_saved_by)

        self._last_saved_on = QLabel()
        layout.addRow('Last saved on', self._last_saved_on)

        layout.addRow(BoldLabel('Scanned image'))
        self._scanned_path = RevealPathLabel()
        layout.addRow('File', self._scanned_path)

        self._scanned_size = QLabel()
        layout.addRow('File size', self._scanned_size)

        self._scanned_dimensions = QLabel()
        layout.addRow('Dimensions', self._scanned_dimensions)

        layout.addRow(BoldLabel('Thumbnail image'))
        self._thumbnail_path = RevealPathLabel()
        layout.addRow('File', self._thumbnail_path)

        self._thumbnail_size = QLabel()
        layout.addRow('File size', self._thumbnail_size)

        self._thumbnail_dimensions = QLabel()
        layout.addRow('Dimensions', self._thumbnail_dimensions)

        labels_widget = QWidget()
        labels_widget.setLayout(layout)
        labels_widget.setVisible(False)

        # Show the labels about the toggle
        vlayout = QVBoxLayout()
        vlayout.setAlignment(Qt.AlignTop)
        vlayout.addWidget(labels_widget)
        vlayout.addWidget(ToggleWidgetLabel('Information', labels_widget))

        self.setLayout(vlayout)

        # self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

    def set_document(self, document):
        """Updates controls to reflect the document. Clears controls if
        document is None.
        """
        if document:
            self._document_path.set_label_and_path(document.document_path)

            p = document.properties
            self._created_by.setText(p.get('Created by'))

            dt = p.get('Created on')
            self._created_on.setText(format_dt_display(dt) if dt else '')

            self._last_saved_by.setText(p.get('Saved by'))

            dt = p.get('Saved on')
            self._last_saved_on.setText(format_dt_display(dt) if dt else '')

            self._scanned_path.set_label_and_path(document.scanned.path)

            fsize = humanize.naturalsize(document.scanned.size_bytes, binary=True)
            self._scanned_size.setText(fsize)

            dim = '{0} x {1}'
            self._scanned_dimensions.setText(dim.format(*(
                locale.format("%d", n, grouping=True)
                for n in document.scanned.dimensions)
            ))

            # Thumbnail might not be present
            if document.thumbnail:
                self._thumbnail_path.set_label_and_path(document.thumbnail.path)

                fsize = humanize.naturalsize(document.thumbnail.size_bytes, binary=True)
                self._thumbnail_size.setText(fsize)
                self._thumbnail_dimensions.setText(dim.format(*(
                    locale.format("%d", n, grouping=True)
                    for n in document.thumbnail.dimensions)
                ))
            else:
                self._thumbnail_path.setText('')
                self._thumbnail_size.setText('')
                self._thumbnail_dimensions.setText('')
        else:
            self._document_path.setText('')
            self._created_by.setText('')
            self._created_on.setText('')
            self._last_saved_by.setText('')
            self._last_saved_on.setText('')
            self._scanned_path.setText('')
            self._scanned_size.setText('')
            self._scanned_dimensions.setText('')
            self._thumbnail_path.setText('')
            self._thumbnail_size.setText('')
            self._thumbnail_dimensions.setText('')
