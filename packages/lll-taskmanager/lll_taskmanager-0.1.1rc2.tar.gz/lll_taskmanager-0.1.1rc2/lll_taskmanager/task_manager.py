from dataclasses import dataclass
from typing import Dict
import warnings
import os

from .autoencoder_utils import _generate_autoencoder, _compute_reconstruction_errors, _build_auto_encoder_model

import tensorflow.keras as keras

from sklearn.preprocessing import MinMaxScaler
import numpy as np
from scipy.stats import mannwhitneyu

"""
    This code was recreated after instructions from

    Omid Gheibi and Danny Weyns. 2022. Lifelong self-adaptation: self-adaptation meets lifelong machine learning.
    In Proceedings of the 17th Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS '22).
    Association for Computing Machinery, New York, NY, USA, 1–12. https://doi.org/10.1145/3524844.3528052

    and their replication package https://people.cs.kuleuven.be/~danny.weyns/software/LLSAS/,
    as well as the GitHub
    https://github.com/dimoibiehg/lifelong_self-adaptation/blob/master/src/lifelong-learning_Second-validation-case_Gas-Delivery-System_SEAMS-2022-ready/lifelong_learner/task_manager.py
    
    Contributions by Ferdinand Koenig, 2025:
    - adapted Data structures, algorithm choice, and Holm's correction
    - added deletion of tasks
    - added interface for adding tasks with external trigger
    - workaround for bug in tuner directory removal on Windows OS and OneDrive environment
"""


class TaskManager:
    @dataclass
    class TaskAutoencoder:
        """
        A data class representing an autoencoder task.

        Attributes:
            autoencoder (keras.Model): The trained autoencoder model for the task.
            training_reconstruction_errors (np.array): A numpy array of reconstruction errors during training.
        """
        autoencoder: keras.Model
        training_reconstruction_errors: np.array

    def __init__(self, scaler=None, update_scaler=True, significance_level=0.05, verbose=False):
        """
        Initializes the TaskManager with the given parameters.

        Parameters:
            scaler (sklearn.preprocessing): A scaler for input data. If None, MinMaxScaler is used by default.
            update_scaler (bool): A flag to indicate whether the scaler should be updated with new data.
            significance_level (float): The significance level for statistical tests.
                Provides when a task is seen as similar.
        """
        self.task_autoencoders: Dict[int, TaskManager.TaskAutoencoder] = {}
        self.scaler = scaler or MinMaxScaler(feature_range=(-1, 1))  # Use MinMaxScaler if scaler is None
        self.update_scaler = update_scaler
        self.SIGNIFICANCE = significance_level
        self.verbose = verbose
        if not self.verbose:
            warnings.filterwarnings("ignore")
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    def detect(self, X):
        """
        Detect whether a new task is introduced or an existing task can be assigned.

        This method computes reconstruction errors and performs statistical tests to determine
        whether the input data `X` is similar to any existing tasks or if it introduces a new task.

        Parameters:
            X (np.array): The input data for task detection.

        Returns:
            tuple: A tuple (task_is_new, task_id, pvalues)
                - task_is_new (bool): A flag indicating whether the task is new.
                - task_id (int): The ID of the detected task (either new or existing).
                - pvalues (list): A list of p-values for statistical tests. These mean can be interpreted as
                    similarities to the tasks
        """
        task_is_new = True
        if self.scaler:
            if self.update_scaler:
                self.scaler.partial_fit(X)
            # Scale the input data and optionally update the scaler
            X = self.scaler.transform(X)
        if not self.task_autoencoders:
            # First task. Initialization
            autoencoder = _generate_autoencoder(X, training_epochs=30)
            training_reconstruction_errors = _compute_reconstruction_errors(autoencoder, X, verbose=self.verbose)
            task_id = 0
            self.task_autoencoders[task_id] = \
                TaskManager.TaskAutoencoder(autoencoder=autoencoder,
                                            training_reconstruction_errors=training_reconstruction_errors)

        else:
            pvalues = self._calculate_p_values(X)

            max_pvalue_idx = max(pvalues, key=pvalues.get)  # Index of encoder with the highest similarity (p-value)
            sorted_pvalues = sorted(pvalues)

            # Holm's method
            holm_thresholds = [self.SIGNIFICANCE / (len(sorted_pvalues) - idx_pval) for idx_pval in
                               range(len(sorted_pvalues))]

            # Decide if it's a new task
            # Similarity p is too low for all autoencoders
            # Reject if all fail
            reject = all(p <= threshold for p, threshold in zip(sorted_pvalues, holm_thresholds))

            # If no similarity is found (reject is False), assign to an existing task
            if not reject:
                task_is_new = False
                task_id = max_pvalue_idx  # Assign to the encoder with the highest similarity

                # Keep training the autoencoder and append the new reconstruction errors
                autoencoder = self.task_autoencoders[task_id].autoencoder
                autoencoder.fit(X, X, verbose=self.verbose)
                self.task_autoencoders[task_id].training_reconstruction_errors = (
                    np.concatenate((self.task_autoencoders[task_id].training_reconstruction_errors,
                                   _compute_reconstruction_errors(autoencoder, X, verbose=self.verbose))))
            else:
                # No similar task found; initialize a new task
                task_id = self.add_new_task(X)

        pvalues = self._calculate_p_values(X)
        return task_is_new, task_id, pvalues

    def _calculate_p_values(self, X, return_dict=True, window_size=5):
        """
        Calculate p-values for each task's autoencoder by comparing reconstruction errors.

        Parameters:
            X (np.array): The input data to calculate p-values for.
            return_dict (bool): If True, return the p-values in a dictionary with their task_id as the key.
            window_size (int): The size of the sliding window for calculating the mean reconstruction errors
                in the statistical test.

        Returns:
            list or dict: A list of p-values corresponding to each task's autoencoder,
                          or a dictionary if return_dict is True, with task_id as the key.
        """
        pvalues = []
        pvalue_dict = {}

        for task_id, task_autoencoder in self.task_autoencoders.items():
            reconstruction_errors = \
                _compute_reconstruction_errors(task_autoencoder.autoencoder, X, verbose=self.verbose)

            # sliding mean over mini-batches of <window_size>
            re_mean = np.convolve(reconstruction_errors, np.ones(window_size) / window_size, mode='valid')
            tre_mean = np.convolve(task_autoencoder.training_reconstruction_errors,
                                   np.ones(window_size) / window_size, mode='valid')

            _, p = mannwhitneyu(re_mean, tre_mean, use_continuity=True, alternative='two-sided')

            if return_dict:
                pvalue_dict[task_id] = p
            else:
                pvalues.append(p)

        if return_dict:
            return pvalue_dict
        else:
            return pvalues

    def add_new_task(self, X):
        """
        Add a new task by creating and training a new autoencoder.

        Parameters:
            X (np.array): The input data for training the new autoencoder.

        Returns:
            int: The ID of the newly added task.
        """
        autoencoder = _generate_autoencoder(X, training_epochs=60)
        training_reconstruction_errors = _compute_reconstruction_errors(autoencoder, X, verbose=self.verbose)
        task_id = max(self.task_autoencoders.keys()) + 1
        self.task_autoencoders[task_id] = \
            TaskManager.TaskAutoencoder(autoencoder=autoencoder,
                                        training_reconstruction_errors=training_reconstruction_errors)
        return task_id

    def delete_task(self, task_id):
        """
        Delete a task from the task manager.

        Parameters:
            task_id (int): The ID of the task to be deleted.
        """
        del self.task_autoencoders[task_id]
