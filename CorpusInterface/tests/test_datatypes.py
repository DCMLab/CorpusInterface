from unittest import TestCase
from CorpusInterface.datatypes import Point, Pitch, Time
from CorpusInterface.datatypes import MIDIPitch, MIDIPitchInterval, MIDIPitchClass, MIDIPitchClassInterval
import numpy as np


class TestPoint(TestCase):

    def test_create_vector_class(self):

        # check for different derived base types
        for Base in [Point, Pitch]:

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
                        self.assertRaises(AttributeError, lambda: NewBase.create_interval_class())
                        # assert overwriting can be forced
                        @NewBase.link_interval_class(force_overwrite=True)
                        class NewBaseInterval(Pitch.Interval):
                            pass

                        # check class assignment
                        self.assertEqual(NewBase._vector_class, NewBaseInterval)
                        self.assertEqual(NewBaseInterval._point_class, NewBase)

                        # create interval objects
                        i1 = NewBaseInterval(np.random.randint(-10, 10))
                        i2 = NewBaseInterval(np.random.randint(-10, 10))

                        # check class
                        self.assertEqual(i1.__class__, NewBaseInterval)
                        # check name attribute was set correctly
                        self.assertEqual(i1.__class__.__name__, "NewBaseInterval")

                        # interval class corresponds to vector class below
                        NewBaseVector = NewBaseInterval
                    elif Base == Time:
                        # create duration class
                        NewBase.create_duration_class()
                        # assert second call raises an error
                        self.assertRaises(AttributeError, lambda: NewBase.create_duration_class())
                        # assert overwriting can be forced
                        NewBaseDuration = NewBase.create_duration_class(force_overwrite=True)

                        # check class assignment
                        self.assertEqual(NewBase._vector_class, NewBaseDuration)
                        self.assertEqual(NewBaseDuration._point_class, NewBase)

                        # create duration objects
                        i1 = NewBaseDuration(np.random.randint(-10, 10))
                        i2 = NewBaseDuration(np.random.randint(-10, 10))

                        # check class
                        self.assertEqual(i1.__class__, NewBaseDuration)
                        # check name attribute was set correctly
                        self.assertEqual(i1.__class__.__name__, "NewBaseDuration")

                        # duration class corresponds to vector class below
                        NewBaseVector = NewBaseDuration
                    else:
                        # create vector class
                        @NewBase.link_vector_class()
                        class NewBaseVector(Point.Vector):
                            pass
                        # assert second call raises an error
                        self.assertRaises(AttributeError, lambda: NewBase.create_vector_class())
                        # assert overwriting can be forced
                        @NewBase.link_vector_class(force_overwrite=True)
                        class NewBaseVector(Point.Vector):
                            pass

                        # check class assignment
                        self.assertEqual(NewBase._vector_class, NewBaseVector)
                        self.assertEqual(NewBaseVector._point_class, NewBase)

                        # create vector objects
                        i1 = NewBaseVector(np.random.randint(-10, 10))
                        i2 = NewBaseVector(np.random.randint(-10, 10))

                        # check class
                        self.assertEqual(i1.__class__, NewBaseVector)
                        # check name attribute was set correctly
                        self.assertEqual(i1.__class__.__name__, "NewBaseVector")

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
            self.assertEqual(MIDIPitchClass(from_flat), MIDIPitchClass(midi_number % 12))
            self.assertEqual(MIDIPitchClass(from_sharp), MIDIPitchClass(midi_number % 12))

    def test_freq(self):
        self.assertEqual(MIDIPitch("A4").freq(), 440)
        self.assertEqual(MIDIPitch("A5").freq(), 880)

    def test_arithmetics(self):
        c4 = MIDIPitch("C4")
        g4 = MIDIPitch("G4")
        i = MIDIPitchInterval(-7)
        self.assertEqual(c4 - g4, i)
        self.assertEqual(i.convert_to(MIDIPitchClassInterval), MIDIPitchClassInterval(5))
        self.assertEqual(i.convert_to(MIDIPitchClassInterval), MIDIPitchClassInterval(i))


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
            pass

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
            pass

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
