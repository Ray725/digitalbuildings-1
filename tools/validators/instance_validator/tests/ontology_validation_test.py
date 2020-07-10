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

"""Tests for ontology_validation.py"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from sys import path

path.append('..')

from instance_validator import generate_universe
from instance_validator import ontology_validation
from absl.testing import absltest

_GOOD_EXAMPLE = {'UK-LON-S2': {'type': 'FACILITIES/BUILDING', 'id': 'FACILITIES/123456'}}
_BAD_TYPE_EXAMPLE = {'UK-LON-S2': {'type': 'FACILITIES/BUILDING/ERROR', 'id': 'FACILITIES/123456'}}
_BAD_ENTITY_EXAMPLE = {'UK-LON-S2': {'type': 'LIGHTING/NOT_A_LAMP', 'id': 'FACILITIES/123456'}}
_BAD_NAMESPACE_EXAMPLE = {'UK-LON-S2': {'type': 'NONEXISTENT/BUILDING', 'id': 'FACILITIES/123456'}}
_UNIVERSE = {}

class OntologyValidationTest(absltest.TestCase):

  def testCanParseUniverse(self):
    universe = generate_universe.build_universe()
    fields, subfields_map, states_map, units_map, entities_map = generate_universe.parse_universe(universe)
    self.assertTrue(fields)
    _UNIVERSE['fields'] = fields

    self.assertTrue(subfields_map)
    _UNIVERSE['subfields_map'] = subfields_map

    self.assertTrue(states_map)
    _UNIVERSE['states_map'] = states_map 

    self.assertTrue(units_map)
    _UNIVERSE['units_map'] = units_map 

    self.assertTrue(entities_map)
    _UNIVERSE['entities_map'] = entities_map 
  
  def testValidateGoodExample(self):
    entity_names = list(_GOOD_EXAMPLE.keys()) 

    for name in entity_names:
        entity = dict(_GOOD_EXAMPLE[name])
        try:
          ontology_validation.validate_entity(entity, 
            _UNIVERSE['fields'], _UNIVERSE['subfields_map'], _UNIVERSE['states_map'], 
            _UNIVERSE['units_map'], _UNIVERSE['entities_map'])
        except:
          self.fail('exception incorrectly raised')

  def testValidateBadNamespaceExample(self):
    entity_names = list(_BAD_NAMESPACE_EXAMPLE.keys()) 

    for name in entity_names:
        entity = dict(_BAD_NAMESPACE_EXAMPLE[name])
        try:
          ontology_validation.validate_entity(entity, 
            _UNIVERSE['fields'], _UNIVERSE['subfields_map'], _UNIVERSE['states_map'], 
            _UNIVERSE['units_map'], _UNIVERSE['entities_map'])
          self.fail('exception failed to raise')
        except:
          pass

  def testValidateBadTypeExample(self):
    entity_names = list(_BAD_TYPE_EXAMPLE.keys()) 

    for name in entity_names:
        entity = dict(_BAD_TYPE_EXAMPLE[name])
        try:
          ontology_validation.validate_entity(entity, 
            _UNIVERSE['fields'], _UNIVERSE['subfields_map'], _UNIVERSE['states_map'], 
            _UNIVERSE['units_map'], _UNIVERSE['entities_map'])
          self.fail('exception failed to raise')
        except:
          pass

  def testValidateBadEntityExample(self):
    entity_names = list(_BAD_ENTITY_EXAMPLE.keys()) 

    for name in entity_names:
        entity = dict(_BAD_ENTITY_EXAMPLE[name])
        try:
          ontology_validation.validate_entity(entity, 
            _UNIVERSE['fields'], _UNIVERSE['subfields_map'], _UNIVERSE['states_map'], 
            _UNIVERSE['units_map'], _UNIVERSE['entities_map'])
          self.fail('exception failed to raise')
        except:
          pass

if __name__ == '__main__':
  absltest.main()