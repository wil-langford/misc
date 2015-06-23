import cmd
import posix
import sys
import os
import signal


class HorribleShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)

        self.set_work_dir(os.getcwd())
        self.prompt = "{}$ ".format(self.work_dir)


    def postcmd(self, stop, line):
        self.prompt = "{}$ ".format(self.work_dir)
        return False

    @property
    def work_dir(self):
        return self._work_dir

    def emptyline(self):
        pass

    def set_work_dir(self, new_dir):
        if not new_dir:
            new_dir = os.path.expanduser('~')

        if new_dir == '.':
            return None

        if new_dir == '..':
            new_dir = os.path.abspath(os.path.join(self.work_dir, os.pardir))

        if not os.path.isdir(new_dir):
            new_dir = os.path.abspath(os.path.join(self.work_dir, new_dir))

        if not os.path.isdir(new_dir):
            print 'Could not change to directory:', new_dir
            return False

        if not new_dir:
            raise Exception("Invalid directory: '{}'".format(new_dir))

        print "New directory is: "
        self._work_dir = new_dir

    def do_help(self, arg):
        all_the_things = dir(self)
        just_commands = [x[3:] for x in all_the_things
                         if x[:3] == 'do_']
        print 'COMMANDS:'
        for command in just_commands:
            if not command == 'EOF':
                print "  ", command

    def do_exit(self, return_val=None):
        if not return_val:
            return_val = 0
        else:
            try:
                return_val = int(return_val)
            except ValueError:
                print return_val
                return_val = 1

        print ''
        sys.exit(return_val)

    def do_stat(self, path):
        if not path:
            path = self._work_dir
        print posix.stat(path)

    def do_pwd(self, arg):
        print self.work_dir

    def do_EOF(self, arg):
        self.do_exit(0)

    def do_ls(self, dummy_path):
        print 'listing: ', self.work_dir

        try:
            root, dirs, files = next(os.walk(self.work_dir))
        except StopIteration:
            print "Couldn't get directory listing of:", self.work_dir
            return False

        for thing in dirs + files:
            print thing

    def do_cd(self, path):
        self.set_work_dir(path)


def main():
    horrible_shell = HorribleShell()

    signal.signal(signal.SIGINT,
                  lambda sig, frame: horrible_shell.do_exit(sig))

    horrible_shell.cmdloop("Welcome to Horrible Shell.")

if __name__ == '__main__':
    main()