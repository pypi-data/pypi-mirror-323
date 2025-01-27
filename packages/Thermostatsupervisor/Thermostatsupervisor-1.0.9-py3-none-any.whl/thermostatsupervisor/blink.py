"""Blink Camera."""
# built-in imports
import asyncio
import os
import pprint
import sys
import time
import traceback
from aiohttp import ClientSession

# third party imports

# local imports
from thermostatsupervisor import blink_config
from thermostatsupervisor import thermostat_api as api
from thermostatsupervisor import thermostat_common as tc
from thermostatsupervisor import environment as env
from thermostatsupervisor import utilities as util

# Blink library
BLINK_DEBUG = True  # debug uses local blink repo instead of pkg
if BLINK_DEBUG and not env.is_azure_environment():
    pkg = "blinkpy.blinkpy"
    mod_path = "..\\blinkpy"
    if env.is_interactive_environment():
        mod_path = "..\\" + mod_path
    blinkpy = env.dynamic_module_import("blinkpy.blinkpy", mod_path, pkg)
    auth = env.dynamic_module_import("blinkpy.auth", mod_path, pkg)
else:
    from blinkpy import auth  # noqa E402, from path / site packages
    from blinkpy import blinkpy  # noqa E402, from path / site packages


class ThermostatClass(blinkpy.Blink, tc.ThermostatCommon):
    """Blink Camera thermostat functions."""

    def __init__(self, zone, verbose=True):
        """
        Constructor, connect to thermostat.

        inputs:
            zone(str):  zone of thermostat.
            verbose(bool): debug flag.
        """
        # Blink server auth credentials from env vars
        self.BL_UNAME_KEY = "BLINK_USERNAME"
        self.BL_PASSWORD_KEY = "BLINK_PASSWORD"
        self.bl_uname = os.environ.get(
            self.BL_UNAME_KEY, "<" + self.BL_UNAME_KEY + "_KEY_MISSING>"
        )
        self.bl_pwd = os.environ.get(
            self.BL_PASSWORD_KEY, "<" + self.BL_PASSWORD_KEY + "_KEY_MISSING>"
        )
        self.auth_dict = {"username": self.bl_uname, "password": self.bl_pwd}
        self.BL_2FA_KEY = "BLINK_2FA"
        self.bl_2fa = os.environ.get(
            self.BL_2FA_KEY, "<" + self.BL_2FA_KEY + "_KEY_MISSING>"
        )
        self.verbose = verbose
        self.zone_number = int(zone)

        # connect to Blink server and authenticate
        self.args = None
        self.thermostat_type = None
        self.blink = None
        if env.get_package_version(blinkpy) >= (0, 22, 0):
            asyncio.run(self.async_auth_start())
        else:
            self.auth_start()

        # get cameras
        self.camera_metadata = {}
        self.get_cameras()

        # configure zone info
        self.zone_name = self.get_zone_name()
        self.device_id = None  # initialize
        self.device_id = self.get_target_zone_id(self.zone_number)
        self.serial_number = None  # will be populated when unit is queried.

    def auth_start(self):
        """
        blinkpy < 0.22.0-compatible start
        """
        # construct the superclass
        # call both parent class __init__
        self.args = [self.bl_uname, self.bl_pwd]

        # set tstat type and debug flag
        self.thermostat_type = blink_config.ALIAS

        # establish connection
        self.blink = blinkpy.Blink()
        if self.blink is None:
            print(traceback.format_exc())
            raise RuntimeError(
                "ERROR: Blink object failed to instantiate "
                f"for zone {self.zone_number}"
            )

        self.blink.auth = auth.Auth(self.auth_dict, no_prompt=True)
        self.blink.start()
        try:
            self.blink.auth.send_auth_key(self.blink, self.bl_2fa)
        except AttributeError:
            error_msg = (
                "ERROR: Blink authentication failed for zone "
                f"{self.zone_number}, this may be due to spamming the "
                "blink server, please try again later."
            )
            banner = "*" * len(error_msg)
            print(banner)
            print(error_msg)
            print(banner)
            sys.exit(1)
        self.blink.setup_post_verify()

    async def async_auth_start(self):
        """
        blinkpy 0.22.0 introducted async start, this is the compatible
        auth_start function.
        """
        async with ClientSession() as session:
            # construct the superclass
            # call both parent class __init__
            self.args = [self.bl_uname, self.bl_pwd]
            # blinkpy.Blink.__init__(self, *self.args)

            # set tstat type and debug flag
            self.thermostat_type = blink_config.ALIAS

            # establish connection
            self.blink = blinkpy.Blink(session=session)
            if self.blink is None:
                print(traceback.format_exc())
                raise RuntimeError(
                    "ERROR: Blink object failed to instantiate "
                    f"for zone {self.zone_number}"
                )
            self.blink.auth = auth.Auth(self.auth_dict, no_prompt=True, session=session)
            await self.blink.start()
            try:
                await self.blink.auth.send_auth_key(self.blink, self.bl_2fa)
            except AttributeError:
                error_msg = (
                    "ERROR: Blink authentication failed for zone "
                    f"{self.zone_number}, this may be due to spamming"
                    " the blink server, please try again later."
                )
                banner = "*" * len(error_msg)
                print(banner)
                print(error_msg)
                print(banner)
                sys.exit(1)
            await self.blink.setup_post_verify()

    def get_zone_name(self):
        """
        Return the name associated with the zone number from metadata dict.

        inputs:
            None
        returns:
            (str) zone name
        """
        return blink_config.metadata[self.zone_number]["zone_name"]

    def get_target_zone_id(self, zone=0):
        """
        Return the target zone ID.

        inputs:
            zone(int): zone number.
        returns:
            (obj): Blink object
        """
        # return the target zone object
        return zone

    def get_cameras(self):
        """
        Get the blink cameras
        """
        table_length = 20
        if self.verbose:
            print("blink camera inventory:")
            print("-" * table_length)
        for name, camera in self.blink.cameras.items():
            if self.verbose:
                print(name)
                print(camera.attributes)
            self.camera_metadata[name] = camera.attributes
        if self.verbose:
            print("-" * table_length)

    def get_all_metadata(self, zone=None):
        """Get all thermostat meta data for device_id from local API.

        inputs:
            zone(): specified zone
        returns:
            (dict): dictionary of meta data.
        """
        return self.get_metadata(zone)

    def get_metadata(self, zone=None, trait=None, parameter=None):
        """Get thermostat meta data for device_id from local API.

        inputs:
            zone(): specified zone
            trait(str): trait or parent key, if None will assume a non-nested
            dict
            parameter(str): target parameter, if None will return all.
        returns:
            (dict): dictionary of meta data.
        """
        del trait  # unused on blink
        zone_name = blink_config.metadata[self.zone_number]["zone_name"]
        if self.blink.cameras == {}:
            raise ValueError(
                "camera list is empty when searching for camera" f" {zone_name}"
            )
        for name, camera in self.blink.cameras.items():
            # print(f"DEBUG: camera {name}: {camera.attributes}")
            if name == zone_name:
                if self.verbose:
                    print(f"found camera {name}: {camera.attributes}")
                if parameter is None:
                    return camera.attributes
                else:
                    return camera.attributes[parameter]
        raise ValueError(f"Camera zone {zone}({zone_name}) was not found")

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
        self.fetch_interval_sec = 10  # age of server data before refresh
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
        self.thermostat_type = blink_config.ALIAS
        self.device_id = Thermostat_obj.device_id
        self.Thermostat = Thermostat_obj
        self.zone_number = Thermostat_obj.zone_number
        self.zone_name = self.get_zone_name()
        self.zone_metadata = Thermostat_obj.get_metadata(zone=self.zone_number)

    def get_display_temp(self) -> float:  # used
        """
        Refresh the cached zone information and return Indoor Temp in °F.

        inputs:
            None
        returns:
            (float): indoor temp in °F.
        """
        raw_temp = self.zone_metadata.get(blink_config.API_TEMPF_MEAN)
        if isinstance(raw_temp, (str, float, int)):
            raw_temp = float(raw_temp)
        elif isinstance(raw_temp, type(None)):
            raw_temp = float(util.BOGUS_INT)
        return raw_temp

    def get_zone_name(self) -> str:
        """
        Return the name associated with the zone number from metadata dict.

        inputs:
            None
        returns:
            (str) zone name
        """
        return blink_config.metadata[self.zone_number]["zone_name"]

    def get_display_humidity(self) -> (float, None):
        """
        Refresh the cached zone information and return IndoorHumidity.

        inputs:
            None
        returns:
            (float, None): indoor humidity in %RH, None if not supported.
        """
        return None  # not available

    def get_is_humidity_supported(self) -> bool:
        """Return humidity sensor status."""
        return self.get_display_humidity() is not None

    def is_heat_mode(self) -> int:
        """Return the heat mode."""
        return 0  # not applicable

    def is_cool_mode(self) -> int:
        """Return the cool mode."""
        return 0  # not applicable

    def is_dry_mode(self) -> int:
        """Return the dry mode."""
        return 0  # not applicable

    def is_auto_mode(self) -> int:
        """Return the auto mode."""
        return 0  # not applicable

    def is_fan_mode(self) -> int:
        """Return the fan mode."""
        return 0  # not applicable

    def is_off_mode(self) -> int:
        """Return the off mode."""
        return 1  # always off

    def is_heating(self) -> int:
        """Return 1 if actively heating, else 0."""
        return 0  # not applicable

    def is_cooling(self) -> int:
        """Return 1 if actively cooling, else 0."""
        return 0  # not applicable

    def is_drying(self) -> int:
        """Return 1 if drying relay is active, else 0."""
        return 0  # not applicable

    def is_auto(self) -> int:
        """Return 1 if auto relay is active, else 0."""
        return 0  # not applicable

    def is_fanning(self) -> int:
        """Return 1 if fan relay is active, else 0."""
        return 0  # not applicable

    def is_power_on(self) -> int:
        """Return 1 if power relay is active, else 0."""
        return 1  # always on

    def is_fan_on(self) -> int:
        """Return 1 if fan relay is active, else 0."""
        return 0  # not applicable

    def is_defrosting(self) -> int:
        """Return 1 if defrosting is active, else 0."""
        return 0  # not applicable

    def is_standby(self) -> int:
        """Return 1 if standby is active, else 0."""
        return 0  # not applicable

    def get_system_switch_position(self) -> int:
        """Return the thermostat mode.

        inputs:
            None
        returns:
            (int): thermostat mode, see tc.system_switch_position for details.
        """
        return self.system_switch_position[self.OFF_MODE]

    def get_wifi_strength(self) -> float:  # noqa R0201
        """Return the wifi signal strength in dBm."""
        raw_wifi = self.zone_metadata.get(blink_config.API_WIFI_STRENGTH)
        if isinstance(raw_wifi, (str, float, int)):
            return float(raw_wifi)
        else:
            return float(util.BOGUS_INT)

    def get_wifi_status(self) -> bool:  # noqa R0201
        """Return the wifi connection status."""
        raw_wifi = self.get_wifi_strength()
        if isinstance(raw_wifi, (float, int)):
            return raw_wifi >= util.MIN_WIFI_DBM
        else:
            return False

    def get_battery_voltage(self) -> float:  # noqa R0201
        """Return the battery voltage in volts."""
        raw_voltage = self.zone_metadata.get(blink_config.API_BATTERY_VOLTAGE)
        if isinstance(raw_voltage, (str, float, int)):
            return float(raw_voltage) / 100.0
        else:
            return float(util.BOGUS_INT)

    def get_battery_status(self) -> bool:  # noqa R0201
        """Return the battery status."""
        raw_status = self.zone_metadata.get(blink_config.API_BATTERY_STATUS)
        if isinstance(raw_status, str):
            raw_status = raw_status == "ok"
        return raw_status


if __name__ == "__main__":
    # verify environment
    env.get_python_version()
    env.show_package_version(blinkpy)

    # get zone override
    api.uip = api.UserInputs(argv_list=None, thermostat_type=blink_config.ALIAS)
    zone_number = api.uip.get_user_inputs(api.uip.zone_name, api.input_flds.zone)

    _, Zone = tc.thermostat_basic_checkout(
        blink_config.ALIAS, zone_number, ThermostatClass, ThermostatZone
    )

    # this code is rem'd out because it will trigger blink server spam detectors.
    # tc.print_select_data_from_all_zones(
    #     blink_config.ALIAS,
    #     blink_config.get_available_zones(),
    #     ThermostatClass,
    #     ThermostatZone,
    #     display_wifi=True,
    #     display_battery=True,
    # )

    # measure thermostat response time
    if blink_config.check_response_time:
        MEASUREMENTS = 30
        meas_data = Zone.measure_thermostat_repeatability(
            MEASUREMENTS,
            func=Zone.pyhtcc.get_zones_info,
            measure_response_time=True,
        )
        ppp = pprint.PrettyPrinter(indent=4)
        ppp.pprint(meas_data)
