# LLL Task Manager

<img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by.png" width="100"/>

This is a Python package that implements the **Task Manager** for the Lifelong Learning Loop (LLL).  
The **Task Manager** is designed to handle task detection and management in lifelong learning systems, utilizing autoencoders for reconstruction-based task similarity detection.

The code is derived from the paper:  
**Omid Gheibi and Danny Weyns**. _Lifelong self-adaptation: self-adaptation meets lifelong machine learning._  
In Proceedings of the 17th Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS '22).  
[https://doi.org/10.1145/3524844.3528052](https://doi.org/10.1145/3524844.3528052)

This is an efficient and packaged version of the task manager code that is available here:  
[GitHub: dimoibiehg / lifelong_self-adaptation](https://github.com/dimoibiehg/lifelong_self-adaptation/blob/master/src/lifelong-learning_Second-validation-case_Gas-Delivery-System_SEAMS-2022-ready/lifelong_learner/task_manager.py)

---

**Contributions by Ferdinand Koenig, 2025:**

- Adjusted data structures, algorithm choice, and adjusted Holm’s correction for improved efficiency and correctness.
- Added functionality for task deletion.
- Developed an interface for adding tasks triggered externally.
- Implemented a workaround for a bug related to tuner directory removal on Windows OS and OneDrive environments.
- Packaged the code into a Python module for easier distribution and usage.
- Enhanced the documentation for better usability and clarity.

---
## Features

- **Task Detection**: Uses reconstruction errors to detect whether a new task is introduced or an existing task can be assigned.
- **Autoencoder-based Learning**: Tasks are managed with autoencoders that detect similarities and update their reconstruction errors accordingly.
- **Efficient Data Structures**: Data structures are optimized for task management efficiency.
- **Holm’s Correction**: Ensures statistically robust task similarity detection using Holm’s method.
- **Extensible Interface**: The package provides functions to interface with external data and manage tasks.

## Installation

You can install the package from the Python Package Index
via

```bash
pip install lll_taskmanager
```

## Key Methods

- **`detect(X)`**: Detects whether the given data `X` introduces a new task or can be assigned to an existing task.
    - Returns: `task_is_new`, `task_id`, `pvalues`
    - `task_is_new`: Boolean flag indicating whether the task is new.
    - `task_id`: ID of the task.
    - `pvalues`: List of p-values for statistical tests.

- **`add_new_task(X)`**: Manually adds a new task by creating a new autoencoder and training it on `X`.

- **`delete_task(task_id)`**: Deletes a task based on its `task_id`.

## Example and Discussion
```python
import numpy as np
from lll_taskmanager import TaskManager

task_manager = TaskManager()

# Test data
# Normal Distribution with mean = 0,  std = 1
X0_1 = np.random.normal(loc=0, scale=1, size=(100, 10))
X0_2 = np.random.normal(loc=0, scale=1, size=(100, 10))
X0_3 = np.random.normal(loc=0, scale=1, size=(70, 10))
# Normal Distribution with mean = 5,  std = 1
X1_1 = np.random.normal(loc=5, scale=1, size=(100, 10))
X1_2 = np.random.normal(loc=5, scale=1, size=(100, 10))
# Uniform Distribution
X2_1 = np.random.uniform(low=-5, high=5, size=(100, 10))
X2_2 = np.random.uniform(low=-5, high=5, size=(80, 10))

print(task_manager.detect(X0_1))
# (True, 0, {0: 1.0})
# New task with id 0
print(task_manager.detect(X0_1))
# (False, 0, {0: 0.968813007996528})
# Task 0 with significance of ~97%
print(task_manager.detect(X0_2))
# (True, 1, {0: 1.4362702261304395e-08, 1: 1.0})
# False Positive of new task.
print(task_manager.detect(X0_3))
# (True, 2, {0: 1.4917703144233305e-05, 1: 1.312398816087575e-05, 2: 1.0})
# False Positive. This is due to the different sample size.
# Under the hood, a Mann-Whitney U test is being used that depends on same sample sizes.
# Make sure that your batches have the same size for accurate results

resultX1_1 = task_manager.detect(X1_1)
print(resultX1_1)
# (True, 3, {0: 2.5495805520903834e-20, 1: 5.170804387535538e-31, 2: 4.60666565667063e-27, 3: 1.0})
# Correct assignment to new task (3)
print(task_manager.detect(X1_2))
# (False, 3, {0: 0.0006248683334076798, 1: 3.4916777010682185e-19, 2: 5.33830704127903e-25, 3: 0.008729918349922575})
# Correct assignment

print(task_manager.detect(X2_1))
# (True, 4, {0: 1.1996356111739001e-43, 1: 5.254326993995392e-33, 2: 8.018213024078718e-27, 3: 8.457238847010412e-44, 4: 1.0})
# Correct assignment to new task (4)
print(task_manager.detect(X2_2))
# (False, 4, {0: 2.776922809508148e-37, 1: 2.4074810570805218e-29, 2: 1.6242946841985236e-24, 3: 1.7855840454361994e-37, 4: 0.718388260985277})
# Correct assignment to task 4

task_manager.delete_task(resultX1_1[1])
# Delete task of X1_1: Expected Behavior: Do not detect it anymore. When task reoccurs, assign new ID
print(task_manager.detect(X1_2))
# (True, 5, {0: 1.6014167268343994e-40, 1: 7.64579055060309e-33, 2: 3.553684842364269e-27, 4: 8.688713292514744e-20, 5: 1.0})
# Correctly assigned to new task, as old task (3) was deleted.
print(task_manager.detect(X1_1))
# (True, 6, {0: 1.3943531255201782e-40, 1: 5.254326993995392e-33, 2: 3.553684842364269e-27, 4: 5.743734298732715e-24, 5: 0.00019656616032667692, 6: 1.0})
# False Positive. Should have been assigned to task 5.
```
The use of the Mann-Whitney U test to compare reconstruction errors between training data and inference data appears to be a novel approach introduced by Gheibi and Weyns, and it has not been applied previously. Consequently, extensive testing and evaluation are necessary to assess its effectiveness.

In some cases, the Autoencoders may not be able to accurately capture the underlying distribution, as observed in the first and last False Positive cases. To address this limitation, future work could explore the use of Variational Autoencoders (VAEs) to better approximate the probability density functions and improve task detection accuracy.

## Supported Versions and Compatibility

Currently, this package supports Python versions **3.9** and **3.10** due to **TensorFlow's** compatibility constraints.  
Therefore, the dependencies are pinned to **TensorFlow 2.11**.

If you'd like to use this package with other versions of Python or TensorFlow, you're welcome to contribute by forking the repository and submitting a pull request with the updated versions in `pytoml`.

### Tested and Confirmed Platforms:
- **Ubuntu**: Python 3.9 and 3.10
- **Windows**: Python 3.9 and 3.10
- **macOS**: Python 3.9


## License
<img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by.png" width="150"/>

This project is licensed under the **CC BY 4.0** license, which allows you to share and adapt the material, as long as you provide appropriate credit.

[CC BY 4.0 License](https://creativecommons.org/licenses/by/4.0/deed)

## References

- **Omid Gheibi and Danny Weyns**. _Lifelong self-adaptation: self-adaptation meets lifelong machine learning._  
  In Proceedings of the 17th Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS '22).  
  [doi.org/10.1145/3524844.3528052](https://doi.org/10.1145/3524844.3528052)
- [GitHub: dimoibiehg / lifelong_self-adaptation](https://github.com/dimoibiehg/lifelong_self-adaptation/)

## Links
- 🐍 PyPI: [pypi.org/project/lll-taskmanager/](https://pypi.org/project/lll-taskmanager/)
- 🛠 GitHub Repository: [ferdinand-koenig / llltaskmanager](https://github.com/ferdinand-koenig/llltaskmanager)


## Contact

For any questions or feedback, feel free to contact me:

**Ferdinand Koenig**  
Email: ferdinand (-at-) koenix.de

## Citing
Please give appropriate credit when using this code by citing both the
[reference paper](https://doi.org/10.1145/3524844.3528052) **and** this Python package:

```bibtex
@software{omid_lll_taskmanager_2025,
    author = {Gheibi, Omid and Weyns, Danny and Koenig, Ferdinand},
    title = {LLL TaskManager: A Python Package for Lifelong Unsupervised Task Management in Machine Learning},
    month = jan,
    year = 2025,
    url = {https://github.com/ferdinand-koenig/llltaskmanager},
    license = {CC BY 4.0}
}

@inproceedings{10.1145/3524844.3528052,
    author = {Gheibi, Omid and Weyns, Danny},
    title = {Lifelong self-adaptation: self-adaptation meets lifelong machine learning},
    year = {2022},
    isbn = {9781450393058},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3524844.3528052},
    doi = {10.1145/3524844.3528052},
    abstract = {In the past years, machine learning (ML) has become a popular approach to support self-adaptation. While ML techniques enable dealing with several problems in self-adaptation, such as scalable decision-making, they are also subject to inherent challenges. In this paper, we focus on one such challenge that is particularly important for self-adaptation: ML techniques are designed to deal with a set of predefined tasks associated with an operational domain; they have problems to deal with new emerging tasks, such as concept shift in input data that is used for learning. To tackle this challenge, we present lifelong self-adaptation: a novel approach to self-adaptation that enhances self-adaptive systems that use ML techniques with a lifelong ML layer. The lifelong ML layer tracks the running system and its environment, associates this knowledge with the current tasks, identifies new tasks based on differentiations, and updates the learning models of the self-adaptive system accordingly. We present a reusable architecture for lifelong self-adaptation and apply it to the case of concept drift caused by unforeseen changes of the input data of a learning model that is used for decision-making in self-adaptation. We validate lifelong self-adaptation for two types of concept drift using two cases.},
    booktitle = {Proceedings of the 17th Symposium on Software Engineering for Adaptive and Self-Managing Systems},
    pages = {1–12},
    numpages = {12},
    location = {Pittsburgh, Pennsylvania},
    series = {SEAMS '22}
}
```