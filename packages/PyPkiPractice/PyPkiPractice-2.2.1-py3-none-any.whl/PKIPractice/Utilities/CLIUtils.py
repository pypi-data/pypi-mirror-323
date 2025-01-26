"""
Module containing all utilities relevant for interacting with a command line interface.
"""

# Relative pathing from project root
import sys
from typing import Union
from os.path import abspath, dirname, join

script_dir = dirname(abspath(__file__))

if script_dir in ['PKI_Practice', 'PKI Practice', 'app']:
    sys.path.append(abspath(script_dir))
elif script_dir == 'PKIPractice':
    sys.path.append(abspath(join(script_dir, '..')))
else:
    sys.path.append(abspath(join(script_dir, '../..')))

from PKIPractice.Utilities.IngestUtils import *
from PKIPractice.Simulation.Network import PKINetwork


def get_default_auto() -> dict:
    """
    Retrieve the default autoconfiguration

    Returns:
        dict: The default autoconfiguration
    """
    auto_config: dict = {
        "level_count": 4,
        "count_by_level": [1, 2, 4, 8],
        "uid_hash": "sha256",
        "sig_hash": "sha256",
        "encrypt_alg": {
            "alg": "rsa",
            "params": {
                "pub_exp": 65537,
                "key_size": 2048
            }
        },
        "revoc_probs": [0.0, 0.0001, 0.001, 0.01],
        "cert_valid_durs": ["none", "00:15:00", "00:10:00", "00:05:00"],
        "cache_durs": ["none", "11:00", "06:00", "01:00"],
        "cooldown_durs": ["none", "5", "5", "5"],
        "timeout_durs": ["none", "20", "20", "20"],
        "log_save_filepath": "output/saved_network_logs_default.csv"
    }

    return auto_config


def get_default_manual() -> dict:
    """
    Retrieve the default manual configuration

    Returns:
        dict: The default manual configuration
    """
    manual_config: dict = {
        "default_root_ca": {
            "location": {
                "level": 1
            },
            "env_overrides": {
                "uid_hash": "sha3_512",
                "sig_hash": "sha3_512",
                "encrypt_alg": {
                    "alg": "ecc",
                    "params": {
                        "curve": "secp256r1"
                    }
                },
                "revoc_prob": 0.0,
                "cert_valid_dur": "none",
                "cache_dur": "none",
                "cooldown_dur": "none",
                "timeout_dur": "none"
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "server",
                "hardware_brand": "dell",
                "os_category": "microsoft",
                "os_subcategory": "windows_server",
                "os_dist": "windows_server_2019",
                "os_subdist": "standard",
                "account_type": "admin",
                "account_subtype": "domain_admin",
                "ca_status": "root_auth"
            },
            "holder_info": {
                "common_name": "Root Enterprises Root CA",
                "country": "US",
                "state": "CA",
                "locality": "San Francisco",
                "org": "Root Enterprises",
                "org_unit": "Certificates",
                "email": "root_ca_team@root_enterprises.com",
                "url": "root_enterprises.com/root_ca"
            }
        },
        "second_lvl_ca_one": {
            "location": {
                "level": 2
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512",
                "encrypt_alg": {
                    "alg": "ecc",
                    "params": {
                        "curve": "secp256r1"
                    }
                }
            },
            "holder_type_info": {
                "os_category": "unix",
                "os_subcategory": "linux",
                "os_dist": "ubuntu_server"
            }
        },
        "second_lvl_ca_two": {
            "location": {
                "level": 2
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512",
                "encrypt_alg": {
                    "alg": "ecc",
                    "params": {
                        "curve": "secp256r1"
                    }
                }
            },
            "holder_type_info": {
                "os_category": "unix",
                "os_subcategory": "linux",
                "os_dist": "ubuntu_server"
            }
        },
        "third_lvl_ca_one": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "Cert Incorporated South America CA",
                "country": "PE",
                "state": "Lima",
                "locality": "Ventanilla",
                "org": "Cert Incorporated",
                "org_unit": "South American Certificates",
                "email": "certs_sa@cert_incorporated.com",
                "url": "cert_incorporated.com/peru/intermediate_ca"
            }
        },
        "third_lvl_ca_two": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "CloudCert Inc West Africa CA",
                "country": "Nigeria",
                "state": "Oyo",
                "locality": "Ibadan",
                "org": "CloudCert Inc",
                "org_unit": "West African Certificates",
                "email": "certs_africa@cloudcert.com",
                "url": "cloudcert.com/nigeria/intermediate_ca"
            }
        },
        "third_lvl_ca_three": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "EuroPass International Norway CA",
                "country": "NO",
                "state": "Bergen",
                "locality": "Kokstad",
                "org": "EuroPass International",
                "org_unit": "Western European Certificates",
                "email": "certs_europe@europass.com",
                "url": "europass.com/norway_intermediate_ca"
            }
        },
        "third_lvl_ca_four": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "Lone Star Networking Houston CA",
                "country": "US",
                "state": "Texas",
                "locality": "Houston",
                "org": "Lone Star Networking",
                "org_unit": "North American Certificates",
                "email": "lone_star_certs@lonestarnet.com",
                "url": "lonestarnet.com/us/houston/intermediate_ca"
            }
        },
        "fourth_level_one": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "network",
                "hardware_subtype": "access_point",
                "hardware_brand": "cisco",
                "os_category": "routing",
                "os_subcategory": "openwrt",
                "os_dist": "openwrt",
                "os_subdist": "openwrt",
                "account_type": "admin",
                "account_subtype": "network_admin"
            }
        },
        "fourth_level_two": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "laptop",
                "hardware_brand": "asus",
                "os_category": "microsoft",
                "os_subcategory": "windows",
                "os_dist": "windows_10",
                "os_subdist": "home",
                "account_type": "user",
                "account_subtype": "personal"
            }
        },
        "fourth_level_three": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "peripheral",
                "hardware_subtype": "smart_card"
            }
        },
        "fourth_level_four": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "phone",
                "account_type": "user"
            }
        },
        "fourth_level_five": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "appliance",
                "hardware_subtype": "utm",
                "hardware_brand": "barracuda"
            }
        },
        "fourth_level_six": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "desktop",
                "os_category": "unix",
                "os_subcategory": "solaris",
                "account_subtype": "cloud_admin"
            }
        },
        "fourth_level_seven": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "iot",
                "hardware_brand": "arduino",
                "os_category": "unix",
                "os_subcategory": "linux",
                "os_dist": "alpine",
                "os_subdist": "alpine",
                "account_type": "user",
                "account_subtype": "guest"
            }
        },
        "fourth_level_eight": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "os_subcategory": "mac_os_x"
            }
        }
    }

    return manual_config


def ingest_config(args: list, default: bool) -> Union[tuple, None]:
    """
    Starts the program using the command-line arguments.

    Args:
        args (list): A list of command-line arguments.
        default (bool, optional): If True, use the default configuration files. Defaults to False.
    """

    # Check if a yaml file is passed on an interpreter before Python 3.10
    if sys.version_info[1] < 10:
        assert all('.yaml' not in arg for arg in args), (
            'Invalid configuration filepath provided.\n'
            '\t   Yaml files do not have support for Python versions before 3.10.\n'
            '\t   Please use a different configuration format (JSON, XML, TOML).\n'
        )

    # Check if there is a proper argument for the auto generation
    if not default:
        assert 'auto' in args[1], (
            'Invalid configuration filepath provided.\n'
            '\t   Please provide a proper auto configuration file by '
            'passing the filepath of your file as an command-line argument.\n'
            '\t   Example: python Main.py Default_Configs/default_auto.yaml\n'
        )

    # Check if there is a proper argument for the manual settings or if it's just one argument
    only_auto_or_default: bool = len(args) == 2 or default
    if only_auto_or_default:
        manual_exists: bool = True
    else:
        manual_exists: bool = 'manual' in args[2]
    assert manual_exists is True, (
        'Invalid configuration filepath provided.\n'
        '\t   Please provide a proper manual configuration file by '
        'passing the filepath of your file as an command-line argument.\n'
        '\t   Example: python Main.py Default_Configs/default_auto.yaml Default_Configs/default_manual.yaml\n'
    )

    # Warn if there are more than the two arguments that have been checked
    if len(args) > 3:
        print('Warning: More than two command-line argument provided.\n'
              '\t Please provide a configuration file by '
              'passing the filepath of your file as an command-line argument.\n'
              '\t   Example: python Main.py Default_Configs/default_auto.yaml '
              'Default_Configs/default_manual.yaml\n')

    # Pass auto argument to ingestion utilities
    if default:
        env_auto_settings: Union[dict, None] = get_default_auto()
        assert validate_settings_auto(env_auto_settings) is True, (
            'Ingested autoconfiguration settings were not found to be valid.\n'
            '\t   Please ensure your configuration file is correctly created.\n'
            '\t   Use the default configuration file as a template.\n'
        )
    else:
        env_auto_settings: Union[dict, None] = parse_config_auto(args[1])

    # Pass manual argument to ingestion utilities
    if default:
        env_manual_settings: Union[dict, None] = get_default_manual()
        env_manual_settings = search_for_typecast_manual(env_manual_settings)
        assert env_manual_settings is not None, (
            'Ingested manual configuration settings were not able to be adjusted due to '
            'unparsable configuration params.\n'
            '\t   Please ensure your configuration file is correctly created.\n'
            '\t   Use the default configuration file as a template.\n'
        )
    else:
        if len(args) > 2:
            env_manual_settings: Union[dict, None] = parse_config_manual(args[2])
        else:
            env_manual_settings: Union[dict, None] = None

    # Check the return values for both
    assert env_auto_settings is not None, (
        'Unparseable autoconfiguration file provided.\n'
        '\t   Please ensure that your configuration file exists or are properly created.\n'
        '\t   Use the default configuration files provided in the Default_Configs folder as a guide.\n'
    )

    if len(args) > 2:
        assert env_manual_settings is not None, (
            'Unparseable manual configuration file provided.\n'
            '\t   Please ensure that your configuration file exists or are properly created.\n'
            '\t   Use the default configuration files provided in the Default_Configs folder as a guide.\n'
        )

    return env_auto_settings, env_manual_settings


def start_program() -> None:
    """
    Starts the program. Used by RunConfig.py and command line call to start program.
    """
    # Name flags
    help_flag = False
    test_flag = False
    default_flag = False

    # Start assertion region
    try:
        pki_network: Union[None, PKINetwork] = None

        # Check if there are more than one argument
        assert len(sys.argv) > 1, (
            'No configuration file provided.\n' 
            '\t   Please provide a configuration file by '
            'passing the filepath of your file as an command-line argument.\n'
            '\t   Example: python Main.py Default_Configs/default_auto.yaml\n'
        )

        # Check if there is a help flag
        if any(arg in sys.argv for arg in ('-h', '--help')):
            print(
                '   Help flag detected.\n'
                '   Welcome to PKI Practice!\n'
                '   This is not really meant for much, I just wanted to practice PKI architecture.\n'
                '   However, that does not mean that it should not be fun to play with.\n'
                '\n'
                '   In terms of command-line usage, you need to provide only to files.\n'
                '   The first is a configuration file for the auto generation of the environment.\n'
                '   The second is a configuration file for the manual configuration of the environment.\n'
                '   The second file is optional to run the program, but the first can be run without the second.\n'
                '\n'
                '   Structure: python Main.py [options] [<autoconfig filepath>] [<manualconfig filepath>]\n'
                '   Example without second: python Main.py Default_Configs/default_auto.yaml\n'
                '   Example with second: python Main.py Default_Configs/default_auto.yaml '
                'Default_Configs/default_manual.yaml\n'
                '\n'
                '   Options:\n'
                '   -h\n'
                '   --help\n'
                "   Prints the help information you see now.\n"
                '   --------\n'
                '   -d\n'
                '   --default\n'
                "   Tells the program to run it's default configuration\n"
                '   --------\n'
                '   -t\n'
                '   --test\n'
                "   Tells the program to run in test mode, where it only runs enough of the program to conduct "
                "assessments.\n"
                '\n\n'
                '   For more details, please check out https://laoluadewoye.github.io/PKI_Practice_Python/.\n'
            )
            help_flag = True
            help_index = next((i for i, arg in enumerate(sys.argv) if arg in ('-h', '--help')), None)
            sys.argv.pop(help_index)

        # Check if there is a test flag
        if any(arg in sys.argv for arg in ('-t', '--test')):
            test_flag = True
            test_index = next((i for i, arg in enumerate(sys.argv) if arg in ('-t', '--test')), None)
            sys.argv.pop(test_index)

        # Check if there is a default flag
        if any(arg in sys.argv for arg in ('-d', '--default')):
            print(
                '   Default flag detected.\n'
                '   Welcome to PKI Practice!\n'
                '   This is not really meant for much, I just wanted to practice PKI architecture.\n'
                '   However, that does not mean that it should not be fun to play with.\n'
                '\n'
                '   In terms of command-line usage, you need to provide only to files.\n'
                '   The first is a configuration file for the auto generation of the environment.\n'
                '   The second is a configuration file for the manual configuration of the environment.\n'
                '   The second file is optional to run the program, but the first can be run without the second.\n'
                '\n'
                "   For more details, please run this command with the help option [-h | --help] "
                "or check out https://laoluadewoye.github.io/PKI_Practice_Python/.\n"
                '\n'
                '   For now though, here is a default run of the program using the default yaml files.\n'
            )
            default_flag = True
            default_index = next((i for i, arg in enumerate(sys.argv) if arg in ('-d', '--default')), None)
            sys.argv.pop(default_index)

        # Start the program if nothing else is needed.
        if not help_flag:
            # Read the configuration files or default configurations
            env_auto_settings, env_manual_settings = ingest_config(sys.argv, default=default_flag)

            # Build the environment
            pki_network = PKINetwork('Sample_Net', env_auto_settings, env_manual_settings)
            pki_network.set_root_certificates()

        # Go even further if not just testing the CLI options.
        if not test_flag and not help_flag:
            print(pki_network)
            pki_network.save_logs()

    # Ultimate error escape
    except AssertionError as e:
        print(f'\nException: {e}')
