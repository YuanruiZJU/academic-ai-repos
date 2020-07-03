#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon 5 Jun 2017.

Fit MGP-RNN model on full data, with Lanczos and CG to speed things up.

@author: josephfutoma
"""

import tensorflow as tf
from tensorflow.python.framework import ops
import numpy as np
from time import time
from sklearn.metrics import roc_auc_score, average_precision_score
import sys
    
from util import pad_rawdata,SE_kernel,OU_kernel,dot,CG,Lanczos,block_CG,block_Lanczos

#####
##### Numpy functions used to simulate data and pad raw data to feed into TF
#####

def gen_MGP_params(M):
    """
    Generate some MGP params for each class. 
    Assume MGP is stationary and zero mean, so hyperparams are just:
        Kf: covariance across time series
        length: length scale for shared kernel across time series
        noise: noise level for each time series
    """
    true_Kfs = []
    true_noises = []
    true_lengths = []
    
    #Class 0
    tmp = rs.normal(0,.2,(M,M))
    true_Kfs.append(np.dot(tmp,tmp.T))
    true_lengths.append(1.0)
    true_noises.append(np.linspace(.02,.08,M))
    
    #Class 1
    tmp = rs.normal(0,.4,(M,M))
    true_Kfs.append(np.dot(tmp,tmp.T))
    true_lengths.append(2.0)
    true_noises.append(np.linspace(.1,.2,M))
    
    return true_Kfs,true_noises,true_lengths
    
    
def sim_dataset(num_encs,M,n_covs,n_meds,pos_class_rate = 0.5,trainfrac=0.2):
    """
    Returns everything we need to run the model.
    
    Each simulated patient encounter consists of:
        Multivariate time series (labs/vitals)
        Static baseline covariates
        Medication administration times (no values; just a point process)
    """
    true_Kfs,true_noises,true_lengths = gen_MGP_params(M)
        
    end_times = np.random.uniform(10,50,num_encs) #last observation time of the encounter
    num_obs_times = np.random.poisson(end_times,num_encs)+3 #number of observation time points per encounter, increase with  longer series 
    num_obs_values = np.array(num_obs_times*M*trainfrac,dtype="int")
    #number of inputs to RNN. will be a grid on integers, starting at 0 and ending at next integer after end_time
    num_rnn_grid_times = np.array(np.floor(end_times)+1,dtype="int") 
    rnn_grid_times = []
    labels = rs.binomial(1,pos_class_rate,num_encs)                      
    
    T = [];  #actual observation times
    Y = []; ind_kf = []; ind_kt = [] #actual data; indices pointing to which lab, which time
    baseline_covs = np.zeros((num_encs,n_covs)) 
    #each contains an array of size num_rnn_grid_times x n_meds 
    #   simulates a matrix of indicators, where each tells which meds have been given between the
    #   previous grid time and the current.  in practice you will have actual medication administration 
    #   times and will need to convert to this form, for feeding into the RNN
    meds_on_grid = [] 

    print('Simming data...')
    for i in range(num_encs):
        if i%500==0:
            print('%d/%d' %(i,num_encs))
        obs_times = np.insert(np.sort(np.random.uniform(0,end_times[i],num_obs_times[i]-1)),0,0)
        T.append(obs_times)
        l = labels[i]
        y_i,ind_kf_i,ind_kt_i = sim_multitask_GP(obs_times,true_lengths[l],true_noises[l],true_Kfs[l],trainfrac)
        Y.append(y_i); ind_kf.append(ind_kf_i); ind_kt.append(ind_kt_i)
        rnn_grid_times.append(np.arange(num_rnn_grid_times[i]))
        if l==0: #sim some different baseline covs; meds for 2 classes
            baseline_covs[i,:int(n_covs/2)] = rs.normal(0.1,1.0,int(n_covs/2))
            baseline_covs[i,int(n_covs/2):] = rs.binomial(1,0.2,int(n_covs/2))
            meds = rs.binomial(1,.02,(num_rnn_grid_times[i],n_meds))
        else:
            baseline_covs[i,:int(n_covs/2)] = rs.normal(0.2,1.0,int(n_covs/2))
            baseline_covs[i,int(n_covs/2):] = rs.binomial(1,0.1,int(n_covs/2))
            meds = rs.binomial(1,.04,(num_rnn_grid_times[i],n_meds))
        meds_on_grid.append(meds)
    
    T = np.array(T)
    Y = np.array(Y); ind_kf = np.array(ind_kf); ind_kt = np.array(ind_kt)
    meds_on_grid = np.array(meds_on_grid)
    rnn_grid_times = np.array(rnn_grid_times)
    
    return (num_obs_times,num_obs_values,num_rnn_grid_times,rnn_grid_times,
            labels,T,Y,ind_kf,ind_kt,meds_on_grid,baseline_covs)
    
def sim_multitask_GP(times,length,noise_vars,K_f,trainfrac):
    """
    draw from a multitask GP.  
    
    we continue to assume for now that the dim of the input space is 1, ie just time

    M: number of tasks (labs/vitals/time series)
    
    train_frac: proportion of full M x N data matrix Y to include

    """
    M = np.shape(K_f)[0]
    N = len(times)
    n = N*M
    K_t = OU_kernel_np(length,times) #just a correlation function
    Sigma = np.diag(noise_vars)

    K = np.kron(K_f,K_t) + np.kron(Sigma,np.eye(N)) + 1e-6*np.eye(n)
    L_K = np.linalg.cholesky(K)
    
    y = np.dot(L_K,np.random.normal(0,1,n)) #Draw normal
    
    #get indices of which time series and which time point, for each element in y
    ind_kf = np.tile(np.arange(M),(N,1)).flatten('F') #vec by column
    ind_kx = np.tile(np.arange(N),(M,1)).flatten()
               
    #randomly dropout some fraction of fully observed time series
    perm = np.random.permutation(n)
    n_train = int(trainfrac*n)
    train_inds = perm[:n_train]
    
    y_ = y[train_inds]
    ind_kf_ = ind_kf[train_inds]
    ind_kx_ = ind_kx[train_inds]
    
    return y_,ind_kf_,ind_kx_

def OU_kernel_np(length,x):
    """ just a correlation function, for identifiability 
    """
    x1 = np.reshape(x,[-1,1]) #colvec
    x2 = np.reshape(x,[1,-1]) #rowvec
    K_xx = np.exp(-np.abs(x1-x2)/length)    
    return K_xx

#####
##### Tensorflow functions 
#####

def draw_GP(Yi,Ti,Xi,ind_kfi,ind_kti):
    """ 
    given GP hyperparams and data values at observation times, draw from 
    conditional GP
    
    inputs:
        length,noises,Lf,Kf: GP params
        Yi: observation values
        Ti: observation times
        Xi: grid points (new times for rnn)
        ind_kfi,ind_kti: indices into Y
    returns:
        draws from the GP at the evenly spaced grid times Xi, given hyperparams and data
    """  
    ny = tf.shape(Yi)[0]
    K_tt = OU_kernel(length,Ti,Ti)
    D = tf.diag(noises)

    grid_f = tf.meshgrid(ind_kfi,ind_kfi) #same as np.meshgrid
    Kf_big = tf.gather_nd(Kf,tf.stack((grid_f[0],grid_f[1]),-1))
    
    grid_t = tf.meshgrid(ind_kti,ind_kti) 
    Kt_big = tf.gather_nd(K_tt,tf.stack((grid_t[0],grid_t[1]),-1))

    Kf_Ktt = tf.multiply(Kf_big,Kt_big)

    DI_big = tf.gather_nd(D,tf.stack((grid_f[0],grid_f[1]),-1))
    DI = tf.diag(tf.diag_part(DI_big)) #D kron I
    
    #data covariance. 
    #Either need to take Cholesky of this or use CG / block CG for matrix-vector products
    Ky = Kf_Ktt + DI + 1e-6*tf.eye(ny)   

    ### build out cross-covariances and covariance at grid
    
    nx = tf.shape(Xi)[0]
    
    K_xx = OU_kernel(length,Xi,Xi)
    K_xt = OU_kernel(length,Xi,Ti)
                       
    ind = tf.concat([tf.tile([i],[nx]) for i in range(M)],0)
    grid = tf.meshgrid(ind,ind)
    Kf_big = tf.gather_nd(Kf,tf.stack((grid[0],grid[1]),-1))
    ind2 = tf.tile(tf.range(nx),[M])
    grid2 = tf.meshgrid(ind2,ind2)
    Kxx_big =  tf.gather_nd(K_xx,tf.stack((grid2[0],grid2[1]),-1))
    
    K_ff = tf.multiply(Kf_big,Kxx_big) #cov at grid points           
                 
    full_f = tf.concat([tf.tile([i],[nx]) for i in range(M)],0)            
    grid_1 = tf.meshgrid(full_f,ind_kfi,indexing='ij')
    Kf_big = tf.gather_nd(Kf,tf.stack((grid_1[0],grid_1[1]),-1))
    full_x = tf.tile(tf.range(nx),[M])
    grid_2 = tf.meshgrid(full_x,ind_kti,indexing='ij')
    Kxt_big = tf.gather_nd(K_xt,tf.stack((grid_2[0],grid_2[1]),-1))

    K_fy = tf.multiply(Kf_big,Kxt_big)
       
    #now get draws!
    y_ = tf.reshape(Yi,[-1,1])
    #Mu = tf.matmul(K_fy,CG(Ky,y_)) #May be faster with CG for large problems
    Ly = tf.cholesky(Ky)
    Mu = tf.matmul(K_fy,tf.cholesky_solve(Ly,y_))
    
    #TODO: it's worth testing to see at what point computation speedup of Lanczos algorithm is useful & needed.
    # For smaller examples, using Cholesky will probably be faster than this unoptimized Lanczos implementation.
    # Likewise for CG and BCG vs just taking the Cholesky of Ky once
    """
    #Never need to explicitly compute Sigma! Just need matrix products with Sigma in Lanczos algorithm
    def Sigma_mul(vec):
        # vec must be a 2d tensor, shape (?,?) 
        return tf.matmul(K_ff,vec) - tf.matmul(K_fy,block_CG(Ky,tf.matmul(tf.transpose(K_fy),vec))) 
    
    def small_draw():   
        return Mu + tf.matmul(tf.cholesky(Sigma),xi)
    def large_draw():             
        return Mu + block_Lanczos(Sigma_mul,xi,n_mc_smps) #no need to explicitly reshape Mu
    
    BLOCK_LANC_THRESH = 1000
    draw = tf.cond(tf.less(nx*M,BLOCK_LANC_THRESH),small_draw,large_draw)     
    """
            
    xi = tf.random_normal((nx*M,n_mc_smps))
    Sigma = K_ff - tf.matmul(K_fy,tf.cholesky_solve(Ly,tf.transpose(K_fy))) + 1e-6*tf.eye(tf.shape(K_ff)[0]) 
    draw = Mu + tf.matmul(tf.cholesky(Sigma),xi)
    draw_reshape = tf.transpose(tf.reshape(tf.transpose(draw),[n_mc_smps,M,nx]),perm=[0,2,1])
    return draw_reshape    
        
def get_GP_samples(Y,T,X,ind_kf,ind_kt,num_obs_times,num_obs_values,
                   num_rnn_grid_times,med_cov_grid):
    """
    returns samples from GP at evenly-spaced gridpoints
    """ 
    grid_max = tf.shape(X)[1]
    Z = tf.zeros([0,grid_max,input_dim])
    
    N = tf.shape(T)[0] #number of observations
        
    #setup tf while loop (have to use this bc loop size is variable)
    def cond(i,Z):
        return i<N
    
    def body(i,Z):
        Yi = tf.reshape(tf.slice(Y,[i,0],[1,num_obs_values[i]]),[-1])
        Ti = tf.reshape(tf.slice(T,[i,0],[1,num_obs_times[i]]),[-1])
        ind_kfi = tf.reshape(tf.slice(ind_kf,[i,0],[1,num_obs_values[i]]),[-1])
        ind_kti = tf.reshape(tf.slice(ind_kt,[i,0],[1,num_obs_values[i]]),[-1])
        Xi = tf.reshape(tf.slice(X,[i,0],[1,num_rnn_grid_times[i]]),[-1])
        X_len = num_rnn_grid_times[i]
                
        GP_draws = draw_GP(Yi,Ti,Xi,ind_kfi,ind_kti)
        pad_len = grid_max-X_len #pad by this much
        padded_GP_draws = tf.concat([GP_draws,tf.zeros((n_mc_smps,pad_len,M))],1) 
        
        medcovs = tf.slice(med_cov_grid,[i,0,0],[1,-1,-1])
        tiled_medcovs = tf.tile(medcovs,[n_mc_smps,1,1])
        padded_GPdraws_medcovs = tf.concat([padded_GP_draws,tiled_medcovs],2)
        
        Z = tf.concat([Z,padded_GPdraws_medcovs],0)        

        return i+1,Z  
    
    i = tf.constant(0)
    i,Z = tf.while_loop(cond,body,loop_vars=[i,Z],
                shape_invariants=[i.get_shape(),tf.TensorShape([None,None,None])])

    return Z

def get_preds(Y,T,X,ind_kf,ind_kt,num_obs_times,num_obs_values,
              num_rnn_grid_times,med_cov_grid):
    """
    helper function. takes in (padded) raw datas, samples MGP for each observation, 
    then feeds it all through the LSTM to get predictions.
    
    inputs:
        Y: array of observation values (labs/vitals). batchsize x batch_maxlen_y
        T: array of observation times (times during encounter). batchsize x batch_maxlen_t
        ind_kf: indiceste into each row of Y, pointing towards which lab/vital. same size as Y
        ind_kt: indices into each row of Y, pointing towards which time. same size as Y
        num_obs_times: number of times observed for each encounter; how long each row of T really is
        num_obs_values: number of lab values observed per encounter; how long each row of Y really is
        num_rnn_grid_times: length of even spaced RNN grid per encounter
                    
    returns:
        predictions (unnormalized log probabilities) for each MC sample of each obs
    """
    Z = get_GP_samples(Y,T,X,ind_kf,ind_kt,num_obs_times,num_obs_values,
                       num_rnn_grid_times,med_cov_grid) #batchsize*num_MC x batch_maxseqlen x num_inputs  
    Z.set_shape([None,None,input_dim]) #somehow lost shape info, but need this
    N = tf.shape(T)[0] #number of observations 
    #duplicate each entry of seqlens, to account for multiple MC samples per observation 
    seqlen_dupe = tf.reshape(tf.tile(tf.expand_dims(num_rnn_grid_times,1),[1,n_mc_smps]),[N*n_mc_smps])
      
    #with tf.variable_scope("",reuse=True):
    outputs, states = tf.nn.dynamic_rnn(cell=stacked_lstm,inputs=Z,
                                            dtype=tf.float32,
                                            sequence_length=seqlen_dupe)
    
    final_outputs = states[n_layers-1][1]
    preds =  tf.matmul(final_outputs, out_weights) + out_biases  
    return preds

def get_probs_and_accuracy(preds,O):
    """
    helper function. we have a prediction for each MC sample of each observation
    in this batch.  need to distill the multiple preds from each MC into a single
    pred for this observation.  also get accuracy. use true probs to get ROC, PR curves in sklearn
    """
    all_probs = tf.exp(preds[:,1] - tf.reduce_logsumexp(preds, axis = 1)) #normalize; and drop a dim so only prob of positive case
    N = tf.cast(tf.shape(preds)[0]/n_mc_smps,tf.int32) #actual number of observations in preds, collapsing MC samples                    
    
    #predicted probability per observation; collapse the MC samples
    probs = tf.zeros([0]) #store all samples in a list, then concat into tensor at end
    #setup tf while loop (have to use this bc loop size is variable)
    def cond(i,probs):
        return i < N
    def body(i,probs):
        probs = tf.concat([probs,[tf.reduce_mean(tf.slice(all_probs,[i*n_mc_smps],[n_mc_smps]))]],0)
        return i+1,probs    
    i = tf.constant(0)
    i,probs = tf.while_loop(cond,body,loop_vars=[i,probs],shape_invariants=[i.get_shape(),tf.TensorShape([None])])
        
    #compare to truth; just use cutoff of 0.5 for right now to get accuracy
    correct_pred = tf.equal(tf.cast(tf.greater(probs,0.5),tf.int32), O)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32)) 
    return probs,accuracy

if __name__ == "__main__":    
    seed = 8675309
    rs = np.random.RandomState(seed) #fixed seed in np
    
    #####
    ##### Setup ground truth and sim some data from a GP
    #####
    num_encs=5000
    M=10
    n_covs=10
    n_meds=5
    
    (num_obs_times,num_obs_values,num_rnn_grid_times,rnn_grid_times,labels,times,
       values,ind_lvs,ind_times,meds_on_grid,covs) = sim_dataset(num_encs,M,n_covs,n_meds)
    N_tot = len(labels) #total encounters
    
    train_test_perm = rs.permutation(N_tot)
    val_frac = 0.1 #fraction of full data to set aside for testing
    te_ind = train_test_perm[:int(val_frac*N_tot)]
    tr_ind = train_test_perm[int(val_frac*N_tot):]
    Nte = len(te_ind); Ntr = len(tr_ind)
    
    #Break everything out into train/test
    covs_tr = covs[tr_ind,:]; covs_te = covs[te_ind,:]
    labels_tr = labels[tr_ind]; labels_te = labels[te_ind]
    times_tr = times[tr_ind]; times_te = times[te_ind]
    values_tr = values[tr_ind]; values_te = values[te_ind]
    ind_lvs_tr = ind_lvs[tr_ind]; ind_lvs_te = ind_lvs[te_ind]
    ind_times_tr = ind_times[tr_ind]; ind_times_te = ind_times[te_ind]
    meds_on_grid_tr = meds_on_grid[tr_ind]; meds_on_grid_te = meds_on_grid[te_ind]
    num_obs_times_tr = num_obs_times[tr_ind]; num_obs_times_te = num_obs_times[te_ind]
    num_obs_values_tr = num_obs_values[tr_ind]; num_obs_values_te = num_obs_values[te_ind]
    rnn_grid_times_tr = rnn_grid_times[tr_ind]; rnn_grid_times_te = rnn_grid_times[te_ind]     
    num_rnn_grid_times_tr = num_rnn_grid_times[tr_ind]; num_rnn_grid_times_te = num_rnn_grid_times[te_ind]  
                           
    print("data fully setup!")    
    sys.stdout.flush()

    #####
    ##### Setup model and graph
    ##### 
    
    # Learning Parameters
    learning_rate = 0.001 #NOTE may need to play around with this or decay it
    L2_penalty = 1e-2 #NOTE may need to play around with this some or try additional regularization
    #TODO: add dropout regularization
    training_iters = 25 #num epochs
    batch_size = 50 #NOTE may want to play around with this
    test_freq = Ntr/batch_size #eval on test set after this many batches
    
    # Network Parameters
    n_hidden = 20 # hidden layer num of features; assumed same
    n_layers = 3 # number of layers of stacked LSTMs
    n_classes = 2 #binary outcome
    input_dim = M+n_meds+n_covs #dimensionality of input sequence.
    n_mc_smps = 25
    
    # Create graph
    ops.reset_default_graph()
    sess = tf.Session()      
    
    ##### tf Graph - inputs 
    
    #observed values, times, inducing times; padded to longest in the batch
    Y = tf.placeholder("float", [None,None]) #batchsize x batch_maxdata_length
    T = tf.placeholder("float", [None,None]) #batchsize x batch_maxdata_length
    ind_kf = tf.placeholder(tf.int32, [None,None]) #index tasks in Y vector
    ind_kt = tf.placeholder(tf.int32, [None,None]) #index inputs in Y vector
    X = tf.placeholder("float", [None,None]) #grid points. batchsize x batch_maxgridlen
    med_cov_grid = tf.placeholder("float", [None,None,n_meds+n_covs]) #combine w GP smps to feed into RNN
    
    O = tf.placeholder(tf.int32, [None]) #labels. input is NOT as one-hot encoding; convert at each iter
    num_obs_times = tf.placeholder(tf.int32, [None]) #number of observation times per encounter 
    num_obs_values = tf.placeholder(tf.int32, [None]) #number of observation values per encounter 
    num_rnn_grid_times = tf.placeholder(tf.int32, [None]) #length of each grid to be fed into RNN in batch
    
    N = tf.shape(Y)[0]                         
                                                                                                                                                                                      
    #also make O one-hot encoding, for the loss function
    O_dupe_onehot = tf.one_hot(tf.reshape(tf.tile(tf.expand_dims(O,1),[1,n_mc_smps]),[N*n_mc_smps]),n_classes)

    ##### tf Graph - variables to learn
        
    ### GP parameters (unconstrained)
    
    #in fully separable case all labs share same time-covariance
    log_length = tf.Variable(tf.random_normal([1],mean=1,stddev=0.1),name="GP-log-length") 
    length = tf.exp(log_length)
    
    #different noise level of each lab
    log_noises = tf.Variable(tf.random_normal([M],mean=-2,stddev=0.1),name="GP-log-noises")
    noises = tf.exp(log_noises)
    
    #init cov between labs
    L_f_init = tf.Variable(tf.eye(M),name="GP-Lf")
    Lf = tf.matrix_band_part(L_f_init,-1,0)
    Kf = tf.matmul(Lf,tf.transpose(Lf))

    ### RNN params

    # Create network    
    stacked_lstm = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.BasicLSTMCell(n_hidden) for _ in range(n_layers)])

    # Weights at the last layer given deep LSTM output
    out_weights = tf.Variable(tf.random_normal([n_hidden, n_classes],stddev=0.1),name="Softmax/W")
    out_biases = tf.Variable(tf.random_normal([n_classes],stddev=0.1),name="Softmax/b")

    ##### Get predictions and feed into optimization
    preds = get_preds(Y,T,X,ind_kf,ind_kt,num_obs_times,num_obs_values,num_rnn_grid_times,med_cov_grid)    
    probs,accuracy = get_probs_and_accuracy(preds,O)
    
    # Define optimization problem
    loss_fit = tf.reduce_sum(tf.nn.softmax_cross_entropy_with_logits(logits=preds,labels=O_dupe_onehot))
    with tf.variable_scope("",reuse=True):
        loss_reg = L2_penalty*tf.reduce_sum(tf.square(out_weights))
        for i in range(n_layers):
            loss_reg = L2_penalty+tf.reduce_sum(tf.square(tf.get_variable('rnn/multi_rnn_cell/cell_'+str(i)+'/basic_lstm_cell/kernel')))
    loss = loss_fit + loss_reg                  
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)
   
    ##### Initialize globals and get ready to start!
    sess.run(tf.global_variables_initializer())
    print("Graph setup!")
     
    #setup minibatch indices
    starts = np.arange(0,Ntr,batch_size)
    ends = np.arange(batch_size,Ntr+1,batch_size)
    if ends[-1]<Ntr: 
        ends = np.append(ends,Ntr)
    num_batches = len(ends) 
    
    T_pad_te,Y_pad_te,ind_kf_pad_te,ind_kt_pad_te,X_pad_te,meds_cov_pad_te = pad_rawdata(
                    times_te,values_te,ind_lvs_te,ind_times_te,rnn_grid_times_te,meds_on_grid_te,covs_te) 
    
    ##### Main training loop
    saver = tf.train.Saver(max_to_keep = None)

    total_batches = 0
    for i in range(training_iters):
        #train
        epoch_start = time()
        print("Starting epoch "+"{:d}".format(i))
        perm = rs.permutation(Ntr)
        batch = 0 
        for s,e in zip(starts,ends):
            batch_start = time()
            inds = perm[s:e]
            T_pad,Y_pad,ind_kf_pad,ind_kt_pad,X_pad,meds_cov_pad = pad_rawdata(
                    times_tr[inds],values_tr[inds],ind_lvs_tr[inds],ind_times_tr[inds],
                    rnn_grid_times_tr[inds],meds_on_grid_tr[inds],covs_tr[inds,:]) 
            feed_dict={Y:Y_pad,T:T_pad,ind_kf:ind_kf_pad,ind_kt:ind_kt_pad,X:X_pad,
               med_cov_grid:meds_cov_pad,num_obs_times:num_obs_times_tr[inds],
               num_obs_values:num_obs_values_tr[inds],
               num_rnn_grid_times:num_rnn_grid_times_tr[inds],O:labels_tr[inds]}                         
                     
            loss_,_ = sess.run([loss,train_op],feed_dict)
            
            print("Batch "+"{:d}".format(batch)+"/"+"{:d}".format(num_batches)+\
                  ", took: "+"{:.3f}".format(time()-batch_start)+", loss: "+"{:.5f}".format(loss_))
            sys.stdout.flush()
            batch += 1; total_batches += 1

            if total_batches % test_freq == 0: #Check val set every so often for early stopping
                #TODO: may also want to check validation performance at additional X hours back
                #from the event time, as well as just checking performance at terminal time
                #on the val set, so you know if it generalizes well further back in time as well 
                test_t = time()
                feed_dict={Y:Y_pad_te,T:T_pad_te,ind_kf:ind_kf_pad_te,ind_kt:ind_kt_pad_te,X:X_pad_te,
                       med_cov_grid:meds_cov_pad_te,num_obs_times:num_obs_times_te,
                       num_obs_values:num_obs_values_te,num_rnn_grid_times:num_rnn_grid_times_te,O:labels_te}                               
                te_probs,te_acc,te_loss = sess.run([probs,accuracy,loss],feed_dict)     
                te_auc = roc_auc_score(labels_te, te_probs)
                te_prc = average_precision_score(labels_te, te_probs)   
                print("Epoch "+str(i)+", seen "+str(total_batches)+" total batches. Testing Took "+\
                      "{:.2f}".format(time()-test_t)+\
                      ". OOS, "+str(0)+" hours back: Loss: "+"{:.5f}".format(te_loss)+ \
                      " Acc: "+"{:.5f}".format(te_acc)+", AUC: "+ \
                      "{:.5f}".format(te_auc)+", AUPR: "+"{:.5f}".format(te_prc))
                sys.stdout.flush()    
            
                #create a folder and put model checkpoints there
                #saver.save(sess, "MGP-RNN-test/", global_step=total_batches)
        print("Finishing epoch "+"{:d}".format(i)+", took "+\
              "{:.3f}".format(time()-epoch_start))     
        
        ### Takes about ~1-2 secs per batch of 50 at these settings, so a few minutes each epoch
        ### Should converge reasonably quickly on this toy example with these settings in a few epochs