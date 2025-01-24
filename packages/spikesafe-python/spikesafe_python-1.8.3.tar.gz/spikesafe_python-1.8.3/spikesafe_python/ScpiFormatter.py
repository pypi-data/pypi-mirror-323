import logging

log = logging.getLogger(__name__)

def get_scpi_format_integer_for_bool(bool_value):
        """Return the SCPI formatted value for a boolean value.

        Returns
        -------
        int
            1 for True, 0 for False.
        """
        if bool_value:
            return 1
        else:
            return 0
        
def get_scpi_format_on_state_for_bool(bool_value):
        """Return the SCPI formatted value for a boolean value. 

        Returns
        -------
        string
            'ON' for True, 'OFF' for False.
        """
        if bool_value:
            return 'ON'
        else:
            return 'OFF'