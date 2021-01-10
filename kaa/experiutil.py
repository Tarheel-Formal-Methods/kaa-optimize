import math
import random as rand
import sympy as sp
import numpy as np
from itertools import product, chain
import multiprocessing as mp

from kaa.temp.pca_strat import *
from kaa.temp.lin_app_strat import *
from kaa.templates import MultiStrategy
from kaa.experiment import Experiment, ExperimentBatch, exec_plot_vol_results
from kaa.settings import KaaSettings

"""
Generate random trajectories from initial set (initial bundle) of model.
@params model: Model
        num: number of trajectories to generate.
        time_steps: number of time steps to generate trajs.
@returns list of Traj objects representing num random trajectories.
"""
def generate_init_traj(model, num, time_steps):
    bund = model.bund
    return bund.generate_traj(num, time_steps)

"""
Generates random points through the generators of the initial box and checking membership. Could be extremely time-consuming if the intersection is thin.
@params bund: Bundle object
        num_trajs: number of trajs to generate
@returns points generated.
"""
def gen_ran_pts_ptope(bund, num_trajs):
    bund_sys = bund.getIntersect()
    points_generated = 0
    gen_pts = []

    ptope = bund.ptopes[0] #Initial Box from Bund.
    gen_expr = ptope.getGeneratorRep()

    while points_generated < num_trajs:
        interval_ran_pts = [(var, rand.uniform(0,1)) for var in bund.vars]
        ran_pt = [expr.subs(interval_ran_pts, simultaneous=True) for expr in gen_expr]

        if bund_sys.check_membership(ran_pt):
            gen_pts.append(ran_pt)
            points_generated += 1

    return gen_pts

"""
Calculates naive supremum bound on the difference between two Flowpipe objects
@params flowpipe1: first Flowpipe object
        flowpipe2: second Flowpipe object
        var_ind: index of variable.
@returns maximum difference calculated along desired projection.
"""
def sup_error_bounds(flowpipe1, flowpipe2, var_ind):
    y1_max, y1_min = flowpipe1.get2DProj(var_ind)
    y2_max, y2_min = flowpipe2.get2DProj(var_ind)

    max_diff = np.absolute(np.subtract(y1_max, y2_max))
    min_diff = np.absolute(np.subtract(y1_min, y2_min))

    return np.amax(np.append(max_diff, min_diff))



def test_strat_comb(model, step_tup, num_steps, num_trials=1, filename="STRATCOMB"):
    NUM_STEPS = num_steps
    PCA_NUM_TRAJ = 300 #Number of sample trajectories we should use for the PCA routine.
    LIN_ITER_STEPS = 1 #Number of steps between each recomputation of LinApp Templates.
    PCA_ITER_STEPS = 1 #Number of steps between each recomputation of PCA Templates.

    MAX_STEP = max(step_tup)

    pca_dirs = GeneratedPCADirs(model, PCA_NUM_TRAJ, NUM_STEPS+MAX_STEP) #Way to deduce lengeth beforehand
    lin_dirs = GeneratedLinDirs(model, NUM_STEPS+MAX_STEP)
    pca_iter_steps = step_tup
    lin_iter_steps = step_tup

    inputs = []
    for pca_step, lin_step in product(pca_iter_steps, lin_iter_steps): #model tossed around too many times.
        pca_strat = PCAStrat(model, iter_steps=pca_step, traj_steps=pca_step, pca_dirs=pca_dirs)
        lin_strat = LinStrat(model, iter_steps=lin_step, lin_dirs=lin_dirs)
        experi_input = dict(model=model,
                            strat=MultiStrategy(pca_strat, lin_strat),
                            label=f"PCA Step {pca_step} and Lin Step {lin_step}",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input)

    experi = Experiment(*inputs, label="Combination with PCA and Lin Strats", num_trials=num_trials)
    experi.execute()
    experi.generate_spreadsheet()

def test_one_one_strat_pca(model, max_step, num_steps, filename="ONEONEPCA"):
    NUM_STEPS = num_steps
    PCA_NUM_TRAJ = 300 #Number of sample trajectories we should use for the PCA routine.
    LIN_ITER_STEPS = 1 #Number of steps between each recomputation of LinApp Templates.
    PCA_ITER_STEPS = 1 #Number of steps between each recomputation of PCA Templates.
    MAX_STEP = max_step

    pca_dirs = GeneratedPCADirs(model, PCA_NUM_TRAJ, NUM_STEPS+MAX_STEP) #Way to deduce lengeth beforehand
    lin_dirs = GeneratedLinDirs(model, NUM_STEPS+MAX_STEP)

    inputs = []
    for pca_step in range(2,6): #model tossed around too many times.
        pca_strat1 = PCAStrat(model, iter_steps=1, pca_dirs=pca_dirs)
        lin_strat1 = LinStrat(model, iter_steps=1, lin_dirs=lin_dirs)
        experi_strat1 = PCAStrat(model, iter_steps=pca_step, traj_steps=pca_step, pca_dirs=pca_dirs)
        experi_input1 = dict(model=model,
                            strat=MultiStrategy(pca_strat1, lin_strat1, experi_strat1),
                            label=f"PCA with Box and 1-1 Temp for {pca_step} steps",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input1)

    exec_plot_vol_results(Experiment(*inputs), filename)

def test_one_one_strat_lin(model, max_step, num_steps, filename="ONEONELIN"):
    NUM_STEPS = num_steps
    PCA_NUM_TRAJ = 300 #Number of sample trajectories we should use for the PCA routine.
    LIN_ITER_STEPS = 1 #Number of steps between each recomputation of LinApp Templates.
    PCA_ITER_STEPS = 1 #Number of steps between each recomputation of PCA Templates.
    MAX_STEP = max_step

    pca_dirs = GeneratedPCADirs(model, PCA_NUM_TRAJ, NUM_STEPS+MAX_STEP) #Way to deduce lengeth beforehand
    lin_dirs = GeneratedLinDirs(model, NUM_STEPS+MAX_STEP)

    inputs = []
    for lin_step in range(2,max_step+1): #model tossed around too many times.
        pca_strat1 = PCAStrat(model, iter_steps=1, pca_dirs=pca_dirs)
        lin_strat1 = LinStrat(model, iter_steps=1, lin_dirs=lin_dirs)
        experi_strat1 = LinStrat(model, iter_steps=lin_step, lin_dirs=lin_dirs)
        experi_input1 = dict(model=model,
                            strat=MultiStrategy(pca_strat1, lin_strat1, experi_strat1),
                            label=f"PCA with Box and 1-1 Temp for {lin_step} steps",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input1)

    exec_plot_vol_results(Experiment(*inputs), filename)

def test_pca_life(model, max_life, num_steps, life_incre=5, filename="SLIDINGPCA"):
    NUM_STEPS = num_steps
    VDP_PCA_NUM_TRAJ = 300 #Number of sample trajectories we should use for the PCA routine.
    LIFE_MAX = max_life
    LIFE_INCREMENT = life_incre

    pca_dirs = GeneratedPCADirs(model, VDP_PCA_NUM_TRAJ, NUM_STEPS+1) #Way to deduce lengeth beforehand
    inputs = []

    for lifespan in range(LIFE_MAX, 0, -LIFE_INCREMENT): #model tossed around too many times.
        experi_strat = SlidingPCAStrat(model, lifespan=lifespan)
        experi_input = dict(model=model,
                            strat=experi_strat,
                            label=f"SlidingPCA with Window Size:{lifespan}",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input)

    for lifespan in range(LIFE_INCREMENT-1, 0, -1): #model tossed around too many times.
        experi_strat = SlidingPCAStrat(model, lifespan=lifespan)
        experi_input = dict(model=model,
                            strat=experi_strat,
                            label=f"SlidingPCA with Window Size:{lifespan}",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input)

    exec_plot_vol_results(Experiment(*inputs), filename)

def test_lin_life(model, max_life, num_steps, life_incre=5, filename="SLIDINGLIN"):
    NUM_STEPS = num_steps
    VDP_PCA_NUM_TRAJ = 300 #Number of sample trajectories we should use for the PCA routine.
    LIFE_MAX = max_life
    LIFE_INCREMENT = life_incre

    lin_dirs = GeneratedLinDirs(model, NUM_STEPS+1) #Way to deduce lengeth beforehand
    inputs = []

    for lifespan in range(LIFE_MAX, 0, -LIFE_INCREMENT): #model tossed around too many times.
        experi_strat = SlidingLinStrat(model, lifespan=lifespan, lin_dirs=lin_dirs)
        experi_input = dict(model=model,
                            strat=experi_strat,
                            label=f"SlidingLin with Window Size:{lifespan}",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input)

    for lifespan in range(LIFE_INCREMENT-1, 0, -1): #model tossed around too many times.
        experi_strat = SlidingLinStrat(model, lifespan=lifespan, lin_dirs=lin_dirs)
        experi_input = dict(model=model,
                            strat=experi_strat,
                            label=f"SlidingLin with Window Size:{lifespan}",
                            num_steps=NUM_STEPS)
        inputs.append(experi_input)

    exec_plot_vol_results(Experiment(*inputs), filename)


def test_comb_stdev_reduction(model, num_steps, num_trials=10, filename="STRATCOMBSTDEV"):
    NUM_STEPS = num_steps
    MAX_STEP = 1

    PCA_ITER_STEPS = 1
    LIN_ITER_STEPS = 1

    inputs = []
    for num_trajs in range(400,1000,100): #model tossed around too many times.
        pca_dirs = GeneratedPCADirs(model, NUM_STEPS+MAX_STEP, num_trajs) #Way to deduce lengeth beforehand
        lin_dirs = GeneratedLinDirs(model, NUM_STEPS+MAX_STEP, num_trajs)

        pca_strat = PCAStrat(model, iter_steps=PCA_ITER_STEPS, pca_dirs=pca_dirs)
        lin_strat = LinStrat(model, iter_steps=LIN_ITER_STEPS, lin_dirs=lin_dirs)
        experi_input = dict(model=model,
                            strat=MultiStrategy(pca_strat, lin_strat),
                            label=f"PCA Step 1 and Lin Step 1 with NUM_TRAJ:{num_trajs}",
                            num_steps=NUM_STEPS)
        
        inputs.append(experi_input)

    experi = Experiment(*inputs, label="Combination with PCA and Lin Strats", num_trials=num_trials)
    experi.execute()
    experi.generate_spreadsheet()
