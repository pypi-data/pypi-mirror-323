import shutil
from functools import partial

import keras_tuner as kt
import tensorflow.keras as keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.regularizers import l1
from tensorflow.keras.optimizers import Adam

import numpy as np

"""
    This code was recreated after instructions from

    Omid Gheibi and Danny Weyns. 2022. Lifelong self-adaptation: self-adaptation meets lifelong machine learning.
    In Proceedings of the 17th Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS '22).
    Association for Computing Machinery, New York, NY, USA, 1–12. https://doi.org/10.1145/3524844.3528052

    and their replication package https://people.cs.kuleuven.be/~danny.weyns/software/LLSAS/,
    as well as the GitHub repository
    https://github.com/dimoibiehg/lifelong_self-adaptation/blob/master/src/lifelong-learning_Second-validation-case_Gas-Delivery-System_SEAMS-2022-ready/lifelong_learner/task_manager.py

    Contributions by Ferdinand Koenig, 2025:
    - adapted Data structures, algorithm choice, and Holm's correction
    - added deletion of tasks
    - added interface for adding tasks with external trigger
    - workaround for bug in tuner directory removal on Windows OS and OneDrive environment
"""


def _compute_reconstruction_errors(autoencoder, X, verbose=True):
    """
    Compute reconstruction errors using the autoencoder.

    Parameters:
        autoencoder (keras.Model): Trained autoencoder model.
        X (np.array): Input data to reconstruct.

    Returns:
        np.array: Reconstruction errors (Euclidean norm).
    """
    predictions = autoencoder.predict(X, verbose=verbose)
    return np.linalg.norm(predictions - X, axis=1)


def _build_auto_encoder_model(hp, input_dim):
    """
    Build an autoencoder model using hyperparameters.

    Parameters:
        hp (HyperParameters): Hyperparameters to tune.
        input_dim (int): The dimensionality of the input data.

    Returns:
        keras.Model: The compiled autoencoder model.
    """
    model = Sequential()

    # Start by defining the input layer
    model.add(Input(shape=(input_dim,)))

    # Choose regularizer rate
    regulizer_rate = hp.Choice("regulizer_rate", [1e-1, 1e-2, 1e-3, 1e-4, 1e-5])

    # Define the layers depending on input_dim
    if input_dim < 30:
        # For small dimensions, fewer layers
        layer_sizes = [input_dim - 2, input_dim - 4, input_dim - 2]
    else:
        # For larger dimensions, more complex architecture
        minimum_diff = 2
        encoder_size = hp.Choice("encoder_size", [input_dim // 2, input_dim // 4, input_dim // 8, input_dim // 16])
        layer_steps = hp.Choice("layer_steps", [input_dim // 2, input_dim // 4, input_dim // 8, input_dim // 16])

        # Initialize first dense layer
        layer_sizes = [input_dim - layer_steps]

        # Add layers, decreasing in size until reaching encoder_size
        current_size = layer_sizes[0]
        while (current_size - layer_steps) > (encoder_size + minimum_diff):
            current_size -= layer_steps
            layer_sizes.append(current_size)

        # Add encoder layer
        layer_sizes.append(encoder_size)

        # Add remaining layers to reach the target size
        while sum(layer_sizes) < input_dim:
            current_size += layer_steps
            layer_sizes.append(current_size)

    # Add the layers to the model
    for size in layer_sizes:
        model.add(Dense(size, activation='relu', kernel_regularizer=l1(regulizer_rate)))

    # Add output layer
    model.add(Dense(input_dim, activation='relu', kernel_regularizer=l1(regulizer_rate)))

    # Compile the model
    learning_rate = hp.Choice("learning_rate", [1e-1, 1e-2, 1e-3, 1e-4, 1e-5])
    model.compile(optimizer=Adam(learning_rate), loss='mse')

    return model


def _generate_autoencoder(X, training_epochs):
    """
    Generate and train an autoencoder model using the input data.

    Parameters:
        X (np.array): Input data for training the autoencoder.
        training_epochs (int): The number of epochs to train the model.

    Returns:
        keras.Model: The trained autoencoder model.
    """
    model_creator = partial(_build_auto_encoder_model, input_dim=len(X[0]))
    tuner = kt.BayesianOptimization(
        model_creator,
        objective='val_loss',
        max_trials=30,
        overwrite=True,
        project_name='temp-kt-lll')  # + _with_considering_per_task_0001_with_top_1_uncertainties

    tuner.search(X, X, epochs=30, validation_split=0.2, verbose=False)

    # Try to delete the project directory after the search is completed
    try:
        shutil.rmtree(tuner.oracle.project_dir)
    except Exception:
        pass

    autoencoder = tuner.get_best_models(1)[0]

    autoencoder.fit(X, X, epochs=training_epochs, batch_size=len(X), verbose=False)

    return autoencoder
