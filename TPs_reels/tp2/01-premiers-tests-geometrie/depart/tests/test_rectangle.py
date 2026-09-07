from geo.rectangle import Rectangle


def test_surface():
    # Arrange
    r = Rectangle(2, 3)
    # Act
    s = r.surface
    # Assert
    assert s == 6
