import numpy as np
from scipy.interpolate import griddata
import glob, os
import re
from refdb.common.models import SetModel
from refdb.common.models import ReferenceModel
import matplotlib
import matplotlib.markers as mark
from matplotlib.markers import MarkerStyle
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import lines as plotline
from matplotlib.pyplot import show, plot, ion, figure
import random
from sklearn.metrics import mean_absolute_error

std_coef = 3

def htmlcolor(r, g, b):
    def _chkarg(a):
        if isinstance(a, int): # clamp to range 0--255
            if a < 0:
                a = 0
            elif a > 255:
                a = 255
        elif isinstance(a, float): # clamp to range 0.0--1.0 and convert to integer 0--255
            if a < 0.0:
                a = 0
            elif a > 1.0:
                a = 255
            else:
                a = int(round(a*255))
        else:
            raise ValueError('Arguments must be integers or floats.')
        return a
    r = _chkarg(r)
    g = _chkarg(g)
    b = _chkarg(b)
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)

class SetPlot:

    def __init__(self, set_id=None):
        self.set = SetModel.objects.with_id(set_id)

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []
        a1_r1 = []
        a1_r1.append(self.set.raw_pressure['aliq1']['run1'])
        a1_r1.append(self.set.raw_uptake['aliq1']['run1'])
        a1_r2 = []
        a1_r2.append(self.set.raw_pressure['aliq1']['run2'])
        a1_r2.append(self.set.raw_uptake['aliq1']['run2'])

        a2_r1 = []
        a2_r1.append(self.set.raw_pressure['aliq2']['run1'])
        a2_r1.append(self.set.raw_uptake['aliq2']['run1'])
        a2_r2 = []
        a2_r2.append(self.set.raw_pressure['aliq2']['run2'])
        a2_r2.append(self.set.raw_uptake['aliq2']['run2'])

        color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(a1_r1[0], a1_r1[1], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq1-run1')
        plt.plot(a1_r2[0], a1_r2[1], 'bs', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq1-run2')

        color2 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(a2_r1[0], a2_r1[1], 'o', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq2-run1')
        plt.plot(a2_r2[0], a2_r2[1], 'bs', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq2-run2')
        
        plt.axis([0, 1.2*max(a1_r1[0]+a1_r2[0]+a2_r1[0]+a2_r2[0]), 0, 1.2*max(a1_r1[1]+a1_r2[1]+a2_r1[1]+a2_r2[1])])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.legend(legend, loc = 2, fontsize = 10)

        self.set_path = 'plots/set-{0}.png'.format(str(self.set.id))
        plt.savefig(self.set_path, dpi=400)
        plt.close()

class Build:

    def __init__(self, ref=None):
        if ref:
            self.ref = ref
            self.sets = []
            for _set_id in self.ref.sets['sets']:
                _set = SetModel.objects.with_id(_set_id['id'])
                if _set:
                    self.sets.append(_set.info())
            self.average  = {'pressure':[], 'uptake':[]}
            self.err_low = []
            self.err_up = []
            self.sizes = []

    def intervalls(self):
        pressure = {'min':self.sets[0]['raw-pressure']['aliq1']['run1'][0], 'max':self.sets[0]['raw-pressure']['aliq1']['run1'][-1]}

        uptake = {'min':self.sets[0]['raw-uptake']['aliq1']['run1'][0], 'max':self.sets[0]['raw-uptake']['aliq1']['run1'][-1]}

        for _set in self.sets:
            print str(_set)
            for a1_r1 in _set['raw-pressure']['aliq1']['run1']:
                if pressure['min'] >= a1_r1:
                    pressure['min'] = a1_r1
            for a1_r2 in _set['raw-pressure']['aliq1']['run2']:
                if pressure['min'] >= a1_r2:
                    pressure['min'] = a1_r2

            for a2_r1 in _set['raw-pressure']['aliq2']['run1']:
                if pressure['min'] >= a2_r1:
                    pressure['min'] = a2_r1
            for a2_r2 in _set['raw-pressure']['aliq2']['run2']:
                if pressure['min'] >= a2_r2:
                    pressure['min'] = a2_r2


            for a1_r1 in _set['raw-pressure']['aliq1']['run1']:
                if pressure['max'] <= a1_r1:
                    pressure['max'] = a1_r1
            for a1_r2 in _set['raw-pressure']['aliq1']['run2']:
                if pressure['max'] <= a1_r2:
                    pressure['max'] = a1_r2

            for a2_r1 in _set['raw-pressure']['aliq2']['run1']:
                if pressure['max'] <= a2_r1:
                    pressure['max'] = a2_r1
            for a2_r2 in _set['raw-pressure']['aliq2']['run2']:
                if pressure['max'] <= a2_r2:
                    pressure['max'] = a2_r2

            ####
            for a1_r1 in _set['raw-uptake']['aliq1']['run1']:
                if uptake['min'] >= a1_r1:
                    uptake['min'] = a1_r1
            for a1_r2 in _set['raw-uptake']['aliq1']['run2']:
                if uptake['min'] >= a1_r2:
                    uptake['min'] = a1_r2

            for a2_r1 in _set['raw-uptake']['aliq2']['run1']:
                if uptake['min'] >= a2_r1:
                    uptake['min'] = a2_r1
            for a2_r2 in _set['raw-uptake']['aliq2']['run2']:
                if uptake['min'] >= a2_r2:
                    uptake['min'] = a2_r2


            for a1_r1 in _set['raw-uptake']['aliq1']['run1']:
                if uptake['max'] <= a1_r1:
                    uptake['max'] = a1_r1
            for a1_r2 in _set['raw-uptake']['aliq1']['run2']:
                if uptake['max'] <= a1_r2:
                    uptake['max'] = a1_r2

            for a2_r1 in _set['raw-uptake']['aliq2']['run1']:
                if uptake['max'] <= a2_r1:
                    uptake['max'] = a2_r1
            for a2_r2 in _set['raw-uptake']['aliq2']['run2']:
                if uptake['max'] <= a2_r2:
                    uptake['max'] = a2_r2

        return [pressure, uptake]



    def compute(self):
        sizes = self.intervalls()
        fine_grid = np.linspace(0, sizes[0]['max'], num=int(sizes[0]['max']/0.1), endpoint=True)

        #grid_p_a1, grid_u_a1 = np.mgrid[0:sizes[0]['max']:int(sizes[0]['max']/0.1), 0:sizes[1]['max']:int(sizes[1]['max']/0.1)]
        # grid_p_a2, grid_u_a2 = np.mgrid[0:sizes[2]['max']:int(sizes[2]['max']/0.1), 0:sizes[3]['max']:int(sizes[3]['max']/0.1)]

        # av = np.zeros(len(fine_grid))
        U = []
        for _set in self.sets:
            # average pressures
            print "Adding set: {0}".format(_set['filename'])
            _set['ref-pressure'] = {'aliq1':{'run1':fine_grid, 'run2':fine_grid}, 'aliq2':{'run1':fine_grid, 'run2':fine_grid}}
            _set['ref-uptake'] = {'aliq1':{'run1':[], 'run2':[]}, 'aliq2':{'run1':[], 'run2':[]}}
            
            if len(_set['raw-pressure']['aliq1']['run1']) >0:
                _set['ref-uptake']['aliq1']['run1'] = np.interp(_set['ref-pressure']['aliq1']['run1'], _set['raw-pressure']['aliq1']['run1'], _set['raw-uptake']['aliq1']['run1'], left=np.nan, right=np.nan, period=None)
                # av_a1 = av_a1 + _set['ref-uptake']['aliq1']['run1']
                U.append(_set['ref-uptake']['aliq1']['run1'])
            if len(_set['raw-pressure']['aliq1']['run2']) >0:
                _set['ref-uptake']['aliq1']['run2'] = np.interp(_set['ref-pressure']['aliq1']['run2'], _set['raw-pressure']['aliq1']['run2'], _set['raw-uptake']['aliq1']['run2'], left=np.nan, right=np.nan, period=None)
                # av_a1 = av_a1 + _set['ref-uptake']['aliq1']['run2']
                U.append(_set['ref-uptake']['aliq1']['run2'])

            if len(_set['raw-pressure']['aliq2']['run1']) >0:
                _set['ref-uptake']['aliq2']['run1'] = np.interp(_set['ref-pressure']['aliq2']['run1'], _set['raw-pressure']['aliq2']['run1'], _set['raw-uptake']['aliq2']['run1'], left=np.nan, right=np.nan, period=None)
                # av_a2 = av_a2 + _set['ref-uptake']['aliq2']['run1']
                U.append(_set['ref-uptake']['aliq2']['run1'])
            if len(_set['raw-pressure']['aliq2']['run2']) >0:
                _set['ref-uptake']['aliq2']['run2'] = np.interp(_set['ref-pressure']['aliq2']['run2'], _set['raw-pressure']['aliq2']['run2'], _set['raw-uptake']['aliq2']['run2'], left=np.nan, right=np.nan, period=None)
                # av_a2 = av_a2 + _set['ref-uptake']['aliq2']['run2']
                U.append(_set['ref-uptake']['aliq2']['run2'])


        # av_a1 = av_a1 / 2*len(self.sets)
        # av_a2 = av_a2 / 2*len(self.sets)

        # av = np.average(U, axis=0)

        mn = np.nanmean(U, axis=0)

        md = np.nanmedian(U, axis=0)

        sd = np.nanstd(U, axis=0)

        self.a_max = np.amax(U, axis=0)


        self.ref.sd_uptake = sd.tolist()
        # self.ref.av_uptake = av.tolist()
        self.ref.mn_uptake = mn.tolist()
        self.ref.md_uptake = md.tolist()
        self.ref.fit_pressure = fine_grid.tolist()
        self.ref.sizes = {'pressure':sizes[0], 'uptake':sizes[1]}
        # Polynomial with 30 components is enough to fit the curb.
        z = np.polyfit(fine_grid, mn, 30)
        self.ref.formula = z.tolist()
        self.ref.save()

    def plot_raw(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []
        for _set in self.sets:
            runA11 = []
            runA11.append(_set['raw-pressure']['aliq1']['run1'])
            runA11.append(_set['raw-uptake']['aliq1']['run1'])
            runA12 = []
            runA12.append(_set['raw-pressure']['aliq1']['run2'])
            runA12.append(_set['raw-uptake']['aliq1']['run2'])
            runA21 = []
            runA21.append(_set['raw-pressure']['aliq2']['run1'])
            runA21.append(_set['raw-uptake']['aliq2']['run1'])
            runA22 = []
            runA22.append(_set['raw-pressure']['aliq2']['run2'])
            runA22.append(_set['raw-uptake']['aliq2']['run2'])

            color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            plt.plot(runA11[0], runA11[1], '^', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run1]'.format(_set['filename']))

            plt.plot(runA12[0], runA12[1], 'v', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run2]'.format(_set['filename']))

            plt.plot(runA21[0], runA21[1], '<', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run1]'.format(_set['filename']))

            plt.plot(runA22[0], runA22[1], '>', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run2]'.format(_set['filename']))
        
        plt.axis([0, 1.1*self.ref.sizes['pressure']['max'], 0, 1.1*self.ref.sizes['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        # plt.legend(legend, loc = 2, fontsize = 10)

        self.ref_path = 'plots/ref-{0}.png'.format(str(self.ref.id))
        plt.savefig(self.ref_path, dpi=400)
        plt.close()

    def plot_all(self):
        self.plot_raw()
        
    def plot_stats(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []

        color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure, self.ref.sd_uptake, 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('standard-deviation')

        # color2 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        # plt.plot(self.ref.fit_pressure, self.ref.av_uptake, 'o', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        # legend.append('average')

        color3 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure, self.ref.mn_uptake, 'o', ms = float(5.0), color = color3, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('mean')

        color4 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure, self.ref.md_uptake, 'o', ms = float(5.0), color = color4, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('median')
        
        plt.axis([0, 1.1*self.ref.sizes['pressure']['max'], 0, 1.1*self.ref.sizes['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.legend(legend, loc = 2, fontsize = 10)

        self.ref_path = 'plots/stats-ref-{0}.png'.format(str(self.ref.id))
        plt.savefig(self.ref_path, dpi=400)
        plt.close()

    def plot_stat(self):
        self.plot_stats()

    def plot_error_bar(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []
        for _set in self.sets:
            runA11 = []
            runA11.append(_set['raw-pressure']['aliq1']['run1'])
            runA11.append(_set['raw-uptake']['aliq1']['run1'])
            runA12 = []
            runA12.append(_set['raw-pressure']['aliq1']['run2'])
            runA12.append(_set['raw-uptake']['aliq1']['run2'])
            runA21 = []
            runA21.append(_set['raw-pressure']['aliq2']['run1'])
            runA21.append(_set['raw-uptake']['aliq2']['run1'])
            runA22 = []
            runA22.append(_set['raw-pressure']['aliq2']['run2'])
            runA22.append(_set['raw-uptake']['aliq2']['run2'])

            color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            # plt.plot(runA11[0], runA11[1], '^', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run1]'.format(_set['filename']))

            # plt.plot(runA12[0], runA12[1], 'v', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run2]'.format(_set['filename']))

            # plt.plot(runA21[0], runA21[1], '<', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run1]'.format(_set['filename']))

            # plt.plot(runA22[0], runA22[1], '>', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        
        # color = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        # plt.plot(self.ref.fit_pressure, self.ref.mn_uptake, '^', ms = float(5.0), color = "red", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.errorbar(self.ref.fit_pressure, self.ref.mn_uptake, yerr=self.ref.sd_uptake, fmt='o', ms = float(5.0), color = "red", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        # plt.fill_between(np.array(self.ref.fit_pressure), np.array(self.ref.mn_uptake)+std_coef*np.array(self.ref.sd_uptake), np.array(self.ref.mn_uptake)-std_coef*np.array(self.ref.sd_uptake), facecolor="red", alpha=0.5)

        p = np.poly1d(self.ref.formula)
        plt.plot(self.ref.fit_pressure, p(self.ref.fit_pressure), ms = float(5.0), color = "blue", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        
        plt.axis([0, 1.1*self.ref.sizes['pressure']['max'], 0, 1.1*self.ref.sizes['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        # plt.legend(legend, loc = 2, fontsize = 10)

        self.ref_path = 'plots/error-{0}.png'.format(str(self.ref.id))
        plt.savefig(self.ref_path, dpi=400)
        plt.close()

    def plot_bars(self):
        self.plot_error_bar()


class Evaluation:
    def __init__(self, eval_id=None, reference=None, pressure=None, uptake=None):
        self.ref = reference
        self.eval_id = eval_id
        self.pressure = pressure
        self.uptake = uptake
        self.results = {}
        self.agrees = []
        self.sets = []
        for set_ in self.ref.sets['sets']:
            _set = SetModel.objects.with_id(set_['id'])
            if _set:
                self.sets.append(_set.info())

    def intervalls(self):
        pressure = {'min':self.sets[0]['raw-pressure']['aliq1']['run1'][0], 'max':self.sets[0]['raw-pressure']['aliq1']['run1'][-1]}

        uptake = {'min':self.sets[0]['raw-uptake']['aliq1']['run1'][0], 'max':self.sets[0]['raw-uptake']['aliq1']['run1'][-1]}

        for _set in self.sets:
            for a1_r1 in _set['raw-pressure']['aliq1']['run1']:
                if pressure['min'] >= a1_r1:
                    pressure['min'] = a1_r1
            for a1_r2 in _set['raw-pressure']['aliq1']['run2']:
                if pressure['min'] >= a1_r2:
                    pressure['min'] = a1_r2

            for a2_r1 in _set['raw-pressure']['aliq2']['run1']:
                if pressure['min'] >= a2_r1:
                    pressure['min'] = a2_r1
            for a2_r2 in _set['raw-pressure']['aliq2']['run2']:
                if pressure['min'] >= a2_r2:
                    pressure['min'] = a2_r2


            for a1_r1 in _set['raw-pressure']['aliq1']['run1']:
                if pressure['max'] <= a1_r1:
                    pressure['max'] = a1_r1
            for a1_r2 in _set['raw-pressure']['aliq1']['run2']:
                if pressure['max'] <= a1_r2:
                    pressure['max'] = a1_r2

            for a2_r1 in _set['raw-pressure']['aliq2']['run1']:
                if pressure['max'] <= a2_r1:
                    pressure['max'] = a2_r1
            for a2_r2 in _set['raw-pressure']['aliq2']['run2']:
                if pressure['max'] <= a2_r2:
                    pressure['max'] = a2_r2

            ####
            for a1_r1 in _set['raw-uptake']['aliq1']['run1']:
                if uptake['min'] >= a1_r1:
                    uptake['min'] = a1_r1
            for a1_r2 in _set['raw-uptake']['aliq1']['run2']:
                if uptake['min'] >= a1_r2:
                    uptake['min'] = a1_r2

            for a2_r1 in _set['raw-uptake']['aliq2']['run1']:
                if uptake['min'] >= a2_r1:
                    uptake['min'] = a2_r1
            for a2_r2 in _set['raw-uptake']['aliq2']['run2']:
                if uptake['min'] >= a2_r2:
                    uptake['min'] = a2_r2


            for a1_r1 in _set['raw-uptake']['aliq1']['run1']:
                if uptake['max'] <= a1_r1:
                    uptake['max'] = a1_r1
            for a1_r2 in _set['raw-uptake']['aliq1']['run2']:
                if uptake['max'] <= a1_r2:
                    uptake['max'] = a1_r2

            for a2_r1 in _set['raw-uptake']['aliq2']['run1']:
                if uptake['max'] <= a2_r1:
                    uptake['max'] = a2_r1
            for a2_r2 in _set['raw-uptake']['aliq2']['run2']:
                if uptake['max'] <= a2_r2:
                    uptake['max'] = a2_r2

        for a1_r1 in self.pressure['aliq1']['run1']:
            if pressure['min'] >= a1_r1:
                pressure['min'] = a1_r1
        for a1_r2 in self.pressure['aliq1']['run2']:
            if pressure['min'] >= a1_r2:
                pressure['min'] = a1_r2

        for a2_r1 in self.pressure['aliq2']['run1']:
            if pressure['min'] >= a2_r1:
                pressure['min'] = a2_r1
        for a2_r2 in self.pressure['aliq2']['run2']:
            if pressure['min'] >= a2_r2:
                pressure['min'] = a2_r2


        for a1_r1 in self.pressure['aliq1']['run1']:
            if pressure['max'] <= a1_r1:
                pressure['max'] = a1_r1
        for a1_r2 in self.pressure['aliq1']['run2']:
            if pressure['max'] <= a1_r2:
                pressure['max'] = a1_r2

        for a2_r1 in self.pressure['aliq2']['run1']:
            if pressure['max'] <= a2_r1:
                pressure['max'] = a2_r1
        for a2_r2 in self.pressure['aliq2']['run2']:
            if pressure['max'] <= a2_r2:
                pressure['max'] = a2_r2

        ####
        for a1_r1 in self.uptake['aliq1']['run1']:
            if uptake['min'] >= a1_r1:
                uptake['min'] = a1_r1
        for a1_r2 in self.uptake['aliq1']['run2']:
            if uptake['min'] >= a1_r2:
                uptake['min'] = a1_r2

        for a2_r1 in self.uptake['aliq2']['run1']:
            if uptake['min'] >= a2_r1:
                uptake['min'] = a2_r1
        for a2_r2 in self.uptake['aliq2']['run2']:
            if uptake['min'] >= a2_r2:
                uptake['min'] = a2_r2


        for a1_r1 in self.uptake['aliq1']['run1']:
            if uptake['max'] <= a1_r1:
                uptake['max'] = a1_r1
        for a1_r2 in self.uptake['aliq1']['run2']:
            if uptake['max'] <= a1_r2:
                uptake['max'] = a1_r2

        for a2_r1 in self.uptake['aliq2']['run1']:
            if uptake['max'] <= a2_r1:
                uptake['max'] = a2_r1
        for a2_r2 in self.uptake['aliq2']['run2']:
            if uptake['max'] <= a2_r2:
                uptake['max'] = a2_r2

        return [pressure, uptake]

    def run(self):
        U = []
        sizes = self.intervalls()
        # fine_grid = np.linspace(0, sizes[0]['max'], num=int(sizes[0]['max']/0.1), endpoint=True)
        fine_grid = self.ref.fit_pressure

        # g1_U = []
        # g2_U = []

        # Should i compare the runs with the mean by meaning them together?
        # Or mean the runs first and mean their mean with the reference mean.

        # average pressures
        # a1_U.append(self.ref.mn_uptake['aliq1'])
        if len(self.pressure['aliq1']['run1']) >0:
            ref1_a1 = np.interp(fine_grid, self.pressure['aliq1']['run1'], self.uptake['aliq1']['run1'], left=np.nan, right=np.nan, period=None)
            U.append(ref1_a1)
        if len(self.pressure['aliq1']['run2']) >0:
            ref2_a1 = np.interp(fine_grid, self.pressure['aliq1']['run2'], self.uptake['aliq1']['run2'], left=np.nan, right=np.nan, period=None)
            U.append(ref2_a1)

        # a2_U.append(self.ref.mn_uptake['aliq2'])
        if len(self.pressure['aliq2']['run1']) >0:
            ref1_a2 = np.interp(fine_grid, self.pressure['aliq2']['run1'], self.uptake['aliq2']['run1'], left=np.nan, right=np.nan, period=None)
            U.append(ref1_a2)
        if len(self.pressure['aliq2']['run2']) >0:
            ref2_a2 = np.interp(fine_grid, self.pressure['aliq2']['run2'], self.uptake['aliq2']['run2'], left=np.nan, right=np.nan, period=None)
            U.append(ref2_a2)

        for _set in self.sets:
            info = _set
            if len(info['raw-pressure']['aliq1']['run1']) >0:
                ref1_a1 = np.interp(fine_grid, info['raw-pressure']['aliq1']['run1'], info['raw-uptake']['aliq1']['run1'], left=np.nan, right=np.nan, period=None)
                U.append(ref1_a1)
            if len(info['raw-pressure']['aliq1']['run2']) >0:
                ref1_a2 = np.interp(fine_grid, info['raw-pressure']['aliq1']['run2'], info['raw-uptake']['aliq1']['run2'], left=np.nan, right=np.nan, period=None)
                U.append(ref1_a2)

            if len(info['raw-pressure']['aliq2']['run1']) >0:
                ref2_a1 = np.interp(fine_grid, info['raw-pressure']['aliq2']['run1'], info['raw-uptake']['aliq2']['run1'], left=np.nan, right=np.nan, period=None)
                U.append(ref2_a1)
            if len(info['raw-pressure']['aliq2']['run2']) >0:
                ref2_a2 = np.interp(fine_grid, info['raw-pressure']['aliq2']['run2'], info['raw-uptake']['aliq2']['run2'], left=np.nan, right=np.nan, period=None)
                U.append(ref2_a2)


        # av = np.average(U, axis=0)

        mn = np.nanmean(U, axis=0)

        md = np.nanmedian(U, axis=0)

        sd = np.nanstd(U, axis=0)

        self.a_max = np.amax(U, axis=0)

        self.results['std'] = sd.tolist()
        # self.results['av'] = av.tolist()
        self.results['mn'] = mn.tolist()
        self.results['md'] = md.tolist()
        self.results['fit-pressure'] = fine_grid

        # The reference data set dispersion is bigger than the dispersion of the evaluated data set with the mean reference.
        # How is > working for lists.
        self.agrees = [self.ref.sd_uptake > sd.tolist(), self.ref.sd_uptake > sd.tolist()]

        # macro_1 = mean_absolute_error(self.ref.mn_uptake, mn.tolist())

        # print "Macro Mean: {0}".format(str(macro_1))

    def plot_result(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []

        color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.results['fit-pressure'], self.results['std'], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('standard-deviation')

        # color2 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        # plt.plot(self.results['fit-pressure'], self.results['av'], 'o', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        # legend.append('average')

        color3 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.results['fit-pressure'], self.results['mn'], 'o', ms = float(5.0), color = color3, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('mean')

        color4 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.results['fit-pressure'], self.results['md'], 'o', ms = float(5.0), color = color4, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('median')
        
        plt.axis([0, 1.1*self.ref.sizes['pressure']['max'], 0, 1.1*self.ref.sizes['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.legend(legend, loc = 2, fontsize = 10)
        plt.draw()


    def plot(self):
        agree = "agreed"
        if not self.agrees[0]:
            agree = "disagreed"
        self.plot_result()
        ref_path = 'plots/tmp-eval-ref-{0}-{1}-{2}.png'.format(str(self.ref.id), self.eval_id.split('.')[0], agree)
        print ref_path
        plt.savefig(ref_path, dpi=400)
        plt.close()
        return ref_path

    def plot_error(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []

        plt.errorbar(self.ref.fit_pressure, self.ref.mn_uptake, yerr=self.results['std'], fmt='o', ms = float(5.0), color = "red", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        # plt.plot(self.ref.fit_pressure, self.ref.md_uptake, 'o', ms = float(5.0), color = "red", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        # plt.fill_between(self.ref.fit_pressure, np.array(self.ref.mn_uptake)+std_coef*np.array(self.ref.sd_uptake), np.array(self.ref.mn_uptake)-std_coef*np.array(self.ref.sd_uptake), facecolor="red", alpha=0.5)
        plt.plot(self.pressure['aliq1']['run1'], self.uptake['aliq1']['run1'], 'o', ms = float(5.0), color = "yellow", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.plot(self.pressure['aliq1']['run2'], self.uptake['aliq1']['run2'], 'o', ms = float(5.0), color = "yellow", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.plot(self.pressure['aliq2']['run1'], self.uptake['aliq2']['run1'], 'o', ms = float(5.0), color = "yellow", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.plot(self.pressure['aliq2']['run2'], self.uptake['aliq2']['run2'], 'o', ms = float(5.0), color = "yellow", mew = .25, ls = '-', lw = float(1.5), zorder = 3)

        # plt.fill_between(self.results['fit-pressure'], np.array(self.results['mn'])+np.array(self.results['std']), np.array(self.results['mn'])-np.array(self.results['std']), facecolor="blue", alpha=0.5)
        # plt.plot(self.results['fit-pressure'], self.results['mn'], 'o', ms = float(5.0), color = "blue", mew = .25, ls = '-', lw = float(1.5), zorder = 3)

        # p = np.poly1d(self.ref.formula)
        # plt.plot(self.ref.fit_pressure, p(self.ref.fit_pressure), ms = float(5.0), color = "blue", mew = .25, ls = '--', lw = float(1.5), zorder = 3)

        plt.axis([0, 1.1*self.ref.sizes['pressure']['max'], 0, 1.1*self.ref.sizes['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.draw()


    def error(self):
        agree = "agreed"
        if not self.agrees[0]:
            agree = "disagreed"
        self.plot_error()
        ref_path = 'plots/evaluate-ref-{0}-{1}-{2}.png'.format(str(self.ref.id), self.eval_id.split('.')[0], agree)
        print ref_path
        plt.savefig(ref_path, dpi=400)
        plt.close()
        return ref_path























