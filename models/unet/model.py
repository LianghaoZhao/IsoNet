from mwr.models.unet import builder,builder_fullconv,builder_fullconv_old
from tensorflow.keras.layers import Input,Add,Activation
from tensorflow.keras.models import Model
from mwr.losses.losses import loss_mae,loss_mse,new_mae
from mwr.losses.wedge_power import wedge_power_gain
from tensorflow.keras.optimizers import Adam
def Unet(filter_base=32,
        depth=2,
        convs_per_depth=2,
        kernel=(3,3),
        batch_norm=False,
        dropout=0.0,
        pool=(2,2),residual = True,
        last_activation = 'linear',
        loss = 'mae',
        lr = 0.0004):

    # model = builder.build_unet(filter_base,depth,convs_per_depth,
    #            kernel,
    #            batch_norm,
    #            dropout,
    #            pool)
#     model = builder_fullconv.build_unet(filter_base,depth,convs_per_depth,
#             kernel,
#             batch_norm,
#             dropout,
#             pool)
    import os
    import sys
    cwd = os.getcwd()
    sys.path.insert(0,cwd)
    import train_settings 
    model = builder_fullconv_old.build_unet(train_settings)
    
    #***** Construct complete model from unet output
    inputs = Input((None,None,None,1))
    unet_out = model(inputs) 
    if residual:
        outputs = Add()([unet_out, inputs])
    else:
        outputs = unet_out
    outputs = Activation(activation=last_activation)(outputs)
    model = Model(inputs=inputs, outputs=outputs)
    optimizer = Adam(lr=lr)
    if loss == 'mae' or loss == 'mse':
        metrics = ('mse', 'mae')
        _metrics = [eval('loss_%s()' % m) for m in metrics]
    elif loss == 'binary_crossentropy':
        _metrics = ['accuracy']
    model.compile(optimizer=optimizer, loss=new_mae, metrics=_metrics,run_eagerly=True)
    return model