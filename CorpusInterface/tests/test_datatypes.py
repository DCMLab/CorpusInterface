from unittest import TestCase
from CorpusInterface.datatypes import Point, Pitch, Time
from CorpusInterface.datatypes import MIDIPitch, MIDIPitchInterval
from CorpusInterface.datatypes import LogFreqPitch
import numpy as np


class TestPoint(TestCase):

    def test_create_vector_class(self):

        # check for different derived base types
        for Base in [Point, Pitch, Time]:

            # check operations/failure for both cases
            for with_vector in [True, False]:

                # create derived point class
                class NewBase(Base):
                    pass

                # create point objects
                p1 = NewBase(np.random.randint(-10, 10))
                p2 = NewBase(np.random.randint(-10, 10))

                if with_vector:

                    if Base == Pitch:
                        # create interval class
                        @NewBase.link_interval_class()
                        class NewBaseInterval(Pitch.Interval):
                            pass
                        # assert second call raises an error
                        try:
                            @NewBase.link_interval_class()
                            class NewBaseInterval(Pitch.Interval):
                                pass
                        except AttributeError:
                            pass
                        else:
                            self.fail("Should have raise AttributeError")
                        # assert overwriting can be forced
                        @NewBase.link_interval_class(overwrite_interval_class=True)
                        class NewBaseInterval(Pitch.Interval):
                            pass

                        # check class assignment
                        self.assertEqual(NewBase._vector_class, NewBaseInterval)
                        self.assertEqual(NewBaseInterval._point_class, NewBase)

                        # create interval objects
                        i1 = NewBaseInterval(np.random.randint(-10, 10))
                        i2 = NewBaseInterval(np.random.randint(-10, 10))

                        # interval class corresponds to vector class below
                        NewBaseVector = NewBaseInterval
                    elif Base == Time:
                        # create duration class
                        @NewBase.link_duration_class()
                        class NewBaseDuration(Time.Duration):
                            pass
                        # assert second call raises an error
                        try:
                            @NewBase.link_duration_class()
                            class NewBaseDuration(Time.Duration):
                                pass
                        except AttributeError:
                            pass
                        else:
                            self.fail("Should have raise AttributeError")
                        # assert overwriting can be forced
                        @NewBase.link_duration_class(overwrite_duration_class=True)
                        class NewBaseDuration(Time.Duration):
                            pass

                        # check class assignment
                        self.assertEqual(NewBase._vector_class, NewBaseDuration)
                        self.assertEqual(NewBaseDuration._point_class, NewBase)

                        # create duration objects
                        i1 = NewBaseDuration(np.random.randint(-10, 10))
                        i2 = NewBaseDuration(np.random.randint(-10, 10))

                        # duration class corresponds to vector class below
                        NewBaseVector = NewBaseDuration
                    else:
                        # create vector class
                        @NewBase.link_vector_class()
                        class NewBaseVector(Point.Vector):
                            pass
                        # assert second call raises an error
                        try:
                            @NewBase.link_vector_class()
                            class NewBaseVector(Point.Vector):
                                pass
                        except AttributeError:
                            pass
                        else:
                            self.fail("Should have raise AttributeError")
                        # assert overwriting can be forced
                        @NewBase.link_vector_class(overwrite_vector_class=True)
                        class NewBaseVector(Point.Vector):
                            pass

                        # check class assignment
                        self.assertEqual(NewBase._vector_class, NewBaseVector)
                        self.assertEqual(NewBaseVector._point_class, NewBase)

                        # create vector objects
                        i1 = NewBaseVector(np.random.randint(-10, 10))
                        i2 = NewBaseVector(np.random.randint(-10, 10))

                    # transform a point to an vector and vice versa
                    self.assertEqual(NewBaseVector(p1._value), p1.to_vector())
                    self.assertEqual(NewBase(i1._value), i1.to_point())

                    # check basic operations (all combinations of point/vector and +/-; multiplication for vectors)
                    self.assertRaises(TypeError, lambda: p1 + p2)
                    self.assertEqual(p1 - p2, NewBaseVector(p1._value - p2._value))
                    self.assertEqual(i1 + i2, NewBaseVector(i1._value + i2._value))
                    self.assertEqual(i1 - i2, NewBaseVector(i1._value - i2._value))
                    self.assertEqual(p1 + i1, NewBase(p1._value + i1._value))
                    self.assertEqual(p1 - i1, NewBase(p1._value - i1._value))
                    self.assertRaises(TypeError, lambda: i1 + p1)
                    self.assertRaises(TypeError, lambda: i1 - p1)
                    self.assertEqual(2 * i1, NewBaseVector(2 * i1._value))
                    self.assertEqual(i1 * 2, NewBaseVector(2 * i1._value))
                else:
                    self.assertRaises(AttributeError, lambda: p1 + p2)
                    self.assertRaises(AttributeError, lambda: p1 - p2)
                    self.assertRaises(AttributeError, lambda: p1.to_vector())


class TestMIDIPitch(TestCase):

    def test_init(self):
        for p in ["C5", "B#4", "A###4", "Dbb5"]:
            self.assertEqual(MIDIPitch(p), MIDIPitch(72))
        for p in ["C5-", "B#b", "c5"]:
            self.assertRaises(ValueError, lambda: MIDIPitch(p))
        for midi_name_sharp, midi_name_flat, midi_number in zip(
                ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                 "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",],
                ["C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4", "A4", "Bb4", "B4",
                 "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5", "A5", "Bb5", "B5",],
                range(60, 85)
        ):
            from_flat = MIDIPitch(midi_name_flat)
            from_sharp = MIDIPitch(midi_name_sharp)
            from_number = MIDIPitch(midi_number)
            self.assertEqual(from_flat, from_number)
            self.assertEqual(from_sharp, from_number)
            self.assertEqual(midi_number, int(from_number))
            self.assertEqual(from_flat.to_pitch_class()._value, midi_number % 12)
            self.assertEqual(from_sharp.to_pitch_class()._value, midi_number % 12)

    def test_freq(self):
        self.assertEqual(MIDIPitch("A4").freq(), 440)
        self.assertEqual(MIDIPitch("A5").freq(), 880)

    def test_arithmetics(self):
        c4 = MIDIPitch("C4")
        d4 = MIDIPitch("D4")
        g4 = MIDIPitch("G4")
        icg = c4 - g4
        idc = d4 - c4
        self.assertEqual(icg, MIDIPitchInterval(-7))
        self.assertEqual(idc, MIDIPitchInterval(2))

        pc_c4 = c4.to_pitch_class()
        pc_d4 = d4.to_pitch_class()
        pc_g4 = g4.to_pitch_class()
        pci_cg = pc_c4 - pc_g4
        pci_dc = pc_d4 - pc_c4

        self.assertEqual(icg.to_interval_class(), MIDIPitchInterval(icg, is_interval_class=True))

        self.assertEqual(pci_cg, MIDIPitchInterval(5, is_interval_class=True))
        self.assertEqual(pci_cg, MIDIPitchInterval(-7, is_interval_class=True))
        self.assertEqual(pci_cg._value, 5)

        self.assertEqual(pci_dc, MIDIPitchInterval(2, is_interval_class=True))
        self.assertEqual(pci_dc, MIDIPitchInterval(-10, is_interval_class=True))
        self.assertEqual(int(pci_dc), 2)

        self.assertEqual(pc_c4.phase(), 0)
        self.assertEqual(pc_g4.phase(), 7 / 12)
        self.assertEqual(pc_d4.phase(), 2 / 12)

        self.assertEqual(pci_cg.phase_diff(), 5 / 12)
        self.assertEqual(pci_dc.phase_diff(), 2 / 12)


class TestLogFreqPitch(TestCase):

    def test_against_MIDI(self):
        c4 = MIDIPitch("C4")
        d4 = MIDIPitch("D4")
        lc4 = c4.convert_to(LogFreqPitch)
        ld4 = d4.convert_to(LogFreqPitch)
        pci = d4.to_pitch_class() - c4.to_pitch_class()
        pci_ = pci
        lpci = ld4.to_pitch_class() - lc4.to_pitch_class()
        lpci_ = lpci
        for _ in range(12):
            # cannot use simple equality check because special case -0.5 and 0.5 have to evaluate to equal, too
            # same point on unit circle (e.g. 0.2 == -0.8)
            self.assertAlmostEqual(pci_.phase_diff() % 1, lpci_.phase_diff() % 1)
            # same magnitude (e.g. 0.2 == -0.2)
            self.assertAlmostEqual(abs(pci_.phase_diff()), abs(lpci_.phase_diff()))
            pci_ = pci_ + pci
            lpci_ = lpci_ + lpci


class TestConverters(TestCase):

    def test_converters(self):
        # define classes A and B with a converter A-->B
        class PitchA(Pitch):
            """Use integer representation: 5 --> 5"""
            def __init__(self, value, *args, **kwargs):
                super().__init__(int(value), *args, **kwargs)
        @PitchA.link_interval_class()
        class PitchAInterval(Pitch.Interval):
            pass

        class PitchB(Pitch):
            """Use string representation: 5 --> '5'"""
            @staticmethod
            def convert_to_PitchA(pitch_b):
                return PitchA(int(pitch_b._value))
            @staticmethod
            def _point_sub(p1, p2):
                return int(p1) - int(p2)
            def __init__(self, value, *args, **kwargs):
                super().__init__(str(value), *args, **kwargs)
            def to_vector(self):
                return self._vector_class(int(self._value))
        Pitch.register_converter(PitchB, PitchA, PitchB.convert_to_PitchA)
        @PitchB.link_interval_class()
        class PitchBInterval(Pitch.Interval):
            @staticmethod
            def _vector_sub(vec1, vec2):
                return str(int(vec1) - int(vec2))
            @staticmethod
            def _vector_add(vec1, vec2):
                return str(int(vec1) + int(vec2))

        # instantiate objects and check (in)equality and conversion)
        a = PitchA(5)
        ai = a.to_interval()
        b = PitchB("5")
        bi = b.to_interval()
        self.assertNotEqual(a, b)
        self.assertNotEqual(ai, bi)
        self.assertEqual(a, b.convert_to(PitchA))
        self.assertEqual(ai, bi.convert_to(PitchAInterval))

        # define another class C with converter C-->A
        class PitchC(Pitch):
            """Use list representation: 5 --> [0, 0, 0, 0, 0]"""
            @staticmethod
            def convert_to_PitchB(pitch_c):
                return PitchB(str(len(pitch_c._value)))
            @staticmethod
            def _point_sub(p1, p2):
                return [0] * (len(p1) - len(p2))
            def __init__(self, value, *args, **kwargs):
                if isinstance(value, int):
                    value = [0] * value
                super().__init__(value, *args, **kwargs)
            def to_vector(self):
                return self._vector_class(len(self._value))
        @PitchC.link_interval_class()
        class PitchCInterval(Pitch.Interval):
            @staticmethod
            def _vector_sub(vec1, vec2):
                return [0] * (len(vec1) - len(vec2))
            @staticmethod
            def _vector_add(vec1, vec2):
                return [0] * (len(vec1) + len(vec2))

        # instantiate object and check (in)equality
        c = PitchC([0, 0, 0, 0, 0])
        ci = c.to_interval()
        self.assertNotEqual(b, c)
        self.assertNotEqual(bi, ci)
        self.assertNotEqual(c, a)
        self.assertNotEqual(ci, ai)

        # register without and with extending implicit converters and check conversion
        for extend_implicit_converters in [False, True]:
            # we avoid an error on the second registration we use give an explicit value to
            # overwrite_explicit_converters (could also be True, just not None)
            Pitch.register_converter(PitchC, PitchB, PitchC.convert_to_PitchB,
                                     extend_implicit_converters=extend_implicit_converters,
                                     overwrite_explicit_converters=False)
            self.assertEqual(b, c.convert_to(PitchB))
            self.assertEqual(bi, ci.convert_to(PitchBInterval))
            if not extend_implicit_converters:
                # should NOT be created implicitly
                self.assertRaises(NotImplementedError, lambda: c.convert_to(PitchA))
                self.assertRaises(NotImplementedError, lambda: ci.convert_to(PitchAInterval))
            else:
                # SHOULD be created implicitly
                self.assertEqual(c.convert_to(PitchA), a)
                self.assertEqual(ci.convert_to(PitchAInterval), ai)

        # define a direct converter C-->A which returns a version scaled by 10
        # (to detect whether the old or now converter was used)
        def direct_but_wrong_converter_from_C_to_A(c):
            return PitchA(10 * len(c._value))
        # check again that the implicit converter exists
        self.assertEqual(c.convert_to(PitchA), a)
        self.assertEqual(ci.convert_to(PitchAInterval), ai)
        # register the converter, which should replace the existing implicit converter
        Pitch.register_converter(PitchC, PitchA, direct_but_wrong_converter_from_C_to_A)

        # check
        self.assertEqual(type(a), type(c.convert_to(PitchA)))
        self.assertEqual(type(ai), type(ci.convert_to(PitchAInterval)))
        self.assertNotEqual(a, c.convert_to(PitchA))
        self.assertNotEqual(ai, ci.convert_to(PitchAInterval))
        self.assertEqual(PitchA(50), c.convert_to(PitchA))
        self.assertEqual(PitchAInterval(50), ci.convert_to(PitchAInterval))

        # trying to re-register should raise a ValueError because a direct converter now exists
        self.assertRaises(ValueError,
                          lambda: Pitch.register_converter(PitchC, PitchA, direct_but_wrong_converter_from_C_to_A))
        # but overwriting can be forced
        Pitch.register_converter(PitchC, PitchA, direct_but_wrong_converter_from_C_to_A,
                                 overwrite_explicit_converters=True)
