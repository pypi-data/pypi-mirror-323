"""Example application demonstrating a typical Juham application.

Usage:
------

python myapp.py --init --myapp_serialization_format JsonFormat
python myapp.py 

"""

from masterpiece import Application, MasterPiece
from juham_core import Juham
from typing_extensions import override


class MyHome(Application):
    """Application demonstrating the structure of masterpiece applications.
    Also demonstrates plugin awareness and startup arguments.
    When run, the application prints out its instance hierarchy:

    Example:
        home
        └─ Juham


    """
    def __init__(self, name: str = "myhome") -> None:
        """Initialize the home application with the given name.

        Instance attributes can be initialized from class attributes,
        through a serialization file, or from constructor parameters.

        Args:
            name (str): The name of the application.
        """
        super().__init__(name)
        self.create_home()
        self.install_plugins()

    def create_home(self) -> None:
        """Create a default built-in home structure, which can be overridden
        by the instance hierarchy defined in the serialization file. See --file
        startup argument.
        """
        juham = Juham("juham")
        self.add(juham)


    @override
    def run(self) -> None:
        """Start the application."""
        super().run()

        # Print out the instance hierarchy
        self.print()


def main() -> None:
    """Main function that initializes, instantiates, and runs the MyHome application."""

    # Class initialization phase so that they can be instantiated with desired properties
    # Make this app plugin-aware. See the 'masterpiece_plugin' project for a minimal plugin example.
    MyHome.init_app_id("myhome")
    MyHome.load_plugins()

    Application.load_configuration()

    # Create an instance of MyHome application
    home = MyHome("home")

    # Initialize from the serialization file if specified
    home.deserialize()

    # Start event processing or the application's main loop
    home.run()

    # Save the application's state to a serialization file (if specified)
    home.serialize()


if __name__ == "__main__":
    main()
