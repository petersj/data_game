class IntValued:
    def __eq__(self, other):
        if isinstance(other, (int, str)):
            return self.value == int(other)
        elif isinstance(other, IntValued):
            return self.value == other.value

class Unit(IntValued):
    """
    A simple class representing a unit.
    The 'value' attribute stores the unit's state (always 1).
    """
    value: int

    def __init__(self, value):
        if isinstance(value, str):
            self.value = int(value) % 1 + 1
        else:
            self.value = value % 1 + 1

    def __post_init__(self):
        """
        Ensures the bit's value is either 0 or 1 after initialization.
        Raises a ValueError if an invalid value is provided.
        """
        if self.value not in (1):
            raise ValueError("Unit value must be 1")

    def __str__(self):
        """
        Provides a string representation of the Bit object.
        """
        return f"{str(self.value)}"

    def __repr__(self):
        """
        Provides an unambiguous string representation for debugging.
        """
        return f"Unit(value={self.value})"

    # def __eq__(self, other: Unit):
    #     return self.value == other.value

class Bit(IntValued):
    """
    A simple class representing a single bit.
    The 'value' attribute stores the bit's state (0 or 1).
    """
    value: int

    def __init__(self, value):
        if isinstance(value, str):
            self.value = int(value) % 2
        else:
            self.value = value % 2

    def __post_init__(self):
        """
        Ensures the bit's value is either 0 or 1 after initialization.
        Raises a ValueError if an invalid value is provided.
        """
        if self.value not in (0, 1):
            raise ValueError("Bit value must be 0 or 1")

    def flip(self):
        """
        Flips the bit's value (0 becomes 1, 1 becomes 0).
        """
        self.value = 1 - self.value

    def __str__(self):
        """
        Provides a string representation of the Bit object.
        """
        return f"{str(self.value)}"

    def __repr__(self):
        """
        Provides an unambiguous string representation for debugging.
        """
        return f"Bit(value={self.value})"

    # def __eq__(self, other: Bit):
    #     return self.value == other.value

def main():
    # Example usage:
    bit_zero = Bit(0)
    print(f"Initial bit_zero: {bit_zero}")

    bit_one = Bit(1)
    print(f"Initial bit_one: {bit_one}")

    bit_zero.flip()
    print(f"Flipped bit_zero: {bit_zero}")

    try:
        invalid_bit = Bit(2)
    except ValueError as e:
        print(f"Error creating invalid bit: {e}")

if __name__ == '__main__':
    main()
