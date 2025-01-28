import numpy as np
np.seterr(all="ignore")
import matplotlib.pyplot as plt

lim = 1
narrow_psfs = np.load('data/narrow_psfs.npy')[:lim]
object = np.load('data/object.npy', allow_pickle=True).item()
data = object['data'][:lim]
noisemaps = object['noisemaps'][:lim]

brightnesses = len(data) * 1 * [15.]
# that is 10 images, each of them with 4 sources: 40 sources.

# a function that generates a model instance and initial guess parameters:
from starred.deconvolution.deconvolution import setup_model
# a parameters handler:
from starred.deconvolution.parameters import ParametersDeconv
# the loss function, basically chi² + regularization
from starred.deconvolution.loss import Loss
# the interface to the optimizer:
from starred.utils.optimization import Optimizer
# a way to propagate the noisemap through starlet layers:
from starred.utils.noise_utils import propagate_noise
# a plot utility to explore our deconvolution at every step
from starred.plots.plot_function import view_deconv_model
from copy import deepcopy

scale = np.nanmax(data[:,30:40, 27:37])
data /= scale
noisemaps /= scale

model, k_init, k_up, k_down, k_fixed = setup_model(data=data[:,30:40, 27:37],
                                                   sigma_2=noisemaps[:,30:40, 27:37]**2,
                                                   s=narrow_psfs,
                                                   xs=[0.],#xs,
                                                   ys=[0.],#ys,
                                                   initial_a=brightnesses,
                                                   subsampling_factor=2)
k_fixed['kwargs_background']['h'] = k_init['kwargs_background']['h']
k_fixed = deepcopy(k_init)
for k, v in k_fixed.items():
    for kk, vv in v.items():
        v[kk] = np.array(vv)
del k_fixed['kwargs_analytic']['a']
del k_fixed['kwargs_analytic']['dx']
del k_fixed['kwargs_analytic']['dy']
del k_fixed['kwargs_background']['mean']


# the params needs the initial guess, fixed params and boundaries:
params = ParametersDeconv(k_init, k_fixed, k_up, k_down)
# the loss needs to see our data, noisemaps, model, and the params class:
loss = Loss(data[:,30:40, 27:37], model, params, noisemaps[:,30:40, 27:37]**2)
# now we can make an optimizer!
optim = Optimizer(loss, params, method='Nelder-Mead')

# optimize (this returns some metrics, but we don't need them here.)
#optim.minimize(max_iterations=5000, init_learning_rate=1e-3)
optim.minimize(maxiter=40)
# the best fit is automatically given to the params:
k_optim = params.best_fit_values(as_kwargs=True)
print(params.kwargs2args(k_optim))
print(loss(params.kwargs2args(k_optim)))
print(len(optim.loss_history), loss(params.kwargs2args(k_optim)))
plt.figure()
plt.plot(optim.loss_history)
plt.show()

