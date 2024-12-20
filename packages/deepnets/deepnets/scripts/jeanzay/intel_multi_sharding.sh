#!/bin/bash
#SBATCH --job-name=test
#SBATCH --output=/gpfswork/rech/iqu/uvm91ap/slurm_bin/%j.out
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=10
#SBATCH --gres=gpu:4
#SBATCH --time=00:05:00
#SBATCH --constraint=v100-32g
#SBATCH --account=iqu@v100
#SBATCH --qos=qos_gpu-dev
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rajah.nutakki@polytechnique.edu

module purge
module load gcc/12.2.0 openmpi/4.1.5-cuda anaconda-py3
conda activate gpu_amd

export NETKET_EXPERIMENTAL_SHARDING=1
export MULTI_PROCESS_GPU=1
export JAX_PLATFORM_NAME=gpu

#test_file=/gpfswork/rech/iqu/uvm91ap/repos/netket_pro/deepnets/multi/test_checkpoint.py
#test_file=/gpfswork/rech/iqu/uvm91ap/repos/netket_pro/deepnets/multi/test.py
run_file=/gpfswork/rech/iqu/uvm91ap/repos/netket_pro/deepnets/optimization/run.py

#srun -n $SLURM_NTASKS python $run_file --L 6 --J 0.8 1.0 --n_blocks 1 --features 24 --expansion_factor=2 --downsample_factor=2 --kernel_width=3 --output_head=Vanilla --samples_per_rank=100 --chains_per_rank=10 --discard_fraction=0.0 --iters 50  --lr 0.01 --alpha 1 --diag_shift 0.01 --diag_shift_end 1 --r=1e-06 --chunk_size=250 --save_every=10 --symmetries=0 --symmetry_ramping=0 --momentum=0.9 --double_precision=1 --time_it=0 --show_progress=1 --checkpoint=1 --seed=280 --save_base /mnt/beegfs/workdir/rajah.nutakki/test/
srun python $run_file --L 6 --J 0.8 1.0 --n_blocks 1 --features 24 --expansion_factor=2 --downsample_factor=2 --kernel_width=3 --output_head=Vanilla --samples_per_rank=100 --chains_per_rank=10 --discard_fraction=0.0 --iters 20 20 10 10  --lr 0.01 0.01 0.01 0.01 --alpha 1 1 1 1 --diag_shift 0.01 0.01 0.01 0.01 --diag_shift_end 1 1 1 1 --r=1e-06 --chunk_size=250 --save_every=10 --symmetries=0 --symmetry_ramping=1 --momentum=0.9 --double_precision=1 --time_it=0 --show_progress=1 --checkpoint=1 --seed=280 --save_base /mnt/beegfs/workdir/rajah.nutakki/test/
#srun -n $SLURM_NTASKS python $test_file