from unittest import TestCase
from corpus_interface.datatypes import Point, Pitch, Time
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
                        NewBase.create_interval_class()
                        # assert second call raises an error
                        self.assertRaises(AttributeError, lambda: NewBase.create_interval_class())
                        # assert overwriting can be forced
                        NewBaseInterval = NewBase.create_interval_class(force_overwrite=True)

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
                        NewBase.create_vector_class()
                        # assert second call raises an error
                        self.assertRaises(AttributeError, lambda: NewBase.create_vector_class())
                        # assert overwriting can be forced
                        NewBaseVector = NewBase.create_vector_class(force_overwrite=True)

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
