#!/bin/bash --login
set -e
conda activate asf-snow
exec python /asf-snow/src/asf_snow/sentinel_1c_snow.py "$@"
