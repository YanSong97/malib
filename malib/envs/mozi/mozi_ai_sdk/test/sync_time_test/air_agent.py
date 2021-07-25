# _*_ coding : utf-8 _*_
'''
作者 : 解洋
时间: 2020-3-24
'''

class CAgent():
    def __init__(self):
        self.class_name = 'aircraft_'
        self.doctrine_num = 0
        self.mission_num = 0
        self.contact_num = 0
        self.aircraft_num = 0
    def test(self,scenario):
        for side_k , side_v in scenario.get_sides().items():
            if len(side_v.aircrafts) > 0:
                pass
            scenario.mozi_server.run_simulate()