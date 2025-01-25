# Pepper
## Version：0
##### Version:0.0.9.6
PepperV0.0.9.6

FFT_PriorFilter: We added a Fourier prior module to the layers/custom_layer.py for prior knowledge filter.

SCTransNet: We reproduce the SCTrans model for infrared small target detection.

##### Version:0.0.9.7
get_all_images: It can get all the images in a directory and pass set the load_images to control whether it load the image or return path.it locate the datasets/dataset_utils.py.

get_img_norm_cfg: It can get the norm parameters in a directory all the images to adjust.it locate the datasets/dataset_utils.py.

DataSetLoader: It is Dataset for IRSTD datasets.it locate the IRSTD/datasets.

##### Version:0.0.9.8
IRSTDTrainer: The training of the task is integrated for IRSTD. It locate the IRSTD/callbacks.

##### Version:0.0.9.8.post1
We repair the IRSTDTrainer's Test epoch num error.

##### Version:0.0.9.9
We reproduce Wavelet Transform as Convolutions.It is located the layers/WTConv.py.

##### Version:0.0.9.10
We reproduce MLPnet on IRSTD/models.

##### Version:0.0.9.11
We reproduce MoE and HeirarchicalMoE in models/mixture_of_experts

##### Version:0.0.9.12
We design the combination of Gate and wavelet dubbed as GateWTConv in layers/GateWTConv

