# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from unittest import mock

from nose.plugins.skip import SkipTest

import horizons.main
from horizons.util.cmdlineoptions import get_option_parser
from horizons.util.random_map import generate_map_from_seed
from tests.unittests import TestCase


class TestHorizonsMain(TestCase):
	"""
	Test all things related to the horizons.main module.
	"""
	def setUp(self):
		self.mock_fife_patcher = mock.patch('horizons.engine.Fife')
		self.mock_fife = self.mock_fife_patcher.start()
		self.mock_set_debug_log_patcher = mock.patch('horizons.main.set_debug_log')
		self.mock_set_debug_log_patcher.start()
		self.mock_gui_patcher = mock.patch('horizons.main.Gui')
		self.mock_gui_patcher.start()

	def tearDown(self):
		self.mock_gui_patcher.stop()
		self.mock_set_debug_log_patcher.stop()
		self.mock_fife_patcher.stop()

	@staticmethod
	def start_game(*args):
		options = get_option_parser().parse_args(list(args) + ['--no-atlas-generation'])[0]
		horizons.main.start(options)

	@mock.patch('tests.gui.logger.setup_gui_logger')
	def test_sets_up_gui_logger(self, mock_setup_gui_logger):
		"""
		Make sure the gui logger is setup when starting UH with --gui-log.

		We need some tricks here because horizons.main has some inline imports that would
		trigger the normal Fife setup. By mocking setup_gui_logger with a special
		exception, we quit the startup process but can still assert that is was called.
		"""
		mock_setup_gui_logger.side_effect = Exception('i was called')

		with self.assertRaisesRegex(Exception, 'i was called'):
			self.start_game('--gui-log')

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_scenario_by_name(self, mock_start_singleplayer):
		"""
		Test that a specific scenario given by name can be started from the command line.
		"""
		instance = self.mock_fife.return_value
		instance.get_locale.return_value = 'de'

		self.start_game('--start-scenario', 'tutorial')

		options = mock_start_singleplayer.call_args[0][0]
		assert options.is_scenario
		assert not options.is_map
		assert not options.is_editor
		assert options.game_identifier == 'content/scenarios/tutorial_de.yaml'

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_scenario_by_path(self, mock_start_singleplayer):
		"""
		Test that a specific scenario given by path can be started from the command line.
		"""
		self.start_game('--start-scenario', 'content/scenarios/tutorial_uk.yaml')

		options = mock_start_singleplayer.call_args[0][0]
		assert options.is_scenario
		assert not options.is_map
		assert not options.is_editor
		assert options.game_identifier == 'content/scenarios/tutorial_uk.yaml'

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_map_by_name(self, mock_start_singleplayer):
		"""
		Test that a game with a specific map given by name can be started from the command line.
		"""
		self.start_game('--start-map', 'development')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert not options.is_editor
		assert options.game_identifier == 'content/maps/development.sqlite'

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_map_by_path(self, mock_start_singleplayer):
		"""
		Test that a game with a specific map given by path can be started from the command line.
		"""
		self.start_game('--start-map', 'content/maps/full-house.sqlite')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert not options.is_editor
		assert options.game_identifier == 'content/maps/full-house.sqlite'

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_dev_map(self, mock_start_singleplayer):
		"""
		Test that a game with the development map can be started from the command line.
		"""
		self.start_game('--start-dev-map')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert not options.is_editor
		assert options.game_identifier == 'content/maps/development.sqlite'

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_random_map(self, mock_start_singleplayer):
		"""
		Test that a game with a random map can be started from the command line.
		"""
		self.start_game('--start-random-map')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert not options.is_editor
		assert options.game_identifier == generate_map_from_seed(None)

	@mock.patch('horizons.main.start_singleplayer')
	def test_start_specific_random_map(self, mock_start_singleplayer):
		"""
		Test that a game with a random map and a specific seed can be started from the command line.
		"""
		self.start_game('--start-specific-random-map', 'custom-seed')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert not options.is_editor
		assert options.game_identifier == generate_map_from_seed('custom-seed')

	@mock.patch('horizons.main.start_singleplayer')
	def test_edit_map_by_name(self, mock_start_singleplayer):
		"""
		Test that a specific map given by name can be loaded into the editor from the command line.
		"""
		self.start_game('--edit-map', 'development')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert options.is_editor
		assert options.game_identifier == 'content/maps/development.sqlite'

	@mock.patch('horizons.main.start_singleplayer')
	def test_edit_map_by_path(self, mock_start_singleplayer):
		"""
		Test that a specific map given by path can be loaded into the editor from the command line.
		"""
		self.start_game('--edit-map', 'content/maps/full-house.sqlite')

		options = mock_start_singleplayer.call_args[0][0]
		assert not options.is_scenario
		assert options.is_map
		assert options.is_editor
		assert options.game_identifier == 'content/maps/full-house.sqlite'

	# NOTE These tests are a bit tricky since we need to place a save file into
	# the user directory. SavegameManager initializes the paths during import,
	# therefore we can't just override the user dir to point to a temporary
	# directory.

	def test_load_game_by_name(self):
		raise SkipTest("Not implemented")

	def test_load_game_by_path(self):
		raise SkipTest("Not implemented")

	def test_edit_game_map_by_name(self):
		raise SkipTest("Not implemented")

	def test_edit_game_map_by_path(self):
		raise SkipTest("Not implemented")