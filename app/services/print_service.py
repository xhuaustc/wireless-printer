import win32print
import win32api

class PrintService:
    @staticmethod
    def print_file(filepath, printer_name=None, orientation='portrait'):
        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()
            
        print_params = f'/d:"{printer_name}"'
        if orientation == 'landscape':
            print_params += ' /o'
            
        win32api.ShellExecute(0, "print", filepath, print_params, ".", 0) 