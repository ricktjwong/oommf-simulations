import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 16
plt.rcParams['lines.linewidth'] = 2
plt.rcParams.update({'figure.autolayout': True})
plt.rcParams['mathtext.default'] = 'regular'


def get_meta_data(file_path: str):
    headers = {}
    with open(file_path) as f:
        for line in f:
            if line[0] != '#': break
            if ':' in line:
                key_value = line.split('# ')[1].split(':')
                key, value = key_value[0], key_value[1].split('\n')[0].strip()
                headers[key] = value
    return int(headers['xnodes']), int(headers['ynodes']), int(headers['znodes']), \
           float(headers['xstepsize']), float(headers['ystepsize']), float(headers['zstepsize'])


def plot_strayfield(file_path: str, mag_dir: str, yslice: [int]):
    x, y, z, _, _, _ = get_meta_data(file_path)
    print(x, y, z)
    zslice = int(z / 2)
    data = np.array(np.loadtxt(file_path))
    data_field = data.reshape(x, y, z, 3, order="F")
    u, v, w = data_field[:,:,:,0], data_field[:,:,:,1], data_field[:,:,:,2]
    if (mag_dir == 'x'):
        mag = u
    elif (mag_dir == 'y'):
        mag = v
    elif (mag_dir == 'z'):
        mag = w
    elif (mag_dir == 'total'):
        mag = (u * u + v * v + w * w) ** 0.5
    # plt.figure()
    for i in yslice:
        mag_slice = mag[:, i, zslice]
        # plt.plot([i * 5 for i in range(x)], mag_slice, label=mag_dir)
        plt.plot([i * 5 for i in range(x)], mag_slice, label=str(i * 5) + 'nm')
    print(max(mag[int(x/3):int(x/3)*2, int(y/2), int(z/2)]))
    print(max(mag_slice))
    # plt.legend()
    # plt.savefig(file_path.split('/')[-1].split('.')[0] + '.pdf', dpi=1000)
    # plt.show()


def plot_strayfield_compare(file_path: str, mag_dir: str, t: int):
    x, y, z, _, _, _ = get_meta_data(file_path)
    zslice = int(z / 2)
    data = np.array(np.loadtxt(file_path))
    data_field = data.reshape(x, y, z, 3, order="F")
    u, v, w = data_field[:,:,:,0], data_field[:,:,:,1], data_field[:,:,:,2]
    if (mag_dir == 'x'):
        mag = u
    elif (mag_dir == 'y'):
        mag = v
    elif (mag_dir == 'z'):
        mag = w
    elif (mag_dir == 'total'):
        mag = (u * u + v * v + w * w) ** 0.5
    yslice = 190
    mag_slice = mag[:, yslice, zslice]
    plt.plot([i * 5 for i in range(x)], mag_slice, label=str(t/100))
    plt.legend()


def compare_strayfields(base_path: str, thicknesses: [int], mag_dir: str):
    thicknesses = [10 * i for i in range(6, 13, 1)]
    for t in thicknesses:
        file_path = base_path + str(t) + ".ovf"
        plot_strayfield_compare(file_path=file_path, mag_dir=mag_dir, t=t)
    plt.savefig(file_path.split('/')[-1].split('.')[0] + '.pdf', dpi=1000)
    plt.show()


def plot_rashba(file_path: str, yslice: [int]):
    eff_m = 0.014
    x, y, z, _, _, _ = get_meta_data(file_path)
    print(x, y, z)
    zslice = int(z / 2)
    data = np.array(np.loadtxt(file_path))
    data_field = data.reshape(x, y, z, 3, order="F")
    u, v, w = data_field[:, :, :, 0], data_field[:, :, :, 1], data_field[:, :, :, 2]
    fig, ax1 = plt.subplots()
    ax1.set_ylabel("alpha (eVm)")
    # ax2 = ax1.twinx()
    # ax2.set_ylabel("Magnetic Field (T)")
    # ax1.set_ylim([1e-12, 5e-11])
    # ax2.set_ylim([0, 0.07])
    for i in yslice:
        Bx = u[:, i, zslice]
        By = v[:, i, zslice]
        B = (u*u + v*v + w*w) ** 0.5
        B = B[:, i, zslice]
        grad_B = np.gradient(B)
        grad_Bx = np.gradient(Bx)
        # assumes in nanometres
        dphi_dx = -(Bx * grad_B - B * grad_Bx)/(B*By*2*np.pi)
        # alt expression but uses sqrt, might have sign issues?
        dphi_dx2 = (Bx * grad_B - B * grad_Bx)/(2*np.pi*B*B*np.sqrt(1-Bx*Bx/(B*B)))
        # extra 2pi factor from X = 2(pi)x
        alpha = (3.818E-11/eff_m) * dphi_dx  # in eVm ## first factor hbar^2/2em, divide by e for eVs
        alpha2 = (3.818E-11/eff_m) * dphi_dx2
        ax1.plot([i * 5 for i in range(x)], alpha, label="alpha", color="blue")
        # ax1.plot([i * 5 for i in range(x)], alpha2, color="orange", linestyle = "--")
        # ax2.plot([i * 5 for i in range(x)], Bx,label= "$B_x$", color="brown")
        # ax2.plot([i * 5 for i in range(x)], By,label="$B_y$", color="green")
        # ax2.plot([i * 5 for i in range(x)], B,label="$|B|$",  color="red")
        # ax2.plot([i * 5 for i in range(x)], Bx/B,label="$Bx/|B|$",  color="red")
        plt.legend()
        plt.show()
    return alpha


def surface_alpha(file_path: str, yrange: tuple):
    eff_m = 0.014
    x, y, z, _, _, _ = get_meta_data(file_path)
    print(x, y, z)
    zslice = int(z / 2)
    data = np.array(np.loadtxt(file_path))
    data_field = data.reshape(x, y, z, 3, order="F")
    u, v, w = data_field[:, :, :, 0], data_field[:, :, :, 1], \
        data_field[:, :, :, 2]
    for i in range(yrange[0], yrange[1]):
        Bx = u[:, i, zslice]
        By = v[:, i, zslice]
        B = (u*u + v*v + w*w) ** 0.5
        B = B[:, i, zslice]
        grad_B = np.gradient(B)
        grad_Bx = np.gradient(Bx)
        dphi_dx = -(Bx * grad_B - B * grad_Bx)/(B*By*2*np.pi)
        alpha = (3.818E-11/eff_m) * dphi_dx
        # a hack to threshold values
        alpha = np.array([i if np.abs(i) < 1e-10
                         else (1e-10 if i > 0 else -1e-10) for i in alpha])
        alpha2D = alpha if i == yrange[0] else np.vstack((alpha2D, alpha))

    # fig, ax = plt.subplots()
    # im = ax.imshow(alpha2D, cmap='seismic', interpolation='nearest',vmin= -9e-11, vmax= 9e-11, origin='lower')
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes("right", size="5%", pad=0.05)
    # plt.colorbar(im, cax=cax)
    # plt.show()

    X, Y = np.meshgrid(np.arange(0, x, 1), np.arange(yrange[0], yrange[1], 1))
    fig2 = plt.figure()
    ax2 = Axes3D(fig2)
    surface = ax2.plot_surface(X, Y, alpha2D, rstride=1, cstride=1,
                               cmap='seismic', vmin=-1e-10, vmax=1e-10)
    fig2.colorbar(surface, shrink=0.8, pad=0.05)
    plt.show()


# plot_strayfield(file_path='./data/stray_field/halbach_switching/switch_study_perm_100_60/halbach_switch_perm.4.out/strayfield5.ovf', mag_dir='total', yslice = [145,155,165])
# plot_strayfield(file_path='./data/stray_field/halbach_switching/switch_study_perm_100_60/halbach_switch_perm.4.out/strayfield5.ovf', mag_dir='x', yslice = [145,155,165])
# plot_strayfield(file_path='./data/stray_field/halbach_switching/switch_study_perm_100_60/halbach_switch_perm.4.out/strayfield5.ovf', mag_dir='y', yslice = [145,155,165])
# plot_rashba(file_path='./data/stray_field/halbach_switching/switch_study_perm_100_60/halbach_switch_perm.4.out/strayfield5.ovf', yslice = [155])
surface_alpha(file_path='./data/stray_field/halbach_switching/switch_study_perm_100_60/halbach_switch_perm.4.out/strayfield5.ovf', yrange=(125, 176))
# plt.savefig('halbach_vary_vwidth_permalloy.pdf', dpi=1000)
plt.show()
