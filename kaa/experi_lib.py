import numpy as np

from kaa.trajectory import Traj, TrajCollection
from kaa.log import Output
from kaa.experiment import Experiment

"""
Experiment to compute the reachable set and estimate the total volume of all of its overapproximations.
"""
class VolumeExperiment(Experiment):

    def __init__(self, *inputs, label="Experiment"):
        super().__init__(*inputs, label=label)

    def execute(self, num_trials):
        num_steps = self.max_num_steps
        num_trajs = self.max_num_trajs

        spreadsheet = self.generate_sheet(num_trials)

        for experi_input in self.inputs:
            loaded_dirs = self.initialize_strat(experi_input, num_trials)

            experi_strat = experi_input['strat']
            experi_supp_mode = experi_input['supp_mode']
            experi_pregen_mode = experi_input['pregen_mode']
            experi_num_trajs = experi_input['num_trajs']

            for trial_num in range(num_trials):
                Output.prominent(f"Running Experiment {experi_input['label']} Trial:{trial_num}")
                Output.prominent(f"Using following parameters for experiments:")
                Output.prominent(f"Use Support Points: {experi_supp_mode}")
                Output.prominent(f"Use Pre-gen Points: {experi_pregen_mode}")

                if experi_pregen_mode:
                    Output.prominent(f"Number of Trajectories Used: {experi_num_trajs}")

                flowpipe = self.gather_vol_data(experi_input)
                flow_label, flow_vol = flowpipe.label, flowpipe.total_volume

                if flowpipe.error:
                    flow_vol = f"{flow_vol} (VOLUME TOO BLOATED) Stopped at {flowpipe.error.total_steps}"

                self.save_data_into_sheet(spreadsheet, trial_num, num_trials, flow_label, flow_vol)
                self.assign_dirs(experi_strat, trial_num, loaded_dirs)

                experi_strat.reset() #Reset attributes for next independent trial.

"""
Experiment to measure deviations between generated directions for a strategy type over the course of the reachable set computation.
"""
class DeviationExperiment(Experiment):

    def __init__(self, *inputs, experi_type, label="Experiment"):
        super().__init__(*inputs, label=label)
        self.experi_type = experi_type

    def execute(self, num_trials):
        idx = dict(PCADev=0,
                   LinDev=1)

        strat_dirs_by_input = []
        row_labels = []
        for experi_input in self.inputs:
            num_steps = experi_input['num_steps']
            num_trajs = experi_input['num_trajs']
            label = experi_input['label']

            for dir_tuple in loaded_dirs:
                strat_dirs = dir_tuple[idx[self.experi_type]] #experi_type determines index of tuple to fetch (first index for PCA, second for LinApp)
                strat_dirs_by_input.append(pca_dirs)
                row_labels.append(label)

        for trial_num in range(num_trials):
            for row_label, strat_dirs_prev, strat_dirs_curr in zip(row_labels, strat_dirs_by_traj, strat_dirs_by_traj[1:]):
                prev_dirs = strat_dirs_prev[trial_num] #Corresponding directions from previous input to compare against
                curr_dirs = strat_dirs_curr[trial_num] #Corresponding directions from current input to compare against

                dirs_dist = self.__calc_dirs_dist(prev_dirs, curr_dirs)
                self.save_data_into_sheet(spreadsheet, trial_num, num_trials, row_label, dirs_dist)

    def __calc_dirs_dist(self, gen_dirs_one, gen_dirs_two):
         norm_dir_one = (gen_dirs_one.dir_mat.T / np.linalg.norm(gen_dirs_one.dir_mat, axis=1)).T
         norm_dir_two = (gen_dirs_two.dir_mat.T / np.linalg.norm(gen_dirs_two.dir_mat, axis=1)).T
         abs_dot_prods = np.abs(np.einsum('ij,ij->i', norm_dir_one, norm_dir_two))
         return np.min(abs_dot_prods)

"""
Experiment to calculate and plot the phase plot.
"""
class PhasePlotExperiment(Experiment):

    def __init__(self, *inputs):
        super().__init__(*inputs)

    def execute(self, *var_tup, separate=False, plot_border_traj=True):

        if plot_border_traj:
            self.plot.add(self.simulate_border_points(10))

        for experi_input in self.inputs:
            self.initialize_strat(experi_input, 10)
            self.plot.add(self.calc_flowpipe(experi_input))

        self.plot.plot2DPhase(*var_tup, separate)

class CompAniExperiment(Experiment):

    def __init__(self, *inputs):
        super().__init__(*inputs)

    def execute(self, x , y, ptope_order, filename, plot_pts=None):
        if not plot_pts: plot_pts = [False for _ in enumerate(self.inputs)]

        flowpipes = []
        for experi_input in self.inputs:
            self.initialize_strat(experi_input, 10)
            flowpipes.append(self.calc_flowpipe(experi_input))

        animation = SlideCompareAnimation(*flowpipes)

        border_trajs = self.simulate_border_points(self.max_num_steps)
        animation.add(border_trajs)

        animation.animate(x, y, ptope_order, plot_pts, filename)