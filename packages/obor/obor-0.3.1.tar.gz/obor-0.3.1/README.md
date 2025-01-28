# Obor
A simple pyTorch additional utilities library created for my paper

# Docs
This package contains

1. utils
contains:
- train()
- create_data_loader()
- train()

2. pruner
- prune_bbs()
- prune_low_magnitude

3. plotter
- plot_dynamic()
- plot_training_history()

# Created By
- name: Mohamad Doddy Sujatmiko
- email: doddy.s@protonmail.com
- github: github.com/doddy-s

# Change Log
## v0.1.0:
- initialize project
- add utils sub-package
- add train() function to simply train pytorch model
- add create_data_loader() function to simply create dataloader needed for training

## v0.2.0:
- add pruner sub-package
- add prune_bbs() function to prune pytorch model with "BANK BALANCE SPARSITY" method

### v0.2.1:
- add type annotation to train() and craete_data_loader()
- minor print change

### v0.3.0
- add prune_low_magnitude() function to prune pytorch model with "LOW MAGNITUDE DETECTION" method
- fix prune_bbs() algorithm
- add train() function to utils
- add plotter sub-package
- add plot_dynamic() function
- add plot_training_history() function

### v0.3.1
- hotfix, check if Arial font-family exist before applying in matplotlib