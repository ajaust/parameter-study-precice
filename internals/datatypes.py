
class InterfaceQuasiNewtonMethod():

    def __init__(self, ignore_time_window_reuse=False):
        self.ignore_time_window_reuse = ignore_time_window_reuse

#class AcceleratorType(Enum):
#    IQN_ILS = "IQN-ILS"
#    IQN_IMVJ = "IQN-IMVJ"
#
#    def __repr__(self):
#        return f"{self.value}"