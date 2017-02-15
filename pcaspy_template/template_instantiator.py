
import os
import shutil


TEMPLATE_DIR = 'template_files'


class TemplateInstatiator:
    
    def __init__(self, args):
        if args.dest is not None:
            d = os.path.realpath(args.dest)
        else:
            d = os.path.realpath(os.curdir)
        self.destination = os.path.join(d, args.name)    
        
        s = os.path.dirname(os.path.realpath(__file__))
        self.source = os.path.join(s, TEMPLATE_DIR)
    
    def instantiate(self):
        self._create_directory()
        self._copy_files()
    
    def _create_directory(self):
        # Will fail if directory already exists
        os.mkdir(self.destination)
    
    def _copy_files(self):
        contents = os.listdir(self.source)
        filenames = [os.path.join(self.source, fn) for fn in contents]
        for fn in filenames:
            shutil.copy(fn, self.destination)
