import re
import numpy as np
import numbers
from functools import total_ordering


@total_ordering
class Point:
    """
    Base class for objects describing a point in a space. Examples would be a pitch, a point in time, or a point in
    Euclidean space. The purpose of this class is to make developing and maintaining these kinds of classes convenient
    by providing basic functionality, like a one-liner to create the associated vector class and basic arithmetic
    operations (see Vector class). Otherwise, the abstract Point class is just a wrapper around some value. The
    semantics of this value and any extended functionality is defined via the derived classes.
    """

    _vector_class = None

    @classmethod
    def link_vector_class(point_class, *, overwrite_point_class=None, overwrite_vector_class=None):
        """
        Class decorator to link 'point_class' and the specified vector class by adding _vector_class and _point_class
        attribute, respectively. Raises an error if one of the classes already has the corresponding attribute, which
        would be overwritten. Overwriting can be forced, which is for instance needed when linking a vector class to a
        point class that was derived from another point class, which already has an associated vector class.
        :param overwrite_point_class: if None (default), adds a point class to the vector class if is does not already
        have one and raises an AttributeError otherwise; if False, never adds a point class to the vector class; if
        True, always adds a point class to the vector class (possibly overwriting an existing one)
        :param overwrite_vector_class: if None (default), adds a vector class to the point class if is does not already
        have one and raises an AttributeError otherwise; if False, never adds a vector class to the point class; if
        True, always adds a vector class to the point class (possibly overwriting an existing one)
        """
        def decorator(vector_class):
            """
            :param vector_class: vector class to be linked (will be modified by adding the _point_class attribute)
            :return: modified vector_class
            """
            # check that provided class is actually derived from Vector
            if Vector not in vector_class.__mro__:
                raise TypeError(f"Provided class {vector_class} does not derive from {Vector}")
            # check if point class already has an associated vector class
            if overwrite_vector_class is None and point_class._vector_class is not None:
                raise AttributeError(
                    f"Class '{point_class}' already has an associated vector class ({point_class._vector_class})")
            # check if vector class already has an associated point class
            if overwrite_point_class is None and vector_class._point_class is not None:
                raise AttributeError(
                    f"Class '{vector_class}' already has an associated point class ({vector_class._point_class})")
            # let the point class know its vector class and vice versa
            if overwrite_vector_class is None or overwrite_vector_class:
                point_class._vector_class = vector_class
            if overwrite_point_class is None or overwrite_point_class:
                vector_class._point_class = point_class
            return vector_class
        return decorator

    @classmethod
    def _assert_has_vector_class(cls):
        if cls._vector_class is None:
            raise AttributeError(f"This class ({cls}) does not have an associated vector class")

    @classmethod
    def _assert_is_point(cls, other):
        if not isinstance(other, cls):
            raise TypeError(f"Object is not of correct type (expected {cls}, got {type(other)}")

    @classmethod
    def _assert_is_vector(cls, other):
        if not isinstance(other, cls._vector_class):
            raise TypeError(f"Object is not of correct type (expected {cls._vector_class}, got {type(other)}")

    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __sub__(self, other):
        self._assert_has_vector_class()
        try:
            self._assert_is_point(other)
            return self._vector_class(self._value - other._value)
        except TypeError:
            self._assert_is_vector(other)
            return self.__class__(self._value - other._value)

    def __add__(self, other):
        self._assert_has_vector_class()
        self._assert_is_vector(other)
        return self.__class__(self._value + other._value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return self._value < other._value

    def to_vector(self):
        self._assert_has_vector_class()
        return self._vector_class(self._value)


@total_ordering
class Vector:
    """
    Base class for objects describing direction and magnitude in a space. A class derived from Vector should have an
    associated Point class and should be defined via the Point class' create_vector_class method, which will also
    take care of letting both classes know of each other. Creating multiple Vector class for the same Point class
    is likely to cause trouble, but you can force it if feel that you absolutely need to.
    """

    _point_class = None

    @classmethod
    def _assert_has_point_class(cls):
        if cls._point_class is None:
            raise AttributeError(f"This class ({cls}) does not have an associated point class")

    @classmethod
    def _assert_is_vector(cls, other):
        if not isinstance(other, cls):
            raise TypeError(f"Object is not of correct type (expected {cls}, got {type(other)}")

    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __sub__(self, other):
        self._assert_is_vector(other)
        return self.__class__(self._value - other._value)

    def __add__(self, other):
        self._assert_is_vector(other)
        return self.__class__(self._value + other._value)

    def __mul__(self, other):
        return self.__class__(self._value * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.__class__(self.__mul__(1 / other))

    def __abs__(self):
        return abs(self._value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return self._value < other._value

    def to_point(self):
        self._assert_has_point_class()
        return self._point_class(self._value)


class Pitch(Point):
    """
    Base class for pitches. Pitch and Interval behave like Point and vector so we add renamed versions for:
        to_point --> to_pitch
        to_vector --> to_interval
        create_vector_class --> create_interval_class
        link_vector_class --> link_interval_class
        Vector --> Interval
    """

    _pitch_class_origin = None
    _pitch_class_period = None

    @staticmethod
    def _check_class_param_consistency(param_value, object_value):
        """
        Check consistency between the two values and set default
        :param param_value: value specified via parameter
        :param object_value: value obtained from object
        :return:
              param_value:  | None  | True  | False
        --------------------------------------------
        object value: None  | False | True  | False
        object value: True  | True  | True  | ERROR
        object value: False | False | ERROR | False
        """
        if param_value is None and object_value is None:
            return False
        elif param_value is None:
            return object_value
        elif object_value is None:
            return param_value
        else:
            if object_value == param_value:
                return param_value
            else:
                raise ValueError(f"Inconsistent values for class parameter between "
                                 f"provided object ({object_value}) and "
                                 f"parameter specification ({param_value})")

    # store converters for classes derived from Pitch;
    # it's a dict of dicts, so that __converters__[A][B] returns is a list of functions that, when executed
    # successively, converts A to B
    _converters_ = {}

    @staticmethod
    def register_converter(from_type, to_type, conv_func,
                           overwrite_explicit_converters=None,
                           overwrite_implicit_converter=True,
                           extend_implicit_converters=True):
        """
        Register a converter from from_type to other type. The converter function should be function taking as its
        single argument an from_type object and returning an other_type object.
        :param to_type: other type derived from Pitch, which the converter function converts to
        :param conv_func: converter function from from_type to other_type
        :param overwrite_explicit_converters: can be True, False, or None (default); if True and there exists an
        explicit converter (i.e. the list of converter functions is of length 1), replace it by this converter function;
        if False, don't replace explicit converters; if None, raise a ValueError if an explicit converter exists
        :param overwrite_implicit_converter: if there exists an implicit converter (i.e. the list of converter functions
        is of length greater than 1) replace it by this converter function
        :param extend_implicit_converters: if there is an (explicit or implicit) converter from type X to type
        from_type, add an implicit converter from type X to other_type by extending the list of converter functions from
        X to from_type by this converter function; if there already exists an (explicit or implicit) converter from X to
        other_type, it will not be overwritten
        """
        # initialise converter dict if it does not exist
        if from_type not in Pitch._converters_:
            Pitch._converters_[from_type] = {}
        # get existing converters from from_type to to_type and decide whether to set new converter
        set_new_converter = False
        try:
            converter = Pitch.get_converter(from_type, to_type)
        except NotImplementedError:
            # no existing converters
            set_new_converter = True
        else:
            # implicit or explicit converter are already registered
            if len(converter) == 1:
                # explicit converter
                if overwrite_explicit_converters is None:
                    raise ValueError("An explicit converter already exists. Set overwrite_explicit_converters=True to "
                                     "overwrite.")
                elif overwrite_explicit_converters:
                    set_new_converter = True
            else:
                # implicit converter
                if overwrite_implicit_converter:
                    set_new_converter = True
        # set the new converter
        if set_new_converter:
            Pitch._converters_[from_type][to_type] = [conv_func]
        # extend implicit converters
        if extend_implicit_converters:
            for another_from_type, other_converters in Pitch._converters_.items():
                # remember new converters to not change dict while iterating over it
                new_converters = []
                for another_to_type, converter_pipeline in other_converters.items():
                    # trying to prepend this converter [from_type --> to_type == another_from_type --> another_to_type]
                    if to_type == another_from_type:
                        # get existing converters from_type --> ???
                        converters = Pitch.get_converter(from_type)
                        # add the extended converter if one does not exist
                        if another_to_type not in converters:
                            converters[another_to_type] = [conv_func] + converter_pipeline
                    # try to append this converter [another_from_type --> another_to_type == from_type --> to_type]
                    if another_to_type == from_type:
                        # already initialised and we have the existing converters another_from_type --> ???
                        # add the extended converter if one does not exist
                        if to_type not in other_converters:
                            new_converters.append((to_type, converter_pipeline + [conv_func]))
                # insert new converters
                for key, val in new_converters:
                    other_converters[key] = val

    @staticmethod
    def get_converter(from_type, to_type=None):
        # return dedicated converter if other_type was specified or list of existing converters otherwise
        if to_type is not None:
            all_converters = Pitch.get_converter(from_type)
            try:
                return all_converters[to_type]
            except KeyError:
                raise NotImplementedError(f"Type '{from_type}' does not have any converter registered for type "
                                          f"'{to_type}'")
        else:
            try:
                return Pitch._converters_[from_type]
            except KeyError:
                raise NotImplementedError(f"There are no converters registered for type '{from_type}'")

    @staticmethod
    def _convert(value, to_type):
        Pitch._check_type(value, bases=(Pitch, Interval))
        Pitch._check_type(to_type, bases=(Pitch, Interval), value_is_type=True)
        if to_type == value.__class__:
            # skip self-conversion
            return value
        else:
            # use conversion pipeline
            ret = value
            for converter in Pitch.get_converter(value.__class__, to_type):
                ret = converter(ret)
            # check for correct type
            if not isinstance(ret, to_type):
                raise TypeError(f"Conversion failed, expected type {to_type} but got {type(ret)}")
            if Pitch in value.__class__.__mro__:
                if not value.is_pitch_class() == ret.is_pitch_class():
                    raise TypeError(f"Conversion failed, inconsistent pitch class attribute "
                                    f"(before: {value.is_pitch_class()}, after: {ret._is_pitch_class})")
                else:
                    return ret if not value.is_pitch_class() else ret.to_pitch_class()
            elif Interval in value.__class__.__mro__:
                if not value.is_interval_class() == ret.is_interval_class():
                    raise TypeError(f"Conversion failed, inconsistent interval class attribute "
                                    f"(before: {value.is_interval_class()}, after: {ret._is_interval_class})")
                else:
                    return ret if not value.is_interval_class() else ret.to_interval_class()

    @classmethod
    def link_interval_class(pitch_class, *, overwrite_pitch_class=None, overwrite_interval_class=None):
        def decorator(interval_class):
            # check that provided class is actually derived from Interval
            if Interval not in interval_class.__mro__:
                raise TypeError(f"Provided class {interval_class} does not derive from {Interval}")
            # execute Point decorator
            interval_class = pitch_class.link_vector_class(
                overwrite_point_class=overwrite_pitch_class,
                overwrite_vector_class=overwrite_interval_class)(interval_class)
            return interval_class
        return decorator

    @staticmethod
    def _check_type(value, types=(), bases=(), value_is_type=False):
        # check for type
        if value_is_type:
            # type was given
            if value in types:
                return True
        else:
            # value was given
            if isinstance(value, types):
                return True
        # check for base classes
        for b in bases:
            if (value_is_type and b in value.__mro__) or (not value_is_type and b in value.__class__.__mro__):
                return True
        raise TypeError(f"argument should be of type [{', '.join([str(t) for t in types])}] "
                        f"or derived from [{', '.join([str(b) for b in bases])}]; "
                        f"got {value} of type {type(value)}")

    @classmethod
    def _map_to_pitch_class(cls, value):
        if cls._pitch_class_origin is None or cls._pitch_class_period is None:
            raise NotImplementedError
        else:
            return (value - cls._pitch_class_origin) % cls._pitch_class_period

    @classmethod
    def pitch_class_origin(cls):
        """Returns the origin with respect to which pitch classes are computed as pitch object"""
        if cls._pitch_class_origin is None:
            raise NotImplementedError
        else:
            return cls(cls._pitch_class_origin)

    @classmethod
    def pitch_class_period(cls):
        """Returns the perior used to compute pitch classes as interval object"""
        if cls._pitch_class_period is None:
            raise NotImplementedError
        else:
            cls._assert_has_vector_class()
            return cls._vector_class(cls._pitch_class_period)

    @classmethod
    def range(cls, start, stop, step=None, *, include_stop=False):
        # start
        start = cls(start)
        if not isinstance(start, cls):
            raise TypeError(f"Start value has to be of type {cls} but is {type(start)}")
        # stop
        stop = cls(stop)
        if not isinstance(stop, cls):
            raise TypeError(f"Stop value has to be of type {cls} but is {type(stop)}")
        # step
        if step is None:
            step = cls._vector_class(1)
        else:
            cls._vector_class(step)
        if not isinstance(step, cls._vector_class):
            raise TypeError(f"Step value has to be of type {cls._vector_class} but is {type(step)}")
        # yield from range created in value type
        for val in range(start._value, (stop._value + step._value if include_stop else stop._value), step._value):
            yield cls(val)

    def __init__(self, value, *args, is_pitch_class=None, **kwargs):
        # if value is derived from Pitch, try to convert to converter to this type and get the _value
        value_is_pitch_class = None
        if Pitch in value.__class__.__mro__:
            value_is_pitch_class = value.is_pitch_class()
            value = value.convert_to(self.__class__)._value
        super().__init__(value=value, *args, **kwargs)
        # check consistency for class parameter
        is_pitch_class = Pitch._check_class_param_consistency(is_pitch_class, value_is_pitch_class)
        # set pitch class and return
        if is_pitch_class:
            self._value = self._map_to_pitch_class(self._value)
            self._is_pitch_class = True
        else:
            self._is_pitch_class = False

    def __sub__(self, other):
        # do arithmetics
        ret = super().__sub__(other)
        # check for class/non-class
        try:
            other_is_class = other.is_pitch_class()
        except AttributeError:
            other_is_class = other.is_interval_class()
        if self.is_pitch_class() != other_is_class:
            raise TypeError(f"Cannot combine pitch class and non-class types "
                            f"(this: {self.is_pitch_class()}, other: {other_is_class})")
        # convert to class if required
        try:
            return ret if not self.is_pitch_class() else ret.to_pitch_class()
        except AttributeError:
            return ret if not self.is_pitch_class() else ret.to_interval_class()

    def __add__(self, other):
        # do arithmetics
        ret = super().__add__(other)
        # check for class/non-class
        if self.is_pitch_class() != other.is_interval_class():
            raise TypeError(f"Cannot combine pitch class and non-class types "
                            f"(this: {self.is_pitch_class()}, other: {other.is_interval_class()})")
        # convert to class if required
        return ret if not self.is_pitch_class() else ret.to_pitch_class()

    def is_pitch_class(self):
        return self._is_pitch_class

    def to_pitch_class(self):
        return self.__class__(value=self._value, is_pitch_class=True)

    def range_to(self, stop, step=None, *, include_stop=False):
        yield from self.range(start=self, stop=stop, step=step, include_stop=include_stop)

    def pitch_class_phase(self, two_pi=False):
        if self._pitch_class_period is None:
            raise NotImplementedError
        if not self.is_pitch_class():
            return self.to_pitch_class().pitch_class_phase(two_pi=two_pi)
        else:
            normed_phase = self._value / self._pitch_class_period
            if two_pi:
                return normed_phase * 2 * np.pi
            else:
                return normed_phase

    def convert_to(self, other_type):
        Pitch._check_type(other_type, bases=(Pitch,), value_is_type=True)
        return Pitch._convert(self, other_type)

    def to_interval(self):
        self._assert_has_vector_class()
        return self._vector_class(self._value, is_interval_class=self.is_pitch_class())


class Interval(Vector):

    @classmethod
    def _map_to_interval_class(cls, value):
        value %= cls._point_class._pitch_class_period
        if value > cls._point_class._pitch_class_period / 2:
            value -= cls._point_class._pitch_class_period
        return value

    def __init__(self, value, *args, is_interval_class=None, **kwargs):
        # if value is derived from Interval, try to convert to converter to this type and get the _value
        value_is_interval_class = None
        if Interval in value.__class__.__mro__:
            value_is_interval_class = value.is_interval_class()
            value = value.convert_to(self.__class__)._value
        super().__init__(value=value, *args, **kwargs)
        # check consistency for class parameter
        is_interval_class = Pitch._check_class_param_consistency(is_interval_class, value_is_interval_class)
        # set interval class and return
        if is_interval_class:
            self._value = self._map_to_interval_class(self._value)
            self._is_interval_class = True
        else:
            self._is_interval_class = False

    def __sub__(self, other):
        # do arithmetics
        ret = super().__sub__(other)
        # check for class/non-class
        if self.is_interval_class() != other.is_interval_class():
            raise TypeError(f"Cannot combine interval class and non-class types "
                            f"(this: {self.is_interval_class()}, other: {other.is_interval_class()})")
        # convert to class if required
        return ret if not self.is_interval_class() else ret.to_interval_class()

    def __add__(self, other):
        # do arithmetics
        ret = super().__add__(other)
        # check for class/non-class
        if self.is_interval_class() != other.is_interval_class():
            raise TypeError(f"Cannot combine interval class and non-class types "
                            f"(this: {self.is_interval_class()}, other: {other.is_interval_class()})")
        # convert to class if required
        return ret if not self.is_interval_class() else ret.to_interval_class()

    def __mul__(self, other):
        ret = super().__mul__(other)
        return ret if not self.is_interval_class() else ret.to_interval_class()

    def is_interval_class(self):
        return self._is_interval_class

    def to_interval_class(self):
        return self.__class__(value=self._value, is_interval_class=True)

    def phase_diff(self, two_pi=False):
        if not self.is_interval_class():
            return self.to_interval_class().phase_diff(two_pi=two_pi)
        else:
            normed_phase_diff = self._value / self._point_class._pitch_class_period
            if two_pi:
                return normed_phase_diff * 2 * np.pi
            else:
                return normed_phase_diff

    def to_pitch(self):
        self._assert_has_point_class()
        return self._point_class(self._value, is_pitch_class=self.is_interval_class())

    def convert_to(self, other_type):
        Pitch._check_type(other_type, bases=(Interval,), value_is_type=True)
        try:
            # try direct converter
            return Pitch._convert(self, other_type)
        except NotImplementedError:
            # try to convert via equivalent pitch classes
            self._assert_has_point_class()
            other_type._assert_has_point_class()
            # convert interval-->equivalent pitch-->other pitch type-->equivalent interval
            other_interval = self.to_pitch().convert_to(other_type._point_class).to_interval()
            # but point<-->value (pitch<-->interval) conversion relies on an implicit origin;
            # if the two origins of the two different pitch classes are not identical,
            # we are off by the corresponding difference;
            # the origin can be retrieved as the equivalent point of the zero vector
            origin_from = (self - self).to_pitch().convert_to(other_type._point_class) # point
            origin_to = (other_interval - other_interval).to_pitch() # point
            origin_difference = origin_to - origin_from # vector
            # now we add that difference (we move from the "from" origin to the "to" origin)
            out = other_interval + origin_difference
            # check for correct type
            if not isinstance(out, other_type):
                raise TypeError(f"Conversion failed, expected type {other_type} but got {type(out)}")
            return out if not self.is_interval_class() else out.to_interval_class()


class Time(Point):
    """
    Base class for time-like types. Behaves like Point/Vector but adds renamed versions for:
        to_point --> to_time
        to_vector --> to_duration
        create_vector_class --> create_duration_class
        link_vector_class --> link_duration_class
    """

    @classmethod
    def link_duration_class(time_class, *, overwrite_time_class=None, overwrite_duration_class=None):
        def decorator(duration_class):
            # check that provided class is actually derived from Duration
            if Duration not in duration_class.__mro__:
                raise TypeError(f"Provided class {duration_class} does not derive from {Duration}")
            # execute Point decorator
            duration_class = time_class.link_vector_class(
                overwrite_point_class=overwrite_time_class,
                overwrite_vector_class=overwrite_duration_class)(duration_class)
            return duration_class
        return decorator

    def to_duration(self):
        return self.to_vector()


class Duration(Vector):

    def __init__(self, value, *args, **kwargs):
        # if value is derived from Duration, try to convert to converter to this type and get the _value
        if Duration in value.__class__.__mro__:
            value = value.convert_to(self.__class__)._value
        super().__init__(value=value, *args, **kwargs)

    def to_time(self):
        self._assert_has_point_class()
        return self._point_class(self._value)


class LinearTime(Time):

    def __init__(self, value, *args, **kwargs):
        super().__init__(value=float(value), *args, **kwargs)

    def __float__(self):
        return float(self._value)


@LinearTime.link_duration_class()
class LinearTimeDuration(Duration):

    def __init__(self, value, *args, **kwargs):
        super().__init__(value=float(value), *args, **kwargs)

    def __float__(self):
        return float(self._value)


class SpelledPitch(Pitch):
    _diatonic_fifth_steps = {"F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5}
    name_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>(-?[0-9]+)?)$")

    _pitch_class_origin = np.array([0, 0])

    @classmethod
    def _map_to_pitch_class(cls, value):
        return np.array([value[0], 0])

    def __init__(self, value, *args, is_pitch_class=None, **kwargs):
        Pitch._check_type(value, (str, np.ndarray, list, tuple), (Pitch,))
        # pre-process value
        if isinstance(value, str):
            str_value = value
            # extract pitch class, modifiers, and octave
            match = SpelledPitch.name_regex.match(value)
            if match is None:
                raise ValueError(f"{value} does not match the regular expression for spelled pitch names "
                                 f"'{SpelledPitch.name_regex.pattern}'.")
            # initialise value with diatonic pitch class
            value = np.array([SpelledPitch._diatonic_fifth_steps[match['class']], 0])
            # add modifiers
            if "#" in match['modifiers']:
                value[0] += 7 * len(match['modifiers'])
            else:
                value[0] -= 7 * len(match['modifiers'])
            # add octave
            if match['octave'] == "":
                if is_pitch_class is None:
                    is_pitch_class = True
                else:
                    if not is_pitch_class:
                        raise ValueError(f"Inconsistent arguments: {str_value} indicates a pitch class but "
                                         f"'is_pitch_class' is {is_pitch_class}")
            else:
                if is_pitch_class is None:
                    is_pitch_class = False
                else:
                    if is_pitch_class:
                        raise ValueError(f"Inconsistent arguments: {str_value} does not indicate a pitch class but "
                                         f"'is_pitch_class' is {is_pitch_class}")
                value[1] += int(match['octave'])
        elif isinstance(value, (np.ndarray, list, tuple)):
            int_value = np.array(value, dtype=np.int)
            if not np.array_equal(int_value, value):
                raise ValueError(f"Expected integer values but got {value}")
            value = int_value
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch_class=is_pitch_class, *args, **kwargs)

    def __repr__(self):
        return self.name()

    def fifth_steps(self):
        return self._value[0]

    def octave(self):
        return self._value[1]

    def freq(self):
        raise NotImplementedError
        # return 2 ** ((self._value - 69) / 12) * 440

    def name(self):
        pitch_class = ["F", "C", "G", "D", "A", "E", "B"][(self._value[0] + 1) % 7]
        sharp_flat = (self._value[0] + 1) // 7
        pitch_class += ('#' if sharp_flat > 0 else 'b') * abs(sharp_flat)
        if self.is_pitch_class():
            return pitch_class
        else:
            return pitch_class + str(self._value[1])


@SpelledPitch.link_interval_class()
class SpelledPitchInterval(Interval):

    def __init__(self, value, *args, **kwargs):
        Pitch._check_type(value, (numbers.Number,), (Interval,))
        int_value = np.array(value, dtype=np.int)
        if not np.array_equal(int_value, value):
            raise ValueError(f"Expected integer values but got {value}")
        super().__init__(value=int_value, *args, **kwargs)


class MIDIPitch(Pitch):

    _base_names_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    _base_names_flat = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    _pitch_class_origin = 60
    _pitch_class_period = 12

    @staticmethod
    def convert_from_SpelledPitch(spelled_pitch):
        fifth_steps_from_f = spelled_pitch.fifth_steps() + 1
        # base pitch
        base_pitch = ((fifth_steps_from_f % 7 - 1) * 7) % 12
        # chromatic semitone steps
        if fifth_steps_from_f >= 0:
            accidentals = fifth_steps_from_f // 7
        else:
            # note: floor divide rounds down (for negative numbers that is equal to the remainder of division minus one)
            accidentals = fifth_steps_from_f // 7
        return MIDIPitch(value=12 * (spelled_pitch.octave() + 1) + base_pitch + accidentals,
                         is_pitch_class=spelled_pitch.is_pitch_class())

    def __init__(self, value, *args, is_pitch_class=None, part=None, expect_int=True, **kwargs):
        Pitch._check_type(value, (str, numbers.Number), (Pitch,))
        # pre-process value
        if isinstance(value, str):
            value = SpelledPitch(value=value, is_pitch_class=is_pitch_class)
        elif isinstance(value, numbers.Number) and expect_int:
            int_value = int(value)
            if int_value != value:
                raise ValueError(f"Expected integer pitch value but got {value}")
            value = int_value
        # hand on initialisation to other base classes
        super().__init__(value=value, is_pitch_class=is_pitch_class, *args, **kwargs)
        # finish initialisation
        self.part = part

    def __int__(self):
        return self._value

    def __repr__(self):
        return self.name()

    def octave(self):
        return self._value // 12 - 1

    def freq(self):
        return 2 ** ((self._value - 69) / 12) * 440

    def fifth_steps(self, sharp_flat=None):
        pitch_class = int(self.to_pitch_class())
        if pitch_class % 2 == 0:
            fifth_steps = pitch_class
        else:
            fifth_steps = (pitch_class + 6) % 12
        if sharp_flat is None:
            if fifth_steps > 6:
                fifth_steps -= 12
        elif sharp_flat == "sharp":
            pass
        elif sharp_flat == "flat":
            fifth_steps %= -12
        else:
            raise ValueError(f"parameter 'sharp_flat' must be one of {['sharp', 'flat', None]}")
        return fifth_steps

    def name(self, sharp_flat=None):
        if sharp_flat is None:
            sharp_flat = "sharp"
        if sharp_flat == "sharp":
            base_names = self._base_names_sharp
        elif sharp_flat == "flat":
            base_names = self._base_names_flat
        else:
            raise ValueError("parameter 'sharp_flat' must be one of ['sharp', 'flat']")
        pc = base_names[self._value % 12]
        if self.is_pitch_class():
            return pc
        else:
            return pc + str(self.octave())


Pitch.register_converter(SpelledPitch, MIDIPitch, MIDIPitch.convert_from_SpelledPitch)


@MIDIPitch.link_interval_class()
class MIDIPitchInterval(Interval):

    def __init__(self, value, *args, **kwargs):
        Pitch._check_type(value, (numbers.Number,), (Interval,))
        super().__init__(value=value, *args, **kwargs)

    def __int__(self):
        return int(self._value)


class LogFreqPitch(Pitch):
    """
    Represents a pitch in continuous frequency space with the frequency value stored in log representation.
    """

    _pitch_class_origin = np.log(1)
    _pitch_class_period = np.log(2)

    @staticmethod
    def convert_from_midi_pitch(midi_pitch):
        return LogFreqPitch(midi_pitch.freq(), is_freq=True, is_pitch_class=midi_pitch.is_pitch_class())

    def __init__(self, value, is_freq=False, *args, **kwargs):
        """
        Initialise from frequency or log-frequency value.
        :param value: frequency or log-frequency (default) value
        :param is_freq: whether value is frequency or log-frequency
        """
        Pitch._check_type(value, (numbers.Number,))
        if is_freq:
            value = np.log(value)
        super().__init__(value=value, *args, **kwargs)

    def freq(self):
        return np.exp(self._value)

    def __float__(self):
        return self._value

    def __repr__(self):
        return f"{np.format_float_positional(self.freq(), fractional=True, precision=2)}Hz"


Pitch.register_converter(MIDIPitch, LogFreqPitch, LogFreqPitch.convert_from_midi_pitch)


@LogFreqPitch.link_interval_class()
class LogFreqPitchInterval(Interval):
    """
    Represents an interval in continuous frequency space. An interval corresponds to a frequency ratio and is stored as
    a log-frequency difference.
    """

    def __init__(self, value, is_freq_ratio=False, *args, **kwargs):
        """
        Initialise from frequency ratio or log-frequency difference.
        :param value: frequency ratio or log-frequency difference (default)
        :param is_freq_ratio: whether value is a frequency ratio or log-frequency difference
        """
        Pitch._check_type(value, (numbers.Number,), (Interval,))
        if is_freq_ratio:
            value = np.log(value)
        super().__init__(value=value, *args, **kwargs)

    def ratio(self):
        return np.exp(self._value)

    def __float__(self):
        return self._value

    def __repr__(self):
        return f"{np.format_float_positional(self.ratio(), fractional=True, precision=3)}"


class Event:

    def __init__(self, time, duration, data):
        self.time = time
        self.duration = duration
        self.data = data

    def __repr__(self):
        return f"{self.__class__.__name__}(time={self.time}, duration={self.duration}, data={self.data})"
