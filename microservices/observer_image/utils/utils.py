from pymongo.change_stream import CollectionChangeStream
from multiprocessing import Process

class Utils:
    __MONGO_NEXT_RESULT = None
    __CURSOR = None

    def __call_mongo_watcher(self):
        if self.__CURSOR is None:
            raise Exception("Workflow error, __CURSOR is not defined")
        self.__MONGO_NEXT_RESULT = self.__CURSOR.next()

    def call_cursor_with_timeout(self,cursor: CollectionChangeStream,
                                 timeout: int = 0):

        print(f"waiting2!! {timeout}", flush=True)
        process = Process(target=self.__call_mongo_watcher,
                          name='call_mongo_watcher')

        print(f"waiting3!! {timeout}", flush=True)
        self.__CURSOR = cursor
        process.start()

        print(f"waiting timeout = {timeout}",flush=True)
        if timeout <= 0:
            process.join()
        else:
            process.join(timeout=timeout)

        print(f"finished timeout = {timeout}",flush=True)
        process.terminate()

        if process.exitcode is None:
            return None

        result = self.__MONGO_NEXT_RESULT
        self.__MONGO_NEXT_RESULT = None

        return result
