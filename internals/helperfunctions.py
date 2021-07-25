def write_precice_configuration_file(testcase, filename, is_serial_coupling=True):

    fstr = open(filename, "w")

    fstr.write(testcase.get_config_header())
    fstr.write(testcase.set_up_acceleration())
    fstr.write(testcase.get_config_footer())

    fstr.close()
