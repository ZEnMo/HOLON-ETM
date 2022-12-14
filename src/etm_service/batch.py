from etm_service.etm_session import ETMConnection

class Batch():
    def __init__(self, endpoint, action='GET'):
        '''
        Create a batch request

        Params:
            endpoint: Valid endpoint of the ETM, can be one of 'curves', 'nodes' or 'queries'
        '''
        self.endpoint = endpoint
        self.action = action
        self._batch = []

    def is_empty(self):
        '''Returns if the batch is empty or not'''
        return len(self._batch) == 0

    def add(self, *values):
        '''Add one or more Values to the batch'''
        for value in values:
            if self.action == 'SET' and not value.is_set():
                continue
            self._batch.append(value)

    def keys(self):
        '''Returns a list of keys that should be requested from the endpoint'''
        return [value.key for value in self._batch]

    def send(self, scenario_id):
        '''Create ETM session with the config stuff and send and handle results'''
        if not self._batch: return

        if self.action == 'GET':
            self._inject_results(ETMConnection(self.endpoint, scenario_id, self.action).connect(self.keys()))
        else:
            # TODO: make this nicer
            for _ in ETMConnection(self.endpoint, scenario_id, self.action).connect(self._values()):
                continue

    # Private

    def _values(self):
        return {value.key: value.value() for value in self._batch}

    def _inject_results(self, results):
        '''Update the Values in the batch with the results from the response'''
        for key, new_value in results:
            for value in self._search(key):
                value.update(new_value)

    def _search(self, key):
        '''Search for a Value in the batch, used for updating'''
        found = False
        for value in self._batch:
            if value.key == key:
                found = True
                yield value

        if not found:
            raise KeyError(f'Could not find {key} in batch {self.endpoint}')
