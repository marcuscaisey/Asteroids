from cx_Freeze import setup, Executable

setup(
    name="Asteroids",
    version="1.0",
    options={"build_exe": {"packages": ["pygame", "pylygon", "numpy"],
                           "include_files": ["assets/fonts/Hyperspace.otf"]}},
    executables=[Executable("asteroids.py", base="Win32GUI")]
    )
