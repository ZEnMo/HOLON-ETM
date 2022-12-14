''' Balances sliders in a balancing group to sum to 100. '''

from .single_request import SingleRequest

BALANCING_GROUPS = [
    [
        'transport_truck_using_electricity_share',
        'transport_truck_using_diesel_mix_share'
    ],
]

# TODO: quick and ugly fix as the balancer should now only work for two types
# of trucks in the KEV. Should definitely be picked up!!!
# There is 0.2 percent gasoline trucks in the mix for the KEV. Keep it for now.
TOTAL = 99.8

class Balancer:
    '''
    Balancer is initialised with slider settings like the ones defined in
    config/inputs. On call it returns said slider settings, altered so that the
    values of sliders in a balancing group sum to 100.
    '''
    def __init__(self):
        '''
        Structure of self.balance
        [
        {
          slider_1: value,
          slider_2: value
        },
        {
          ...
        },
        ...
        ]

        '''
        self.requests = []
        self.extra_requests = []
        self.balance = [{slider: 0 for slider in sliders} for sliders in BALANCING_GROUPS]

    def add(self, single_request):
        etm_key = single_request.etm_key()
        for group in self.balance:
            if etm_key in group:
                self.requests.append(single_request)
                group[etm_key] = single_request.value()
                return

    def resolve(self):
        '''
        Main function
        Changes the values of the requests so that the sliders in each balancing
        group sum to 100. Returns self.extra_requests
        '''
        for sliders in self.balance:
            # Check if the set sliders in the share group sum to 100
            total = sum(sliders.values())

            if total == TOTAL:
                continue

            if total == 0:
                self.__deactivate_requests(sliders)

            elif total < TOTAL:
                losses = TOTAL - total
                self.__add_losses_to_other(sliders, losses)

            else:
                factor = TOTAL / total
                self.__rescale_values(sliders, factor)

        return self.extra_requests

    def __distribute_losses(self, sliders, losses):
        '''
        Even distribution over all set sliders, also set untouched sliders
        in share group to 0
        TODO: also untouched sliders are altered, fix that
        '''
        distribution = losses / float(len(sliders))
        for slider, old_value in sliders.items():
            self.__update_or_create_request(slider, old_value + distribution)

    def __add_losses_to_other(self, sliders, losses):
        '''
        Distribute losses to the one untouched slider (in this case diesel trucks)
        NOTE: MVP hack
        '''
        for slider, old_value in sliders.items():
            # Which means we have the diesel slider
            if old_value == 0:
                # Dump all losses in there
                self.__update_or_create_request(slider, losses)

    def __rescale_values(self, sliders, factor):
        '''
        Multpily all set sliders by factor, also set untouched sliders
        in share group to 0
        '''
        for slider, old_value in sliders.items():
            self.__update_or_create_request(slider, old_value * factor)

    def __update_or_create_request(self, etm_key, new_value):
        for request in self.requests:
            if request.etm_key() == etm_key:
                request.set_value(new_value)
                return

        new_req = self.__new_balancer_request(etm_key)
        new_req.set_value(new_value)
        self.extra_requests.append(new_req)

    def __new_balancer_request(self, etm_key):
        return SingleRequest(
                f'{etm_key}_balanced',
                'SET',
                value= {
                    'type': 'input',
                    'data': 'value',
                    'etm_key': etm_key,
                }
            )

    def __deactivate_requests(self, sliders):
        '''Deactivate requests for these sliders'''
        for request in self.requests:
            if request.etm_key() in sliders:
                request.converter.main_value.unset()
