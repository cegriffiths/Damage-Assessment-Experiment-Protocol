## STAGE SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the stage

class stage:
    '''Stage Object: Controls position of the stage, and deals with calibrration'''
    def __init__(self):
        self.pos

    def calibrate(self):
        '''Calibrates the linear stage'''
        ## TODO

    def movedist(self, dist):
        '''Moves the linear stage a distance dist'''
        ## TODO

    def moveto(self, finalpos):
        '''Moves the linear stage to finalpos'''
        ## TODO
        print("Move stage to ", finalpos)