import argparse
import os
import sys

parser = argparse.ArgumentParser()

parser.add_argument('-V', '--version',
    help='use specific version of an app')

commands = parser.add_mutually_exclusive_group()
commands.add_argument('-l', '--list', action='store_true',
    help='print installed versions of given app')
commands.add_argument('-w', '--which', action='store_true',
    help='print which program will be called')

parser.add_argument('-p', '--python', action='store_true',
    help='run Python interpreter for app')

parser.add_argument('app_name')

def main(argv=None):

    from . import _vendor
    _vendor.install()
    import pkg_resources

    args = parser.parse_args(argv)

    # Grab the named app.
    app_ep = next(pkg_resources.iter_entry_points('appinit_apps', args.app_name), None)
    if not app_ep:
        print >> sys.stderr, 'no appinit app named %r' % args.app_name
        exit(10)
    app_cls = app_ep.load()

    installed_apps = list(app_cls.iter_installed())
    if not installed_apps:
        print >> sys.stderr, 'no known versions of %s' % args.app_name
        exit(11)

    if args.version:
        installed_apps = [app for app in installed if app.version == args.version]
        if not installed_apps:
            print >> sys.stderr, 'no version %s of %s' % (args.version, args.app_name)
            exit(12)

    installed_apps.sort(key=lambda app: app.version)

    if args.list:
        for app in installed_apps:
            print app.version, app.path
        return

    app = installed_apps[0]
    executable = app.get_python() if args.python else app.get_executable()

    if args.which:
        if executable:
            print executable
        exit(0 if executable else 1)

    os.execve(executable, [executable], os.environ)



