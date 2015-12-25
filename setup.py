from distutils.core import setup

setup(name         = 'xrandr-dimmer',
      version      = '1.0',
      package_dir  = {'xrandr-dimmer': 'src/xrandr-dimmer'},
      packages     = ['xrandr-dimmer'],
      author       = 'Velizar Hristov',
      author_email = 'velizar.hs@gmail.com',
      license      = 'BSD-3',
      url          = 'https://github.com/VelizarHristov/xrandr-dimmer',
      description  = 'A GUI application for screen dimming with xrandr',
#     long_description = """TODO""",
      requires     = ["PyQt5 (>=5.3)"],
      )
