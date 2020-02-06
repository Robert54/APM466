# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import scipy.optimize as optimize

par_value = 100

def bond_ytm(price, par_value, term, coupon, freq=2, guess=0.05):
    # term: The number of coupon payment term left to be completed
    coupon = coupon * par_value / float(freq)
    term_l = [(i + 1) / freq for i in range(int(term * freq))]
    # x in this place is the ytm
    ytm_func = lambda x: sum([coupon / ((1 + x/freq) ** (freq * t)) for t in term_l]) + par_value / (1 + x/freq) ** (freq * term) - price        
    return optimize.newton(ytm_func, guess) * 100

def ytm_matrix_generator(bonds, date_list):
    # ytm data matrix
    ytm_matrix = pd.DataFrame(columns=date_list, index=bonds["Bond"]) 
    for date_index in range(len(date_list)):
        curr_date = date_list[date_index]
        for bond_index in range(len(bonds)):
            maturity_date = bonds["Maturity Date"][bond_index]
            # 6 months == half year == 182 days
            term = (pd.to_datetime(maturity_date) - pd.to_datetime(curr_date)).days // 182 + 1
            closing_price = float(bonds[curr_date][bond_index])
            coupon_rate = float(bonds["Coupon"][bond_index])
            ytm = bond_ytm(closing_price, par_value, term, coupon_rate)
            ytm_matrix.iloc[bond_index, date_index] = ytm
    return ytm_matrix

def plot_ytm(bonds, ytm_matrix, date_list):
    # create plots of ytm       
    plt.figure(figsize=(15, 5), dpi= 80)
    fig = plt.subplot(1, 1, 1)
    for date_index in range(len(date_list)):
        fig.plot(bonds["Times to Maturity"], ytm_matrix.iloc[:, date_index], label=date_list[date_index])
    plt.xlim(0, 5)
    plt.xlabel("Time to Maturity (Years)")
    plt.ylabel("Yield to Maturity (%)")
    plt.title("YTM curve")
    fig.legend(ytm_matrix.columns, loc='lower right', ncol=2)
    plt.grid(True, axis = 'both')
    plt.show()

def zero_coupon_bond(price, curr_date, maturity_date):
    time_to_maturity = (pd.to_datetime(maturity_date) - pd.to_datetime(curr_date)).days / 365
    zcb_rate = -np.log(price / par_value) / time_to_maturity
    return zcb_rate * 100

def spot_rate(bonds, spot_matrix, date_index, bond_index, date_list):
    curr_date = date_list[date_index]
    # days remaining 
    num_days_remain = (pd.to_datetime(bonds["Maturity Date"][bond_index]) - pd.to_datetime(curr_date)).days % 182
    clean_price = float(bonds[curr_date][bond_index])
    coupon_rate = float(bonds["Coupon"][bond_index])
    accrued_interest = num_days_remain / 365 * coupon_rate * clean_price
    dirty_price =  accrued_interest + clean_price
    if bond_index == 1:
        t1 = bonds["Times to Maturity"][0]
        t2 = bonds["Times to Maturity"][1]
    else:
        maturity_date = bonds["Maturity Date"]
        first_period = (pd.to_datetime(maturity_date[bond_index - 1]) - pd.to_datetime(maturity_date[bond_index - 2])).days
        second_period = (pd.to_datetime(maturity_date[bond_index]) - pd.to_datetime(maturity_date[bond_index - 2])).days
        t1 = first_period / 365
        t2 = second_period / 365
    c_t1 = float(bonds["Coupon"][bond_index - 1] * 100) / 2
    r_t1 = np.exp((spot_matrix.iloc[bond_index - 1, date_index]) * t1)
    c_t2 = 100 + float(bonds["Coupon"][bond_index] * 100) / 2
    r_t2 = np.log(c_t2 / (dirty_price - (c_t1 / r_t1))) / t2    
    return r_t2 * 100

def spot_matrix_generator(bonds, date_list):
    # spot rate data matrix
    spot_matrix = pd.DataFrame(columns=date_list, index=bonds["Bond"])
    zero_coupon_bond_l = []
    for date_index in range(len(date_list)):
        curr_date = date_list[date_index]
        spot_rate_zcb = zero_coupon_bond(bonds[curr_date][0], curr_date, bonds["Maturity Date"][date_index])
        zero_coupon_bond_l.append(spot_rate_zcb)
    spot_matrix.iloc[0,:] = zero_coupon_bond_l
    for date_index in range(len(date_list)):
        curr_date = date_list[date_index]
        for bond_index in range(len(bonds)):
            if bond_index != 0:
                spot_r = spot_rate(bonds, spot_matrix, date_index, bond_index, date_list)
                spot_matrix[curr_date][bond_index] = abs(spot_r)
    return spot_matrix

def plot_spot(bonds, spot_matrix, date_list):
    # create plots of ytm       
    plt.figure(figsize=(15,5), dpi= 80)
    fig = plt.subplot(1, 1, 1)
    for date_index in range(len(date_list)):
        fig.plot(bonds["Times to Maturity"], spot_matrix.iloc[:, date_index], label=date_list[date_index])
    plt.xlim(0, 5)
    plt.xlabel("Time to Maturity (Years)")
    plt.ylabel("Spot rate (%)")
    plt.title("Spot rate curve")
    fig.legend(spot_matrix.columns, loc='lower right', ncol=2)
    plt.grid(True, axis = 'both')
    plt.show()

def forward_matrix_generator(spot_matrix, date_list):
    forward_matrix = pd.DataFrame(columns=date_list, index=["1yr-1yr","1yr-2yr", "1yr-3yr", "1yr-4yr"])
    # Only for bonds mature in March  
    for date_index in range(len(date_list)):
        base_spot_rate = spot_matrix.iloc[0, date_index] / 100
        for bond_index in range(0, 4):
            numerator = (1 + spot_matrix.iloc[(bond_index + 1) * 2, date_index] / 100) ** (bond_index + 2)
            denominator = (1 + base_spot_rate) 
            forward = (numerator / denominator) ** (1 / (bond_index + 1)) - 1
            forward_matrix.iloc[bond_index, date_index] = forward
    return forward_matrix

def plot_forward(bonds, forward_matrix, date_list):
    #plot of forward rate       
    plt.figure(figsize=(15,5), dpi= 80)
    fig = plt.subplot(1, 1, 1)
    for date_index in range(len(date_list)):
        fig.plot(forward_matrix.iloc[:, date_index])
    plt.xlabel("Time to Maturity (Years)")
    plt.ylabel("Forward rate (%)")
    plt.title("Forward rate curve")
    fig.legend(forward_matrix.columns, loc='upper right', ncol=2)
    plt.grid(True, axis = 'both')
    plt.show()

def yield_covariance(ytm_matrix):   
    cov_mat = np.zeros([9, 5])
    for i in range(0, 5):
        for j in range(1, 10):
            X_ij = np.log((ytm_matrix.iloc[i * 2, j]) / (ytm_matrix.iloc[i * 2, j - 1]))
            cov_mat[j - 1, i] = X_ij
    ytm_cov = np.cov(cov_mat.T)
    eig_val, eig_vec = np.linalg.eig(ytm_cov)
    print(ytm_cov)
    print((eig_val, eig_vec))
    print(eig_val[0] / sum(eig_val) * 100)


def forward_covarience(forward_matrix):
    cov_mat = np.zeros([9, 4])
    for i in range(0, 4):
        for j in range(1, 10):
            X_ij = np.log((forward_matrix.iloc[i, j]) / (forward_matrix.iloc[i, j - 1]))
            cov_mat[j - 1, i] = X_ij
    forward_cov = np.cov(cov_mat.T)
    eig_val, eig_vec = np.linalg.eig(forward_cov)
    print(forward_cov)
    print((eig_val, eig_vec))
    print(eig_val[0] / sum(eig_val) * 100)

if __name__ == '__main__':
    bonds = pd.read_excel(r'/Users/zhangtingyu/Desktop/APM466/A1/Ten Bonds Selected (with closing price).xlsx') 
    date_list = list(bonds.columns.values)[5:]
    bonds["Times to Maturity"] = [round((pd.to_datetime(bonds["Maturity Date"][i]) - pd.to_datetime('1/15/2020')).days / 365, 3) for i in range(len(date_list))]
    ytm_matrix = ytm_matrix_generator(bonds, date_list)
    # plot_ytm(bonds, ytm_matrix, date_list)
    spot_matrix = spot_matrix_generator(bonds, date_list)
    # plot_spot(bonds, spot_matrix, date_list)
    forward_matrix = forward_matrix_generator(spot_matrix, date_list)
    # plot_forward(bonds, forward_matrix, date_list)
    yield_covariance(ytm_matrix)
    forward_covarience(forward_matrix)
    
    


