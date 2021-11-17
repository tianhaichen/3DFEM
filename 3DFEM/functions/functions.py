##############################################################################
#                                                                            #
# This Python file is part of the 3DFEM code available at:                   #
# https://github.com/rcapillon/3DFEM                                         #
# under GNU General Public License v3.0                                      #
#                                                                            #
# Code written by Rémi Capillon                                              #
#                                                                            #
##############################################################################

import numpy as np
import copy
import matplotlib.pyplot as plt
from scipy import stats

def find_nodes_in_yzplane(points, x):
    ls_nodes = np.where(points[:,0] == x)[0].tolist()
    
    return ls_nodes
    
def find_nodes_in_xzplane(points, y):
    ls_nodes = np.where(points[:,1] == y)[0].tolist()
    
    return ls_nodes
    
def find_nodes_in_xyplane(points, z):
    ls_nodes = np.where(points[:,2] == z)[0].tolist()
    
    return ls_nodes

def find_nodes_with_coordinates(points, coords):    
    nodes = np.where(((points[:,0] == coords[0]).astype(int) + (points[:,1] == coords[1]).astype(int) + (points[:,2] == coords[2]).astype(int)) == 3)[0].tolist()
    
    return nodes

def find_nodes_in_yzplane_within_tolerance(points, x, tol):
    array_nodes = np.where(np.abs(points[:,0] - x) <= tol)[0].tolist()
    
    return array_nodes
    
def find_nodes_in_xzplane_within_tolerance(points, y, tol):
    array_nodes = np.where(np.abs(points[:,1] - y) <= tol)[0].tolist()
    
    return array_nodes
    
def find_nodes_in_xyplane_within_tolerance(points, z, tol):
    array_nodes = np.where(np.abs(points[:,2] - z) <= tol)[0].tolist()
    
    return array_nodes

def find_nodes_with_coordinates_within_tolerance(points, coords, tol):
    nodes = np.where(((np.abs(points[:,0] - coords[0]) <= tol).astype(int) + (np.abs(points[:,1] - coords[1]) <= tol).astype(int) + (np.abs(points[:,2] - coords[2]) <= tol).astype(int)) == 3)[0].tolist()
    
    return nodes

def export_mesh_to_vtk(file_name, mesh, n_points=None, n_faces=None, n_cols=None):
    file = open(file_name + ".vtk","w")
    
    if n_points == None:
        n_points = mesh.get_n_points()
    
    if n_faces == None:
        n_faces = 0
    if n_cols == None:
        n_cols = 0
    
    if n_faces == None or n_cols == None:
        for element in mesh.get_elements_list():
            element_faces = element.get_faces()
            if n_faces == None:
                n_faces += len(element_faces)
            if n_cols == None:
                for face in element_faces:
                    n_cols += 1 + len(face)
    
    str_beginning = "# vtk DataFile Version 1.0\n" + file_name + "\nASCII\n\nDATASET POLYDATA\nPOINTS " + str(n_points) + " float\n"
    file.write(str_beginning)
    
    for ii in range(n_points):
        point_ii = mesh.get_points()[ii,:]
        point_x = point_ii[0]
        point_y = point_ii[1]
        point_z = point_ii[2]
        
        str_points = "%.6f" % point_x + " " + "%.6f" % point_y + " " + "%.6f" % point_z + "\n"
        
        file.write(str_points)
    
    polygons = "POLYGONS " + str(n_faces) + " " + str(n_cols) + "\n"
    file.write(polygons)
    
    for element in mesh.get_elements_list():
        element_faces = element.get_faces()
        for face in element_faces:
            str_face = str(len(face))
            for node_num in face:
                str_face += " " + str(element.get_nodes_nums()[node_num])
            file.write(str_face + "\n")
    
    file.close()
    
def export_mode_animation(file_name, mesh, mode, scale, n_frames):
    
    n_points = mesh.get_n_points()
    
    n_faces = 0
    n_cols = 0

    for element in mesh.get_elements_list():
        element_faces = element.get_faces()
        n_faces += len(element_faces)
        for face in element_faces:
            n_cols += 1 + len(face)
    
    for ii in range(n_frames):
        deformed_mesh = copy.deepcopy(mesh)
        deformed_mesh.add_U_to_points(scale * np.sin(2 * np.pi * ii / n_frames) * mode)
        animation_frame_name = file_name + str(ii)
        export_mesh_to_vtk(animation_frame_name, deformed_mesh, n_points, n_faces, n_cols)
        
def export_U_on_mesh(file_name, mesh, vec_U, scale):
    n_points = mesh.get_n_points()
    
    n_faces = 0
    n_cols = 0

    for element in mesh.get_elements_list():
        element_faces = element.get_faces()
        n_faces += len(element_faces)
        for face in element_faces:
            n_cols += 1 + len(face)
    
    deformed_mesh = copy.deepcopy(mesh)
    deformed_mesh.add_U_to_points(scale * vec_U)
    export_mesh_to_vtk(file_name, deformed_mesh, n_points, n_faces, n_cols)
    
def export_U_newmark_animation(file_name, solver, scale):
    n_frames = len(solver.get_x_axis())
    
    n_points = solver.get_structure().get_mesh().get_n_points()
    
    n_faces = 0
    n_cols = 0

    for element in solver.get_structure().get_mesh().get_elements_list():
        element_faces = element.get_faces()
        n_faces += len(element_faces)
        for face in element_faces:
            n_cols += 1 + len(face)
    
    for ii in range(n_frames):
        deformed_mesh = copy.deepcopy(solver.get_structure().get_mesh())
        U = solver.get_vec_U_step(ii)
        deformed_mesh.add_U_to_points(scale * U)
        animation_frame_name = file_name + str(ii)
        export_mesh_to_vtk(animation_frame_name, deformed_mesh, n_points, n_faces, n_cols)
        
def plot_observed_U(file_name, solver, x_name="", y_name="", plot_type="linear"):
    vec_x = solver.get_x_axis()
    ls_dofs_observed = solver.get_structure().get_mesh().get_observed_dofs()
    mat_U = solver.get_mat_U_observed()
    
    for ii in range(len(ls_dofs_observed)):
        dof_number = ls_dofs_observed[ii]
        image_name = file_name + str(dof_number)
        
        vec_U = mat_U[ii, :]
        
        fig, ax = plt.subplots()
        if plot_type == "linear":
            ax.plot(vec_x, vec_U)
        elif plot_type == "semilogy":
            ax.semilogy(vec_x, vec_U)
        elif plot_type == "semilogx":
            ax.semilogx(vec_x, vec_U)
        elif plot_type == "loglog":
            ax.loglog(vec_x, vec_U)
        
        ax.set(xlabel = x_name, ylabel = y_name, title="DOF " + str(dof_number))
        ax.grid()
    
        fig.savefig(image_name + ".png")
        
def plot_random_observed_U(file_name, solver, confidence_level, x_name="", y_name="", plot_type="linear", add_deterministic=False):
    vec_x = solver.get_x_axis()
    ls_dofs_observed = solver.get_structure().get_mesh().get_observed_dofs()
    array_U = solver.get_array_U_rand_observed()
    
    if add_deterministic == True:
        mat_U_deterministic = solver.get_mat_U_observed()
    
    mat_mean_U = np.mean(array_U, axis=2)
    
    n_samples = array_U.shape[2]
    n_leftout_up = round(n_samples * (1 - confidence_level) / 2)
    n_leftout_down = n_leftout_up
    
    sorted_array_U = np.sort(array_U, axis=2)
        
    mat_lowerbound_U = sorted_array_U[:, :, n_leftout_down]
    mat_upperbound_U = sorted_array_U[:, :, -(1 + n_leftout_up)]
    
    for ii in range(len(ls_dofs_observed)):
        dof_number = ls_dofs_observed[ii]
        image_name = file_name + str(dof_number)
        
        vec_mean_U = mat_mean_U[ii, :]
        vec_lowerbound_U = mat_lowerbound_U[ii, :]
        vec_upperbound_U = mat_upperbound_U[ii, :]
        
        if add_deterministic == True:
            vec_U_deterministic = mat_U_deterministic[ii, :]
        
        fig, ax = plt.subplots()
        if plot_type == "linear":
            ax.plot(vec_x, vec_lowerbound_U, '-k', linewidth=0.7)
            ax.plot(vec_x, vec_upperbound_U, '-k', linewidth=0.7)
            ax.fill_between(vec_x, vec_lowerbound_U, vec_upperbound_U, color='c', alpha=0.3)
            ax.plot(vec_x, vec_mean_U, '-b')
            if add_deterministic == True:
                ax.plot(vec_x, vec_U_deterministic, '-r')
        elif plot_type == "semilogy":
            ax.semilogy(vec_x, vec_lowerbound_U, '-k', linewidth=0.7)
            ax.semilogy(vec_x, vec_upperbound_U, '-k', linewidth=0.7)
            ax.fill_between(vec_x, vec_lowerbound_U, vec_upperbound_U, color='c', alpha=0.3)
            ax.semilogy(vec_x, vec_mean_U, '-b')
            if add_deterministic == True:
                ax.plot(vec_x, vec_U_deterministic, '-r')
        elif plot_type == "semilogx":
            ax.semilogx(vec_x, vec_lowerbound_U, '-k', linewidth=0.7)
            ax.semilogx(vec_x, vec_upperbound_U, '-k', linewidth=0.7)
            ax.fill_between(vec_x, vec_lowerbound_U, vec_upperbound_U, color='c', alpha=0.3)
            ax.semilogx(vec_x, vec_mean_U, '-b')
            if add_deterministic == True:
                ax.plot(vec_x, vec_U_deterministic, '-r')
        elif plot_type == "loglog":
            ax.loglog(vec_x, vec_lowerbound_U, '-k', linewidth=0.7)
            ax.loglog(vec_x, vec_upperbound_U, '-k', linewidth=0.7)
            ax.fill_between(vec_x, vec_lowerbound_U, vec_upperbound_U, color='c', alpha=0.3)
            ax.loglog(vec_x, vec_mean_U, '-b')
            if add_deterministic == True:
                ax.plot(vec_x, vec_U_deterministic, '-r')
        
        ax.set(xlabel = x_name, ylabel = y_name, title="DOF " + str(dof_number))
        ax.grid()
    
        fig.savefig(image_name + ".png")
        
def plot_ksdensity_random_observed_U(file_name, solver, confidence_level, num_step, x_name=""):
    x = solver.get_x_axis()[num_step]
    ls_dofs_observed = solver.get_structure().get_mesh().get_observed_dofs()
    mat_U = np.squeeze(solver.get_array_U_rand_observed()[:, num_step, :])