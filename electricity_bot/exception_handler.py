from telebot import ExceptionHandler

class TGEBExceptionHandler(ExceptionHandler):
    def handle(self, exception):
        # logging.error(f"{exception} occured. Take actions regarding this error as soon as possible.")
        print(exception)
        return True