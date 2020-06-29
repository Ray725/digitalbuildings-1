# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared base class for all configuration folders."""
import re
import os
from pathlib import Path

from yamlformat.validator import base_lib
from yamlformat.validator import findings_lib


def IsValidFolderForType(path, component_type):
  """Checks a folder is named correctly and in a valid tree for component type.

  Args:
    path: a relative path from ontology root with no leading or trailing
      slashes. Path should be the top level for the component.
    component_type: the base_lib.ComponentType that this folder is for.

  Returns:
    True if the path is valid.
  """
  # print(f'[LOGGING {path}] :: IsValidFolderForType component_type', component_type)
  # print(f'[LOGGING {path}] :: IsValidFolderForType SUBFOLDER_NAMES', base_lib.SUBFOLDER_NAMES[component_type])
  # print(f'[LOGGING {path}] :: IsValidFolderForType dir_name', os.path.dirname(path))

  subfolder_names = base_lib.SUBFOLDER_NAMES[component_type]
  dir_name = path

  # no subfolders
  if os.path.dirname(dir_name) == '':
    return subfolder_names in path

  while os.path.dirname(dir_name) != '':
    dir_name = os.path.dirname(dir_name)

  # print(f'[LOGGING {path}] :: IsValidFolderForType final_check_vars:', os.path.normpath(os.path.join(dir_name, subfolder_names)), path)
  # print(f'[LOGGING {path}] :: IsValidFolderForType result:', os.path.normpath(os.path.join(dir_name, subfolder_names)) in path)
  return os.path.normpath(os.path.join(dir_name, subfolder_names)) in path

  '''
  # replace regex check to allow windows filepath format
  m = re.match(r'(\w*)/?{0}'.format(base_lib.SUBFOLDER_NAMES[component_type]),
               path)
  if m is None:
    return False
  return True
  '''

class ConfigFolder(findings_lib.Findings):
  """Parent class for folder classes that wraps up some of the validation logic.

  Args:
    folderpath: a path relative to ontology root with no leading or trailing
      slashes. Path should be the top level of a component folder (like
      'somenamespace/fields').
    component_type: The type of component this folder contains configs for.
  Attributes:
    local_namespace: object representing the contents of the local namespace.
      Must be set to a non-None value in the subclass init method.

  Returns:
    a ConfigFolder object
  """

  def __init__(self, folderpath, component_type):
    super(ConfigFolder, self).__init__()
    if not IsValidFolderForType(folderpath, component_type):
      raise RuntimeError('{0} is not a correct resource path for {1}'.format(
          folderpath,
          base_lib.ComponentType(component_type).name))
    self._component_type = component_type

    # print(f'[LOGGING] ConfigFolder init :: folderpath', folderpath)
    self._folderpath = folderpath
    # DEPRECATE REGEX
    # self._this_folder_yaml_regex = re.compile(r'^{0}/.*\.yaml'.format(self._folderpath))

    self._namespace_name = self._GetNamespaceFromPath()
    if self._namespace_name is None:
      raise RuntimeError('Cannot get a valid namespace name for {0}'.format(
          self._folderpath))
    self._local_namespace = None

  @property
  def local_namespace(self):
    return self._local_namespace

  @local_namespace.setter
  def local_namespace(self, local_namespace):
    self._local_namespace = local_namespace

  def _GetDynamicFindings(self, filter_old_warnings):
    if self._local_namespace is None:
      raise RuntimeError('Local namespace has not been set')
    return self.local_namespace.GetFindings(filter_old_warnings)

  def GetFolderpath(self):
    return self._folderpath

  def Finalize(self):
    """Override to provide finalization logic for completed folders.

    This will be called on the folder after file parsing has finished. For most
    items in the ontology, this step is a no-op, but for entity types the
    finalization step is used to generate qualified parent names.
    """
    return

  def AddFromConfig(self, documents, config_filename):
    """Reads the list of extracted yaml documents and adds all ontology items found.

    Method checks that config_filename is a path in the correct folder.
    Valid items are added to the appropriate namespace objects.
    Findings are saved on objects if found. Errors do not halt processing.

    Args:
      documents: output of a yaml safe_load_all()
      config_filename: relative path to the yaml file from config root

    Raises:
      RuntimeError: if the path is not valid for the component type
    """
    context = findings_lib.FileContext(config_filename)

    if documents is None:
      self.AddFinding(findings_lib.EmptyFileWarning(context))
      return

    # Validate that the ontology item is from the correct folder
    if not self._IsYamlUnderThisFolder(config_filename):
      self.AddFinding(
          findings_lib.InconsistentFileLocationError(
              self._folderpath + r'/*.yaml', context))
      return

    for document in documents:
      self._AddFromConfigHelper(document, context)

  def _AddFromConfigHelper(self, document, context):
    """Reads a single yaml document and adds all ontology items found.

    Also adds any findings to the object.

    This should be overridden by subclasses.

    Args:
      document: yaml document
      context: config file context
    """
    return

  def _IsYamlUnderThisFolder(self, path):
    """Checks that a filename .yaml in the same folder as this class.

    Args:
      path: path relative to ontology root with no leading or trailing slashes.

    Returns:
      True if the path is in the folder and has a .yaml extension.
    """
    '''
    # DEPRECATE REGEX
    if self._this_folder_yaml_regex.match(path) is None:
      return False
    return True
    '''
    if path.startswith(self._folderpath) and path.endswith('.yaml'):
      return True
    return False

  def _GetNamespaceFromPath(self):
    """Extracts the namespace name from the filepath.

    Returns:
      The namespace name or None
    """
    # print('[LOGGING GetNamespaceFromPath] :: SUBFOLDER_NAMES', base_lib.SUBFOLDER_NAMES[self._component_type])

    '''
    regex = re.compile(r'^(\w*)/?{0}.*'.format(
        base_lib.SUBFOLDER_NAMES[self._component_type]))
    m = regex.match(self._folderpath)
    if m is not None:
      return m.group(1)
    return None
    '''
    if base_lib.SUBFOLDER_NAMES[self._component_type] not in self._folderpath:
      return None

    path = Path(self._folderpath)
    # print('[LOGGING GetNamespaceFromPath] :: Path', path)
    # print('[LOGGING GetNamespaceFromPath] :: Path.root', path.root)
    # for p in path.parents:
      # print('[LOGGING GetNamespaceFromPath] :: parents', p)

    return path.parents[0]