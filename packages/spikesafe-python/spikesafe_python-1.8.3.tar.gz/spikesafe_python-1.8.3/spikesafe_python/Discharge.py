import logging
import time
from .Threading import wait

log = logging.getLogger(__name__)

def get_spikesafe_channel_discharge_time(compliance_voltage):
    """
    Returns the time to fully discharge the SpikeSafe channel based on the compliance voltage

    Parameters
    ----------
    compliance_voltage : float
        Compliance voltage to factor in discharge time
    
    Returns
    -------
    float
        Discharge time in seconds

    Raises
    ------
    None
    """
    # Discharge time accounting for compliance voltage, voltage readroom, and discharge voltage per second
    voltage_headroom_voltage = 7
    discharge_voltage_per_second = 1000
    discharge_time = (compliance_voltage + voltage_headroom_voltage) / discharge_voltage_per_second
    return discharge_time
