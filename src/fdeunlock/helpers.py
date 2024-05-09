# -*- coding: utf-8 -*-

"""
fdeunlock helpers
"""

from __future__ import absolute_import

import os
import logging
import configparser
from glob import glob

from appdirs import user_config_dir, user_data_dir
from paramiko import SSHConfig

LOG = logging.getLogger(__name__)


def ensure_permissions(path, mode):
    try:
        path_stat = os.stat(path)
    except FileNotFoundError:
        return

    previous_mode = path_stat.st_mode & 0o7777
    mode &= 0o7777
    if previous_mode != mode:
        os.chmod(path, mode)
        LOG.info(
            "Changed permissions of \"{}\" from {:0>4o} to {:0>4o}.".format(
                path,
                previous_mode,
                mode,
            )
        )


def get_user_dir(dir_type):
    dir_path = None
    if dir_type == 'config':
        dir_path = user_config_dir(appname='fdeunlock')
    elif dir_type == 'data':
        dir_path = user_data_dir(appname='fdeunlock')
    else:
        raise NotImplementedError
    os.makedirs(dir_path, exist_ok=True)  # pylint: disable=unexpected-keyword-arg
    return dir_path


def read_config():
    config_dir = get_user_dir('config')
    cfg_files = glob(os.path.join(config_dir, 'config.d/*.cfg'))
    cfg_files.append(os.path.join(config_dir, 'config.cfg'))
    for cfg_file in cfg_files:
        ensure_permissions(cfg_file, 0o0600)
    cfg = configparser.ConfigParser(defaults={
        'start_command': 'None',  # Is converted by configparser to a str anyway.
        'start_command_shell': 'False',
        'additional_checksum_commands': '',
        'diff_command': 'diff',
        'authenticated_latency_deviation': '10.0',
        'unauthenticated_latency_deviation': '1.0',
    })
    cfg.read(cfg_files)
    LOG.debug("Read configuration files: {}".format(cfg_files))
    return cfg


def read_properties_config():
    config_dir = get_user_dir('config')
    properties = configparser.ConfigParser()
    properties_file = os.path.join(config_dir, 'properties.ini')
    ensure_permissions(properties_file, 0o0600)
    properties.read(properties_file)
    LOG.debug("Read properties file: {}".format(properties_file))
    return properties


def write_properties_config(properties):
    config_dir = get_user_dir('config')
    properties_file = os.path.join(config_dir, 'properties.ini')
    with open(properties_file, 'w') as properties_fh:
        properties.write(properties_fh)
    ensure_permissions(properties_file, 0o0600)


def read_ssh_config():
    ssh_config_file = os.path.join(
        os.environ['HOME'],
        '.ssh',
        'config')

    ssh_cfg = None
    try:
        with open(ssh_config_file) as ssh_cfg_fh:
            ssh_cfg = SSHConfig()
            ssh_cfg.parse(ssh_cfg_fh)
    except Exception as err:  # pylint: disable=broad-except
        LOG.warning("Default SSH configuration could not be read: {}".format(err))

    return ssh_cfg
