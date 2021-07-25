class PreciceConfigurationGenerator():

    def __init__( self, template: str ):
        self.template = template



    def write_precice_configuration_file(self, filename: str, configuration: str ):
        with open(filename, "w") as fstr:
            fstr.write(configuration)
            #fstr.write(testcase.get_config_header())
            #fstr.write(testcase.set_up_acceleration())
            #fstr.write(testcase.get_config_footer())

    def generate_configuration(self, filename: str, subsitutions: dict ):

        new_precice_config = self.template




        self.write_precice_configuration_file( filename, new_precice_config )


