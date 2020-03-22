import logging
logging.basicConfig(filename='output.log',
                            filemode='a+',
                            format='%(asctime)s.%(msecs)d | %(name)s | %(levelname)s | %(message)s',
                            datefmt='%Y/%m/%d %H:%M:%S',
                            level=logging.INFO)
logger = logging.getLogger('reddit_deleter')