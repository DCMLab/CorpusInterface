from unittest import TestCase
from CorpusInterface.datatypes import LinearTime, LogFreqPitch, EnharmonicPitch
from CorpusInterface.util import chordify, linspace, prange
from CorpusInterface.readers import read_midi
import numpy as np
import unittest


class TestChordify(TestCase):

    def test_chordify(self):
        piece = read_midi('CorpusInterface/tests/chordify_test.mid', quantise=1 / 32)
        # for p in piece:
        #     print(p)
        # print("")
        chordified_piece = chordify(piece)
        # for c in chordified_piece:
        #     print(c)
        # print("")
        self.assertEqual(len(chordified_piece), 5)
        self.assertEqual([float(e.time) for e in chordified_piece], [0., 1., 2., 3.5, 3.75])
        self.assertEqual([float(e.duration) for e in chordified_piece], [1., 1., 1.5, 0.25, 6.25])


class TestLinspace(TestCase):

    def test_against_numpy(self):
        for _ in range(10):
            for t in [np.float, LinearTime, LogFreqPitch]:
                start, stop = tuple(sorted(np.random.uniform(-20, 20, 2)))
                num = np.random.randint(2, 20)
                endpoint, retstep = np.random.randint(0, 2, 2).astype(bool)
                np_linspace = np.linspace(start=start, stop=stop, num=num, endpoint=endpoint, retstep=retstep)
                util_linspace = linspace(start=t(start), stop=t(stop), num=num, endpoint=endpoint, retstep=retstep)
                self.assertEqual(len(np_linspace), len(util_linspace))
                if retstep:
                    np_samples, np_step = np_linspace
                    util_samples, util_step = util_linspace
                else:
                    np_step = 0
                    util_step = 0
                    np_samples = np_linspace
                    util_samples = util_linspace
                util_samples = [float(s) for s in util_samples]
                util_step = float(util_step)
                np.testing.assert_array_almost_equal(np_step, util_step)
                np.testing.assert_array_almost_equal(np_samples, util_samples)


class TestPrange(TestCase):

    def test_against_range(self):
        for _ in range(10):
            for t in [int, EnharmonicPitch]:
                start, stop = tuple(sorted(np.random.randint(-20, 20, 2)))
                step = np.random.choice([-3, -2, -1, None, 1, 2, 3])
                if step is not None and step < 0:
                    start, stop = stop, start
                endpoint = np.random.randint(0, 2, 1).astype(bool)
                if step is None:
                    range_based = list(range(start, stop))
                else:
                    range_based = list(range(start, stop, step))
                prange_based = [int(p) for p in prange(start=start, stop=stop, step=step, endpoint=endpoint)]
                try:
                    if endpoint and (step is None or (stop - start) % step == 0):
                        self.assertEqual(range_based, prange_based[:-1])
                        self.assertEqual(prange_based[-1], stop)
                    else:
                        self.assertEqual(range_based, prange_based)
                except:
                    raise
