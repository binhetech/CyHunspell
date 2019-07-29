#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import unittest

if sys.version_info >= (3, 0):
    PY3 = True
    from unittest.mock import patch
    from io import StringIO
else:
    PY3 = False
    from mock import patch
    from StringIO import StringIO

from contextlib import contextmanager
from cacheman.cacher import get_cache_manager
from hunspell import Hunspell, HunspellFilePathError

DICT_DIR = os.path.join(os.path.dirname(__file__), '..', 'dictionaries')


@contextmanager
def captured_c_stderr_file():
    '''
    Handles flipping the stderr file descriptor to a temp file and back.
    This is the only way to capture stderr messages sent by Hunspell.

    Yields: path to the captured stderr file
    '''
    old_err = sys.stderr
    try:
        sys.stderr.flush()
        new_err = os.dup(sys.stderr.fileno()) # Clone the err file handler

        # Can't use tempdir context because os.dup2 needs a filename
        temp_dir = tempfile.mkdtemp()
        temp_name = os.path.join(temp_dir, 'errcap')
        with open(temp_name, 'a'):
            os.utime(temp_name, None)
        temp_file = os.open(temp_name, os.O_WRONLY)
        os.dup2(temp_file, 2)
        os.close(temp_file)
        sys.stderr = os.fdopen(new_err, 'w')
        yield temp_name
    finally:
        try:
            try:
                os.close(temp_file)
            except:
                pass
            shutil.rmtree(temp_dir) # Nuke temp content
        except:
            pass
        sys.stderr = old_err # Reset back
        os.dup2(sys.stderr.fileno(), 2)

class HunspellTest(unittest.TestCase):
    def assertRegexpSearch(self, *args, **kwargs):
        if PY3:
            self.assertRegex(*args, **kwargs)
        else:
            self.assertRegexpMatches(*args, **kwargs)

    def setUp(self):
        self.h = Hunspell('test', hunspell_data_dir=DICT_DIR)

    def tearDown(self):
        try:
            del self.h
        except AttributeError:
            pass

    def assertAllIn(self, checked, expected):
        self.assertTrue(all(x in expected for x in checked),
            u"{} not all found in {}".format(checked, expected))

    def test_create_destroy(self):
        del self.h

    def test_missing_dict(self):
        with self.assertRaises(HunspellFilePathError):
            Hunspell('not_avail', hunspell_data_dir=DICT_DIR)

    @patch('os.path.isfile', return_value=True)
    @patch('os.access', return_value=True)
    def test_bad_path_encoding(self, *mocks):
        if PY3:
            with self.assertRaises(HunspellFilePathError):
                Hunspell('not_checked',
                    hunspell_data_dir=u'bad/\udcc3/decoding')
        else:
            # Python 2 just make an illegal string instead of raising
            with captured_c_stderr_file() as caperr:
                Hunspell('not_checked',
                    hunspell_data_dir=u'bad/\udcc3/decoding')
                with open(caperr, 'r') as err:
                    self.assertRegexpSearch(err.read(), r'error:[^\n]*bad/[^\n]*/decoding')

    @patch('hunspell.hunspell.WIN32_LONG_PATH_PREFIX', '/not/valid')
    def test_windows_utf_8_encoding_applies_prefix(self, *mocks):
        with captured_c_stderr_file() as caperr:
            with patch("os.name", 'nt'):
                # If python file existance checks used prefix, this would raise a HunspellFilePathError
                Hunspell('test', system_encoding='UTF-8')
            with open(caperr, 'r') as err:
                # But the Hunspell library lookup had the prefix applied
                self.assertRegexpSearch(err.read(), r'error:[^\n]*/not/valid[^\n]*')

    def test_spell(self):
        self.assertFalse(self.h.spell('dpg'))
        self.assertTrue(self.h.spell('dog'))

    def test_spell_utf8(self):
        self.assertTrue(self.h.spell(u'café'))
        self.assertFalse(self.h.spell(u'uncafé'))

    def test_spell_empty(self):
        self.assertTrue(self.h.spell(''))

    def test_suggest(self):
        required = ('dog', 'pg', 'deg', 'dig', 'dpt', 'dug', 'mpg', 'd pg')
        suggest = self.h.suggest('dpg')
        self.assertIsInstance(suggest, tuple)
        self.assertAllIn(required, suggest)

    def test_suggest_utf8(self):
        required = (u'café', u'Cerf')
        for variant in ('cefé', u'cefé'):
            suggest = self.h.suggest(variant)
            self.assertIsInstance(suggest, tuple)
            self.assertAllIn(required, suggest)

    def test_suggest_empty(self):
        self.assertEqual(self.h.suggest(''), ())

    def test_stem(self):
        self.assertEqual(self.h.stem('dog'), ('dog',))
        self.assertEqual(self.h.stem('permanently'), ('permanent',))

    def test_bulk_suggest(self):
        self.h.set_concurrency(3)
        suggest = self.h.bulk_suggest(['dog', 'dpg'])
        self.assertEqual(sorted(suggest.keys()), ['dog', 'dpg'])
        self.assertIsInstance(suggest['dog'], tuple)
        self.assertAllIn(('dog',), suggest['dog'])

        required = ('dog', 'pg', 'deg', 'dig', 'dpt', 'dug', 'mpg', 'd pg')
        self.assertIsInstance(suggest['dpg'], tuple)
        self.assertAllIn(required, suggest['dpg'])

        checked = ['bjn', 'dog', 'dpg', 'dyg', 'foo', 'frg', 'opg', 'pgg', 'qre', 'twg']
        suggest = self.h.bulk_suggest(checked)
        self.assertEqual(sorted(suggest.keys()), checked)

    def test_bulk_stem(self):
        self.h.set_concurrency(3)
        self.assertDictEqual(self.h.bulk_stem(['dog', 'permanently']), {
            'permanently': ('permanent',),
            'dog': ('dog',)
        })
        self.assertDictEqual(self.h.bulk_stem(['dog', 'twigs', 'permanently', 'unrecorded']), {
            'unrecorded': ('recorded',),
            'permanently': ('permanent',),
            'twigs': ('twig',),
            'dog': ('dog',)
        })

    def test_non_overlapping_caches(self):
        test_suggest = self.h.suggest('testing')
        test_stem = self.h.stem('testing')

        self.h._suggest_cache['made-up'] = test_suggest
        self.assertEqual(self.h.suggest('made-up'), test_suggest)
        self.h._stem_cache['made-up'] = test_stem
        self.assertEqual(self.h.stem('made-up'), test_stem)

        h2 = Hunspell('en_US', hunspell_data_dir=DICT_DIR)
        self.assertNotEqual(h2.suggest('made-up'), test_suggest)
        self.assertNotEqual(h2.stem('made-up'), test_stem)

    def test_overlapping_caches(self):
        test_suggest = self.h.suggest('testing')
        test_stem = self.h.stem('testing')

        self.h._suggest_cache['made-up'] = test_suggest
        self.assertEqual(self.h.suggest('made-up'), test_suggest)
        self.h._stem_cache['made-up'] = test_stem
        self.assertEqual(self.h.stem('made-up'), test_stem)

        del self.h
        self.h = Hunspell('test', hunspell_data_dir=DICT_DIR)
        self.assertEqual(self.h.suggest('made-up'), test_suggest)
        self.assertEqual(self.h.stem('made-up'), test_stem)

    def test_save_caches_persistance(self):
        temp_dir = tempfile.mkdtemp()
        try:
            h1 = Hunspell('test',
                hunspell_data_dir=DICT_DIR,
                disk_cache_dir=temp_dir,
                cache_manager='disk_hun')
            test_suggest = h1.suggest('testing')
            test_stem = h1.stem('testing')

            h1._suggest_cache['made-up'] = test_suggest
            self.assertEqual(h1.suggest('made-up'), test_suggest)
            h1._stem_cache['made-up'] = test_stem
            self.assertEqual(h1.stem('made-up'), test_stem)

            h1.save_cache()
            del h1

            cacheman = get_cache_manager('disk_hun')
            cacheman.deregister_all_caches()
            self.assertEqual(len(cacheman.cache_by_name), 0)

            h2 = Hunspell('test',
                hunspell_data_dir=DICT_DIR,
                disk_cache_dir=temp_dir,
                cache_manager='disk_hun')

            self.assertNotEqual(len(h2._suggest_cache), 0)
            self.assertNotEqual(len(h2._stem_cache), 0)
            self.assertEqual(h2.suggest('made-up'), test_suggest)
            self.assertEqual(h2.stem('made-up'), test_stem)
        finally:
            shutil.rmtree(temp_dir) # Nuke temp content

    def test_clear_caches_persistance(self):
        temp_dir = tempfile.mkdtemp()
        try:
            h1 = Hunspell('test',
                hunspell_data_dir=DICT_DIR,
                disk_cache_dir=temp_dir,
                cache_manager='disk_hun')
            test_suggest = h1.suggest('testing')
            test_stem = h1.stem('testing')

            h1._suggest_cache['made-up'] = test_suggest
            self.assertEqual(h1.suggest('made-up'), test_suggest)
            h1._stem_cache['made-up'] = test_stem
            self.assertEqual(h1.stem('made-up'), test_stem)

            h1.save_cache()
            h1.clear_cache()
            del h1

            cacheman = get_cache_manager('disk_hun')
            cacheman.deregister_all_caches()
            self.assertEqual(len(cacheman.cache_by_name), 0)

            h2 = Hunspell('test',
                hunspell_data_dir=DICT_DIR,
                disk_cache_dir=temp_dir,
                cache_manager='disk_hun')

            self.assertEqual(len(h2._suggest_cache), 0)
            self.assertEqual(len(h2._stem_cache), 0)
            self.assertNotEqual(h2.suggest('made-up'), test_suggest)
            self.assertNotEqual(h2.stem('made-up'), test_stem)
        finally:
            shutil.rmtree(temp_dir) # Nuke temp content

    def test_clear_caches_non_peristance(self):
        test_suggest = self.h.suggest('testing')
        test_stem = self.h.stem('testing')

        self.h._suggest_cache['made-up'] = test_suggest
        self.assertEqual(self.h.suggest('made-up'), test_suggest)
        self.h._stem_cache['made-up'] = test_stem
        self.assertEqual(self.h.stem('made-up'), test_stem)

        self.h.clear_cache()

        del self.h
        self.h = Hunspell('test', hunspell_data_dir=DICT_DIR)
        self.assertNotEqual(self.h.suggest('made-up'), test_suggest)
        self.assertNotEqual(self.h.stem('made-up'), test_stem)

if __name__ == '__main__':
    unittest.main()
