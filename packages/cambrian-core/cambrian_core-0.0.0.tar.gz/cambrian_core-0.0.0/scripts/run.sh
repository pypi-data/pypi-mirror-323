#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=4-00:00:00
#SBATCH --job-name cambrian
#SBATCH --output=out/R-%x.%j_%a.out
#SBATCH --error=out/R-%x.%j_%a.err

[ $# -eq 0 ] && (echo "Please provide the script" && return 0)
SCRIPT=$1
shift

# Set mujoco gl depending on system
# Mac will be cgl
# all else will be egl
if [[ "$OSTYPE" == "darwin"* ]]; then
    MUJOCO_GL=${MUJOCO_GL:-cgl}
else
    MUJOCO_GL=${MUJOCO_GL:-egl}
fi

cmd="MUJOCO_GL=${MUJOCO_GL} python $SCRIPT $@"
echo "Running command: $cmd" | tee /dev/stderr
eval $cmd
