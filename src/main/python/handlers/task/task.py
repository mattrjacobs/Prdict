from handlers.handler import AbstractHandler

class AbstractTaskHandler(AbstractHandler):
    def __init__(self):
        self.CRON_HEADER = "X-AppEngine-Cron"

    # used for cron
    def get(self):
        if self.is_dev_host() or self.is_cron_request():
            self.run_task()

    def run_task(self):
        raise "Must be implemented in subclass!"

    # used for task queue
    def post(self):
        logging.error("Shouldn't be receiving a POST here")
        
    def is_cron_request(self):
        hdr = self.get_header(self.CRON_HEADER)
        if hdr:
            return hdr.lower() == "true"
        else:
            return False

        
