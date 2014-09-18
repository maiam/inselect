"""Settings file

Holds the list of available settings and default values

Usage
-----
    import inselect.settings

    # Run once at the very start of the application
    inselect.settings.init()
    # Get a value
    inselect.settings.get(name)
    # Set a value
    inselect.settings.setValue(name, value)

    # Alternatively, modules can use a QSettings object directly:
    from PySide.QtCore import QSettings
    q = QSettings(*inselect.settings.namespace)
    q.value(name)
    q.setValue(name, value)
"""

import sys
from PySide import QtCore
from inselect.lib import validators
from inselect.gui.settings import SettingsDialog

# Settings namespace
namespace = ('NHM', 'Inselect')

# Define the available settings. Each entry associates the internal setting name to a dictionary defining:
# label : str, required
#     Label as shown to the user.
# description : str, optional
#     Description as shown to the user. This is required if editable is True.
# editable : bool, optional
#     True if the setting can be changed by the user.
# type : str, optional
#     One of 'int', 'float', 'bool', 'list' or 'str' (default).
# validate : function, optional
#     Validation function, returns a boolean.
# default : object, required
#     Default value for the setting.
_settings = {
    'annotation_fields': {
        'label': "Annotation fields",
        'description': 'Comma separated list of fields available in the annotation editor',
        'editable': True,
        'type': 'list',
        'validate': validators.not_empty,
        'default': ['Specimen Number', 'Current Taxon Name', 'Location in Collection']
    },
    'export_template': {
        'label': 'Export file name',
        'description': 'Template for image export file names. You can use any of the annotation fields<br/> between {'
                       'curly brackets}. To insert plain curly brackets, double them.',
        'editable': True,
        'type': 'str',
        'validate': validators.validate_export_template,
        'default': 'BMNHE_{Specimen Number}{Current Taxon Name}'
    },
    'working_directory': {
        'label': 'Working directory',
        'editable': False,
        'type': 'str',
        'default': None
    }
}
_q_settings = None


def init():
    """Create the global QSettings object and setup the default values"""
    global _settings, _q_settings
    if sys.platform == 'win32':
        _settings['working_directory']['default'] = QtCore.QCoreApplication.applicationDirPath()
    else:
        _settings['working_directory']['default'] = QtCore.QDir.currentPath()
    _q_settings = QtCore.QSettings(*namespace)
    for name in _settings:
        if not _q_settings.contains(name):
            _q_settings.setValue(name, _settings[name]['default'])


def get(name):
    """Return the given setting's value

    Parameters
    ----------
    name: Name of setting

    Returns
    -------
    object
        Setting value
    """
    return _q_settings.value(name)


def set_value(name, value):
    """Set the given settings's value

    Parameters
    ----------
    name: Name of setting
    value: Value of setting
    """
    return _q_settings.setValue(name, value)


def definition():
    """Returns setting definition list"""
    return _settings


def open_settings_dialog():
    """Open the settings dialog"""
    dialog = SettingsDialog()
    dialog.exec_()


def reset(name=None):
    """Reset settings to default values

    If setting is None, then all settings are reset.

    Parameters
    ----------
    name : str, None
        The setting to reset, or None
    """
    global _settings, _q_settings
    if name:
        _q_settings.setValue(name, _settings[name]['default'])
    else:
        _q_settings.clear()
        init()
