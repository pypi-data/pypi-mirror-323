"""KumoCloud integration using local API for data."""
# built-in imports
import os
import pprint
import time

# third party imports

# local imports
from thermostatsupervisor import kumolocal_config
from thermostatsupervisor import thermostat_api as api
from thermostatsupervisor import thermostat_common as tc
from thermostatsupervisor import environment as env
from thermostatsupervisor import utilities as util

# pykumo
PYKUMO_DEBUG = False  # debug uses local pykumo repo instead of pkg
if PYKUMO_DEBUG and not env.is_azure_environment():
    mod_path = "..\\pykumo\\pykumo"
    if env.is_interactive_environment():
        mod_path = "..\\" + mod_path
    pykumo = env.dynamic_module_import("pykumo", mod_path)
else:
    import pykumo  # noqa E402, from path / site packages


class ThermostatClass(pykumo.KumoCloudAccount, tc.ThermostatCommon):
    """KumoCloud thermostat functions."""

    def __init__(self, zone, verbose=True):
        """
        Constructor, connect to thermostat.

        inputs:
            zone(str):  zone of thermostat.
            verbose(bool): debug flag.
        """
        # Kumocloud server auth credentials from env vars
        self.KC_UNAME_KEY = "KUMO_USERNAME"
        self.KC_PASSWORD_KEY = "KUMO_PASSWORD"
        self.kc_uname = os.environ.get(
            self.KC_UNAME_KEY, "<" + self.KC_UNAME_KEY + "_KEY_MISSING>"
        )
        self.kc_pwd = os.environ.get(
            self.KC_PASSWORD_KEY, "<" + self.KC_PASSWORD_KEY + "_KEY_MISSING>"
        )

        # construct the superclass
        # call both parent class __init__
        self.args = [self.kc_uname, self.kc_pwd]
        # kumocloud account init sets the self._url
        pykumo.KumoCloudAccount.__init__(self, *self.args)
        tc.ThermostatCommon.__init__(self)

        # set tstat type and debug flag
        self.thermostat_type = kumolocal_config.ALIAS
        self.verbose = verbose

        # configure zone info
        self.zone_number = int(zone)
        self.zone_name = self.get_zone_name()
        self.device_id = None  # initialize
        self.device_id = self.get_target_zone_id(self.zone_number)
        self.serial_number = None  # will be populated when unit is queried.

    def get_zone_name(self):
        """
        Return the name associated with the zone number from metadata dict.

        inputs:
            None
        returns:
            (str) zone name
        """
        return kumolocal_config.metadata[self.zone_number]["zone_name"]

    def get_target_zone_id(self, zone=0):
        """
        Return the target zone ID.

        inputs:
            zone(int): zone number.
        returns:
            (obj): PyKumo object
        """
        # populate the zone dictionary
        # establish local interface to kumos, must be on local net
        kumos = self.make_pykumos()
        device_id = kumos[self.zone_name]
        # print zone name the first time it is known
        if self.device_id is None and self.verbose:
            util.log_msg(
                f"zone {zone} name='{self.zone_name}', " f"device_id={device_id}",
                mode=util.DEBUG_LOG + util.STDOUT_LOG,
                func_name=1,
            )
        self.device_id = device_id

        # return the target zone object
        return self.device_id

    def get_kumocloud_thermostat_metadata(self, zone=None, debug=False):
        """Get all thermostat meta data for zone from kumocloud.

        inputs:
            zone(): specified zone, if None will print all zones.
            debug(bool): debug flag.
        returns:
            (dict): JSON dict
        """
        del debug  # unused
        try:
            serial_num_lst = list(self.get_indoor_units())  # will query unit
        except UnboundLocalError:  # patch for issue #205
            util.log_msg(
                "WARNING: Kumocloud refresh failed due to timeout",
                mode=util.BOTH_LOG,
                func_name=1,
            )
            time.sleep(10)
            serial_num_lst = list(self.get_indoor_units())  # retry
        util.log_msg(
            f"indoor unit serial numbers: {str(serial_num_lst)}",
            mode=util.DEBUG_LOG + util.STDOUT_LOG,
            func_name=1,
        )

        # validate serial number list
        if not serial_num_lst:
            raise tc.AuthenticationError(
                "pykumo meta data is blank, probably"
                " due to an Authentication Error,"
                " check your credentials."
            )

        for serial_number in serial_num_lst:
            util.log_msg(
                f"Unit {self.get_name(serial_number)}: address: "
                f"{self.get_address(serial_number)} credentials: "
                f"{self.get_credentials(serial_number)}",
                mode=util.DEBUG_LOG + util.STDOUT_LOG,
                func_name=1,
            )
        if zone is None:
            # returned cached raw data for all zones
            raw_json = self.get_raw_json()  # does not fetch results,
        else:
            # return cached raw data for specified zone
            try:
                self.serial_number = serial_num_lst[zone]
            except IndexError as exc:
                raise IndexError(
                    f"ERROR: Invalid Zone, index ({zone}) does "
                    "not exist in serial number list "
                    f"({serial_num_lst})"
                ) from exc
            raw_json = self.get_raw_json()[2]["children"][0]["zoneTable"][
                serial_num_lst[zone]
            ]
        return raw_json

    def get_all_metadata(self, zone=None, retry=False):
        """Get all thermostat meta data for device_id from local API.

        inputs:
            zone(): specified zone
            retry(bool): if True will retry once.
        returns:
            (dict): dictionary of meta data.
        """
        del retry  # not used
        return self.get_metadata(zone)

    def get_metadata(self, zone=None, trait=None, parameter=None):
        """Get thermostat meta data for device_id from local API.

        inputs:
            zone(str or int): (unused) specified zone
            trait(str): trait or parent key, if None will assume a non-nested
                        dict
            parameter(str): target parameter, if None will return all.
            debug(bool): debug flag.
        returns:
            (dict): dictionary of meta data.
        """
        del trait  # not used on Kumolocal
        del zone  # unused

        # refresh device status
        self.device_id.update_status()
        meta_data = {}
        meta_data["status"] = self.device_id.get_status()
        # pylint: disable=protected-access
        meta_data["sensors"] = self.device_id._sensors
        # pylint: disable=protected-access
        meta_data["profile"] = self.device_id._profile
        if parameter is None:
            return meta_data
        else:
            return meta_data[parameter]

    def print_all_thermostat_metadata(self, zone):
        """Print all metadata for zone to the screen.

        inputs:
            zone(int): specified zone, if None will print all zones.
        returns:
            None, prints result to screen
        """
        self.exec_print_all_thermostat_metadata(self.get_all_metadata, [zone])


class ThermostatZone(tc.ThermostatCommonZone):
    """
    KumoCloud single zone on local network.

    Class needs to be updated for multi-zone support.
    """

    def __init__(self, Thermostat_obj, verbose=True):
        """
        Zone constructor.

        inputs:
            Thermostat(obj): Thermostat class instance.
            verbose(bool): debug flag.
        """
        # construct the superclass, requires auth setup first
        super().__init__()

        # runtime parameter defaults
        self.poll_time_sec = 10 * 60  # default to 10 minutes
        self.connection_time_sec = 8 * 60 * 60  # default to 8 hours

        # server data cache expiration parameters
        self.fetch_interval_sec = 60  # age of server data before refresh
        self.last_fetch_time = time.time() - 2 * self.fetch_interval_sec

        # switch config for this thermostat
        self.system_switch_position[tc.ThermostatCommonZone.COOL_MODE] = "cool"
        self.system_switch_position[tc.ThermostatCommonZone.HEAT_MODE] = "heat"
        self.system_switch_position[tc.ThermostatCommonZone.OFF_MODE] = "off"
        self.system_switch_position[tc.ThermostatCommonZone.DRY_MODE] = "dry"
        self.system_switch_position[tc.ThermostatCommonZone.AUTO_MODE] = "auto"
        self.system_switch_position[tc.ThermostatCommonZone.FAN_MODE] = "vent"

        # zone info
        self.verbose = verbose
        self.thermostat_type = kumolocal_config.ALIAS
        self.device_id = Thermostat_obj.device_id
        self.Thermostat = Thermostat_obj
        self.zone_number = Thermostat_obj.zone_number
        self.zone_name = Thermostat_obj.zone_name
        self.zone_name = self.get_zone_name()

    def get_zone_name(self):
        """
        Return the name associated with the zone number from device memory.

        inputs:
            None
        returns:
            (str) zone name
        """
        self.refresh_zone_info()
        zone_name = self.device_id.get_name()
        # update metadata dict
        kumolocal_config.metadata[self.zone_number]["zone_name"] = zone_name
        return zone_name

    def get_display_temp(self) -> float:  # used
        """
        Refresh the cached zone information and return Indoor Temp in °F.

        inputs:
            None
        returns:
            (float): indoor temp in °F.
        """
        self.refresh_zone_info()
        return util.c_to_f(self.device_id.get_current_temperature())

    def get_display_humidity(self) -> (float, None):
        """
        Refresh the cached zone information and return IndoorHumidity.

        inputs:
            None
        returns:
            (float, None): indoor humidity in %RH, None if not supported.
        """
        self.refresh_zone_info()
        return self.device_id.get_current_humidity()

    def get_is_humidity_supported(self) -> bool:  # used
        """
        Refresh the cached zone information and return the
          True if humidity sensor data is trustworthy.

        inputs:
            None
        returns:
            (booL): True if is in humidity sensor is available and not faulted.
        """
        return self.get_display_humidity() is not None

    def is_heat_mode(self) -> int:
        """
        Refresh the cached zone information and return the heat mode.

        inputs:
            None
        returns:
            (int) heat mode, 1=enabled, 0=disabled.
        """
        self.refresh_zone_info()
        return int(
            self.device_id.get_mode()
            == self.system_switch_position[tc.ThermostatCommonZone.HEAT_MODE]
        )

    def is_cool_mode(self) -> int:
        """
        Refresh the cached zone information and return the cool mode.

        inputs:
            None
        returns:
            (int): cool mode, 1=enabled, 0=disabled.
        """
        self.refresh_zone_info()
        return int(
            self.device_id.get_mode()
            == self.system_switch_position[tc.ThermostatCommonZone.COOL_MODE]
        )

    def is_dry_mode(self) -> int:
        """
        Refresh the cached zone information and return the dry mode.

        inputs:
            None
        returns:
            (int): dry mode, 1=enabled, 0=disabled.
        """
        self.refresh_zone_info()
        return int(
            self.device_id.get_mode()
            == self.system_switch_position[tc.ThermostatCommonZone.DRY_MODE]
        )

    def is_fan_mode(self) -> int:
        """
        Refresh the cached zone information and return the fan mode.

        inputs:
            None
        returns:
            (int): fan mode, 1=enabled, 0=disabled.
        """
        return int(
            self.get_system_switch_position()
            == self.system_switch_position[tc.ThermostatCommonZone.FAN_MODE]
        )

    def is_auto_mode(self) -> int:
        """
        Refresh the cached zone information and return the auto mode.

        inputs:
            None
        returns:
            (int): auto mode, 1=enabled, 0=disabled.
        """
        self.refresh_zone_info()
        return int(
            self.device_id.get_mode()
            == self.system_switch_position[tc.ThermostatCommonZone.AUTO_MODE]
        )

    def is_off_mode(self) -> int:
        """
        Refresh the cached zone information and return the off mode.

        inputs:
            None
        returns:
            (int): off mode, 1=enabled, 0=disabled.
        """
        return int(
            self.get_system_switch_position()
            == self.system_switch_position[tc.ThermostatCommonZone.OFF_MODE]
        )

    def is_heating(self):
        """Return 1 if heating relay is active, else 0."""
        return int(
            self.is_heat_mode()
            and self.is_power_on()
            and self.get_heat_setpoint_raw() > self.get_display_temp()
        )

    def is_cooling(self):
        """Return 1 if cooling relay is active, else 0."""
        return int(
            self.is_cool_mode()
            and self.is_power_on()
            and self.get_cool_setpoint_raw() < self.get_display_temp()
        )

    def is_drying(self):
        """Return 1 if drying relay is active, else 0."""
        return int(
            self.is_dry_mode()
            and self.is_power_on()
            and self.get_cool_setpoint_raw() < self.get_display_temp()
        )

    def is_auto(self):
        """Return 1 if auto relay is active, else 0."""
        return int(
            self.is_auto_mode()
            and self.is_power_on()
            and (
                self.get_cool_setpoint_raw() < self.get_display_temp()
                or self.get_heat_setpoint_raw() > self.get_display_temp()
            )
        )

    def is_fanning(self):
        """Return 1 if fan relay is active, else 0."""
        return int(self.is_fan_on() and self.is_power_on())

    def is_power_on(self):
        """Return 1 if power relay is active, else 0."""
        self.refresh_zone_info()
        return int(self.device_id.get_mode() != "off")

    def is_fan_on(self):
        """Return 1 if fan relay is active, else 0."""
        self.refresh_zone_info()
        return int(self.device_id.get_fan_speed() != "off")

    def is_defrosting(self):
        """Return 1 if defrosting is active, else 0."""
        self.refresh_zone_info()
        return int(self.device_id.get_status("defrost") == "True")

    def is_standby(self):
        """Return 1 if standby is active, else 0."""
        self.refresh_zone_info()
        return int(self.device_id.get_standby())

    def get_heat_setpoint_raw(self) -> float:  # used
        """
        Refresh the cached zone information and return the heat setpoint.

        inputs:
            None
        returns:
            (float): heating set point in °F.
        """
        self.refresh_zone_info()
        return util.c_to_f(self.device_id.get_heat_setpoint())

    def get_heat_setpoint(self) -> str:
        """Return heat setpoint with units as a string."""
        return util.temp_value_with_units(self.get_heat_setpoint_raw())

    def get_schedule_heat_sp(self) -> float:  # used
        """
        Return the schedule heat setpoint.

        inputs:
            None
        returns:
            (float): scheduled heating set point in °F.
        """
        return float(kumolocal_config.MAX_HEAT_SETPOINT)  # max heat set point allowed

    def get_schedule_cool_sp(self) -> float:
        """
        Return the schedule cool setpoint.

        inputs:
            None
        returns:
            (float): scheduled cooling set point in °F.
        """
        return float(kumolocal_config.MIN_COOL_SETPOINT)  # min cool set point allowed

    def get_cool_setpoint_raw(self) -> float:
        """
        Return the cool setpoint.

        inputs:
            None
        returns:
            (float): cooling set point in °F.
        """
        self.refresh_zone_info()
        return util.c_to_f(self.device_id.get_cool_setpoint())

    def get_cool_setpoint(self) -> str:
        """Return cool setpoint with units as a string."""
        return util.temp_value_with_units(self.get_cool_setpoint_raw())

    def get_is_invacation_hold_mode(self) -> bool:  # used
        """
        Return the
          'IsInVacationHoldMode' setting.

        inputs:
            None
        returns:
            (booL): True if is in vacation hold mode.
        """
        return False  # no schedule, hold not implemented

    def get_vacation_hold(self) -> bool:
        """
        Return the
        VacationHold setting.

        inputs:
            None
        returns:
            (bool): True if vacation hold is set.
        """
        return False  # no schedule, hold not implemented

    def get_system_switch_position(self) -> int:  # used
        """
        Return the system switch position, same as mode.

        inputs:
            None
        returns:
            (int) current mode for unit, should match value
                  in self.system_switch_position
        """
        self.refresh_zone_info()
        return self.device_id.get_mode()

    def set_heat_setpoint(self, temp: int) -> None:
        """
        Set a new heat setpoint.

        This will also attempt to turn the thermostat to 'Heat'
        inputs:
            temp(int): desired temperature in F
        returns:
            None
        """
        self.device_id.set_heat_setpoint(util.f_to_c(temp))

    def set_cool_setpoint(self, temp: int) -> None:
        """
        Set a new cool setpoint.

        This will also attempt to turn the thermostat to 'Cool'
        inputs:
            temp(int): desired temperature in ° F.
        returns:
            None
        """
        self.device_id.set_cool_setpoint(util.f_to_c(temp))

    def refresh_zone_info(self, force_refresh=False):
        """
        Refresh zone info from KumoCloud.

        inputs:
            force_refresh(bool): if True, ignore expiration timer.
        returns:
            None, device_id object is refreshed.
        """
        now_time = time.time()
        # refresh if past expiration date or force_refresh option
        if force_refresh or (
            now_time >= (self.last_fetch_time + self.fetch_interval_sec)
        ):
            self.Thermostat._need_fetch = True  # pylint: disable=protected-access
            try:
                self.Thermostat._fetch_if_needed()  # pylint: disable=protected-access
            except UnboundLocalError:  # patch for issue #205
                util.log_msg(
                    "WARNING: Kumocloud refresh failed due to timeout",
                    mode=util.BOTH_LOG,
                    func_name=1,
                )
            self.last_fetch_time = now_time
            # refresh device object
            self.device_id = self.Thermostat.get_target_zone_id(self.zone_name)


if __name__ == "__main__":
    # verify environment
    env.get_python_version()
    env.show_package_version(pykumo)

    # get zone override
    api.uip = api.UserInputs(argv_list=None, thermostat_type=kumolocal_config.ALIAS)
    zone_number = api.uip.get_user_inputs(api.uip.zone_name, api.input_flds.zone)

    _, Zone = tc.thermostat_basic_checkout(
        kumolocal_config.ALIAS, zone_number, ThermostatClass, ThermostatZone
    )

    tc.print_select_data_from_all_zones(
        kumolocal_config.ALIAS,
        kumolocal_config.get_available_zones(),
        ThermostatClass,
        ThermostatZone,
        display_wifi=False,
        display_battery=False,
    )

    # measure thermostat response time
    if kumolocal_config.check_response_time:
        MEASUREMENTS = 30
        meas_data = Zone.measure_thermostat_repeatability(
            MEASUREMENTS,
            func=Zone.pyhtcc.get_zones_info,
            measure_response_time=True,
        )
        ppp = pprint.PrettyPrinter(indent=4)
        ppp.pprint(meas_data)
