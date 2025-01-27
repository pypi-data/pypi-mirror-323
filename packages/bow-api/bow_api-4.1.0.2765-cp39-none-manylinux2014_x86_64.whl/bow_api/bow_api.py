"""! @package bow_client
This is the documentation for the bow_client module.

This module provides an interface for the BOW python SDK which allows you to connect to and interact with robots running a BOW driver.
"""

# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_data
from lib_client import animus_client as bow_client
import logging
from typing import Union, Tuple, Any, List, Optional

## A logging.Logger object created to write information about this BOW client to the logs and terminal.
log = bow_data.create_logger("BOWClient", logging.INFO)
_bow_messages_version = "v1.1.55"
_bow_core_version = "v4.5.3.1898"
_bow_client_version = "v4.1.0.2765"
_sdk_version = "v2.1.1.3624"
_sdk_build_date = "2025-01-27-00:44:33-GMT"

# Setup default audio parameters for the built-in audio player
# Backends = ["alsa", "wasapi", "dsound", "winmm", "pulse", "jack", "coreaudio",
#                   "sndio", "audio4", "oss", "opensl", "openal", "sdl"]
# SampleRate
# Channels
# packets transmitted per second
# sizeinframes - leave true
from typing import TypedDict

## The Robot class.
# Each instance represents a robot connection. You can have multiple robots connected, each with their own class to allow for multiple synchronised robot control.
class Robot:

    class ChannelsDict(TypedDict):
        vision: bow_data.ImageSamplesChannel
        audition: bow_data.AudioSamplesChannel
        tactile: bow_data.TactileSamplesChannel
        proprioception: bow_data.ProprioceptionSampleChannel
        motor: bow_data.MotorSampleChannel
        speech: bow_data.StringSampleChannel
        voice: bow_data.AudioSamplesChannel
        interoception: bow_data.InteroceptionSampleChannel
        exteroception: bow_data.ExteroceptionSampleChannel


    ## The Robot class initialiser.
    # The constructor accepts the robot details obtained from bow_client.get_robots()
    # @param robot_details **bow_utils.Robot**: The chosen robot selected from the array of robots returned when running bow_client.get_robots().
    def __init__(self, robot_details: bow_data.Robot):
        self.robot_details = robot_details
        self.robot_id = self.robot_details.robot_id

        self.vision = bow_data.ImageSamplesChannel("vision", self.get_channel, self.set_channel)
        self.audition = bow_data.AudioSamplesChannel("audition", self.get_channel, self.set_channel)
        self.tactile = bow_data.TactileSamplesChannel("tactile", self.get_channel, self.set_channel)
        self.proprioception = bow_data.ProprioceptionSampleChannel("proprioception", self.get_channel, self.set_channel)
        self.motor = bow_data.MotorSampleChannel("motor", self.get_channel, self.set_channel)
        self.speech = bow_data.StringSampleChannel("speech", self.get_channel, self.set_channel)
        self.voice = bow_data.AudioSamplesChannel("voice", self.get_channel, self.set_channel)
        self.interoception = bow_data.InteroceptionSampleChannel("interoception", self.get_channel, self.set_channel)
        self.exteroception = bow_data.ExteroceptionSampleChannel("exteroception", self.get_channel, self.set_channel)

        self.channels = ChannelsDict = {
            "vision": self.vision,
            "audition": self.audition,
            "tactile": self.tactile,
            "proprioception": self.proprioception,
            "motor": self.motor,
            "speech": self.speech,
            "voice": self.voice,
            "interoception": self.interoception,
            "exteroception": self.exteroception,
        }

    ## Starts a connection with the robot.
    # This method starts a peer to peer connection with the robot using the robot details previously passed in to the constructor.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful connection. If error.Success is False you can inspect error.Description for more information.
    def connect(self) -> bow_data.Error:
        log.info("Connecting with robot {}".format(self.robot_details.name))

        connect_request = bow_data.ChosenRobotProto(
            chosenOne=self.robot_details
        ).SerializeToString()

        return bow_data.Error().FromString(
            bow_client.Connect(connect_request, len(connect_request))
        )

    ## Opens a channel.
    # Opens a channel between the robot and client, over which data for the chosen channel is transmitted.
    # @param channel_name **str**: The name of the channel you wish to open. Available options are specific to the robot but can be vision, audition, proprioception, motor, voice, speech or tactile.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful open. If error.Success is False you can inspect error.Description for more information.
    def open_channel(self, channel_name: str) -> bow_data.Error:
        log.info("Opening {} channel".format(channel_name))

        open_channel_request = bow_data.OpenModalityProto(
            modalityName=channel_name,
            fps=30
        ).SerializeToString()

        openError = bow_data.Error().FromString(
            bow_client.OpenModality(self.robot_id.encode(), open_channel_request, len(open_channel_request))
        )

        if openError.Success:
            if self.channels.__contains__(channel_name):
                self.channels[channel_name].open = True

        return openError

    ## Sends data on an open channel.
    # This sends a sample of data of the correct type over the open channel to the robot.
    # @param channel_name **str**: The name of the channel you wish to send data on.
    # @param sample **bow_utils.MotorSample**, **bow_utils.AudioSamples**, **bow_utils.StringSample**:
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful send. If error.Success is False you can inspect error.Description for more information.
    def set_channel(self, channel_name: str, sample: Union[
        bow_data.AudioSample,
        bow_data.AudioSamples,
        List[bow_data.AudioSample],
        bow_data.TactileSamples,
        bow_data.TactileSample,
        List[bow_data.TactileSample],
        bow_data.ProprioceptionSample,
        bow_data.MotorSample,
        bow_data.StringSample,
        bow_data.BlobSample,
        bow_data.Int64Array,
        bow_data.Float32Array,
        bow_data.Command,
        str,
        List[float],
        List[int]]
                     ) -> bow_data.Error:

        # Sample is validated in validate_encode_data before being transmitted
        dtype, data, data_len = bow_data.encode_data(sample)
        if dtype is not None:
            return bow_data.Error().FromString(
                bow_client.SetModality(self.robot_id.encode(), channel_name.encode(), dtype, data, data_len)
            )
        else:
            error = bow_data.Error()
            error.Success = False
            error.Code = -1
            error.Description = "Failed to encode data"
            return error

    ## @brief Reads data from an open channel.
    # This reads a data sample from the robot on the named open channel.
    # @param channel_name **str**: The name of the channel you wish to receive data on.
    # @param blocking **bool**: Optional parameter, if True, function will block until data is received from the robot.
    # @return **bow_utils.ProprioceptionSample**, **bow_utils.ExteroceptionSample**, **bow_utils.InteroceptionSample**, **List[bow_utils.AudioSample]**, **List[bow_utils.ImageSampleHelper]**, **List[utils.TactileSample]**: type depends on the chosen channel.
    def get_channel(self,
                     channel_name: str,
                     blocking: Optional[bool] = False
                     ) -> Tuple[Union[List[bow_data.AudioSample],
                                List[bow_data.TactileSample],
                                bow_data.MotorSample,
                                bow_data.ProprioceptionSample,
                                bow_data.ExteroceptionSample,
                                bow_data.InteroceptionSample,
                                bow_data.StringSample,
                                bow_data.BlobSample,
                                bow_data.Float32Array,
                                bow_data.Int64Array,
                                None],
                                bow_data.Error]:
        get_result = bow_client.GetModality(self.robot_id.encode(), channel_name.encode(), int(bool(blocking)))
        sample = bow_data.GetModalityProto().FromString(get_result)

        if not sample.error.Success:
            return None, sample.error

        new_sample = bow_data.decode_data(sample.sample)
        if new_sample is None:
            sample.error.Success = False
            sample.error.Code = -1
            return None, sample.error

        return new_sample, sample.error

    ## Closes an open channel.
    # This closes the named open channel.
    # @param channel_name **str**: The name of the channel you wish to close.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful closure. If error.Success is False you can inspect error.Description for more information.
    def close_channel(self, channel_name: str) -> bow_data.Error:
        log.info("Closing {} channel".format(channel_name))
        return bow_data.Error().FromString(
            bow_client.CloseModality(self.robot_id.encode(), channel_name.encode())
        )

    ## Close the connection to the robot.
    # This closes the peer to peer connection between client and robot.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful disconnection. If error.Success is False you can inspect error.Description for more information.
    def disconnect(self) -> bow_data.Error:
        log.info("Disconnecting from {}".format(self.robot_details.name))
        return bow_data.Error().FromString(
            bow_client.Disconnect(self.robot_id.encode())
        )

    # DEPRECATED
    def open_modality(self, channel_name: str) -> bow_data.Error:
        log.warning(
            "open_modality has been deprecated. Please use open_channel instead. This will be removed in the future")
        return self.open_channel(channel_name)

    def set_modality(self, channel_name: str, sample: Any) -> bow_data.Error:
        log.warning("set_modality has been deprecated. Please use set_channel instead. This will be removed in the future")
        return self.set_channel(channel_name, sample)

    def get_modality(self, channel_name: str, blocking: bool) -> Any:
        log.warning("get_modality has been deprecated. Please use get_channel instead. This will be removed in the future")
        return self.get_channel(channel_name, blocking)

    def close_modality(self, channel_name: str) -> bow_data.Error:
        log.warning("close_modality has been deprecated. Please use close_channel instead. This will be removed in the future")
        return self.close_channel(channel_name)


## Gets the SDK version information.
# Gets the version of the bow client and animus core libraries.
# @return **str**: A version string in the form:
# @code
# BOW Client version v3.2.1.1683 \nBOW Core version v3.2.1.1201\nBuilt with BowMessages v0.10.31 on 2023-08-24-14:13:43-UTC \nCopyright (C) 2023 Bettering Our Worlds (BOW) Ltd. - All Rights Reserved\n'
# @endcode
def version() -> str:
    version_string = bow_client.VersionGo()
    log.info(version_string)
    return version_string


## Quick connect function to simplify process of connecting to a robot and opening channels.
# Quick connect talks to the system tray application to login, get a list of robots, connect to the robot chosen via the system tray and open the requested channels.
# @param app_name **str**: Can be created with bow_util.create_logger(). A logging object which enables the SDK to output useful information about your robot and robot connection to the terminal.
# @param channels **List[str]**: A list of the channels you wish to open on the robot. Channels are specific to the robot but can be vision, audition, proprioception, motor, voice, speech and tactile.
# @param verbose **bool**: Determines whether latency information is printed out. The latency information includes the measured round trip latency between the sdk and the robot as well as framerate and latency information for all channels separately.
# @param audio_params **bow_utils.AudioParams**: Configures the settings for the audio streams. Use None for default settings.
# @return Robot: Returns an instance of the Robot class, which represents the connected robot. Returns None if no connection made.
# @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful connection. If error.Success is False you can inspect error.Description for more information.
def quick_connect(app_name: str,
                  channels: List[str],
                  verbose: bool = True,
                  audio_params: bow_data.AudioParams = bow_data.AudioParams(
                    Backends=[""],
                    SampleRate=16000,
                    Channels=1,
                    SizeInFrames=True,
                    TransmitRate=30)
                  ) -> Tuple[Union[Robot, None], bow_data.Error]:

    pylog = bow_data.create_logger(app_name, logging.DEBUG)

    setup_result = setup(pylog.name, verbose, audio_params)
    if not setup_result.Success:
        return None, setup_result

    login_result = login_user("", "", True)
    if login_result.Success:
        pylog.info("Logged in")
    else:
        return None, login_result

    get_robots_result = get_robots(False, False, True)
    if not get_robots_result.localSearchError.Success:
        pylog.error(get_robots_result.localSearchError.Description)

    if not get_robots_result.remoteSearchError.Success:
        pylog.error(get_robots_result.remoteSearchError.Description)

    if len(get_robots_result.robots) == 0:
        pylog.info("No Robots found")
        close_client_interface()
        return None, bow_data.Error(Success=False, Code=62, Description="No Robots Found")

    chosen_robot_details = get_robots_result.robots[0]

    myrobot = Robot(chosen_robot_details)
    connected_result = myrobot.connect()
    if not connected_result.Success:
        pylog.error("Could not connect with robot {}".format(myrobot.robot_details.robot_id))
        close_client_interface()
        return None, connected_result

    all_robot_channels = (list(chosen_robot_details.robot_config.input_modalities)
                            + list(chosen_robot_details.robot_config.output_modalities))
    print(all_robot_channels)
    for channel in channels:
        if channel in all_robot_channels:
            open_result = myrobot.open_channel(channel)
            if not open_result.Success:
                pylog.error(f"Failed to open {channel} channel: {open_result.Description}")
        else:
            pylog.warning(f"{channel} channel is not available for the chosen robot. Channel ignored")

    err = bow_data.Error()
    err.Success = True
    err.Code = 0
    err.Description = ""
    return myrobot, err

## Configures variables required for a BOW client.
# This function sets up the audio sampling and playback settings, sets the folder name for the log files and otherwise initialises all the variables required for a BOW client.
# @param audio_params **bow_utils.AudioParams**: Configures the settings for the audio streams. Use None for default settings.
# @param logdir **str**: Name of the desired directory for logs. Should take logging.Logger.name.
# @param verbose **bool**: Determines whether the latency of messages are reported in the log.
# @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful setup. If error.Success is False you can inspect error.Description for more information.
def setup(app_name: str, verbose: bool, audio_params: bow_data.AudioParams = bow_data.AudioParams(
                    Backends=[""],
                    SampleRate=16000,
                    Channels=1,
                    SizeInFrames=True,
                    TransmitRate=30)) -> bow_data.Error:

    setup_request = bow_data.SetupClientProto(
        audio_params=audio_params,
        logDir=app_name,
        latencyLogging=verbose,
    ).SerializeToString()
    return bow_data.Error().FromString(
        bow_client.Setup(setup_request, len(setup_request))
    )

## Login to your BOW account.
# Login with your BOW username and password to initialise communication session and therefore communicate with robots associated with your account.
# If you have the System Tray application installed, then you can bypass entering your username and password by setting system_login to True which will login using the credentials used for the Systray application.
# @param username **str**: Your BOW username.
# @param password **str**: Your BOW password.
# @param system_login **bool**: True logs in using System Tray Application credentials, False uses provided credentials.
def login_user(username: str, password: str, system_login: bool) -> bow_data.Error:
    log.info("Logging in user")

    login_request = bow_data.LoginProto(
        username=username,
        password=password,
        systrayLogin=system_login
    ).SerializeToString()

    return bow_data.Error().FromString(
        bow_client.LoginUser(login_request, len(login_request))
    )

## Get list of available robots.
# Returns the list of robots associated with your BOW account that are available on the local network or remotely.
# @param get_local **bool**: True to include robots on local network in search.
# @param get_remote **bool**: True to include robots available remotely in search.
# @param get_system **bool**: True returns the robot currently selected in the Systray.
# @return **bow_util.GetRobotsProtoReply**: This object consists of:
# **remoteSearchError** of type *bow_utils.Error*,
# **localSearchError** of type *bow_utils.Error* and
# **robots** an iterable containing the robot details for each robot detected. Each element can be passed to the Robot class constructor.
#
# **Example**
# @code
# get_robots_result = get_robots(False, False, True)
# chosen_robot_details = get_robots_result.robots[0]
# myrobot = Robot(chosen_robot_details)
# @endcode
def get_robots(get_local: bool = False, get_remote: bool = False, get_system: bool = False) -> bow_data.GetRobotsProtoReply:
    if get_local:
        log.warning("Getting local robots is not yet available. Setting to false")
        get_local = False

    get_robots_request = bow_data.GetRobotsProtoRequest(
        getLocal=get_local,
        getRemote=get_remote,
        systrayRobot=get_system
    ).SerializeToString()

    return bow_data.GetRobotsProtoReply().FromString(
        bow_client.GetRobots(get_robots_request, len(get_robots_request))
    )

## Closes your BOW client.
# This closes the BOW client, to restart a BOW client after closing, the setup function would need to be called again.
def close_client_interface() -> None:
    log.info("Bow Session closed")
    bow_client.CloseClientInterfaceGo()


